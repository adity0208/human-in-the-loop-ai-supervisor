# Frontend Deployment on Vercel (Frontend Only)

Deploy just the frontend static files on Vercel while backend runs separately.

## Prerequisites

- ✅ Backend deployed (see `BACKEND_DEPLOYMENT.md`)
- ✅ Backend URL obtained (e.g., `https://your-backend.railway.app`)
- ✅ Vercel account (free at https://vercel.com)
- ✅ GitHub repository with code pushed

## Step 1: Deploy Frontend on Vercel

### Option A: Via Vercel Web Dashboard (Easiest)

1. Go to https://vercel.com/new
2. Click "Import Git Repository"
3. Select your GitHub repository
4. Configure project:
   - **Project Name:** `human-in-the-loop-ai-supervisor` (or your choice)
   - **Framework:** Select "Other" (static frontend)
   - **Root Directory:** `.` (default)
   - **Build Command:** (leave blank)
   - **Output Directory:** `frontend`
5. Click "Deploy" (takes 1-2 minutes)
6. Get your Vercel URL: `https://your-project-name.vercel.app`

### Option B: Via Vercel CLI

```bash
# Install Vercel CLI
npm install -g vercel

# Login
vercel login

# Deploy
cd /path/to/human-in-the-loop-ai-supervisor
vercel

# Follow prompts, select "frontend" as output directory
# Get your URL from output
```

## Step 2: Configure Frontend with Backend URL

Once frontend is deployed, set the backend URL. Choose one method:

### Method 1: Settings Page (User-Friendly) ⭐ Recommended

1. Add a settings page at `frontend/settings.html`:

```html
<!DOCTYPE html>
<html>
<head>
    <title>App Settings</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <nav class="navbar navbar-dark bg-primary">
        <div class="container-fluid">
            <span class="navbar-brand">Settings</span>
        </div>
    </nav>
    
    <div class="container mt-4">
        <div class="card">
            <div class="card-body">
                <h5 class="card-title">Backend Configuration</h5>
                <p class="text-muted">Enter your deployed backend URL</p>
                
                <div class="mb-3">
                    <label class="form-label">Backend API URL</label>
                    <input type="text" id="apiUrl" class="form-control" 
                           placeholder="https://your-backend-url.railway.app"
                           value="">
                </div>
                
                <div class="mb-3">
                    <button class="btn btn-primary" onclick="saveConfig()">Save Configuration</button>
                    <button class="btn btn-secondary ms-2" onclick="testConnection()">Test Connection</button>
                </div>
                
                <div id="status"></div>
            </div>
        </div>
    </div>
    
    <script>
        // Load saved config on page load
        document.addEventListener('DOMContentLoaded', () => {
            const saved = localStorage.getItem('API_BASE_URL');
            if (saved) {
                document.getElementById('apiUrl').value = saved;
            }
        });
        
        function saveConfig() {
            const url = document.getElementById('apiUrl').value.trim();
            
            if (!url) {
                showStatus('Please enter a valid URL', 'danger');
                return;
            }
            
            if (!url.startsWith('http://') && !url.startsWith('https://')) {
                showStatus('URL must start with http:// or https://', 'danger');
                return;
            }
            
            localStorage.setItem('API_BASE_URL', url);
            showStatus('✅ Backend URL saved! Reload other pages to apply.', 'success');
        }
        
        async function testConnection() {
            const url = document.getElementById('apiUrl').value.trim();
            
            if (!url) {
                showStatus('Please enter a URL first', 'warning');
                return;
            }
            
            showStatus('Testing connection...', 'info');
            
            try {
                const response = await fetch(`${url}/docs`);
                if (response.ok) {
                    showStatus('✅ Successfully connected to backend!', 'success');
                } else {
                    showStatus('⚠️ Backend responded but with status ' + response.status, 'warning');
                }
            } catch (e) {
                showStatus('❌ Could not connect: ' + e.message, 'danger');
            }
        }
        
        function showStatus(message, type) {
            const statusDiv = document.getElementById('status');
            statusDiv.innerHTML = `<div class="alert alert-${type}">${message}</div>`;
        }
    </script>
</body>
</html>
```

2. Update `frontend/index.html` navbar to add settings link:

```html
<a href="settings.html" class="nav-link" style="position: absolute; right: 20px; top: 15px;">
    <i class="bi bi-gear"></i> Settings
</a>
```

3. Access settings at: `https://your-app.vercel.app/settings.html`

### Method 2: Browser Console (Temporary)

```javascript
// Paste in browser console (F12)
localStorage.setItem('API_BASE_URL', 'https://your-backend-url.railway.app');
location.reload();
```

### Method 3: Environment Variables in Vercel (Advanced)

1. Go to Vercel Dashboard → Your Project → Settings → Environment Variables
2. Add:
   - **Name:** `NEXT_PUBLIC_API_BASE_URL`
   - **Value:** `https://your-backend-url.railway.app`
3. Redeploy: Push code or click "Redeploy" in Vercel

Then update `frontend/index.html` to use it:
```javascript
const API_BASE = (() => {
    // Try environment variable first
    if (typeof process !== 'undefined' && process.env.NEXT_PUBLIC_API_BASE_URL) {
        return process.env.NEXT_PUBLIC_API_BASE_URL;
    }
    // Try localStorage
    const stored = localStorage.getItem('API_BASE_URL');
    if (stored) return stored;
    // Defaults
    if (window.location.hostname === 'localhost') return 'http://127.0.0.1:8000';
    return 'http://127.0.0.1:8000';
})();
```

## Step 3: Verify Deployment

1. Open your Vercel URL: `https://your-app.vercel.app`
2. Go to Settings page and enter backend URL
3. Click "Test Connection" to verify backend is reachable
4. Navigate through app pages - should now fetch from backend

## Architecture Diagram

```
┌─────────────────────────────────────────────────────┐
│             User's Browser                          │
└─────────────────────────────────────────────────────┘
              ↓                           ↓
   ┌──────────────────────────┐  ┌──────────────────────┐
   │ Vercel (Frontend)        │  │ Railway (Backend)    │
   │ https://app.vercel.app   │  │ https://api.railway  │
   │                          │  │                      │
   │ - index.html             │→ │ - FastAPI app        │
   │ - pending.html           │→ │ - Firestore          │
   │ - history.html           │→ │ - LiveKit tokens     │
   │ - kb.html                │  │                      │
   │ - resolve.html           │  │                      │
   │ - voice.html             │  │                      │
   │ - settings.html          │  │                      │
   └──────────────────────────┘  └──────────────────────┘
```

## Deployment Checklist

- [ ] Backend deployed and URL obtained
- [ ] Frontend pushed to GitHub
- [ ] Vercel project created and deployed
- [ ] Settings page accessible at `https://your-app.vercel.app/settings.html`
- [ ] Backend URL configured via settings page
- [ ] Test connection passing
- [ ] Dashboard loads and fetches data
- [ ] Pending requests page works
- [ ] History page works
- [ ] Knowledge base page works
- [ ] Can resolve requests

## Troubleshooting

### "API_BASE_URL not configured" warning in console

**Solution:** Go to settings page and enter your backend URL

```javascript
localStorage.setItem('API_BASE_URL', 'https://your-backend.railway.app');
```

### CORS Error: "Access-Control-Allow-Origin"

**Issue:** Browser blocks request to backend

**Solution:** 
- Verify backend has CORS enabled (check `backend/main.py`)
- Backend should have: `app.add_middleware(CORSMiddleware, ...)`
- Try exact URL without trailing slash

### 404 "Not Found" on some pages

**Issue:** URL structure might be wrong

**Solution:**
- Ensure all HTML files are in `frontend/` directory
- Check Vercel build output: Settings → Deployments

### Backend URL not saving

**Issue:** localStorage not working

**Solution:**
- Check browser privacy/cookie settings
- Try incognito/private mode
- Allow third-party cookies

## Updating Deployment

### Update Frontend (Vercel)

```bash
# Make changes
git add .
git commit -m "Update frontend"
git push origin main

# Vercel auto-deploys on GitHub push
```

### Update Backend (Railway)

```bash
# Make changes
git add .
git commit -m "Update backend"
git push origin main

# Railway auto-deploys on GitHub push
```

## Custom Domain (Optional)

### Add Domain to Vercel

1. Go to Vercel Dashboard → Your Project → Settings → Domains
2. Add your custom domain
3. Follow DNS setup instructions from your domain provider
4. Wait 5-10 minutes for DNS propagation

Example: `app.yourdomain.com`

## Performance Tips

1. **Enable Vercel Analytics** (optional, free):
   - Vercel Dashboard → Settings → Analytics

2. **Monitor API calls**:
   - Browser DevTools → Network tab
   - Check response times

3. **Optimize images** (if added):
   - Use WebP format
   - Lazy load with `loading="lazy"`

## Support

- **Vercel Docs:** https://vercel.com/docs
- **Vercel Status:** https://www.vercelstatus.com
- **GitHub Issues:** Create issue in your repository
