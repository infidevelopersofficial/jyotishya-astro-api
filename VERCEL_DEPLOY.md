# Astro Core Python - Vercel Deployment Guide

Production-ready FastAPI astrology service with internal calculation engine.

## 🚀 Quick Deploy to Vercel

### Prerequisites
- GitHub account
- Vercel account (free tier works)
- Git installed locally

---

## Step 1: Create GitHub Repository

```bash
# Navigate to the standalone service directory
cd services/astro-core-python-standalone

# Initialize git repo
git init

# Add all files
git add .

# Initial commit
git commit -m "feat: astro-core-python standalone Vercel deployment"

# Create repo on GitHub (using GitHub CLI, or do manually)
gh repo create jyotishya-astro-api --public --source=. --push

# Or manually:
# 1. Go to https://github.com/new
# 2. Create repo named "jyotishya-astro-api"
# 3. Push:
git remote add origin https://github.com/YOUR_USERNAME/jyotishya-astro-api.git
git branch -M main
git push -u origin main
```

---

## Step 2: Deploy to Vercel

### Option A: Vercel Dashboard (Recommended)

1. Go to [vercel.com/new](https://vercel.com/new)
2. Click "Import Project"
3. Select your `jyotishya-astro-api` repository
4. Configure:
   - **Framework Preset**: Other
   - **Root Directory**: `.` (leave as root)
   - **Build Command**: (leave empty)
   - **Output Directory**: (leave empty)
5. Add Environment Variables:
   ```
   ASTROLOGY_BACKEND = internal
   ```
6. Click "Deploy"

### Option B: Vercel CLI

```bash
# Install Vercel CLI
npm i -g vercel

# Login
vercel login

# Deploy from the project directory
cd services/astro-core-python-standalone
vercel

# For production deployment
vercel --prod
```

---

## Step 3: Configure Environment Variables

In Vercel Dashboard → Project Settings → Environment Variables:

| Variable | Value | Required |
|----------|-------|----------|
| `ASTROLOGY_BACKEND` | `internal` | ✅ Yes |
| `FREE_API_KEY` | Your API key | Only if using `freeastrology` backend |
| `DEFAULT_TIMEZONE` | `Asia/Kolkata` | Optional |

---

## Step 4: Verify Deployment

After deployment, you'll get a URL like:
```
https://jyotishya-astro-api.vercel.app
```

### Test Endpoints

```bash
# Health check
curl https://jyotishya-astro-api.vercel.app/health

# Calculate birth chart
curl -X POST https://jyotishya-astro-api.vercel.app/planets \
  -H "Content-Type: application/json" \
  -d '{
    "year": 1990,
    "month": 5,
    "date": 15,
    "hours": 10,
    "minutes": 30,
    "seconds": 0,
    "latitude": 28.6139,
    "longitude": 77.209,
    "timezone": 5.5,
    "observation_point": "topocentric",
    "ayanamsha": "lahiri"
  }'
```

---

## Step 5: Connect to Next.js Frontend

In your Next.js project's `.env.local`:

```bash
# Add your deployed API URL
ASTRO_CORE_URL=https://jyotishya-astro-api.vercel.app
```

**No frontend code changes needed!** The existing provider will automatically use the real API.

---

## File Structure

```
astro-core-python-standalone/
├── api/
│   └── index.py          # Vercel serverless entry point
├── internal/
│   ├── __init__.py
│   ├── houses.py         # House calculations
│   ├── nakshatras.py     # Nakshatra data
│   ├── planetary.py      # Planetary positions (Skyfield)
│   ├── routes.py         # FastAPI routes
│   └── signs.py          # Zodiac sign data
├── freeastrology/
│   ├── __init__.py
│   ├── client.py         # FreeAstrologyAPI client
│   ├── config.py         # Settings configuration
│   ├── main.py           # Proxy routes
│   ├── models.py         # Pydantic models
│   └── translator.py     # Response translation
├── de421.bsp             # NASA ephemeris data (~16MB)
├── router.py             # Main FastAPI app
├── requirements.txt      # Pinned dependencies
├── vercel.json           # Vercel configuration
├── .env.example          # Environment template
├── .gitignore
└── VERCEL_DEPLOY.md      # This file
```

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Service info |
| `/health` | GET | Health check |
| `/planets` | POST | Calculate birth chart |
| `/horoscope-chart-svg-code` | POST | Generate chart SVG |

---

## Troubleshooting

### "Module not found" errors
- Ensure `de421.bsp` is committed to the repo (it's ~16MB)
- Check that `internal/` and `freeastrology/` directories are included

### Cold start delays
- First request after inactivity takes 2-5 seconds (normal for serverless)
- Subsequent requests are fast (~100-300ms)

### Ephemeris file missing
The `de421.bsp` file is required for planetary calculations. If missing:
```bash
python -c "from skyfield.api import load; load('de421.bsp')"
```

---

## Cost Considerations

| Item | Vercel Free Tier |
|------|------------------|
| Function Invocations | 100,000/month |
| Bandwidth | 100GB/month |
| Function Duration | 10 seconds max |

For most astrology apps, the free tier is sufficient.

---

## Next Steps

1. ✅ Deploy to Vercel
2. ✅ Test `/health` and `/planets` endpoints
3. ✅ Set `ASTRO_CORE_URL` in your Next.js `.env.local`
4. ✅ Verify horoscope data loads from real API
5. 🔲 (Optional) Add custom domain
6. 🔲 (Optional) Enable Vercel Analytics
