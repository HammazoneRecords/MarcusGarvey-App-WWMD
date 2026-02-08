# Deployment Setup Guide — Whirlwind KB
**Date Created**: February 7, 2026  
**Status**: Ready for Configuration

---

## Phase 1: Backend Deployment ⏳

### Step 1.1: Choose Hosting Platform

**Options** (pick one):

| Platform | Pros | Cons | Setup Time |
|----------|------|------|------------|
| **Heroku** | Simple, auto-SSL, easy logging | Cost ($7-25/mo), platform overhead | 15 min |
| **AWS (EC2 + RDS)** | Scalable, flexible, pay-per-use | More complex, requires DevOps knowledge | 1-2 hours |
| **DigitalOcean App Platform** | Simple, affordable ($12/mo), fast | Smaller ecosystem than AWS | 20 min |
| **Render.com** | Good balance of simplicity & power, free tier | Smaller company | 20 min |
| **Docker + Own Server** | Maximum control, no platform lock-in | Must manage infrastructure, SSL, scaling | 2-4 hours |
| **PythonAnywhere** | Python-specific, simple | Limited flexibility, scalability | 15 min |

**Recommendation for launch**: **Render.com or DigitalOcean App Platform** (simple, affordable, supports Python/Flask)

---

### Step 1.2: Prepare Backend for Production

#### Create `requirements.txt` (Main + RAG)

**Status**: `backend/requirements.txt` exists with Flask + Flask-CORS

**Missing**: Full RAG stack dependencies  
**Action Required**: Verify `ragbox/requirements.txt` is complete

```bash
# From backend/ directory
pip install -r requirements.txt
pip install -r ragbox/requirements.txt  # Full RAG stack
```

#### Create Production Environment File

**File**: `.env` (at project root, DO NOT commit)

```env
# API Configuration
ARK_API_HOST=0.0.0.0
ARK_API_PORT=5050

# Secrets (set in your hosting platform env vars, not in repo)
GEMINI_API_KEY=your_actual_api_key

# CORS (set this to your frontend domain)
CORS_ORIGINS=https://app.your-domain.com

# Development only
VITE_API_BASE_URL=http://localhost:5050
```

**Important**:
- `.env` is in `.gitignore` ✅ (keep secrets out of repo)
- Set `CORS_ORIGINS` to your actual frontend domain (including https://)
- Use platform env vars, not a committed `.env` file

#### Health Check Endpoint

**Status**: ✅ Already configured  
**URL**: `GET /api/health`  
**Response**: 200 OK

---

### Step 1.3: Set Up Production Server

#### Option A: Heroku (Easiest)

1. **Install Heroku CLI**
   ```bash
   npm install -g heroku
   heroku login
   ```

2. **Create Heroku app**
   ```bash
   heroku create whirlwind-kb-api
   ```

3. **Set environment variables**
   ```bash
   heroku config:set GEMINI_API_KEY="your_key" -a whirlwind-kb-api
   heroku config:set CORS_ORIGINS="https://app.your-domain.com" -a whirlwind-kb-api
   ```

4. **Deploy**
   ```bash
   git push heroku main
   ```

#### Option B: Render.com (Recommended)

1. **Connect GitHub repo** to Render.com
2. **Create Web Service**
   - Language: Python
   - Build command: `pip install -r backend/requirements.txt && pip install -r backend/ragbox/requirements.txt`
   - Start command: `gunicorn -w 2 -b 0.0.0.0:$PORT "api.server:app"`
   - Working directory: `backend/`

3. **Set environment variables** in Render dashboard:
   ```
   GEMINI_API_KEY=your_key
   CORS_ORIGINS=https://app.your-domain.com
   ARK_API_HOST=0.0.0.0
   ARK_API_PORT=8000 (or whatever Render assigns)
   ```

4. **Deploy** — Render auto-deploys on push

#### Option C: Docker + Self-Hosted

**Dockerfile** for backend:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY backend/requirements.txt requirements.txt
COPY backend/ragbox/requirements.txt ragbox-requirements.txt

RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -r ragbox-requirements.txt

COPY backend/ .

ENV ARK_API_HOST=0.0.0.0
ENV ARK_API_PORT=5050

EXPOSE 5050

CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:5050", "api.server:app"]
```

Build & run:
```bash
docker build -t whirlwind-kb-api .
docker run -p 5050:5050 \
  -e GEMINI_API_KEY=your_key \
  -e CORS_ORIGINS="https://app.your-domain.com" \
  whirlwind-kb-api
```

---

### Step 1.4: Verify Backend Deployment

**After deployment**, test:

```bash
# Health check
curl https://your-api-domain.com/api/health
# Expected: 200 OK

# Library endpoint
curl https://your-api-domain.com/api/library
# Expected: JSON with facts

# WWMD endpoint
curl -X POST https://your-api-domain.com/api/wwmd \
  -H "Content-Type: application/json" \
  -d '{"situation": "test", "mode": "Personal"}'
# Expected: JSON response with principle, analogy, actions, receipts
```

---

## Phase 2: Frontend Deployment ⏳

### Step 2.1: Build Frontend for Production

```bash
# Set API endpoint at build time
export VITE_API_BASE_URL=https://your-api-domain.com

# Build
npm run install:frontend
npm run build

# Output: frontend/dist/
```

### Step 2.2: Deploy to CDN/Static Host

**Options**:

| Platform | Setup | Cost | Auto-deployments |
|----------|-------|------|-----------------|
| **Vercel** | Connect GitHub, auto-build | Free tier available | ✅ Yes |
| **Netlify** | Connect GitHub, auto-build | Free tier available | ✅ Yes |
| **AWS S3 + CloudFront** | Manual upload, CDN | $1-5/mo | ❌ Manual |
| **GitHub Pages** | Push to gh-pages branch | Free | ⚠️ Limited |

**Recommendation**: **Vercel or Netlify** (easiest, auto-deploys on push)

#### Using Vercel

1. **Install Vercel CLI** (or use web UI)
   ```bash
   npm install -g vercel
   ```

2. **Link project**
   ```bash
   vercel link
   ```

3. **Set environment** (in Vercel dashboard or CLI)
   ```
   VITE_API_BASE_URL=https://your-api-domain.com
   ```

4. **Deploy**
   ```bash
   vercel --prod
   ```

#### Using Netlify

1. **Install Netlify CLI**
   ```bash
   npm install -g netlify-cli
   ```

2. **Configure** (`netlify.toml` in project root)
   ```toml
   [build]
   command = "npm run build"
   functions = "backend"
   publish = "frontend/dist"

   [dev]
   command = "npm run dev:frontend"
   ```

3. **Deploy**
   ```bash
   netlify deploy --prod
   ```

---

### Step 2.3: Configure SPA Routing

**If using static host** (S3, Netlify, Vercel), ensure all 404s redirect to `index.html` so React Router works correctly.

**Netlify** (`netlify.toml`):
```toml
[[redirects]]
from = "/*"
to = "/index.html"
status = 200
```

**Vercel** (`vercel.json`):
```json
{
  "rewrites": [
    {
      "source": "/((?!api/.*).*)",
      "destination": "/index.html"
    }
  ]
}
```

---

## Phase 3: CORS Configuration ✅

### Step 3.1: Set `CORS_ORIGINS`

**In backend env vars**, set:

```env
CORS_ORIGINS=https://app.your-domain.com
```

**Backend code** (already implemented):
```python
CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "").strip()
if CORS_ORIGINS:
    origins = [o.strip() for o in CORS_ORIGINS.split(",") if o.strip()]
    CORS(app, origins=origins, supports_credentials=False)
else:
    CORS(app)  # dev default: allow all
```

### Step 3.2: Multiple Domains (if needed)

```env
CORS_ORIGINS=https://app.your-domain.com,https://www.your-domain.com
```

### Step 3.3: Verify CORS

After deploying both frontend and backend:

1. **From browser console**, call backend:
   ```javascript
   fetch('https://your-api-domain.com/api/library')
     .then(r => r.json())
     .then(data => console.log(data))
   ```

2. **Expected**: Data returned (no CORS error)

3. **If CORS error**, check:
   - Frontend domain matches `CORS_ORIGINS` exactly (including https://)
   - Backend restarted after env var change
   - No typos in domain

---

## Phase 4: SSL/TLS (HTTPS) ✅

### Step 4.1: Frontend

**Vercel/Netlify auto-provide HTTPS** ✅

Set custom domain → auto SSL certificate

### Step 4.2: Backend

**Option 1: Hosted Platform** (Heroku, Render, DigitalOcean)
- Auto-provides HTTPS ✅
- Just set custom domain

**Option 2: Self-Hosted**
- Use **Let's Encrypt** (free):
  ```bash
  certbot certonly --standalone -d api.your-domain.com
  ```
- Put **nginx/Caddy** in front as reverse proxy for TLS termination
- Never expose Flask directly over HTTP

---

## Phase 5: Testing & Validation ⏳

### Pre-Launch Checklist

- [ ] Backend deployed and health check passes
- [ ] Frontend deployed and loads
- [ ] Frontend can call `/api/library` and display facts
- [ ] WWMD Lens works (submit situation, get response)
- [ ] CORS configured correctly (no browser errors)
- [ ] Theme toggle works
- [ ] Profile settings persist
- [ ] Sign out clears all data ✅ (from earlier fix)
- [ ] All source links load correctly
- [ ] Footer displays: "Mindwave Jamaica • Whirlwind KB v2.0.6 • Grounded in History"
- [ ] No dev console errors

### Browser Testing

**Browsers to test**:
- Chrome (latest)
- Firefox (latest)
- Safari (macOS + iOS)
- Edge (latest)

**Key flows**:
1. Load Home → daily reflection displays
2. Search Library → get facts
3. Submit WWMD → get response with citations
4. Save fact → appears in Profile
5. Toggle theme → persists on reload
6. Sign in/out → works with Supabase (if configured)

---

## Phase 6: Post-Launch Monitoring ⏳

### Set Up Monitoring

1. **Backend health checks**
   ```
   Tool: UptimeRobot, Vercel/Render health checks, or cron
   URL: https://your-api-domain.com/api/health
   Interval: Every 5 minutes
   Alert: Email if down 5+ min
   ```

2. **Frontend monitoring**
   ```
   Tool: Sentry, Rollbar, or plain error monitoring
   Track: JavaScript errors, API failures
   Alert: Critical errors
   ```

3. **Logs**
   - Backend: Check stdout/logs in platform dashboard
   - Frontend: Browser console (users can report)

### Keep Documentation Updated

- [ ] Update contact info in Legal docs (already `ovandobrown@mindwaveja.com`) ✅
- [ ] Document your API domain and frontend domain
- [ ] Save `.env` values securely (password manager or platform vault)
- [ ] Document backup schedule for any user data

---

## Deployment Checklists

### Before Frontend Deploy
- [ ] Rebuild with correct `VITE_API_BASE_URL`
- [ ] Test locally: `npm run preview`
- [ ] PWA icons in place ✅
- [ ] No console errors

### Before Backend Deploy
- [ ] `.env` has valid `GEMINI_API_KEY`
- [ ] `CORS_ORIGINS` set to frontend domain
- [ ] Database writable (`backend/data/`)
- [ ] `gunicorn` or process manager configured
- [ ] HTTPS/SSL ready

### Post-Launch (Day 1)
- [ ] Health check passes
- [ ] Frontend loads
- [ ] Library displays facts
- [ ] WWMD returns results
- [ ] No CORS errors
- [ ] All links work

---

## Support Contacts

| Contact | Role |
|---------|------|
| ovandobrown@mindwaveja.com | Operator (legal/support) |
| [Your hosting support] | Infrastructure issues |
| [Your Git repo] | Code issues/PRs |

---

## Estimated Timeline

| Phase | Platform | Time |
|-------|----------|------|
| Backend setup | Render/DigitalOcean | 20-30 min |
| Frontend setup | Vercel/Netlify | 15-20 min |
| Testing | All platforms | 30 min |
| **Total** | | **1-2 hours** |

---

**Status**: 🟡 **Ready to deploy** — All configuration files in place, just needs hosting platform selection and environment variable setup.
