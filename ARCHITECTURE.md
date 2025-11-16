# Deployment Architecture & Strategy

## Overview

This application follows a **decoupled frontend-backend architecture** with independent deployment:

```
┌─────────────────────────────────────────────────────────────────┐
│                        User's Browser                           │
└─────────────────────────────────────────────────────────────────┘
           ↓                                    ↓
┌──────────────────────────┐    ┌─────────────────────────────────┐
│   FRONTEND (Vercel)      │    │    BACKEND (Railway/Render)     │
│                          │    │                                 │
│  Static HTML + JS        │←→  │  FastAPI + Python               │
│  https://app.vercel.app  │    │  https://api.railway.app        │
│                          │    │                                 │
│  - index.html            │    │  ✓ Firestore integration        │
│  - pending.html          │    │  ✓ LiveKit token generation     │
│  - history.html          │    │  ✓ Help request management      │
│  - kb.html               │    │  ✓ Knowledge base management    │
│  - resolve.html          │    │                                 │
│  - voice.html            │    │                                 │
│  - settings.html         │    │                                 │
└──────────────────────────┘    └─────────────────────────────────┘
           ↓                                    ↓
    Uses localStorage             Reads/writes to Firebase Firestore
    to store backend URL
```

## Why This Architecture?

### Benefits

| Aspect | Frontend on Vercel | Backend on Railway |
|--------|------------------|------------------|
| **Hosting** | Edge CDN globally | Scalable containerized backend |
| **Cost** | Free tier available | Free tier + pay-as-you-grow |
| **Deploy Speed** | Instant (static files) | 1-2 minutes (Python runtime) |
| **Scaling** | Auto (edge cache) | Auto (container orchestration) |
| **Maintainability** | Update UI without API restart | Update API without frontend rebuild |
| **Performance** | ~50-100ms globally | Backend handles business logic |
| **CORS** | N/A (different domains) | Handled in backend code |

### Trade-offs

| Consideration | Solution |
|---------------|----------|
| **Configuration** | Settings page in frontend (localStorage) |
| **CORS** | Backend has `CORSMiddleware` enabled |
| **Secrets** | Backend env vars, frontend has none |
| **Local Dev** | Run backend locally on `localhost:8000` |
| **Production** | Backend on Railway, frontend on Vercel |

## Deployment Workflow

### Step 1: Deploy Backend First

1. Choose platform: **Railway** (recommended) or Render
2. Connect GitHub repository
3. Set environment variables:
   - `FIRESTORE_CREDENTIALS` (JSON string)
   - `LIVEKIT_API_KEY`
   - `LIVEKIT_API_SECRET`
   - `LIVEKIT_URL`
4. Set start command: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
5. Deploy and get URL: `https://your-backend.railway.app`

**See:** `BACKEND_DEPLOYMENT.md`

### Step 2: Deploy Frontend

1. Go to Vercel
2. Import GitHub repository
3. Set output directory: `frontend`
4. Deploy and get URL: `https://your-app.vercel.app`
5. Open settings page: `https://your-app.vercel.app/settings.html`
6. Enter backend URL from Step 1
7. Click "Test Connection"
8. App now works with remote backend!

**See:** `FRONTEND_DEPLOYMENT.md`

### Step 3: Production Access

- **Frontend:** `https://your-app.vercel.app`
- **Backend API:** `https://your-backend.railway.app`
- **Swagger Docs:** `https://your-backend.railway.app/docs`

## Local Development

For local testing before deployment:

### Backend
```bash
# Install dependencies
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Configure .env with Firebase/LiveKit credentials
cp .env.example .env
# Edit .env with your values

# Start backend
python backend/main.py
# Runs on http://127.0.0.1:8000
```

### Frontend
```bash
# Option 1: Open HTML files in browser
open frontend/index.html

# Option 2: Use Python simple server
cd frontend
python -m http.server 5500
# Then open http://localhost:5500

# Option 3: Use Live Server extension in VS Code
# Right-click index.html → Open with Live Server
```

### Configure Frontend for Local Backend
```javascript
// In browser console while on localhost pages
localStorage.setItem('API_BASE_URL', 'http://127.0.0.1:8000');
location.reload();
```

## File Structure

```
human-in-the-loop-ai-supervisor/
├── backend/                          # Backend code (runs on Railway/Render)
│   ├── main.py                      # FastAPI entry point
│   ├── config.py                    # Configuration
│   ├── firebase_credentials.json     # Firebase service account (do not commit)
│   ├── models/                      # Pydantic models
│   ├── routes/                      # API endpoints
│   ├── services/                    # Business logic
│   └── database/                    # Firestore integration
│
├── frontend/                        # Frontend code (deploys to Vercel)
│   ├── index.html                  # Dashboard
│   ├── pending.html                # Pending requests (supervisor queue)
│   ├── history.html                # Request history
│   ├── kb.html                     # Knowledge base
│   ├── resolve.html                # Resolve request page
│   ├── voice.html                  # LiveKit voice demo
│   ├── settings.html               # ⭐ Backend configuration page
│   └── style.css                   # Global styles
│
├── api/                             # Not used (Vercel frontend only)
│   └── index.py                    # (Vercel serverless wrapper - ignore)
│
├── requirements.txt                # Python dependencies
├── vercel.json                     # Vercel config (frontend static only)
├── .env.example                    # Configuration template
├── .gitignore                      # Excludes secrets
│
└── DEPLOYMENT_*.md                 # Deployment guides
    ├── BACKEND_DEPLOYMENT.md        # How to deploy backend
    ├── FRONTEND_DEPLOYMENT.md       # How to deploy frontend
    └── DEPLOYMENT_CHECKLIST.md      # Pre/post checks
```

## Configuration Management

### Environment Variables

**Backend (.env file)** - Keep secret, never commit:
```env
FIRESTORE_CREDENTIALS={"type":"service_account",...}
LIVEKIT_API_KEY=APIxxxxx
LIVEKIT_API_SECRET=SECxxxxx
LIVEKIT_URL=https://instance.livekit.cloud
```

**Frontend** - Set at runtime via settings page:
1. Open `https://your-app.vercel.app/settings.html`
2. Enter backend URL
3. Click "Save Configuration"
4. Stored in browser localStorage (per browser, per domain)

### How Configuration Works

```
Local Development:
  - Backend auto-detects localhost:8000
  - No configuration needed
  - Works automatically

Production:
  - Frontend stored backend URL in localStorage
  - On page load: checks localStorage.getItem('API_BASE_URL')
  - Falls back to localhost:8000 if not set (shows warning)
  - User sets via settings.html page
```

## Troubleshooting Deployment

### Frontend can't connect to backend

**Check:**
1. Backend URL is correct: `https://backend-url.railway.app`
2. Backend is running: Visit `https://backend-url.railway.app/docs` (should show Swagger UI)
3. CORS is enabled in backend (check `backend/main.py`)
4. localStorage is set: Open browser DevTools → Application → localStorage → check `API_BASE_URL`

**Fix:**
```javascript
// In browser console
localStorage.setItem('API_BASE_URL', 'https://your-backend.railway.app');
location.reload();
```

### Backend deployment failed

**Check Railway logs:**
1. Railway Dashboard → Select project → Logs tab
2. Look for Python errors
3. Verify environment variables are set

**Common issues:**
- Missing `FIRESTORE_CREDENTIALS`
- Invalid JSON in `FIRESTORE_CREDENTIALS`
- Port not exposed (should be `$PORT`)

### Settings page shows "Could not connect"

**Causes:**
1. Backend URL is wrong
2. Backend is down
3. CORS not enabled
4. Firewall blocking request

**Test:**
```bash
curl https://your-backend.railway.app/docs
# Should return HTML
```

## Scaling Considerations

### Frontend Scaling (Vercel)
- ✅ Auto-scales globally with CDN
- ✅ No configuration needed
- ✅ Can handle 10,000+ concurrent users
- Edge cache reduces latency to <100ms worldwide

### Backend Scaling (Railway)
- ✅ Auto-scales on CPU/memory usage
- ✅ Container-based (replace at any time)
- ⚠️ Firestore is auto-scaling (no action needed)
- Consider: Connection pooling, query optimization for high load

### Database Scaling (Firestore)
- ✅ Auto-scales globally
- ✅ Document-based (good for UI state)
- ⚠️ Watch for hot collections (add sharding if needed)
- Pricing: Pay per read/write/delete ($0.06 per 100K reads)

## Cost Estimation (USD/month)

| Component | Tier | Cost | Notes |
|-----------|------|------|-------|
| Frontend (Vercel) | Pro | $20 | or free for hobby tier |
| Backend (Railway) | Pay-as-you-go | $5-50 | Depends on usage |
| Firestore | Pay-per-use | $10-100 | ~1M ops typical |
| LiveKit | Pro | $99 | or free for testing |
| **Total** | | **$134-270** | Scales with usage |

**Cost-saving tips:**
- Use free tiers during development
- Railway: 500 hours/month free = ~$5/month for always-on
- Firestore: Generous free tier (1M reads/month)
- LiveKit: Free tier for development

## Next Steps

1. ✅ **Local Testing**
   ```bash
   python backend/main.py
   # Open http://127.0.0.1:8000/docs
   # Open frontend/index.html in browser
   ```

2. ✅ **Deploy Backend**
   - Follow `BACKEND_DEPLOYMENT.md`
   - Get production URL

3. ✅ **Deploy Frontend**
   - Follow `FRONTEND_DEPLOYMENT.md`
   - Configure settings page

4. ✅ **Verify Integration**
   - Test all pages
   - Monitor backend logs

5. ✅ **Optional: Custom Domain**
   - Add domain to Vercel
   - Configure DNS records

## References

- **Vercel Docs:** https://vercel.com/docs
- **Railway Docs:** https://docs.railway.app
- **FastAPI Docs:** https://fastapi.tiangolo.com
- **Firestore Docs:** https://firebase.google.com/docs/firestore
