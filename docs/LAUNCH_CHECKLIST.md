# Launch Checklist — Whirlwind KB

> Single list of **next steps** to complete before going live.  
> Tick each item when done. For full criteria see `PRE_PUBLICATION_CHECKLIST.md`.

**Progress:** Legal "Last updated" set to February 6, 2025 in Privacy Policy and Terms of Use. Production build (`npm run build`) verified. Contact placeholder in both docs still needs your email or support link before publication.

---

## 1. Assets & config

- [ ] **PWA icons** — Add `pwa-192x192.png` (192×192) and `pwa-512x512.png` (512×512) to `frontend/public/`. See `frontend/public/PWA_ICONS_README.txt`. Use Whirlwind KB / Mindwave Jamaica branding.
- [ ] **Favicon** — Confirm or replace `/vite.svg` in `index.html` with proper favicon.
- [ ] **Production env** — Set production `.env` (or platform env vars): `GEMINI_API_KEY`, `CORS_ORIGINS` (frontend origin only), `VITE_API_BASE_URL` (public backend URL). Do not commit `.env`.
- [x] **Frontend build** — Run `npm run build` from `frontend/` (verified). Run `npm run preview` and smoke-test before deploy.

---

## 2. Content & citation

- [ ] **Source URLs** — Open every `url` in `frontend/src/mock/db.json` and confirm it loads and matches the cited document. See `CONTENT_SOURCES.md` for current direct/search links.
- [ ] **Facts sample** — Have a subject-matter reviewer spot-check a sample of facts (e.g. Black Star Line, Convention 1920, Declaration of Rights, UNIA membership) for accuracy and wording.
- [ ] **Daily content sample** — Spot-check a sample of daily quotes for correct attribution and accuracy.
- [ ] **Gallery images** — Confirm licensing for each file in `frontend/public/assets/gallery/`. Especially: `marcus-1.jpg`, `marcus-garvey-1922-91d215.jpg`, `marcus-garvey-president-general-of-the-african-republic-news-photo-1737995391.avif`. Add attribution in UI or `CONTENT_SOURCES.md` if required. LoC images already credited in captions/UI.

---

## 3. Legal

- [x] **Privacy policy** — **Last updated** set to February 6, 2025. Replace **[Your contact email or support link]** with real contact before publication.
- [x] **Terms of use** — **Last updated** set to February 6, 2025. Replace **[Your contact email or support link]** with real contact before publication.
- [ ] **Legal disclaimer** — Confirm Legal Disclaimer (Home + Profile) wording is final. Already states source-grounded research instrument and no roleplay/impersonation.

---

## 4. Security & backend

- [ ] **Secrets** — No API keys or secrets in repo. `.env` in `.gitignore`; verify with `git status`.
- [ ] **CORS** — Production backend uses `CORS_ORIGINS` allowlist (frontend origin only). See backend `server.py`.
- [ ] **HTTPS** — Backend served behind HTTPS (reverse proxy or load balancer). No production API over plain HTTP.
- [ ] **Health check** — `GET /api/health` returns 200. Use for readiness if needed.

---

## 5. QA — Core flows

- [ ] **Home** — Daily reflection, gallery, footer (“Mindwave Jamaica • Whirlwind KB v2.0.6 • Grounded in History”), Legal Disclaimer load correctly.
- [ ] **Knowledge Base** — Search/filters, fact cards, “Access Source,” save (bookmark) work. Saved count appears on Profile.
- [ ] **WWMD (Garvey Lens)** — Submit situation; get principle, analogy, action steps, receipts. “New Analysis” clears form. From Library lens result modal, “New Analysis” goes to `/wwmd`.
- [ ] **Toolkit** — Templates load; open, edit, save work. New toolkits (Budget, Membership, Committee Report, Fundraising, Bylaws) visible.
- [ ] **Profile** — Theme toggle, stats (Saved Facts, Custom Templates), Saved Recommended Actions, About, Legal Disclaimer. “Saved Facts” links to Library. No wrong counts after refresh (hydration).

---

## 6. QA — Version, branding, polish

- [ ] **Version/branding** — Footer and sidebar show “Mindwave Jamaica • Whirlwind KB v2.0.6 • Grounded in History” everywhere intended.
- [ ] **Testing panel** — Hidden in production (`TESTING_PANEL_VISIBLE = false` in Layout).
- [ ] **No dev artifacts** — No stray `console.log`, no localhost URLs in production build.
- [ ] **Accessibility** — Icon-only buttons have `aria-label`; keyboard and one screen reader pass if possible.

---

## 7. Deploy & post-launch

- [ ] **Frontend hosting** — Static build deployed (e.g. Vercel, Netlify, S3+CloudFront) with correct `VITE_API_BASE_URL` at build time.
- [ ] **Backend hosting** — API deployed with env vars; run behind gunicorn (or similar), not raw `flask run`.
- [ ] **DNS/SSL** — Domains and SSL certs valid for app and API (if custom).
- [ ] **Docs** — README deployment section and `docs/DEPLOYMENT.md` reflect your host. See `docs/POST_LAUNCH_RUNBOOK.md` for monitoring and rollback.

---

## Quick reference — Must-haves before live

| Area           | Before launch                                      |
|----------------|----------------------------------------------------|
| Assets         | PWA icons in `public/`; favicon set                |
| Content        | Source URLs verified; facts/daily sample reviewed; gallery licensing confirmed |
| Legal          | Privacy & Terms: contact + last updated set        |
| Security       | No secrets in repo; CORS restricted; API over HTTPS |
| Frontend       | Production build works; correct API base URL       |
| Backend        | Health check OK; HTTPS; process manager             |
| QA             | Home, Library, WWMD, Toolkit, Profile flows pass    |
| Branding       | Footer: Mindwave Jamaica • Whirlwind KB v2.0.6     |

---

*Companion to `PRE_PUBLICATION_CHECKLIST.md`. Update as you complete steps. Last updated for Whirlwind KB v2.0.6.*
