# Post-Launch Runbook — Whirlwind KB

Use this after publishing to the public. Update with your actual URLs and contacts.

## Monitoring and health

- **Backend health**: `GET https://<your-api-domain>/api/health` — should return 200. Set up a simple uptime check (e.g. cron, UptimeRobot, or your host’s health check) to hit this every 5–10 minutes.
- **Frontend**: Static site; host uptime is the main check. Optionally monitor for 4xx/5xx on key pages.
- **Logs**: Where do backend logs go (stdout, file, platform dashboard)? Know how to tail or search them for errors (e.g. 500s, RAG failures, missing GEMINI_API_KEY).

## Common issues

| Symptom | Check | Fix |
|--------|--------|-----|
| CORS errors in browser | Backend `CORS_ORIGINS` includes the exact frontend origin (scheme + host + port if not 80/443). | Add origin to `CORS_ORIGINS` and restart backend. |
| "Missing situation" / 400 from /api/wwmd | Request body and Content-Type. | Ensure frontend sends `application/json` and `situation` string. |
| Garvey Lens fails / 500 | Backend logs; `.env` has valid `GEMINI_API_KEY`; RAG/DB paths writable. | Fix key or paths; restart backend. |
| Knowledge Base empty or mock data only | `VITE_API_BASE_URL` was set at build time and points to running backend. | Rebuild frontend with correct `VITE_API_BASE_URL` and redeploy. |
| PWA / "Add to Home Screen" broken | `pwa-192x192.png` and `pwa-512x512.png` in `frontend/public/` before build. | Add icons, rebuild, redeploy. |

## Backups

- **Backend DBs**: `backend/data/*.db` — schedule periodic copies to a safe location (e.g. daily). If you store user data server-side (e.g. testing panel state), include those DBs.
- **Environment**: Keep a secure copy of production `.env` (or documented env vars) so you can recreate the deployment.

## Rollback

- **Frontend**: Redeploy the previous `frontend/dist/` build (keep last 1–2 builds as artifacts). If using a host that supports instant rollback (e.g. Vercel/Netlify), use that.
- **Backend**: Redeploy the previous version of the API (code or container). Restart the process. If a dependency or env change caused the issue, revert that change and restart.
- **Database**: If you restored a DB backup, stop the API, replace the DB file(s), start the API.

## Contact and escalation

- **Operator**: [Mindwave Jamaica contact]
- **Hosting/support**: [Your host’s support or status page]
- **Incident log**: Keep a simple log (date, issue, action) for recurring problems and post-mortems.

---

*Update this runbook as you add monitoring, backups, or new failure modes.*
