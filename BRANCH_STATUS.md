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
| main | 2026-06-10 | ✅ Production (deployed code) — **large local uncommitted changeset on main, see below** | Live at marcusgarvey876.com |

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
  - `git rm --cached` run on `backend/data/memory.db`, `backend/data/nodes.db`, and 3 checkpoint/orphan `.db` files — these were tracked in the **public** repo and the working copy contained real user PII (emails, magic-link tokens) from this session's testing. Last commit (Feb 6 2026) had `memory.db` empty (0 tables), so PII had not yet leaked into history. Files remain on disk, just untracked. **Staged, not yet committed.**
  - Added `MAGIC_LINK_COOLDOWN_SECONDS = 60` — `request_magic_link()` in `auth.py` now enforces a 60s per-email cooldown before issuing another magic link, preventing email-bombing via Resend. Verified via curl.
- Verified login/logout/cross-account isolation via Playwright (`/c/tmp/pw_login_logout.js`) — sign-in, sign-out clears JWT + local store, switching accounts on same device leaks no data client- or server-side.
**Schema migration:** new SQLite tables created via `auth.init_auth_tables()` on dev DB (`backend/data/memory.db`) — **not yet applied to VPS production DB** (`/opt/mw/marcus-app/backend/data/memory.db`)
**Verification:** `npx tsc --noEmit` clean; dev server (`localhost:5175`) browser-checked across home/library/fact-detail/wwmd/chat — no console errors. Magic link delivery confirmed to external email (`skygovament@gmail.com`, landed in spam — expected for new domain).

**⚠️ Not yet committed or pushed** — large uncommitted diff across frontend/backend, plus staged `git rm --cached` on PII db files (see `git status`). This is a feature-branch-sized changeset sitting directly on `main`, against the three-branch model. Needs a commit (and ideally should have been a feature branch) before VPS deploy.

**⚠️ Production CORS wide open** (`Access-Control-Allow-Origin` reflects any origin) — but the new auth system isn't deployed to prod yet. Set `CORS_ORIGINS=https://marcusgarvey876.com` in VPS docker-compose env when deploying this auth code.

---

## Active Feature Branches

| Branch | Purpose | Created | Status |
|---|---|---|---|
| — | — | — | — |

## Pending Merges

None

---

## History

| Date | Branch | Action | Notes |
|---|---|---|---|
| 2026-05-02 | main | Initial BRANCH_STATUS.md created | Nav border-b hotfix |
| 2026-06-10 | main | Magic-link auth + sync hardening (uncommitted) | Resend domain verified; toast/retry sync; merge-on-sign-in; see Last Action |
| 2026-06-10 | main | WWMD-only launch prep + data-breach audit (uncommitted) | Chat.tsx → Coming Soon page; PII db files untracked; magic-link cooldown added; see Last Action |
