# Backend Deployment Guide

Deploy the FastAPI backend separately from the frontend for better scalability and maintenance.

## Best Hosting Options

### 1. **Railway.app** (Recommended - Easiest)
- Free tier: 500 hours/month
- Easy deployment from GitHub
- Environment variables in UI
- PostgreSQL/Redis available
- Perfect for FastAPI

**Steps:**
1. Go to https://railway.app
2. Click "Start a New Project" → "Deploy from GitHub"
3. Select your repository
4. Add environment variables:
   - `FIRESTORE_CREDENTIALS` (JSON string)
   - `LIVEKIT_API_KEY`
   - `LIVEKIT_API_SECRET`
   - `LIVEKIT_URL`
5. Set start command: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
6. Deploy!
7. Copy your Railway URL (e.g., `https://your-app.railway.app`)

### 2. **Render.com** (Good Alternative)
- Free tier with limited hours
- Auto-deploys from GitHub
- Managed PostgreSQL available
- Clean dashboard

**Steps:**
1. Go to https://render.com
2. Click "New +" → "Web Service"
3. Connect GitHub repository
4. Set build command: `pip install -r requirements.txt`
5. Set start command: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
6. Add environment variables same as Railway
7. Deploy and get your URL

### 3. **PythonAnywhere.com** (Beginner-Friendly)
- Free tier available
- Beginner-friendly interface
- Limited resources

### 4. **Heroku** (Legacy, paid now)
- Was free, now requires paid dynos
- Still widely used
- https://www.heroku.com

### 5. **AWS EC2 + Gunicorn + Nginx** (Most Control)
- Requires more setup
- Pay-as-you-go pricing
- Full control over infrastructure

## Railway.app Setup (Step-by-Step)

### 1. Prepare Backend Code

Your `backend/main.py` already includes:
- ✅ CORS enabled for any origin
- ✅ Environment variable handling via `.env`
- ✅ Firestore initialization
- ✅ All required routes

### 2. Create `.env.railway` File

```
FIRESTORE_CREDENTIALS={"type":"service_account","project_id":"...","private_key":"..."}
LIVEKIT_API_KEY=your_key
LIVEKIT_API_SECRET=your_secret
LIVEKIT_URL=https://your-livekit-instance.livekit.cloud
```

### 3. Deploy on Railway

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Create project
railway init

# Link your project directory
cd /path/to/human-in-the-loop-ai-supervisor
railway init

# Deploy
railway up
```

### 4. Get Backend URL

After deployment, Railway gives you a URL like: `https://human-in-the-loop-prod.railway.app`

This is your `BACKEND_URL`.

## Update Frontend with Backend URL

After backend is deployed, set the API endpoint on the frontend:

### Option A: Set in Browser Console (Temporary)
```javascript
localStorage.setItem('API_BASE_URL', 'https://your-backend-url.railway.app');
// Reload page
window.location.reload();
```

### Option B: Create a Settings Page (Better)
Add to `frontend/settings.html`:
```html
<input type="text" id="apiUrl" placeholder="https://your-backend.railway.app">
<button onclick="saveApiUrl()">Save</button>
<script>
  function saveApiUrl() {
    const url = document.getElementById('apiUrl').value;
    localStorage.setItem('API_BASE_URL', url);
    alert('Backend URL saved! Reload pages to take effect.');
  }
</script>
```

### Option C: Set in Vercel Environment (Production)
Add to Vercel deployment:
- Set `API_BASE_URL` environment variable in Vercel dashboard
- Create `public/config.js` that reads from fetch:
```javascript
// In index.html head
<script src="/config.js"></script>
<script>
  // config.js sets window.API_BASE_URL from environment
</script>
```

## Environment Variables Reference

| Variable | Example | Where to Get |
|----------|---------|--------------|
| `FIRESTORE_CREDENTIALS` | `{"type":"service_account",...}` | Firebase Console → Service Accounts |
| `LIVEKIT_API_KEY` | `APIxxxxx` | LiveKit Cloud Console |
| `LIVEKIT_API_SECRET` | `SECxxxx` | LiveKit Cloud Console |
| `LIVEKIT_URL` | `https://your-instance.livekit.cloud` | LiveKit Cloud Console |

## Monitoring & Logs

### Railway
- Dashboard: https://railway.app/dashboard
- Logs: Click project → Logs tab
- Metrics: Real-time CPU/Memory usage

### Render
- Dashboard: https://dashboard.render.com
- Logs: Click service → Logs tab

### Health Checks
```bash
# Test backend is running
curl https://your-backend.railway.app/docs

# Should see Swagger UI
```

## Troubleshooting

### "502 Bad Gateway"
- Check backend logs for startup errors
- Verify `PORT` environment variable is set
- Check Firestore credentials format

### "Connection refused"
- Backend URL might be wrong
- Check frontend localStorage: `localStorage.getItem('API_BASE_URL')`
- Verify CORS is enabled in backend

### "CORS error in browser"
- Backend needs CORS enabled (already done in main.py)
- Verify request URL matches backend domain exactly

### Firestore connection fails
- Check FIRESTORE_CREDENTIALS format (must be valid JSON string)
- Verify Firebase project allows service account access
- Check Firestore security rules

## Scaling & Performance

### Auto-scaling
- Railway: Automatically scales on memory/CPU usage
- Render: Configure concurrency limits

### Database Optimization
- Firestore auto-scales (no action needed)
- Consider caching frequent queries

### Monitoring
- Add Sentry for error tracking: `pip install sentry-sdk`
- Use Railway/Render built-in metrics

## Comparison Table

| Feature | Railway | Render | Heroku | PythonAnywhere |
|---------|---------|--------|--------|----------------|
| Free Tier | ✅ 500h | ✅ Limited | ❌ Paid | ✅ |
| GitHub Deploy | ✅ | ✅ | ✅ | ❌ |
| Auto-scaling | ✅ | ⚠️ | ✅ | ❌ |
| Ease of Setup | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Cost | Low | Low | High | Low |

**Recommendation:** Use **Railway** for best combination of ease-of-use, free tier, and features.

## Next Steps

1. Choose a hosting platform (Railway recommended)
2. Deploy backend and get URL
3. Update frontend with backend URL
4. Deploy frontend on Vercel
5. Test end-to-end integration
