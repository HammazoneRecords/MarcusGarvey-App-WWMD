# Pre-Publication Checklist — Whirlwind KB

> In-depth checklist of what must be done before publishing to the public.  
> Use this as a gate before launch; tick items when complete.

**Implementation pass (this session):** Root `.gitignore` (including `.env`) added; backend CORS allowlist via `CORS_ORIGINS`, input length limits for WWMD/chat; `.env.example` created; `docs/CONTENT_SOURCES.md`, `docs/DEPLOYMENT.md`, `docs/PRIVACY_POLICY.md`, `docs/TERMS_OF_USE.md`, `docs/POST_LAUNCH_RUNBOOK.md` added; Privacy and Terms routes and footer links; aria-labels on icon buttons; route-level code splitting; README deployment section and doc index. **You still need:** Add PWA icons (`pwa-192x192.png`, `pwa-512x512.png`), set production env (including `CORS_ORIGINS`, `VITE_API_BASE_URL`), fill contact in privacy/terms, verify source URLs and image rights, and run your own QA.

---

## 1. Security & Configuration

### 1.1 Secrets & environment
- [ ] **`.env` is never committed** — Ensure `.env` is in `.gitignore` at project root (and any backend subfolders). Verify with `git status` and repo search for `GEMINI_API_KEY` / `API_KEY` in tracked files.
- [ ] **API keys only server-side** — `GEMINI_API_KEY` (and any other LLM keys) are used only in the backend. Frontend Profile API fields (Ollama, Open Router, Gemini) are stored in localStorage only; confirm no keys are sent to a third party from the frontend unless intended and documented.
- [ ] **Production env file** — Create a production `.env` (or use platform env vars) with `GEMINI_API_KEY`, `ARK_API_HOST`, `ARK_API_PORT`, and any other required vars. Do not commit this file.
- [ ] **Frontend API base URL** — For production build, set `VITE_API_BASE_URL` to the public backend URL (e.g. `https://api.yourdomain.com`) so the app calls the correct API. Document in README/deployment docs.

### 1.2 Backend security
- [ ] **CORS** — Restrict CORS in production: replace `CORS(app)` with origin allowlist (e.g. your frontend origin only). See Flask-CORS `origins` parameter.
- [ ] **Host binding** — In production, avoid binding to `0.0.0.0` unless behind a reverse proxy; use a process manager (gunicorn/uwsgi) and proxy (nginx) for TLS and rate limiting.
- [ ] **Rate limiting** — Consider adding rate limits on `/api/wwmd` and `/api/chat` to prevent abuse.
- [ ] **Input validation** — Ensure `situation` and other user inputs are validated and length-limited on the backend to reduce DoS or injection risk.

---

## 2. Content & Citation Accuracy

### 2.1 Source URLs and receipts
- [ ] **All source URLs verified** — Every `url` in `frontend/src/mock/db.json` (and backend nodes DB if used) points to a real, working page. Replace any generic hub links (e.g. UCLA mgpp) with direct document links or clearly labeled “hub” + “direct link TBD” where applicable.
- [ ] **fact-unia-membership and related facts** — Confirm sources cited for UNIA membership and other high-traffic facts are primary or reputable secondary sources; no generic “about Marcus Garvey” pages as sole citation.
- [ ] **Archive.org / external links** — Check that archive.org and other external links open correctly and match the cited document (e.g. UNIA Constitution, Convention proceedings).

### 2.2 Copy and claims
- [ ] **Fact claims reviewed** — Have someone with subject-matter knowledge spot-check a sample of facts for historical accuracy and wording.
- [ ] **Daily reflection content** — Ensure daily quotes and context are correctly attributed and not misleading.
- [ ] **Legal disclaimer visible** — LegalDisclaimer is shown on Home; confirm wording is final and that “Garvey Lens” / “Whirlwind KB” disclaimers are appropriate for public use.

### 2.3 Rights and attribution
- [ ] **Image licensing** — Confirm all images in `frontend/public/assets/gallery/` (and any other assets) are licensed for public use (e.g. public domain, LoC, or permission). Add attribution in UI or docs if required.
- [ ] **Quote attribution** — All Garvey quotes and historical text are correctly attributed; no unattributed or misattributed content.

---

## 3. Technical & Deployment

### 3.1 Frontend
- [ ] **Production build** — Run `npm run build` from `frontend/` (or root); fix any TypeScript or build errors. Run `npm run preview` and smoke-test.
- [ ] **PWA icons** — Manifest references `pwa-192x192.png` and `pwa-512x512.png`. Add these files to `frontend/public/` or update manifest to use existing icons (e.g. favicon-derived). Test “Add to Home Screen” on a device.
- [ ] **Favicon** — Replace or confirm `/vite.svg` in `index.html` with a proper favicon (e.g. Whirlwind KB / Mindwave Jamaica branding).
- [ ] **Meta and SEO** — `index.html` has correct `<title>` and `<meta name="description">`. Add Open Graph / Twitter card meta tags if you want link previews.
- [ ] **Base URL / SPA routing** — If the app is served from a subpath (e.g. `/app/`), set Vite `base` and ensure React Router basename is correct so routes and assets load.

### 3.2 Backend
- [ ] **Python and dependencies** — Backend runs on Python 3.10+; `pip install -r backend/requirements.txt` (and ragbox requirements if needed) succeeds. Document full RAG stack install if required.
- [ ] **Databases** — `backend/data/` (memory.db, nodes.db, testing_panel.db) are created and seeded as needed. Document migration/seed steps for a fresh deploy. Ensure data directory is writable and backed up if needed.
- [ ] **Health check** — `GET /api/health` returns 200. Configure your host or load balancer to use it for readiness.
- [ ] **Process manager** — Run Flask with gunicorn (or similar) in production; do not rely on `flask run` for public traffic.
- [ ] **TLS** — Backend is behind HTTPS (reverse proxy or load balancer). No production API over plain HTTP.

### 3.3 Hosting and DNS
- [ ] **Frontend hosting** — Static build deployed to CDN/host (e.g. Vercel, Netlify, S3+CloudFront). Correct `VITE_API_BASE_URL` used at build time.
- [ ] **Backend hosting** — API deployed to a server/container with stable URL and env vars set.
- [ ] **DNS and domains** — Domains for app and API (if custom) point to the right services; SSL certs valid.

---

## 4. Legal & Compliance

### 4.1 Policies
- [ ] **Privacy policy** — If you collect any PII (e.g. optional account, analytics, or stored preferences), publish a privacy policy and link it from the app (e.g. footer or Profile). State what is stored (e.g. localStorage), for how long, and who to contact.
- [ ] **Terms of use** — If required for your jurisdiction or platform (e.g. app stores), add terms of use and link from the app.
- [ ] **Data disclaimer** — Existing LegalDisclaimer is appropriate for “source-grounded research instrument” and “not roleplay/impersonation.” Confirm with legal if in doubt.

### 4.2 Third-party services
- [ ] **Google Gemini (or other LLM)** — Comply with provider’s terms (e.g. Google AI). Ensure API key is not exposed client-side; usage and logging policies are understood.
- [ ] **Fonts (Google Fonts)** — Check Google Fonts terms and attribution if required; ensure privacy policy mentions third-party resources if needed.

---

## 5. User Experience & Accessibility

### 5.1 Core flows
- [ ] **Home** — Daily reflection, quick actions, research highlight, gallery, footer (Mindwave Jamaica • Whirlwind KB v2.0.6) load and display correctly. No console errors.
- [ ] **Knowledge Base** — Search and filters work; fact cards and “Access Source” open correct content; fact detail and bookmark (save) work.
- [ ] **WWMD (Garvey Lens)** — Submit situation; receive principle, analogy, action steps, receipts, mirror questions. “New Analysis” clears and returns to form. From Library lens result modal, “New Analysis” navigates to /wwmd.
- [ ] **Toolkit** — Templates load; open template detail; edit and save (localStorage) work. New toolkits (Budget, Membership, Committee Report, Fundraising, Bylaws) appear and open.
- [ ] **Profile** — Theme toggle, stats (Saved Facts, Custom Templates), API info section, Saved Recommended Actions, Recent Lens Activity, About/Disclaimer all behave correctly. “Saved Facts” card links to Library.

### 5.2 Accessibility
- [ ] **Keyboard** — All interactive elements (links, buttons, form fields) reachable and operable by keyboard; focus visible.
- [ ] **Screen reader** — Critical UI has sensible labels (e.g. `aria-label` on icon-only buttons). Test with one screen reader (e.g. NVDA, VoiceOver).
- [ ] **Contrast** — Text and controls meet WCAG AA contrast where possible (light and dark themes).
- [ ] **Touch targets** — Buttons and links large enough on mobile (e.g. ≥44px).

### 5.3 Responsive and browsers
- [ ] **Mobile** — Layout works on small viewports; bottom nav and main content are usable.
- [ ] **Desktop** — Sidebar, main content, and any modals display correctly.
- [ ] **Browsers** — Smoke-test on Chrome, Firefox, Safari (or Edge) for critical paths.

---

## 6. Performance & Reliability

### 6.1 Frontend
- [ ] **Bundle size** — Build warns on large chunks (>500kB). Consider code-splitting or lazy routes if needed for slow networks.
- [ ] **Images** — Gallery and other images are appropriately sized/compressed; consider modern formats (e.g. WebP/AVIF) where supported.
- [ ] **Caching** — Static assets cached (e.g. via CDN/host headers); PWA cache strategy is acceptable for your update cadence.

### 6.2 Backend
- [ ] **Response times** — `/api/wwmd` and `/api/chat` respond within acceptable time under normal load; add timeouts and error handling in frontend.
- [ ] **Errors** — API returns clear error messages without leaking internals. Frontend handles errors (e.g. “Connection error” fallback for WWMD).

---

## 7. Testing & QA

### 7.1 Manual testing
- [ ] **Full user journey** — From Home → Knowledge Base → open fact → Access Source; Home → WWMD → submit → read result → check action steps → New Analysis; Home → Toolkit → open template → edit; Profile → change theme, view saved facts and saved actions.
- [ ] **Offline / API down** — With API unreachable, app still loads; Library uses mock data where designed; errors are user-friendly.
- [ ] **Testing panel** — Confirmed hidden in production (`TESTING_PANEL_VISIBLE = false` in Layout).

### 7.2 Data and config
- [ ] **Version and branding** — Footer and sidebar show “Mindwave Jamaica • Whirlwind KB v2.0.6 • Grounded in History” and correct version everywhere.
- [ ] **No dev artifacts** — No `console.log`/debug code, no localhost URLs in production build, no test data that should be removed.

---

## 8. Documentation & Support

### 8.1 For deployers
- [ ] **README** — Deployment section describes: build command, env vars, backend start, optional reverse proxy, and where to set `VITE_API_BASE_URL`.
- [ ] **Environment variables** — List all required and optional env vars (frontend and backend) in README or a dedicated env doc.

### 8.2 For users
- [ ] **User manual** — `docs/USER_MANUAL.md` (or in-app help) is up to date with current features (e.g. Garvey Lens single “Analyze” flow, Saved Recommended Actions, toolkit list).
- [ ] **Contact / support** — If you offer support, add contact link or email in the app (e.g. footer or Profile/About).

---

## 9. Post-Launch Readiness

- [ ] **Monitoring** — Plan for uptime/health checks and error monitoring (e.g. backend logs, frontend error reporting).
- [ ] **Backups** — Backend DBs and any user data (if stored server-side) have a backup strategy.
- [ ] **Rollback** — Know how to roll back frontend or backend (e.g. previous build, previous API version) if a critical issue appears after publish.

---

## Quick reference — Critical before going live

| Area              | Must-have before public launch                          |
|-------------------|----------------------------------------------------------|
| Security          | No API keys in repo; CORS restricted; HTTPS for API     |
| Content           | Source URLs valid; disclaimer and attribution in place   |
| Frontend          | Production build works; PWA icons exist; correct API URL|
| Backend           | Health check OK; run behind HTTPS and process manager   |
| Legal             | Privacy/terms if you collect data or use third parties |
| UX                | Core flows work; keyboard and basic a11y; mobile OK     |
| Version/branding  | Footer and version (e.g. v2.0.6, Mindwave Jamaica) set  |

---

*Update this checklist as the product and launch criteria evolve. Last structured for Whirlwind KB v2.0.6.*
