# ⚡ RAILWAY FIX - Quick Reference

## The Issue ❌
```
Railpack could not determine how to build the app
⚠ Script start.sh not found
```

## The Fix ✅
Created 4 config files:
- ✅ `start.sh` - Build script
- ✅ `Procfile` - Process config
- ✅ `runtime.txt` - Python 3.11.7
- ✅ `railway.json` - Railway config

## Deploy Now (Copy & Paste)

```bash
# 1. Commit
git add .
git commit -m "Railway config files"
git push

# 2. Wait 3 min for Railway to build

# 3. Check dashboard
# https://dashboard.railway.app
# Look for green ✓ Success
```

## Get Backend URL

Railway Dashboard → Project → Service URL

Format: `https://your-project-xxxxx.railway.app`

## Test Backend

```bash
# Should return Swagger UI
https://your-backend-xxxxx.railway.app/docs

# Should return {"requests":[]}
curl https://your-backend-xxxxx.railway.app/help/requests
```

## Next: Deploy Frontend

1. Go: https://vercel.com/new
2. Import repo
3. Output: `frontend`
4. Deploy
5. Go to: `/settings.html`
6. Paste backend URL
7. Done! ✅

## Files Info

| File | What It Does |
|------|-------------|
| `start.sh` | Tells Railway how to build & run |
| `Procfile` | Defines the web process |
| `runtime.txt` | Python version: 3.11.7 |
| `railway.json` | Additional config |

## Troubleshooting

**Build still failing?**
→ Check environment variables in Railway
→ Ensure FIRESTORE_CREDENTIALS set

**Backend won't connect?**
→ Check Firestore credentials valid JSON
→ Check LiveKit variables set

**Need more help?**
→ See `RAILWAY_FIX.md` (detailed)
→ See `RAILWAY_QUICK_FIX.md` (quick)
→ See `DEPLOYMENT_READY.md` (overview)

---

**Status:** Ready to deploy! Just push code. 🚀
