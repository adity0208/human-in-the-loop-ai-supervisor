# Vercel Deployment Checklist

## Pre-Deployment Steps

### 1. Environment Setup
- [ ] GitHub repository created and all files pushed
- [ ] Firebase project created and credentials generated
- [ ] LiveKit account created with API key and secret
- [ ] All credentials stored securely (NOT in git, only in .env locally)

### 2. Local Testing
- [ ] Run `python -m venv .venv` and activate virtual environment
- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Create `.env` file with all required variables (use .env.example as template)
- [ ] Start backend: `python backend/main.py` (runs on http://127.0.0.1:8000)
- [ ] Open frontend in browser (open `frontend/index.html`)
- [ ] Verify all pages load and API calls work
- [ ] Test pending requests flow (view → resolve → history)

### 3. Vercel Project Setup
- [ ] Login to Vercel (https://vercel.com)
- [ ] Click "Add New..." → "Project"
- [ ] Import GitHub repository
- [ ] Configure build settings:
  - **Framework Preset:** Other
  - **Build Command:** (leave blank or `vercel build`)
  - **Output Directory:** `frontend`
- [ ] Add Environment Variables (Settings → Environment Variables):
  - `FIRESTORE_CREDENTIALS` (full JSON string from firebase_credentials.json)
  - `LIVEKIT_API_KEY`
  - `LIVEKIT_API_SECRET`
  - `LIVEKIT_URL`
  - `BACKEND_URL` (leave empty, auto-detected as `/api`)
  - `FRONTEND_URL` (set to your Vercel domain, e.g., `https://your-app.vercel.app`)
- [ ] Deploy project

### 4. Post-Deployment Verification
- [ ] Open deployed app in browser
- [ ] Verify dashboard loads and shows metrics
- [ ] Check pending requests page
- [ ] Test creating a new help request (if UI allows)
- [ ] Verify request history loads
- [ ] Check knowledge base page
- [ ] Test resolution flow
- [ ] Monitor Vercel logs for errors: Settings → Logs

### 5. Production Monitoring
- [ ] Set up error tracking (optional: Sentry, LogRocket)
- [ ] Monitor API response times
- [ ] Check database usage in Firebase console
- [ ] Set up alerts for function failures
- [ ] Document any issues encountered

## Common Issues & Solutions

### "Failed to load API"
- Check that environment variables are set in Vercel
- Verify FIRESTORE_CREDENTIALS is properly formatted JSON string
- Check browser console for CORS errors

### "Placeholder token" from LiveKit endpoint
- Ensure LIVEKIT_API_KEY and LIVEKIT_API_SECRET are set
- Verify LiveKit SDK is installed: `pip show livekit-server-sdk`

### Firestore authentication fails
- Check FIRESTORE_CREDENTIALS format (must be JSON string, not object)
- Verify Firebase project permissions
- Check Firestore security rules allow read/write from backend

### Pages showing "No pending requests" on first load
- This is normal if no requests have been submitted yet
- Test by submitting a help request through the application

## Deployment Commands Reference

```bash
# Local development
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
python backend/main.py

# Then open http://127.0.0.1:8000/docs to see API documentation
```

## Vercel URLs After Deployment

- **App:** `https://[your-project-name].vercel.app`
- **API:** `https://[your-project-name].vercel.app/api`
- **Logs:** `https://vercel.com/dashboard/[your-project-name]/monitoring`

## Troubleshooting

1. **Check Vercel Build Logs:** Vercel Dashboard → Select Project → Deployments → Latest → Build Output
2. **Check Vercel Runtime Logs:** Vercel Dashboard → Select Project → Logs
3. **Backend Health Check:** `https://[your-app].vercel.app/api/docs` should show Swagger UI
4. **Frontend Health Check:** `https://[your-app].vercel.app` should load dashboard

## Next Steps After Deployment

1. Share app URL with team
2. Monitor performance and errors
3. Consider setting up custom domain
4. Implement user authentication (optional enhancement)
5. Add API rate limiting (optional enhancement)
