# Production Deployment to Vercel — Marcus Garvey App WWMD

**Date**: February 8, 2026  
**Target**: Production deployment with Vercel  
**Estimated Time**: 1-2 hours  

---

## Pre-Deployment Checklist

Before deploying, verify:

- [x] `.env` is in `.gitignore` (verified)
- [x] Build is successful locally (`npm run build` passes)
- [ ] Git repo is clean (no uncommitted secrets)
- [ ] GitHub repo is connected to Vercel
- [ ] Frontend and backend domains determined
- [ ] GEMINI_API_KEY is ready (production key)
- [ ] CORS_ORIGINS determined (frontend domain)

---

## Architecture Overview

```
┌────────────────────────────────────────────┐
│ FRONTEND (Vercel)                          │
│ https://app.your-domain.com                │
│ - React/Vite SPA                           │
│ - Static hosting                           │
└────────────────────────────────────────────┘
          ↓ API calls
┌────────────────────────────────────────────┐
│ BACKEND API (Vercel or Self-Hosted)        │
│ https://api.your-domain.com                │
│ - Flask server                             │
│ - Python RAG pipeline                      │
│ - Gemini API calls (via Bearer token)      │
└────────────────────────────────────────────┘
          ↓ SQL queries
┌────────────────────────────────────────────┐
│ DATABASE (SQLite in /backend/data/)        │
│ - line_chunks (21,469 lines)               │
│ - chunks (parent sections)                 │
│ - anchors (sources)                        │
└────────────────────────────────────────────┘
```

---

## Deployment Plan

### Phase 1: Frontend (Vercel)

**Time**: 10-15 minutes

1. **Connect GitHub to Vercel**
   - Go to [vercel.com](https://vercel.com)
   - Sign in (or create account)
   - Click "New Project"
   - Select your GitHub repo: `HammazoneRecords/MarcusGarvey-App-WWMD`
   - Vercel auto-detects monorepo structure

2. **Configure Frontend Build**
   - Framework: Vite
   - Build Command: `npm run build` ✅ (auto-detected)
   - Output Directory: `frontend/dist` ✅ (auto-detected)
   - Install Command: `npm install` ✅

3. **Set Environment Variables** (Vercel dashboard → Settings → Environment Variables)
   ```
   VITE_API_BASE_URL=https://api.your-domain.com
   ```
   - This tells frontend where to send API requests
   - Must be HTTPS in production

4. **Deploy**
   - Click "Deploy"
   - Wait for build to complete (should take 2-3 minutes)
   - Vercel auto-provides HTTPS and auto-deploys on git push

5. **Get Frontend URL**
   - Vercel assigns: `https://whirlwind-kb.vercel.app` (or your custom domain)
   - Note this for backend CORS setup

---

### Phase 2: Backend (Vercel Serverless or Self-Hosted)

**Options**:

#### Option A: Vercel Serverless (Recommended for Small Scale)

**Pros**: Simple, same platform, auto-scaling  
**Cons**: Cold starts, limited runtime (15 min max), SQLite not ideal for serverless

1. **Create Vercel API Functions**
   - Must create `/api` directory in project root
   - Vercel converts Python files to serverless functions
   - Recommended: Use Render or DigitalOcean instead (see Option B)

#### Option B: Render.com (Recommended Production)

**Pros**: Better for Python/Flask, persistent SQLite, simple setup  
**Cons**: Another platform to manage

1. **Prepare Backend for Render**

   Create `Procfile` (if not exists):
   ```bash
   echo 'web: cd backend && gunicorn -w 2 -b 0.0.0.0:$PORT "api.server:app"' > Procfile
   ```

2. **Push to GitHub**
   ```bash
   git add Procfile vercel.json
   git commit -m "chore: add deployment configs"
   git push origin main
   ```

3. **Deploy to Render.com**
   - Go to [render.com](https://render.com)
   - Click "New +" → "Web Service"
   - Connect GitHub repo
   - Settings:
     - **Build Command**: `pip install -r backend/requirements.txt`
     - **Start Command**: `cd backend && gunicorn -w 2 -b 0.0.0.0:$PORT "api.server:app"`
     - **Working Directory**: `/` (root)
     - **Instance Type**: Starter (free tier)

4. **Set Environment Variables** (Render dashboard → Environment)
   ```
   GEMINI_API_KEY=sk_prod_xxx_xxx_xxx
   CORS_ORIGINS=https://app.your-domain.com
   DIAGNOSTIC_MODE=0
   ```

5. **Enable HTTPS**
   - Render auto-provides SSL ✅
   - Get API URL: `https://whirlwind-kb-api.onrender.com`

6. **Add Custom Domain** (Optional)
   - Render → Settings → Custom Domain
   - Point `api.your-domain.com` to Render endpoint

---

### Phase 3: Frontend Environment Setup

After backend is live:

1. **Update Frontend Environment**
   - Vercel dashboard → Settings → Environment Variables
   - Update `VITE_API_BASE_URL` to backend URL (if changed)

2. **Redeploy Frontend**
   - Vercel → Deployments → Click latest → Redeploy

---

### Phase 4: Configure CORS

Once both frontend and backend are live:

1. **Set `CORS_ORIGINS` in backend** (Render/Platform env vars)
   ```
   CORS_ORIGINS=https://whirlwind-kb.vercel.app
   ```
   or with custom domain:
   ```
   CORS_ORIGINS=https://app.your-domain.com
   ```

2. **Restart Backend**
   - Render: Auto-restarts on env var change
   - Vercel: Redeploy function

3. **Test CORS**
   ```bash
   curl -X POST https://api.your-domain.com/api/health -H "Origin: https://app.your-domain.com"
   ```

---

## Step-by-Step Commands

### 1. Prepare Git

```bash
# Verify no secrets in Git history
git log --all -p -- .env | head -20  # Should show nothing

# Ensure .env is ignored
git check-ignore .env  # Should return .env (meaning it's ignored)

# Verify clean working directory
git status  # Should show clean or only untracked dotfiles
```

### 2. Verify Build

```bash
# From project root
npm install
npm run build

# Test frontend loads
npm run preview
# Visit http://localhost:4173 (should load without errors)
```

### 3. Deploy Frontend to Vercel

```bash
# Option A: Via Vercel CLI
npm install -g vercel
vercel --prod

# Option B: Via Git push (recommended)
# After connecting GitHub to Vercel:
git push origin main
# Vercel auto-deploys
```

### 4. Deploy Backend to Render.com

```bash
# Create Procfile (if missing)
cat > Procfile << 'EOF'
web: cd backend && gunicorn -w 2 -b 0.0.0.0:$PORT "api.server:app"
EOF

# Commit and push
git add Procfile
git commit -m "chore: add Procfile for Render deployment"
git push origin main

# Then in Render dashboard:
# - Click "New Web Service"
# - Connect GitHub repo
# - Fill in settings (see Phase 2 above)
# - Deploy
```

### 5. Verify Deployment

```bash
# Check frontend
curl https://app.your-domain.com/
# Should return HTML (index page)

# Check backend health
curl https://api.your-domain.com/api/health
# Should return: {"status": "ok", "service": "WhirlwindDB ARK Connect"}

# Check WWMD endpoint (with dummy key)
curl -X POST https://api.your-domain.com/api/key-diagnostic \
  -H "Content-Type: application/json" \
  -d '{}'
# Should return: { "env_key_present": true, "using_env_key": true, ... }

# Test full WWMD flow (from frontend)
# Open https://app.your-domain.com in browser
# Go to "Ask Marcus" page
# Enter question and submit
# Should get response with citations
```

---

## Environment Variables (Production)

### Frontend (Vercel)
```
VITE_API_BASE_URL=https://api.your-domain.com
```

### Backend (Render or Vercel)
```
GEMINI_API_KEY=sk_prod_xxxxx_xxxxx_xxxxx  # Your production Gemini key
CORS_ORIGINS=https://app.your-domain.com
ARK_API_HOST=0.0.0.0
ARK_API_PORT=5000  # (Render/platform assigns)
DIAGNOSTIC_MODE=0  # Disable diagnostics in production
PYTHONUTF8=1
PYTHONIOENCODING=utf-8
```

---

## Custom Domains (Optional)

### Frontend Domain
1. Buy domain (GoDaddy, Namecheap, Google Domains, etc.)
2. In Vercel dashboard:
   - Project → Settings → Domains
   - Add domain: `app.your-domain.com`
   - Follow DNS setup instructions
   - Vercel auto-provides HTTPS ✅

### Backend Domain
1. In Render dashboard:
   - Service → Settings → Custom Domain
   - Add domain: `api.your-domain.com`
   - Follow CNAME setup instructions
   - Render auto-provides HTTPS ✅

---

## Post-Deployment Checklist

After deployment:

- [ ] Frontend loads at https://app.your-domain.com
- [ ] Backend health check passes: `curl https://api.your-domain.com/api/health`
- [ ] CORS working: no browser errors when frontend calls backend
- [ ] WWMD query returns response with citations
- [ ] User can save fact to Profile
- [ ] Theme toggle persists across reload
- [ ] Sign out clears all data ✅
- [ ] No console errors in browser DevTools
- [ ] HTTPS enabled for both frontend and backend
- [ ] DIAGNOSTIC_MODE disabled (set to 0)
- [ ] `.env` NOT in Git history
- [ ] Monitoring set up (Vercel/Render dashboards)

---

## Monitoring & Alerts

### Vercel (Frontend)
- Dashboard → Analytics
- Check for build failures
- Set up email alerts for deployment failures

### Render (Backend) 
- Dashboard → Health checks
- Monitor uptime
- Check logs for errors

### Manual Monitoring
- Daily: Check `https://api.your-domain.com/api/health`
- Weekly: Test full WWMD query flow
- Monthly: Review Gemini API usage/costs

---

## Rollback Plan

If deployment fails:

1. **Frontend**: Vercel auto-keeps previous versions
   - Vercel → Deployments → Select previous → Redeploy

2. **Backend**: Render keeps build history
   - Render → Deployments → Select previous → Redeploy

3. **Quick Kill Switch**
   - Render: Pause service (Settings → Pause)
   - Vercel: Disable domain (Settings → Domains → Remove)

---

## Security Final Check

- [ ] `.env` in `.gitignore` ✅
- [ ] No secrets printed in logs ✅
- [ ] GEMINI_API_KEY in platform env vars (not repo)
- [ ] CORS_ORIGINS set to exact frontend domain
- [ ] HTTPS enabled for backend and frontend ✅
- [ ] DIAGNOSTIC_MODE disabled ✅
- [ ] Authorization header used for Gemini calls ✅
- [ ] Input validation enabled ✅

---

## Support & Troubleshooting

| Issue | Solution |
|-------|----------|
| Frontend won't load | Check Vercel build logs, ensure `npm run build` passes locally |
| Backend 500 error | Check Render logs: `journalctl -u render --no-pager` |
| CORS error in browser | Verify CORS_ORIGINS matches frontend domain exactly |
| WWMD returns "Missing API Key" | Check GEMINI_API_KEY is set in backend env vars |
| Slow response | Check Render instance type, add more resources if needed |
| Database locked error | SQLite limitation; upgrade to PostgreSQL if needed |

---

## Next Steps After Production

1. **Monitor**: Check dashboards daily for first week
2. **Backup**: Set up automated backups of SQLite database
3. **Docs**: Update user documentation with production URLs
4. **Analytics**: Set up usage tracking (Sentry, LogRocket, etc.)
5. **Scaling**: Monitor costs; upgrade if needed
6. **Updates**: Set up auto-patches for dependencies

---

**Questions?** Check [SECURITY_GUIDELINES.md](SECURITY_GUIDELINES.md) or [DEPLOYMENT_SETUP_GUIDE.md](../DEPLOYMENT_SETUP_GUIDE.md) for more details.

**Last Updated**: February 8, 2026
