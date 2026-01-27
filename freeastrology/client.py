from __future__ import annotations

from collections.abc import Mapping
import json
from datetime import datetime, timezone
from typing import Any, Optional, Dict

import httpx
from zoneinfo import ZoneInfo

from .config import get_settings


class FreeAstrologyApiError(Exception):
  """Raised when FreeAstrologyAPI responds with an error."""


class FreeAstrologyApiClient:
  def __init__(self, timeout: Optional[float] = None) -> None:
    settings = get_settings()
    self._base_url = settings.free_api_base_url.rstrip("/")
    self._timeout = timeout or settings.http_timeout_seconds
    self._api_key = settings.free_api_key
    self._settings = settings

  async def get_daily_horoscope_data(
    self,
    sign: str,
    locale: str,
    date: Optional[str] = None,
    timezone_name: Optional[str] = None,
  ) -> Mapping[str, Any]:
    payload = self._build_payload(date=date, timezone_name=timezone_name)
    payload["language"] = locale
    return await self._post("/planets", payload)

  async def get_today_panchang(
    self,
    locale: str,
    date: Optional[str] = None,
    timezone_name: Optional[str] = None,
  ) -> Mapping[str, Any]:
    payload = self._build_payload(date=date, timezone_name=timezone_name)
    payload["language"] = locale
    return await self._post("/complete-panchang", payload)

  def _build_payload(self, date: Optional[str], timezone_name: Optional[str]) -> Dict[str, Any]:
    tz = timezone_name or self._settings.default_timezone
    try:
      zone = ZoneInfo(tz)
    except Exception:
      zone = timezone.utc

    if date:
      parsed = _parse_date(date, zone)
      target = parsed or datetime.now(zone)
    else:
      target = datetime.now(zone)

    offset_hours = zone.utcoffset(target).total_seconds() / 3600 if target.tzinfo else 0

    return {
      "year": target.year,
      "month": target.month,
      "date": target.day,
      "hours": target.hour,
      "minutes": target.minute,
      "seconds": target.second,
      "latitude": self._settings.default_latitude,
      "longitude": self._settings.default_longitude,
      "timezone": offset_hours,
      "ayanamsa": "lahiri",
    }

  async def _post(self, path: str, payload: Mapping[str, Any]) -> Mapping[str, Any]:
    headers = {
      "Accept": "application/json",
      "Content-Type": "application/json",
      "x-api-key": self._api_key,
    }

    async with httpx.AsyncClient(timeout=self._timeout) as client:
      response = await client.post(f"{self._base_url}{path}", json=payload, headers=headers)

      if response.status_code >= 400:
        raise FreeAstrologyApiError(f"FreeAstrology API error {response.status_code}: {response.text}")

      try:
        return response.json()
      except json.JSONDecodeError as exc:
        raise FreeAstrologyApiError(f"Unable to decode FreeAstrology API response: {exc}") from exc


def _parse_date(raw: str, zone: ZoneInfo) -> datetime | None:
  normalized = raw.strip()
  if normalized.endswith("Z"):
    normalized = normalized[:-1] + "+00:00"
  try:
    dt = datetime.fromisoformat(normalized)
    if dt.tzinfo is None:
      dt = dt.replace(tzinfo=zone)
    return dt.astimezone(zone)
  except ValueError:
    return None
