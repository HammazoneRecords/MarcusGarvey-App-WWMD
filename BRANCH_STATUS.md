# BRANCH_STATUS — Marcus Garvey App

**App path:** `active_apps/MarcusGarvey-App-WWMD/`
**Live domain:** `marcusgarvey876.com`
**VPS container:** `mw-marcus`
**VPS port:** 5050
**Repo:** `https://github.com/HammazoneRecords/MarcusGarvey-App-WWMD`

---

## Current State

| Branch | Last Updated | Deployed? | Notes |
|---|---|---|---|
| main | 2026-06-19 | 🚀 Pushed to GitHub — VPS deploy pending (see below) | Live at marcusgarvey876.com |

## Last Action

**Date:** 2026-06-10
**Branch:** main
**Action:** Magic-link auth (Resend) wired end-to-end + local-first sync hardening + WWMD-only launch prep + data-breach audit
**What changed:**
- New `backend/api/auth.py` — passwordless email auth (magic links, JWT, SQLite tables: `users`, `magic_links`, `user_saved_facts`, `user_lens_results`, `user_toolkit_edits`, `tts_leads`)
- `RESEND_FROM_EMAIL` switched to verified `noreply@marcusgarvey876.com` (domain verified 2026-06-10) — see `active_apps/RESEND_EMAIL_AUTH_SETUP.md`
- New `auth/` reference folder at workspace root (user manual, cross-app integration guide, SQL queries, backup plan)
- New frontend: `AuthVerify.tsx`, `useIdentity.ts`, `services/userData.ts`, `Profile.tsx` updates, `NameCaptureModal.tsx`, `Chat.tsx`, `TTSEarlyAccessBanner.tsx`
- Sync hardening (INS-116): `useToastStore.ts` + `syncHelpers.ts` (`trackSync`) + `Toast.tsx` (`ToastContainer`, mounted in `App.tsx`) — failed server syncs now surface a retry toast instead of failing silently
- `useUserDataSync.ts` rewritten — merges local-only/unsynced data into server snapshot on sign-in instead of overwriting
- 4 sync call sites updated to use `trackSync`: `FactDetail.tsx`, `TemplateDetail.tsx`, `WWMD.tsx`, `ResponseView.tsx`
- Removed Supabase remnants (`services/supabase.ts`, `services/supabaseUserData.ts`)
- **`Chat.tsx` rewritten** as "Ask Marcus — Coming Soon" notify-signup page (reuses `submitTTSLead` with `source: 'chatbot-coming-soon'`) — part of launching with WWMD as the only live conversational feature; nav labels ("Chat" / "Ask Marcus") left as-is since the page content now communicates "coming soon"
- **Data-breach audit fixes:**
  - `.gitignore` expanded — `backend/data/*.db`, `*.db-journal`, `checkpoints/*.db`, `orphans/*.db` now ignored (previously commented out)
  - `git rm --cached` run on `backend/data/memory.db`, `backend/data/nodes.db`, and 3 checkpoint/orphan `.db` files — these were tracked in the **public** repo and the working copy contained real user PII (emails, magic-link tokens) from this session's testing. Last commit (Feb 6 2026) had `memory.db` empty (0 tables), so PII had not yet leaked into history. Files remain on disk, just untracked.
  - Added `MAGIC_LINK_COOLDOWN_SECONDS = 60` — `request_magic_link()` in `auth.py` now enforces a 60s per-email cooldown before issuing another magic link, preventing email-bombing via Resend. Verified via curl.
- Verified login/logout/cross-account isolation via Playwright (`/c/tmp/pw_login_logout.js`) — sign-in, sign-out clears JWT + local store, switching accounts on same device leaks no data client- or server-side.
**Schema migration:** new SQLite tables created via `auth.init_auth_tables()` on dev DB (`backend/data/memory.db`) — **not yet applied to VPS production DB** (`/opt/mw/marcus-app/backend/data/memory.db`)
**Verification:** `npx tsc --noEmit` clean; dev server (`localhost:5175`) browser-checked across home/library/fact-detail/wwmd/chat — no console errors. Magic link delivery confirmed to external email (`skygovament@gmail.com`, landed in spam — expected for new domain).

**✅ Committed** as `e6a2d039` on `main` (2026-06-10) — 51 files changed. **Pushed to GitHub 2026-06-19. VPS deploy pending.**

**⚠️ VPS deploy required** — run the deploy sequence below. Must set `CORS_ORIGINS` and `FRONTEND_URL` before rebuilding container.

---

## Active Feature Branches

| Branch | Purpose | Created | Status |
|---|---|---|---|
| — | — | — | — |

## Pending Merges

None

---

## VPS Deploy Sequence (run when ready)

```bash
# 1. Health check first
ssh root@<VPS_IP> 'free -m && df -h && docker ps | grep marcus'

# 2. Backup production DBs (CON-023)
ssh root@<VPS_IP> 'cp /opt/mw/marcus-app/backend/data/memory.db /opt/mw/marcus-app/backend/data/memory.db.bak-$(date +%Y%m%d) && cp /opt/mw/marcus-app/backend/data/nodes.db /opt/mw/marcus-app/backend/data/nodes.db.bak-$(date +%Y%m%d)'

# 3. Set CORS_ORIGINS in VPS environment — add to /opt/mw/.env or docker-compose env
ssh root@<VPS_IP> 'echo "CORS_ORIGINS=https://marcusgarvey876.com" >> /opt/mw/marcus-app/.env'

# 4. Set FRONTEND_URL in VPS .ark (for magic-link email URLs)
ssh root@<VPS_IP> 'sed -i "s|FRONTEND_URL=.*|FRONTEND_URL=https://marcusgarvey876.com|" /opt/mw/marcus-app/.ark || echo '\''FRONTEND_URL=https://marcusgarvey876.com'\'' >> /opt/mw/marcus-app/.ark'

# 5. Pull new commit
ssh root@<VPS_IP> 'cd /opt/mw/marcus-app && git pull origin main'

# 6. Rebuild and restart (auth tables auto-create on first run via CREATE TABLE IF NOT EXISTS)
ssh root@<VPS_IP> 'cd /opt/mw && docker compose build --no-cache marcus && docker compose up -d marcus'

# 7. Verify
ssh root@<VPS_IP> 'docker logs mw-marcus --tail 20'
curl -s -o /dev/null -w "%{http_code}\n" https://marcusgarvey876.com
```

**Note on CORS_ORIGINS:** `server.py` reads from `os.environ` only — must be set as a Docker environment variable, not in `.ark`. Check how marcus service gets env vars in `/opt/mw/docker-compose.yml` and add there if needed.

**Auth tables:** `init_auth_tables()` runs on startup using `CREATE TABLE IF NOT EXISTS` — no manual migration needed. Tables create themselves.

---

## History

| Date | Branch | Action | Notes |
|---|---|---|---|
| 2026-05-02 | main | Initial BRANCH_STATUS.md created | Nav border-b hotfix |
| 2026-06-10 | main | Magic-link auth + sync hardening (uncommitted) | Resend domain verified; toast/retry sync; merge-on-sign-in; see Last Action |
| 2026-06-10 | main | WWMD-only launch prep + data-breach audit + commit `e6a2d039` | Chat.tsx → Coming Soon page; PII db files untracked; magic-link cooldown added; not yet pushed/deployed; see Last Action |
