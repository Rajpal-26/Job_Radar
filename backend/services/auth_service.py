# ==============================================================================
# WATERMARK: Rajpal Singh Tanwar
# Copyright (c) 2026 Rajpal Singh Tanwar. All rights reserved.
# JobRadar Authentication, Multi-Tenancy & Credit Service
# ==============================================================================

import os
import time
import json
import base64
import hmac
import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from flask import request, make_response
from models.database import db
from models.auth import User, Tenant, TenantMembership, CreditWallet, CreditLedger, UserSession

SECRET_KEY = os.getenv("SECRET_KEY", "jobradar-production-super-secret-auth-key-2026")
TOKEN_EXPIRY_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRY_MINUTES", "1440"))  # 24 hours for seamless UX
WELCOME_CREDITS = 10  # As per Career Platform Feature Specification Section 5

# ==============================================================================
# CRYPTOGRAPHY & JWT HELPERS (Zero external crypto dependency requirement)
# ==============================================================================

def hash_password(password: str) -> str:
    """Hash password using PBKDF2-HMAC-SHA256 with cryptographically random salt."""
    salt = secrets.token_hex(16)
    key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000)
    return f"pbkdf2_sha256${salt}${key.hex()}"

def verify_password(password: str, hashed: str) -> bool:
    """Verify password against PBKDF2 hash."""
    if not hashed or "$" not in hashed:
        return False
    try:
        parts = hashed.split("$")
        if len(parts) != 3 or parts[0] != "pbkdf2_sha256":
            return False
        salt = parts[1]
        stored_key = parts[2]
        key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000)
        return hmac.compare_digest(key.hex(), stored_key)
    except Exception:
        return False

def _b64_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("utf-8").rstrip("=")

def _b64_decode(data: str) -> bytes:
    padding = "=" * ((4 - len(data) % 4) % 4)
    return base64.urlsafe_b64decode(data + padding)

def create_jwt_token(payload: dict, expires_in_minutes: int = TOKEN_EXPIRY_MINUTES) -> str:
    """Generate compact HS256 JWT Token."""
    header = {"alg": "HS256", "typ": "JWT"}
    payload_copy = payload.copy()
    payload_copy["iat"] = int(time.time())
    payload_copy["exp"] = int(time.time()) + (expires_in_minutes * 60)
    
    header_b64 = _b64_encode(json.dumps(header).encode("utf-8"))
    payload_b64 = _b64_encode(json.dumps(payload_copy).encode("utf-8"))
    
    signature = hmac.new(SECRET_KEY.encode("utf-8"), f"{header_b64}.{payload_b64}".encode("utf-8"), hashlib.sha256).digest()
    sig_b64 = _b64_encode(signature)
    
    return f"{header_b64}.{payload_b64}.{sig_b64}"

def verify_jwt_token(token: str) -> dict:
    """Validate HS256 JWT Token signature and expiration."""
    if not token or token.count(".") != 2:
        return None
    try:
        header_b64, payload_b64, sig_b64 = token.split(".")
        expected_sig = hmac.new(SECRET_KEY.encode("utf-8"), f"{header_b64}.{payload_b64}".encode("utf-8"), hashlib.sha256).digest()
        actual_sig = _b64_decode(sig_b64)
        
        if not hmac.compare_digest(expected_sig, actual_sig):
            return None
            
        payload = json.loads(_b64_decode(payload_b64).decode("utf-8"))
        if payload.get("exp", 0) < time.time():
            return None  # Expired
            
        return payload
    except Exception:
        return None


# ==============================================================================
# AUTH SERVICE BUSINESS LOGIC
# ==============================================================================

class AuthService:

    @staticmethod
    def provision_user(email: str, password: str = None, full_name: str = None, auth_provider: str = "email", provider_user_id: str = None, avatar_url: str = None) -> tuple[User, Tenant, CreditWallet]:
        """Atomically provisions a user, default personal workspace tenant, membership, and credit wallet with welcome credits."""
        email_clean = email.strip().lower()
        existing_user = User.query.filter_by(email=email_clean).first()
        if existing_user:
            raise ValueError(f"An account with email {email_clean} already exists. Please sign in.")

        # 1. Create User
        user = User(
            email=email_clean,
            hashed_password=hash_password(password) if password else None,
            full_name=full_name or email_clean.split("@")[0].replace(".", " ").title(),
            avatar_url=avatar_url,
            auth_provider=auth_provider,
            provider_user_id=provider_user_id,
            global_role="job_seeker",
            plan="free",
            is_active=True,
            is_verified=True if auth_provider != "email" else False
        )
        db.session.add(user)
        db.session.flush()

        # 2. Create Personal Workspace Tenant
        base_slug = email_clean.split("@")[0].lower()
        slug = f"{base_slug}-{secrets.token_hex(3)}"
        tenant = Tenant(
            name=f"{user.full_name}'s Workspace",
            slug=slug,
            tenant_type="personal",
            sso_domain=email_clean.split("@")[1] if "@" in email_clean else None
        )
        db.session.add(tenant)
        db.session.flush()

        # 3. Create Tenant Membership
        membership = TenantMembership(
            user_id=user.id,
            tenant_id=tenant.id,
            role="owner",
            is_default=True
        )
        db.session.add(membership)

        # 4. Create Credit Wallet with Welcome Credits
        wallet = CreditWallet(
            user_id=user.id,
            tenant_id=tenant.id,
            balance=WELCOME_CREDITS,
            subscription_credits=WELCOME_CREDITS,
            topup_credits=0,
            promo_credits=0
        )
        db.session.add(wallet)
        db.session.flush()

        # 5. Record Welcome Credits in Immutable Audit Ledger
        ledger_entry = CreditLedger(
            wallet_id=wallet.id,
            user_id=user.id,
            amount=WELCOME_CREDITS,
            balance_after=WELCOME_CREDITS,
            transaction_type="grant",
            reference_id="welcome_signup_bonus",
            description="Initial welcome grant for 10 free AI Job Search & Auto-Apply credits"
        )
        db.session.add(ledger_entry)

        db.session.commit()
        return user, tenant, wallet

    @staticmethod
    def authenticate_user(email: str, password: str) -> tuple[User, str, Tenant, CreditWallet]:
        """Authenticate user with email/password and issue session JWT."""
        email_clean = email.strip().lower()
        user = User.query.filter_by(email=email_clean).first()
        if not user or not user.hashed_password:
            raise ValueError("Invalid email or password.")
            
        if not verify_password(password, user.hashed_password):
            raise ValueError("Invalid email or password.")
            
        if not user.is_active:
            raise ValueError("This account has been deactivated. Please contact support.")

        return AuthService._create_user_session(user)

    @staticmethod
    def social_login(provider: str, email: str, full_name: str = None, provider_user_id: str = None, avatar_url: str = None) -> tuple[User, str, Tenant, CreditWallet]:
        """Handle 1-Click Social Sign-In (Google / GitHub). Auto-provisions on first login."""
        email_clean = email.strip().lower()
        user = User.query.filter_by(email=email_clean).first()

        if not user:
            # First time signup via OAuth
            user, _, _ = AuthService.provision_user(
                email=email_clean,
                full_name=full_name,
                auth_provider=provider,
                provider_user_id=provider_user_id or f"{provider}_{secrets.token_hex(6)}",
                avatar_url=avatar_url
            )
        else:
            # Update social profile info
            if avatar_url and not user.avatar_url:
                user.avatar_url = avatar_url
            if full_name and not user.full_name:
                user.full_name = full_name
            user.is_verified = True
            db.session.commit()

        return AuthService._create_user_session(user)

    @staticmethod
    def enterprise_sso_lookup(email: str) -> dict:
        """Inspects email domain to verify if company has active SAML/OIDC SSO enforced."""
        if "@" not in email:
            return {"sso_enforced": False, "domain": None}
        domain = email.split("@")[1].strip().lower()
        
        tenant = Tenant.query.filter_by(sso_domain=domain).first()
        if tenant and tenant.sso_enforced:
            return {
                "sso_enforced": True,
                "domain": domain,
                "tenant_name": tenant.name,
                "tenant_id": tenant.id,
                "idp_redirect_url": f"/api/auth/sso/saml/login?domain={domain}"
            }
        return {"sso_enforced": False, "domain": domain}

    @staticmethod
    def _create_user_session(user: User, tenant_id: str = None) -> tuple[User, str, Tenant, CreditWallet]:
        """Creates session and issues JWT token for user."""
        user.last_login_at = datetime.now(timezone.utc)
        
        # Resolve active tenant
        membership = None
        if tenant_id:
            membership = TenantMembership.query.filter_by(user_id=user.id, tenant_id=tenant_id).first()
        if not membership:
            membership = TenantMembership.query.filter_by(user_id=user.id, is_default=True).first()
        if not membership:
            membership = TenantMembership.query.filter_by(user_id=user.id).first()

        active_tenant = membership.tenant if membership else None
        active_wallet = CreditWallet.query.filter_by(user_id=user.id).first()

        # Generate JWT Token payload
        session_id = secrets.token_hex(16)
        token_payload = {
            "sub": user.id,
            "email": user.email,
            "name": user.full_name,
            "role": membership.role if membership else user.global_role,
            "global_role": user.global_role,
            "plan": user.plan,
            "tenant_id": active_tenant.id if active_tenant else None,
            "tenant_name": active_tenant.name if active_tenant else "Personal",
            "session_id": session_id,
            "session_version": user.session_version
        }
        
        token = create_jwt_token(token_payload)

        # Store session record in DB
        session_record = UserSession(
            user_id=user.id,
            tenant_id=active_tenant.id if active_tenant else None,
            session_token=session_id,
            ip_address=request.remote_addr if request else "127.0.0.1",
            user_agent=request.headers.get("User-Agent", "Unknown") if request else "Local",
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=TOKEN_EXPIRY_MINUTES)
        )
        db.session.add(session_record)
        db.session.commit()

        return user, token, active_tenant, active_wallet

    @staticmethod
    def get_current_user():
        """Extract and validate current authenticated user from cookie or Authorization header."""
        token = None
        
        # 1. Check HttpOnly Cookie
        if request and "jobradar_token" in request.cookies:
            token = request.cookies.get("jobradar_token")
            
        # 2. Check Authorization Bearer Header
        elif request and "Authorization" in request.headers:
            auth_header = request.headers.get("Authorization")
            if auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]

        if not token:
            return None

        payload = verify_jwt_token(token)
        if not payload or "sub" not in payload:
            return None

        user = User.query.get(payload["sub"])
        if not user or not user.is_active:
            return None

        # Check global session invalidation
        if payload.get("session_version", 1) != user.session_version:
            return None

        # Attach dynamic payload metadata
        user.active_tenant_id = payload.get("tenant_id")
        user.active_tenant_name = payload.get("tenant_name", "Personal")
        user.active_role = payload.get("role", user.global_role)
        
        wallet = CreditWallet.query.filter_by(user_id=user.id).first()
        user.credit_balance = wallet.balance if wallet else 0

        return user

    @staticmethod
    def revoke_current_session():
        """Revoke current user session and return clear cookie response."""
        user = AuthService.get_current_user()
        if user and request and "jobradar_token" in request.cookies:
            payload = verify_jwt_token(request.cookies.get("jobradar_token"))
            if payload and "session_id" in payload:
                session_rec = UserSession.query.filter_by(session_token=payload["session_id"]).first()
                if session_rec:
                    session_rec.is_revoked = True
                    db.session.commit()
        return True

    @staticmethod
    def revoke_all_sessions(user_id: str):
        """Global logout: Increments session_version to instantly invalidate all active JWTs."""
        user = User.query.get(user_id)
        if user:
            user.session_version += 1
            UserSession.query.filter_by(user_id=user_id).update({"is_revoked": True})
            db.session.commit()
            return True
        return False
