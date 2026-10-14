# ==============================================================================
# WATERMARK: Rajpal Singh Tanwar
# Copyright (c) 2026 Rajpal Singh Tanwar. All rights reserved.
# JobRadar Auth, Multi-Tenancy, RBAC & Credit Ledger Models
# ==============================================================================

from datetime import datetime, timezone
import uuid
from models.database import db

def generate_uuid():
    return str(uuid.uuid4())

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    hashed_password = db.Column(db.String(255), nullable=True)
    full_name = db.Column(db.String(150), nullable=True)
    avatar_url = db.Column(db.Text, nullable=True)
    auth_provider = db.Column(db.String(50), default="email")  # 'email', 'google', 'github', 'sso_saml'
    provider_user_id = db.Column(db.String(255), nullable=True)
    global_role = db.Column(db.String(50), default="job_seeker")  # 'job_seeker', 'recruiter', 'tenant_admin', 'super_admin'
    plan = db.Column(db.String(50), default="free")  # 'free', 'pro', 'premium', 'enterprise'
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    session_version = db.Column(db.Integer, default=1)  # For global logout invalidation
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    last_login_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    memberships = db.relationship("TenantMembership", backref="user", cascade="all, delete-orphan", lazy="dynamic")
    wallets = db.relationship("CreditWallet", backref="user", cascade="all, delete-orphan", lazy="dynamic")
    sessions = db.relationship("UserSession", backref="user", cascade="all, delete-orphan", lazy="dynamic")

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "full_name": self.full_name or self.email.split("@")[0].title(),
            "avatar_url": self.avatar_url,
            "auth_provider": self.auth_provider,
            "role": self.global_role,
            "plan": self.plan,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_login_at": self.last_login_at.isoformat() if self.last_login_at else None
        }


class Tenant(db.Model):
    __tablename__ = "tenants"

    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    name = db.Column(db.String(150), nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False, index=True)
    tenant_type = db.Column(db.String(50), default="personal")  # 'personal', 'organization', 'team'
    sso_domain = db.Column(db.String(255), nullable=True, index=True)
    sso_enforced = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    memberships = db.relationship("TenantMembership", backref="tenant", cascade="all, delete-orphan", lazy="dynamic")
    wallets = db.relationship("CreditWallet", backref="tenant", cascade="all, delete-orphan", lazy="dynamic")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "slug": self.slug,
            "tenant_type": self.tenant_type,
            "sso_domain": self.sso_domain,
            "sso_enforced": self.sso_enforced,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class TenantMembership(db.Model):
    __tablename__ = "tenant_memberships"

    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    user_id = db.Column(db.String(36), db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    tenant_id = db.Column(db.String(36), db.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    role = db.Column(db.String(50), default="member")  # 'owner', 'admin', 'recruiter', 'member', 'viewer'
    allocated_credits = db.Column(db.Integer, default=0)
    is_default = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "tenant_id": self.tenant_id,
            "role": self.role,
            "is_default": self.is_default
        }


class CreditWallet(db.Model):
    __tablename__ = "credit_wallets"

    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    user_id = db.Column(db.String(36), db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    tenant_id = db.Column(db.String(36), db.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=True)
    balance = db.Column(db.Integer, default=10)  # Starting with 10 welcome credits as in Spec
    subscription_credits = db.Column(db.Integer, default=10)
    topup_credits = db.Column(db.Integer, default=0)
    promo_credits = db.Column(db.Integer, default=0)
    holds = db.Column(db.Integer, default=0)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "wallet_id": self.id,
            "user_id": self.user_id,
            "tenant_id": self.tenant_id,
            "balance": self.balance,
            "available": max(0, self.balance - self.holds),
            "subscription_credits": self.subscription_credits,
            "topup_credits": self.topup_credits,
            "promo_credits": self.promo_credits,
            "holds": self.holds,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class CreditLedger(db.Model):
    __tablename__ = "credit_ledger"

    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    wallet_id = db.Column(db.String(36), db.ForeignKey("credit_wallets.id", ondelete="CASCADE"), nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    amount = db.Column(db.Integer, nullable=False)  # Positive for additions, negative for deductions
    balance_after = db.Column(db.Integer, nullable=False)
    transaction_type = db.Column(db.String(50), nullable=False)  # 'grant', 'purchase', 'hold', 'capture', 'release', 'refund', 'expire', 'adjust'
    reference_id = db.Column(db.String(255), nullable=True)  # e.g., 'welcome_bonus', 'auto_apply_job_12', 'stripe_tx_123'
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "id": self.id,
            "amount": self.amount,
            "balance_after": self.balance_after,
            "transaction_type": self.transaction_type,
            "reference_id": self.reference_id,
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class UserSession(db.Model):
    __tablename__ = "user_sessions"

    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    user_id = db.Column(db.String(36), db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    tenant_id = db.Column(db.String(36), nullable=True)
    session_token = db.Column(db.String(255), unique=True, nullable=False, index=True)
    refresh_token_hash = db.Column(db.String(255), nullable=True)
    ip_address = db.Column(db.String(100), nullable=True)
    user_agent = db.Column(db.Text, nullable=True)
    is_revoked = db.Column(db.Boolean, default=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
