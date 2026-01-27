from datetime import datetime
from typing import Any, Optional, Dict

from pydantic import BaseModel, Field


class HoroscopeSummary(BaseModel):
  date: datetime = Field(default_factory=datetime.utcnow)
  sunSign: str
  guidance: str
  mood: Optional[str] = None
  luckyNumber: Optional[str] = None
  luckyColor: Optional[str] = None
  snapshot: Optional[Dict[str, Any]] = None


class ProviderMetadata(BaseModel):
  provider: str = "freeastrologyapi"
  generatedAt: datetime = Field(default_factory=datetime.utcnow)
  timezone: Optional[str] = None
  raw: Optional[Any] = None


class DailyHoroscopeResult(BaseModel):
  source: str = "freeastrologyapi"
  metadata: ProviderMetadata
  horoscope: HoroscopeSummary


class PanchangDetails(BaseModel):
  date: datetime
  tithi: str
  nakshatra: str
  yoga: str
  karana: str
  sunrise: str
  sunset: str


class PanchangResult(BaseModel):
  source: str = "freeastrologyapi"
  metadata: ProviderMetadata
  panchang: PanchangDetails


class ErrorResponse(BaseModel):
  error: str
  message: str
  details: Optional[Any] = None
