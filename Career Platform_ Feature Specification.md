[Overview](#overview)[Authentication](#auth)[RBAC](#rbac)[Credit system](#credits)[Plans](#plans)[Resume storage](#resume)[ATS matching](#ats)[Auto apply](#apply)[Recruiter check](#recruiter)[Payments](#payments)[Gmail notifications](#email)[Data and API](#data)[Non-functional](#nfr)[Rollout](#rollout)

# Career Platform: Feature Specification

Covers sign-in and tenancy, role-based access, a credit-metered feature set (resume optimization, ATS scoring, auto apply, recruiter checks), paid plans, payments and email notifications. Version 1.0, October 2026.

## 1. Overview

Users sign in once, hold credits granted by a plan or bought as top-ups, and spend them on AI-assisted job-search actions. Every spend is recorded in an append-only ledger. Access to features depends on role and plan; spending depends on credit balance.

| Module | Purpose |
| --- | --- |
| Identity | OAuth/OIDC login, SSO, sessions, tenant membership |
| RBAC | Roles, permissions, plan entitlements |
| Credits | Wallet, ledger, holds, refunds, expiry |
| Resume | Upload, parsing, versioned storage, AI optimization |
| ATS | Resume-to-job matching and 0-100 score |
| Auto apply | Queued job applications on the user's behalf |
| Recruiter check | Profile verification of a recruiter or poster |
| Billing | Plans, checkout, subscriptions, invoices, webhooks |
| Notifications | Gmail-delivered transactional email |

### Reference architecture

- Web client (SPA) and API gateway in front of stateless services.
- PostgreSQL for relational data, Redis for sessions, rate limits and queues, S3-compatible object storage for files.
- Workers consume queues for parsing, scoring, applying and sending email.
- All requests carry a `tenant_id` resolved from the session; every query is scoped by it.

## 2. Authentication, login and logout

### 2.1 Sign-in methods

- **Social login:** Google and GitHub through OAuth 2.0 authorization code flow with PKCE. Microsoft can be added using the same provider interface.
- **Email and password:** optional fallback, Argon2id hashing, email verification required, breached-password check.
- **Magic link:** single-use link, 15 minute expiry.
- **Enterprise SSO:** SAML 2.0 and OIDC per tenant, configured by the tenant admin with metadata or discovery URL.

### 2.2 Multi-tenant model

- A **tenant** is an organization or an individual workspace. A **user** is a global identity that can belong to many tenants through a `membership` carrying a role.
- Individual job seekers get a personal tenant on signup.
- Tenant resolution: by subdomain (`acme.app.com`), by email domain mapping for SSO, or by a tenant switcher after login.
- Account linking: the same verified email across providers maps to one user. Linking a new provider requires an active session or a verified email.

### 2.3 One-click SSO flow

1. User clicks "Continue with Google/GitHub", or enters a work email.
2. For a work email, the domain is looked up; if a tenant has SSO enforced, the user is redirected to that tenant's IdP.
3. The API creates `state`, `nonce` and PKCE verifier, stores them in Redis for 10 minutes and redirects to the provider.
4. The callback validates `state`, exchanges the code, verifies the ID token signature, issuer, audience and nonce.
5. First sign-in: create user, personal tenant, wallet and welcome credits in one transaction. Returning: update last login.
6. Issue session and redirect to the saved destination. If the user has several tenants, show the switcher.

- Just-in-time provisioning for SSO users; optional SCIM for deprovisioning in enterprise.
- Tenant admins may enforce SSO, which disables password and social login for that tenant.

### 2.4 Sessions and tokens

- Short-lived access JWT (15 min) with `sub`, `tenant_id`, `role`, `plan`; rotating refresh token (30 days) stored hashed, in an HttpOnly, Secure, SameSite=Lax cookie.
- Refresh-token reuse detection revokes the whole token family.
- Optional TOTP two-factor; required for admins.
- CSRF token on cookie-authenticated mutations; login rate limit of 10 attempts per 15 minutes per IP and account.

### 2.5 Logout flow

- **Logout:** revoke the current refresh token family, clear cookies, delete the Redis session, redirect to the sign-in page.
- **Logout everywhere:** revoke all sessions for the user; increments a `session_version` checked on each request.
- **Single logout (SSO):** if the session came from an enterprise IdP, call its end-session endpoint or process its logout request.
- Forced logout on password change, role removal, tenant removal and suspected token theft.

## 3. Role-based access control

Permission = role grants action, plan entitles feature, credits pay for it. All three checks run server-side in one policy function.

| Role | Scope | Key permissions |
| --- | --- | --- |
| Super admin | Platform | Manage tenants, plans, pricing, feature flags, credit adjustments |
| Tenant owner | Tenant | Billing, SSO setup, delete tenant, assign any role |
| Tenant admin | Tenant | Manage members, allocate credits, view usage |
| Recruiter / Team member | Tenant | Use recruiter-check, ATS and job features within allocated credits |
| Job seeker (member) | Own data | Resumes, optimization, ATS, auto apply on own balance |
| Viewer / Support | Tenant | Read-only; support has time-boxed, audited impersonation |

### Entitlements by plan and role

- Permissions are strings such as `resume:optimize`, `apply:auto`, `recruiter:check`, `billing:manage`, stored in a role-permission table so custom roles are possible for enterprise.
- Plan entitlements gate features and limits (for example auto apply daily cap, resume slots).
- A user holding several roles gets the union of permissions; a deny rule overrides.
- Credit-based gating: a feature call proceeds only if permission, entitlement and sufficient credits all pass. Responses use 401 (unauthenticated), 403 (role or plan), 402 (insufficient credits).
- Credit allocation: tenant admins can set per-member monthly credit limits from the shared tenant pool.
- Every permission denial and role change is written to the audit log.

## 4. Credit system

### 4.1 Concepts

- **Wallet** per user (personal) and optionally per tenant (shared pool).
- **Credit buckets**: subscription credits (reset or expire at period end), top-up credits (valid 12 months), promotional credits (short expiry). Spending order: expiring soonest first, then promotional, subscription, top-up.
- **Ledger**: append-only entries, never edited. Balance = sum of entries. Types: `grant`, `purchase`, `hold`, `capture`, `release`, `refund`, `expire`, `adjust`.

### 4.2 Price table (configurable)

| Action | Credits | Notes |
| --- | --- | --- |
| Resume parse and storage | 0 | Free, limited by slots |
| ATS score (basic) | 1 | Per resume and job pair |
| AI resume optimization | 5 | Per job-targeted rewrite |
| Auto apply, standard | 3 | Per application submitted |
| Auto apply, tailored resume | 8 | Optimization plus apply |
| Recruiter profile check | 2 | Per profile; cached 7 days |

Prices live in a `credit_price` table with effective dates, so changes never affect past charges.

### 4.3 Spend flow

1. Request arrives with an `Idempotency-Key`.
2. Policy check (role, plan, limits).
3. Place a **hold** for the cost inside a database transaction with a row lock on the wallet.
4. Run the job. On success, **capture**; on failure or timeout, **release** the hold automatically.
5. Emit a usage event and, if balance is below threshold, a low-credit email.

- Refund rules: failed jobs and platform-side errors refund automatically; a user-side rejection by an employer does not.
- Abuse controls: per-action rate limits, daily spend cap, anomaly alerts, and welcome credits limited per verified email and device.
- User view: balance, bucket expiry dates, itemized history, CSV export.

## 5. Multi-tier plans

|  | Free | Pro | Premium | Team / Enterprise |
| --- | --- | --- | --- | --- |
| Monthly credits | 10 | 150 | 500 | Per seat, pooled |
| Resume slots | 1 | 5 | 20 | Unlimited |
| ATS scoring | Basic | Full report | Full plus keyword plan | Full, API access |
| Auto apply per day | Off | 10 | 30 | Custom |
| Recruiter checks | Off | 10 / month | 50 / month | Custom |
| Notifications | Essential | All | All | All, plus digests |
| SSO, audit log, SCIM | No | No | No | Yes |
| Support | Community | Email | Priority | Dedicated |

Figures are starting values and live in configuration. Plans are billed monthly or yearly (yearly discount), with top-up packs available on any paid plan.

- **Upgrade:** immediate, prorated charge, credits granted proportionally.
- **Downgrade:** effective at period end; features beyond the lower plan's limits become read-only, never deleted.
- **Cancellation:** access continues to period end, then reverts to Free; unused subscription credits expire, top-up credits remain.
- Free trial for Pro (7 days, card required), one per user.

## 6. Resume storage and optimization

### 6.1 Upload and storage

- Accepted: PDF, DOCX; max 5 MB; MIME and magic-byte validation, antivirus scan before processing.
- Files stored in private object storage under `tenant/user/resume_id/version`, encrypted at rest (AES-256, per-tenant key where enabled). Access only through short-lived signed URLs.
- Metadata in the database: title, source file hash, parsed JSON, version number, status, created time.
- Parsed structure: contact, summary, experience, education, skills, projects, certifications. The structured JSON is the source of truth for editing and export.
- Versioning: each optimization creates a new version; users can compare, restore and name versions, and mark one as the default for auto apply.
- Export to PDF and DOCX using ATS-safe templates (single column, standard headings).
- Privacy: delete on request removes files, parsed data and derived embeddings within 30 days; retention policy per tenant.

### 6.2 Optimization flow

1. User selects a resume version and pastes or links a job description.
2. System runs ATS match (section 7) to find gaps.
3. LLM rewrites bullet points, summary and skills ordering using only facts present in the resume. It must not invent employers, titles, dates or skills.
4. User sees a diff with accept/reject per change and the projected score.
5. Accepted result saved as a new version; credits captured.