# Career Platform — Figma-Style Design File

A self-contained Figma mock of every screen in **`Career Platform_ Feature Specification.md`** (v1.0, October 2026).
No install, no build — double-click to open:

**→ [`career-platform-figma.html`](career-platform-figma.html)** (open in Chrome / Edge / Firefox)

## Pages (left panel, like Figma)

| Page | Contents |
| --- | --- |
| **Hi-Fi Screens** — 18 frames @ 1440×900 | 01 Sign In (OAuth / password / magic link / SSO) · 02 Two-Factor · 03 Tenant Switcher · 04 First-Run Welcome · 05 Wallet & Ledger · 06 Pricing (4 tiers, monthly/yearly) · 07 Checkout · 08 Billing Portal · 09 Resume Library · 10 AI Optimization diff · 11 ATS Report · 12 Version Compare · 13 Auto Apply · 14 Auto Apply Live Run · 15 Recruiter Check · 16 Team & Roles · 17 Audit & Security · 18 Notifications & Gmail templates |
| **Wireframes** — 19 frames | One gray-box wireframe per screen (W1–W19, incl. Dashboard), each with blue spec annotations |
| **Prototype & Motion** | Smart-animate player (Sign in → Verifying → 2FA → Dashboard, auto-plays) + 8 live micro-interaction specs |

## What's animated

- ATS **score gauges** (0 → 78), usage **meters**, **credit counters**
- **Ledger capture row** sliding in (`hold → capture`), low-credit **toast**
- **Queue status stepper** cycling queued → tailoring → submitting → submitted
- Upload **progress + virus scan**, parsing **skeleton shimmer**, **confetti** on first run
- Diff **accept / reject** (click the ✓ / ✕ buttons), pricing **monthly ⇄ yearly** swap
- Prototype player: play/pause, restart, clickable step dots, running timer

## How it maps to the spec

- Credit prices (ATS 1 · optimize 5 · apply 3/8 · recruiter check 2), bucket expiry order,
  refund rules and the `hold → capture/release` flow appear on screens 05 / 13 / 14.
- RBAC matrix, permission strings (`resume:optimize`, `billing:manage`…) on 16 / 17.
- Plan matrix (credits, slots, daily caps, SSO) on 06; proration/downgrade rules on 07 / 08.
- Session/JWT, logout-everywhere, impersonation audit on 02 / 17.
- Facts-only optimization guardrail on 10 / 12; 7-day recruiter cache on 15.

Yellow/green/blue sticky notes on the canvas quote the spec sections each row implements.
