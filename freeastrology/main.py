from typing import Annotated, Optional, Dict

from fastapi import Depends, FastAPI, HTTPException, Query

from .client import FreeAstrologyApiClient, FreeAstrologyApiError
from .config import Settings, get_settings
from .models import DailyHoroscopeResult, ErrorResponse, PanchangResult
from .translator import normalize_daily, normalize_panchang

app = FastAPI(
  title="Jyotishya Astro Core (FreeAstrologyAPI Proxy)",
  version="0.3.0",
  docs_url="/api/docs",
  redoc_url="/api/redoc",
)


def get_client(settings: Annotated[Settings, Depends(get_settings)]) -> FreeAstrologyApiClient:
  return FreeAstrologyApiClient(timeout=settings.http_timeout_seconds)


@app.get("/healthz")
async def health() -> Dict[str, str]:
  return {"status": "ok", "source": "freeastrologyapi-proxy"}


@app.get(
  "/api/astro-core/horoscope/daily",
  response_model=DailyHoroscopeResult,
  responses={502: {"model": ErrorResponse}, 422: {"model": ErrorResponse}},
)
async def daily_horoscope(
  sun_sign: Annotated[str, Query(alias="sunSign")],
  locale: Annotated[Optional[str], Query()] = None,
  date: Annotated[Optional[str], Query()] = None,
  timezone: Annotated[Optional[str], Query()] = None,
  client: FreeAstrologyApiClient = Depends(get_client),
  settings: Settings = Depends(get_settings),
) -> DailyHoroscopeResult:
  target_locale = locale or settings.default_locale
  try:
    payload = await client.get_daily_horoscope_data(sign=sun_sign, locale=target_locale, date=date, timezone_name=timezone)
    return normalize_daily(sign=sun_sign, payload=payload, timezone=timezone)
  except FreeAstrologyApiError as exc:
    raise HTTPException(status_code=502, detail={"error": "freeastrologyapi_failure", "message": str(exc)})


@app.get(
  "/api/astro-core/horoscope/daily/batch",
  responses={200: {"description": "Dictionary keyed by Western sun sign"}, 502: {"model": ErrorResponse}},
)
async def daily_batch(
  locale: Annotated[Optional[str], Query()] = None,
  date: Annotated[Optional[str], Query()] = None,
  timezone: Annotated[Optional[str], Query()] = None,
  client: FreeAstrologyApiClient = Depends(get_client),
  settings: Settings = Depends(get_settings),
) -> Dict[str, Dict[str, Optional[str]]]:
  target_locale = locale or settings.default_locale
  signs = [
    "aries",
    "taurus",
    "gemini",
    "cancer",
    "leo",
    "virgo",
    "libra",
    "scorpio",
    "sagittarius",
    "capricorn",
    "aquarius",
    "pisces",
  ]

  results: Dict[str, Dict[str, Optional[str]]] = {}
  for sign in signs:
    try:
      payload = await client.get_daily_horoscope_data(sign=sign, locale=target_locale, date=date, timezone_name=timezone)
    except FreeAstrologyApiError as exc:
      raise HTTPException(status_code=502, detail={"error": "freeastrologyapi_failure", "message": str(exc)})

    normalized = normalize_daily(sign=sign, payload=payload, timezone=timezone).horoscope
    results[sign.capitalize()] = {
      "summary": normalized.guidance,
      "mood": normalized.mood,
      "luckyNumber": normalized.luckyNumber,
      "luckyColor": normalized.luckyColor,
    }

  return results


@app.get(
  "/api/astro-core/panchang/today",
  response_model=PanchangResult,
  responses={502: {"model": ErrorResponse}},
)
async def today_panchang(
  locale: Annotated[Optional[str], Query()] = None,
  date: Annotated[Optional[str], Query()] = None,
  timezone: Annotated[Optional[str], Query()] = None,
  client: FreeAstrologyApiClient = Depends(get_client),
  settings: Settings = Depends(get_settings),
) -> PanchangResult:
  target_locale = locale or settings.default_locale
  try:
    payload = await client.get_today_panchang(locale=target_locale, date=date, timezone_name=timezone)
    return normalize_panchang(payload=payload, timezone=timezone)
  except FreeAstrologyApiError as exc:
    raise HTTPException(status_code=502, detail={"error": "freeastrologyapi_failure", "message": str(exc)})
