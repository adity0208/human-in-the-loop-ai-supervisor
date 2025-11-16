# Vercel Deployment Guide

## Prerequisites
- Vercel account (free at vercel.com)
- GitHub repository (push your code first)
- Firebase Firestore credentials JSON
- LiveKit API credentials

---

## Step 1: Prepare Your Repository

### Update `.env` with your credentials:
```bash
cp .env.example .env
```

Fill in the actual values:
- `FIRESTORE_CREDENTIALS` - Path to Firebase credentials JSON file
- `LIVEKIT_API_KEY` - Your LiveKit API key
- `LIVEKIT_API_SECRET` - Your LiveKit API secret
- `LIVEKIT_URL` - Your LiveKit URL

### Push to GitHub:
```bash
git add .
git commit -m "Prepare for Vercel deployment"
git push origin main
```

---

## Step 2: Create Vercel Project

1. Go to [vercel.com](https://vercel.com)
2. Click "New Project"
3. Select your GitHub repository
4. Click "Import"

---

## Step 3: Configure Environment Variables

In the Vercel dashboard:

1. Go to **Settings** → **Environment Variables**
2. Add each variable from your `.env` file:

| Key | Value |
|-----|-------|
| `FIRESTORE_CREDENTIALS` | *Paste full JSON content of your firebase_credentials.json* |
| `LIVEKIT_API_KEY` | Your LiveKit API key |
| `LIVEKIT_API_SECRET` | Your LiveKit API secret |
| `LIVEKIT_URL` | Your LiveKit URL (wss://...) |

**Important:** For `FIRESTORE_CREDENTIALS`, paste the **entire JSON object as a string**, not line by line.

---

## Step 4: Configure Build & Deploy

The `vercel.json` file already handles routing:

- **Backend**: `/api/*` routes to FastAPI
- **Frontend**: All other routes serve from `/frontend`

---

## Step 5: Deploy

Click the **Deploy** button. Vercel will:

1. Build the Python backend
2. Serve static frontend files
3. Route API calls appropriately

**Deployment URL** will be shown after successful build.

---

## Step 6: Access Your App

- **Frontend**: `https://your-project.vercel.app`
- **Backend API**: `https://your-project.vercel.app/api`

The frontend automatically detects the API endpoint based on the domain.

---

## Common Issues

### Issue: "Module not found"
**Solution:** Ensure `requirements.txt` has all dependencies:
```bash
pip freeze > requirements.txt
git push
```

### Issue: API calls returning 404
**Solution:** Frontend auto-detects API endpoint. On Vercel:
- Local: `http://127.0.0.1:8000`
- Production: `https://your-project.vercel.app/api`

### Issue: CORS errors
**Solution:** Backend already has CORS enabled. If issues persist:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust as needed
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Issue: Firestore credentials not working
**Solution:** Verify:
1. JSON is properly pasted as environment variable
2. Firestore API is enabled in Firebase console
3. Service account has correct permissions

---

## Local Development (Optional)

To test locally before deploying:

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export FIRESTORE_CREDENTIALS=./backend/firebase_credentials.json
export LIVEKIT_API_KEY=your_key
export LIVEKIT_API_SECRET=your_secret
export LIVEKIT_URL=your_url

# Run backend
uvicorn backend.main:app --reload

# In another terminal, serve frontend
cd frontend
python -m http.server 5500
```

Access at `http://localhost:5500`

---

## Production Best Practices

1. **Use environment variables** for all secrets
2. **Enable Vercel Analytics** to monitor performance
3. **Set up custom domain** in Vercel settings
4. **Enable automatic deployments** on git push
5. **Monitor Firestore quotas** - may need upgrade as usage grows
6. **Add request rate limiting** for API endpoints

---

## Scaling Considerations

- **Vercel Functions**: Scale automatically with traffic
- **Firestore**: Free tier includes generous quotas
- **Bandwidth**: Vercel includes free bandwidth
- **Monitor logs** via Vercel dashboard

---

## Rollback

If deployment fails:

1. Go to **Deployments** in Vercel
2. Find the last successful deployment
3. Click **...** → **Promote to Production**

---

## Next Steps

After deployment:

1. ✅ Test all endpoints via frontend
2. ✅ Verify Firestore reads/writes
3. ✅ Test LiveKit integration (if using voice.html)
4. ✅ Share deployment URL with team

---

**Your app is now live on the web! 🚀**
