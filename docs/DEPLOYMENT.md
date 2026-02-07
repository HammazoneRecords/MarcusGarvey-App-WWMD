# Deployment Guide — Whirlwind KB

Follow this and the [Pre-Publication Checklist](PRE_PUBLICATION_CHECKLIST.md) before going live.

## Environment variables

See [.env.example](../.env.example) at project root. Copy to `.env` and set values. Never commit `.env`.

| Variable | Where | Purpose |
|----------|--------|---------|
| `GEMINI_API_KEY` | Backend | Required for Garvey Lens / chat (RAG) |
| `ARK_API_HOST`, `ARK_API_PORT` | Backend | API bind address (default 0.0.0.0:5050) |
| `CORS_ORIGINS` | Backend | Production: comma-separated frontend origins (e.g. `https://app.example.com`) |
| `VITE_API_BASE_URL` | Frontend build | Production API URL (e.g. `https://api.example.com`) so the app calls your API |

## Frontend (static build)

1. **Install and build**
   ```bash
   cd frontend
   npm ci
   npm run build
   ```
2. **Set API URL at build time**
   ```bash
   export VITE_API_BASE_URL=https://api.your-domain.com
   npm run build
   ```
3. **PWA icons** — The manifest expects `pwa-192x192.png` and `pwa-512x512.png` in `frontend/public/`. Add these (e.g. your logo or Whirlwind KB icon). Without them, "Add to Home Screen" may fail or show a generic icon.
4. **Deploy** — Upload the contents of `frontend/dist/` to your CDN or static host (Vercel, Netlify, S3+CloudFront, etc.). Configure SPA fallback: all routes → `index.html`.
5. **Base path** — If the app is served from a subpath (e.g. `https://site.com/app/`), set Vite `base: '/app/'` in `vite.config.ts` and React Router `basename="/app"` in the router.

## Backend (Flask API)

1. **Install**
   ```bash
   cd backend
   pip install -r requirements.txt
   # If using full RAG stack: pip install -r ragbox/requirements.txt
   ```
2. **Set production env** — At minimum: `GEMINI_API_KEY`, `CORS_ORIGINS` (your frontend origin).
3. **Run with a process manager** — Do not use `flask run` for production. Example with gunicorn:
   ```bash
   gunicorn -w 2 -b 0.0.0.0:5050 "api.server:app"
   ```
   Or use your platform’s process manager (e.g. systemd, Docker, Heroku).
4. **HTTPS** — Put the API behind a reverse proxy (nginx, Caddy) or load balancer with TLS. Do not expose the API over plain HTTP in production.
5. **Databases** — On first request, `backend/data/` will be created (nodes.db, testing_panel.db, etc.). Ensure the process has write access. Seed from `frontend/src/mock/db.json` via nodes_db if required (see backend docs).

## Health check

- **Backend**: `GET /api/health` should return 200. Use this for readiness probes.
- **Frontend**: Static; host health is sufficient unless you add a custom endpoint.

## Post-deploy

- Confirm the frontend loads and can call the API (e.g. open Knowledge Base, run a Garvey Lens query).
- Check browser console and network tab for CORS or 4xx/5xx errors.
- Verify version and footer: "Mindwave Jamaica • Whirlwind KB v2.0.6 • Grounded in History".
