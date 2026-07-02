# StudioApp — PRD & Build Log

## Original Problem Statement
Turn a single-tenant wedding photography gallery system into a **multi-tenant SaaS** called **StudioApp** (studioapp.uk). Super admin (platform owner "Mark") sits above tenant photographers, who manage wedding galleries; clients access password-protected branded galleries. Per-tenant branding (remove all "Weddings By Mark"), "Site Designed & Hosted by StudioApp" footer everywhere, storage plans (Starter 250GB / Pro 500GB / Studio 1TB), Stripe billing, video transcoding (VAAPI), NGINX secure_link video serving, TrueNAS/Docker deployment target.

## Architecture (preview environment)
- Backend: FastAPI (modular), MongoDB (motor), JWT multi-tier auth, PIL thumbnails, local-disk storage under UPLOAD_DIR.
- Frontend: React 19 + React Router 7, Tailwind, Framer Motion, sonner, lucide-react. Dark luxury theme (charcoal #0A0A0B + champagne gold #D4AF37), Cormorant Garamond + Manrope fonts.
- Multi-tenancy: every collection carries tenant_id; all tenant endpoints filter by JWT tenant_id. Disk: UPLOAD_DIR/{tenant_id}/{gallery_id}/{subfolder_slug}/.
- Auth tiers: super_admin -> tenant_admin (impersonation supported) -> share links (clients).

## User Personas
1. Super Admin (Mark) — manages all tenants, billing, storage, impersonation.
2. Tenant Admin (Photographer) — galleries, uploads, shares, branding, settings.
3. Client (Couple) — views/favourites/downloads via share links.

## Implemented (2026-07-02)
- Multi-tier JWT auth (bcrypt): super admin + tenant admin, impersonation, suspend gate.
- Super Admin dashboard: list/create/suspend/unsuspend/delete tenants, overview (count/active/MRR/storage), impersonate.
- Tenant onboarding wizard (business, logo URL, brand colours) + branding/password settings.
- Galleries: CRUD, default subfolders, templates, subfolder cover, delete subfolder.
- File uploads (multipart) with storage-quota enforcement (413), background thumbnail + preview generation (separate 8-worker thumb pool / 2-worker transcode pool retained).
- Media serving: thumb/preview/original (public by gallery_id UUID capability — MVP).
- Share links: create/list/toggle/delete, password (bcrypt), access levels, expiry, custom slug, guest-upload mode; password-gated downloads via signed grant token.
- Public ShareView: branding, password gate, subfolder tabs, grid + lightbox, favourites + submit, Download All (ZIP), guest uploads, 30s heartbeat, dark/light toggle, album instruction cards, watermark overlay.
- Dashboard stats (5 cards), Live Gallery Visitors panel, activity logging.
- Per-tenant branding throughout; "Site Designed & Hosted by StudioApp" footer everywhere.
- Seeded: superadmin + demo tenant. Tested: 29/29 backend pytest + frontend E2E pass.

## DEFERRED / Backlog (not yet built)
- P0: Stripe subscription billing + webhooks + auto-suspend on failed payment.
- P0: Video transcoding (FFmpeg + VAAPI GPU/CPU fallback), transcode progress, ensure_faststart. (No ffmpeg/GPU in preview env.)
- P0: NGINX video container + secure_link signed URLs + entrypoint.sh (deployment artifact).
- P1: SMTP per-tenant (notify couple, broadcast, templates, expiry reminders, email log, awards badge). formataddr() From header required.
- P1: TOTP 2FA (pyotp) setup/enable/disable.
- P1: QR code PDFs (3 designs), print sizes + orders + PayPal.
- P1: Chunked 40GB+ uploads; backup system + backup-aware delete UI.
- P1: Activity auto-archive (6mo), archive tab, email log tab, slideshow (Ken Burns + audio).
- P2: Docker Compose (4 containers) + TrueNAS mount paths, logo file upload (object storage).
- Security: gate /api/media/* behind share token / admin auth before production.

## Next Tasks
1. Confirm scope/priority with user (billing vs email vs video first).
2. Stripe billing (test key available in env) or SMTP email suite next.
