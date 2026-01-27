# Astro Core Python (Internal Calculation Engine + FreeAstrologyAPI Proxy)

This FastAPI microservice provides **two backends**:

1. **Internal Calculation Engine** (default) - In-house Vedic astrology calculations using Skyfield ephemeris
2. **FreeAstrologyAPI Proxy** (fallback) - Proxies FreeAstrologyAPI.com when needed

Switch between backends via environment variable `ASTROLOGY_BACKEND=internal|freeastrology|mock` with **zero frontend changes**.

## Features

### Internal Calculation Engine (NEW!)

- `POST /planets`: Calculate birth chart with planetary positions using Skyfield (JPL DE421 ephemeris)
- Sidereal (Vedic) coordinates with Lahiri ayanamsha
- Ascendant & house calculations (Whole Sign + Placidus)
- Nakshatras, signs, retrograde detection
- **Unlimited requests** (no API limits!)
- Same API contract as FreeAstrologyAPI

### FreeAstrologyAPI Proxy (Legacy)

- `GET /horoscope/daily`: Fetches planetary snapshot data for a single sign
- `GET /horoscope/daily/batch`: Hydrates all twelve signs in parallel
- `GET /panchang/today`: Returns Panchang details
- Normalised error responses, request/response logging

## Quick Start

### Option 1: Internal Engine (Recommended)

```bash
cd services/astro-core-python

# Setup (creates venv, installs deps, downloads ephemeris)
chmod +x setup.sh
./setup.sh

# Configure
cp .env.example .env
# Edit .env: Set ASTROLOGY_BACKEND=internal

# Start service
source .venv/bin/activate
python router.py

# Or with auto-reload
uvicorn router:app --port 4001 --reload
```

Service runs on `http://localhost:4001` with **unlimited requests** and no API costs!

### Option 2: FreeAstrologyAPI Proxy

```bash
cd services/astro-core-python
source .venv/bin/activate

# Configure
export ASTROLOGY_BACKEND=freeastrology
export FREE_API_KEY=your_api_key_here

# Start
python router.py
```

### Frontend Integration

In Next.js `.env.local`:

```bash
ASTRO_CORE_URL=http://localhost:4001
```

**No code changes needed!** Backend selection is transparent to frontend.

## Environment Variables

See `.env.example` for all options. Key settings:

```bash
# Backend selection (internal, freeastrology, mock)
ASTROLOGY_BACKEND=internal

# FreeAstrologyAPI settings (only needed if backend=freeastrology)
FREE_API_BASE_URL=https://json.freeastrologyapi.com
FREE_API_KEY=your_api_key_here

# Server settings
APP_PORT=4001
DEFAULT_LOCALE=en
DEFAULT_TIMEZONE=Asia/Kolkata
DEFAULT_LATITUDE=28.6139
DEFAULT_LONGITUDE=77.2090
```

## API Endpoints

### Internal Engine Mode

- `POST /planets` - Calculate birth chart with planetary positions
- `POST /horoscope-chart-svg-code` - Generate chart SVG (placeholder for MVP)
- `GET /health` - Health check

### FreeAstrologyAPI Proxy Mode

- `GET /horoscope/daily` - Daily horoscope for a sign
- `GET /horoscope/daily/batch` - All 12 signs
- `GET /panchang/today` - Panchang data
- `GET /healthz` - Health check

See `INTERNAL_ENGINE.md` for detailed API documentation.

## Testing

### Validation Tests (Internal Engine)

```bash
source .venv/bin/activate
python test_validation.py

# Should output: ✅ ALL TESTS PASSED
```

### Unit Tests

```bash
pytest
```

## Why Use Internal Engine?

| Feature           | Internal Engine       | FreeAstrologyAPI              |
| ----------------- | --------------------- | ----------------------------- |
| **Cost**          | Free                  | $0 (50 req/day) or paid plans |
| **Requests**      | Unlimited             | 50/day (free tier)            |
| **Accuracy**      | JPL DE421 (NASA data) | Commercial ephemeris          |
| **Privacy**       | Local calculations    | External API calls            |
| **Latency**       | 5-15ms                | 200-500ms                     |
| **Customization** | Full control          | Limited                       |
| **Dependencies**  | Skyfield (~50MB)      | None                          |

## Documentation

- **INTERNAL_ENGINE.md** - Complete guide to internal calculation engine
- **README.md** (this file) - Quick start and overview

## Migration Path

1. **Current state**: Using FreeAstrologyAPI directly from frontend
2. **Phase 1**: Deploy astro-core-python with `ASTROLOGY_BACKEND=freeastrology` (proxy mode)
3. **Phase 2**: Switch to `ASTROLOGY_BACKEND=internal` (no frontend changes!)
4. **Future**: Extend with custom features, more ayanamsha systems, divisional charts
