# Quick Start - Deployment Guide

Deploy your app in **3 simple steps**. Choose your path:

## 🚀 Quick Deployment Path

### **Local Development** (5 min)
```bash
# 1. Setup backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 2. Copy .env
cp .env.example .env
# Edit .env with Firebase & LiveKit credentials

# 3. Start backend
python backend/main.py
# Runs on http://127.0.0.1:8000

# 4. Open frontend
# Open: http://127.0.0.1:8000/docs (to see API)
# Or: Open frontend/index.html in browser
```

---

### **Production Deployment** (15 min)

#### **Step 1: Deploy Backend** (5 min)

**Choose ONE platform:**

**Option A: Railway** ⭐ (Recommended)
```bash
# 1. Sign up: https://railway.app
# 2. Click "Deploy from GitHub"
# 3. Select your repository
# 4. Add environment variables:
#    - FIRESTORE_CREDENTIALS
#    - LIVEKIT_API_KEY
#    - LIVEKIT_API_SECRET
#    - LIVEKIT_URL
# 5. Set start command: uvicorn backend.main:app --host 0.0.0.0 --port $PORT
# 6. Deploy!
# 7. Copy your URL: https://your-backend.railway.app
```

**Option B: Render.com**
```bash
# Similar to Railway, see BACKEND_DEPLOYMENT.md
```

#### **Step 2: Deploy Frontend** (5 min)

```bash
# 1. Push code to GitHub (if not already)
git add .
git commit -m "Deploy to production"
git push

# 2. Go to: https://vercel.com/new
# 3. Select "Import Git Repository"
# 4. Choose your GitHub repo
# 5. Configure:
#    - Output Directory: frontend
#    - Build Command: (leave blank)
# 6. Click "Deploy"
# 7. Wait 1-2 minutes
# 8. Copy your URL: https://your-app.vercel.app
```

#### **Step 3: Configure Backend URL** (2 min)

```bash
# 1. Open: https://your-app.vercel.app/settings.html
# 2. Paste your backend URL:
#    https://your-backend.railway.app
# 3. Click "Test Connection"
# 4. Should see: ✅ Successfully connected!
# 5. Done! All pages now work
```

---

## 📊 What You Get

| Component | Where | URL |
|-----------|-------|-----|
| **Frontend** | Vercel | `https://your-app.vercel.app` |
| **Backend API** | Railway | `https://your-backend.railway.app` |
| **API Docs** | - | `https://your-backend.railway.app/docs` |
| **Settings** | Frontend | `https://your-app.vercel.app/settings.html` |

---

## ✅ Deployment Checklist

- [ ] Backend deployed and URL copied
- [ ] Frontend deployed and URL copied
- [ ] Settings page opened: `https://your-app.vercel.app/settings.html`
- [ ] Backend URL pasted and "Test Connection" passed
- [ ] Dashboard loads: `https://your-app.vercel.app`
- [ ] Can view pending requests
- [ ] Can view history
- [ ] Can view knowledge base

---

## 🔧 Troubleshooting

### "Cannot connect to backend"
```javascript
// In browser console (F12):
localStorage.setItem('API_BASE_URL', 'https://your-backend.railway.app');
location.reload();
```

### "Settings page not found"
Make sure file exists in `frontend/settings.html` (it does!)

### "Backend deployment failed"
Check Railway logs:
1. Railway Dashboard → Your Project → Logs
2. Look for Python errors
3. Verify environment variables are set

---

## 📚 Detailed Guides

For more information, see:

- **BACKEND_DEPLOYMENT.md** - Full backend deployment guide
- **FRONTEND_DEPLOYMENT.md** - Full frontend deployment guide  
- **ARCHITECTURE.md** - System architecture & design decisions
- **DEPLOYMENT_CHECKLIST.md** - Pre/post-deployment checks

---

## 🎯 Architecture Overview

```
User Browser
     ↓
Vercel Frontend (static)
     ↓ (API calls to)
Railway Backend (FastAPI)
     ↓ (reads/writes)
Firebase Firestore + LiveKit
```

---

## 💡 Pro Tips

1. **Local backend not working?**
   ```bash
   # Make sure you:
   pip install -r requirements.txt
   export FIRESTORE_CREDENTIALS="..." (or set in .env)
   python backend/main.py
   ```

2. **CORS errors?**
   - Backend has CORS enabled automatically
   - Check that frontend URL matches (should be)

3. **Want custom domain?**
   - Go to Vercel Dashboard → Your Project → Settings → Domains
   - Add your domain and follow DNS setup

4. **Backend URL in localStorage?**
   ```javascript
   localStorage.getItem('API_BASE_URL')
   ```

---

## 🚨 Common Issues

| Issue | Solution |
|-------|----------|
| Settings page won't load | File: `frontend/settings.html` should exist |
| Can't connect to backend | Paste URL in settings, click Test |
| Backend shows 502 error | Check Railway logs for Python errors |
| CORS error in console | Backend CORS should be enabled (it is) |
| localStorage not saving | Try incognito mode or clear cookies |

---

## 🎓 Next Steps

1. Deploy backend first (Railway recommended)
2. Deploy frontend (Vercel)
3. Configure backend URL in settings
4. Test all pages
5. Optional: Add custom domain to Vercel

---

**Ready to deploy? Start with BACKEND_DEPLOYMENT.md →**
