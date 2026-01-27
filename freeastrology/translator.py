from datetime import datetime
from typing import Any, Mapping, Sequence, Union, Optional

from .models import DailyHoroscopeResult, HoroscopeSummary, PanchangDetails, PanchangResult, ProviderMetadata


def normalize_daily(sign: str, payload: Union[Mapping[str, Any], Sequence[Any]], timezone: Optional[str] = None) -> DailyHoroscopeResult:
  envelope = _extract_envelope(payload)
  summary_text = _build_guidance(envelope, sign)

  snapshot = {}
  if isinstance(envelope.get("planets"), Sequence):
    snapshot["planets"] = envelope.get("planets")
  if isinstance(envelope.get("planet_positions"), Sequence):
    snapshot["planetPositions"] = envelope.get("planet_positions")

  summary = HoroscopeSummary(
    date=_parse_datetime(envelope.get("date") or envelope.get("timestamp")) or datetime.utcnow(),
    sunSign=sign.lower(),
    guidance=summary_text,
    mood=envelope.get("mood"),
    luckyNumber=_string(envelope.get("lucky_number") or envelope.get("luckyNumber")),
    luckyColor=envelope.get("lucky_color") or envelope.get("luckyColor"),
    snapshot=snapshot or None,
  )

  metadata = ProviderMetadata(
    generatedAt=_parse_datetime(envelope.get("generatedAt") or envelope.get("timestamp")) or datetime.utcnow(),
    timezone=timezone,
    raw=payload,
  )

  return DailyHoroscopeResult(metadata=metadata, horoscope=summary)


def normalize_panchang(payload: Union[Mapping[str, Any], Sequence[Any]], timezone: Optional[str] = None) -> PanchangResult:
  envelope = _extract_envelope(payload)

  details = PanchangDetails(
    date=_parse_datetime(envelope.get("date") or envelope.get("day")) or datetime.utcnow(),
    tithi=envelope.get("tithi") or envelope.get("tithi_name") or "Unknown",
    nakshatra=envelope.get("nakshatra") or envelope.get("nakshatra_name") or "Unknown",
    yoga=envelope.get("yoga") or envelope.get("yoga_name") or "Unknown",
    karana=envelope.get("karana") or envelope.get("karana_name") or "Unknown",
    sunrise=envelope.get("sunrise") or envelope.get("sunrise_time") or "",
    sunset=envelope.get("sunset") or envelope.get("sunset_time") or "",
  )

  metadata = ProviderMetadata(
    generatedAt=_parse_datetime(envelope.get("generatedAt") or envelope.get("timestamp")) or datetime.utcnow(),
    timezone=timezone,
    raw=payload,
  )

  return PanchangResult(metadata=metadata, panchang=details)


def _build_guidance(envelope: Mapping[str, Any], sign: str) -> str:
  moon_sign = envelope.get("moon_sign") or envelope.get("moonSign")
  tithi = envelope.get("tithi") or envelope.get("tithi_name")
  yoga = envelope.get("yoga") or envelope.get("yoga_name")
  planets = envelope.get("planets") or envelope.get("planet_positions")

  components = [f"Planetary snapshot for {sign.capitalize()}."]
  if moon_sign:
    components.append(f"Moon transits {moon_sign}.")
  if tithi:
    components.append(f"Tithi: {tithi}.")
  if yoga:
    components.append(f"Yoga: {yoga}.")
  if planets and isinstance(planets, Sequence):
    first_planet = next(iter(planets), None)
    if isinstance(first_planet, Mapping):
      name = first_planet.get("name") or first_planet.get("planet")
      sign_name = first_planet.get("sign") or first_planet.get("rashi")
      if name and sign_name:
        components.append(f"{name} currently resides in {sign_name}.")

  components.append("Detailed guidance requires LLM interpretation.")
  return " ".join(components)


def _parse_datetime(value: Any) -> Optional[datetime]:
  if not value:
    return None
  if isinstance(value, datetime):
    return value

  for fmt in ("%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
    try:
      return datetime.strptime(str(value), fmt)
    except ValueError:
      continue
  return None


def _string(value: Any) -> Optional[str]:
  if value in (None, ""):
    return None
  return str(value)


def _extract_envelope(payload: Union[Mapping[str, Any], Sequence[Any]]) -> Mapping[str, Any]:
  if isinstance(payload, Mapping):
    data = payload.get("data")
    if isinstance(data, Mapping):
      return data
    if isinstance(data, Sequence):
      first = next(iter(data), None)
      if isinstance(first, Mapping):
        return first
    return payload

  if isinstance(payload, Sequence):
    first = next(iter(payload), None)
    if isinstance(first, Mapping):
      return first

  return {}
