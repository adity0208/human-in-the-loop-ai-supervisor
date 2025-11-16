# Railway.app Deployment - Fixed Build Issues

## The Problem

Railway couldn't detect how to build your Python app because it was looking for:
- A `start.sh` script
- A `Procfile` 
- A `runtime.txt` file specifying Python version

## The Solution

I've created all required files. Here's what they do:

### 1. `start.sh` (Build Script)
Tells Railway how to build and start your app:
```bash
pip install -r requirements.txt
uvicorn backend.main:app --host 0.0.0.0 --port $PORT
```

### 2. `Procfile` (Process File)
Tells Railway which process to run:
```
web: uvicorn backend.main:app --host 0.0.0.0 --port $PORT
```

### 3. `runtime.txt` (Python Version)
Specifies Python version:
```
python-3.11.7
```

### 4. `railway.json` (Configuration)
Additional Railway-specific config for environment variables.

---

## How to Deploy Now

### Step 1: Push Changes to GitHub

```bash
cd /path/to/human-in-the-loop-ai-supervisor

git add .
git commit -m "Add Railway deployment configuration (start.sh, Procfile, runtime.txt)"
git push origin main
```

### Step 2: Redeploy on Railway

**Option A: Auto-Deploy (Recommended)**
- Railway automatically redeploys when you push to GitHub
- Wait 2-3 minutes for build to complete
- Check build logs in Railway dashboard

**Option B: Manual Redeploy**
1. Go to Railway Dashboard → Your Project
2. Click "Deploy" or "Redeploy"
3. Select your branch (main)
4. Wait for build

### Step 3: Monitor Build Logs

1. Go to Railway Dashboard
2. Select your project
3. Click "Deployments" tab
4. Click latest deployment
5. View "Build Output" logs
6. Should see:
   ```
   ✓ Installing Python 3.11.7
   ✓ Installing requirements from requirements.txt
   ✓ Starting: uvicorn backend.main:app --host 0.0.0.0 --port $PORT
   ✓ Uvicorn running on 0.0.0.0:PORT
   ```

### Step 4: Get Your Backend URL

Once deployment succeeds:
1. Railway Dashboard → Your Project
2. Look for "Service URL" or "Domain"
3. Format: `https://your-project-xxxxx.railway.app`
4. Save this URL

### Step 5: Test Backend

```bash
# Test that backend is running
curl https://your-project-xxxxx.railway.app/docs

# Should return Swagger UI HTML
```

---

## Environment Variables

Make sure these are set in Railway:

### Required (Add in Railway Dashboard)

1. **FIRESTORE_CREDENTIALS**
   - Go to Firebase Console → Project Settings → Service Accounts
   - Click "Generate New Private Key"
   - Copy entire JSON content
   - Paste as Railway env variable (as JSON string)

2. **LIVEKIT_API_KEY**
   - Get from LiveKit Cloud Console
   - Format: `APIxxxxxxxxxxxxx`

3. **LIVEKIT_API_SECRET**
   - Get from LiveKit Cloud Console
   - Format: `SECxxxxxxxxxxxxxx`

4. **LIVEKIT_URL**
   - Get from LiveKit Cloud Console
   - Format: `https://your-instance.livekit.cloud`

### How to Add Environment Variables in Railway

1. Railway Dashboard → Your Project → Variables
2. Click "Add Variable"
3. Name: `FIRESTORE_CREDENTIALS`
4. Value: `{"type":"service_account",...}` (full JSON)
5. Click "Add"
6. Repeat for other variables
7. Redeploy

---

## Troubleshooting

### Build Error: "Python not found"

**Solution:**
- Check `runtime.txt` exists and has correct format
- Format should be: `python-3.11.7` (not `Python 3.11.7`)

### Build Error: "requirements.txt not found"

**Solution:**
- `requirements.txt` should be in root directory
- Not in a subfolder

### Build Error: "Module not found: firebase_admin"

**Solution:**
- Check `requirements.txt` has all dependencies
- Should include:
  ```
  fastapi
  uvicorn
  firebase-admin
  python-dotenv
  pydantic
  ```

### Build Success but App Won't Start

**Check logs:**
1. Railway Dashboard → Deployments → Latest
2. Look for "Runtime Output" (not Build Output)
3. Check for Python errors
4. Usually: Missing environment variables

**Solution:**
- Verify all 4 environment variables are set
- Check `FIRESTORE_CREDENTIALS` is valid JSON
- Redeploy after adding variables

### Error: "FIRESTORE_CREDENTIALS not in expected format"

**Cause:** JSON not properly formatted as string

**Fix:**
1. Get full JSON from Firebase Service Account
2. Make it a single-line JSON string (no newlines)
3. Example:
   ```
   {"type":"service_account","project_id":"my-project",...}
   ```

---

## Testing Deployment

### 1. Test Backend is Running

```bash
curl https://your-backend.railway.app/docs
# Should return Swagger UI
```

### 2. Test API Endpoints

```bash
# Get all requests
curl https://your-backend.railway.app/help/requests

# Should return: {"requests": []}
```

### 3. Test Firestore Connection

Open `https://your-backend.railway.app/docs` and try:
- GET `/help/requests` - Should work if Firestore is connected

### 4. Test LiveKit Token Generation

```bash
curl "https://your-backend.railway.app/livekit/token?identity=test&room=test"
# Should return: {"url": "...", "token": "..."}
```

---

## What's New (Files Created)

| File | Purpose |
|------|---------|
| `start.sh` | Build/startup script for Railway |
| `Procfile` | Defines web process for Railway |
| `runtime.txt` | Specifies Python 3.11.7 |
| `railway.json` | Railway-specific configuration |

---

## Next Steps

1. ✅ Push files to GitHub (`git push`)
2. ✅ Railway auto-detects and builds
3. ✅ Get backend URL
4. ✅ Add to frontend settings page
5. ✅ Deploy frontend to Vercel
6. ✅ Test end-to-end

---

## Local Development Still Works

```bash
# Your local setup is unchanged
python backend/main.py

# Still runs on http://127.0.0.1:8000
# No new steps needed!
```

---

## If Build Still Fails

### Check These:

1. **Files exist:**
   ```bash
   ls -la start.sh Procfile runtime.txt requirements.txt
   ```

2. **Python syntax:**
   ```bash
   python -m py_compile backend/main.py
   # Should not output anything if OK
   ```

3. **requirements.txt format:**
   ```bash
   pip install -r requirements.txt
   # Should work locally first
   ```

4. **Railway logs detail:**
   - Check "Build Output" for exact error
   - Copy error message and search online
   - Common: missing dependency, Python version issue

### Still Stuck?

Try these alternatives:

**Option A: Use Render.com instead**
- Similar to Railway but sometimes more reliable
- See `BACKEND_DEPLOYMENT.md` for Render setup

**Option B: Self-host on AWS/Heroku**
- More control but more complex
- See `ARCHITECTURE.md` for options

**Option C: Use Railway with Docker**
- Create `Dockerfile` instead of `Procfile`
- More complex but very reliable

---

## Success Indicators

When deployment succeeds, you should see:

✅ Railway Dashboard shows "Running" status
✅ API Docs page loads: `https://your-backend.railway.app/docs`
✅ Environment variables all set
✅ No errors in runtime logs
✅ Can reach from frontend settings page

---

## Next: Deploy Frontend

Once backend is running:

1. Get backend URL from Railway
2. Go to `FRONTEND_DEPLOYMENT.md`
3. Deploy frontend to Vercel
4. Add backend URL to settings page
5. Done! 🎉
