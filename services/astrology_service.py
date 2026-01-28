"""
Astrology Service Layer with Hybrid Fallback

Production-ready service layer that:
1. Tries internal engine first (fast, unlimited, no API costs)
2. Falls back to external API if internal fails (graceful degradation)
3. Exposes which backend was used in every response
4. Handles errors gracefully with detailed logging
"""

import logging
from typing import Dict, Any, Optional, Tuple
from datetime import datetime
from enum import Enum

from freeastrology.config import get_settings, AstrologyBackend

logger = logging.getLogger(__name__)


class BackendUsed(str, Enum):
    """Which backend actually processed the request"""
    INTERNAL = "internal"
    EXTERNAL = "external"
    FALLBACK = "fallback"  # Internal failed, used external
    MOCK = "mock"


class AstrologyServiceError(Exception):
    """Raised when all backends fail"""
    def __init__(self, message: str, internal_error: Optional[str] = None, external_error: Optional[str] = None):
        super().__init__(message)
        self.internal_error = internal_error
        self.external_error = external_error


async def calculate_birth_chart(
    year: int,
    month: int,
    date: int,
    hours: int,
    minutes: int,
    seconds: int,
    latitude: float,
    longitude: float,
    timezone: float,
    observation_point: str = "topocentric",
    ayanamsha: str = "lahiri"
) -> Tuple[Dict[str, Any], BackendUsed]:
    """
    Calculate birth chart using the configured backend strategy.
    
    Returns:
        Tuple of (chart_data, backend_used)
        
    Raises:
        AstrologyServiceError: If all backends fail
    """
    settings = get_settings()
    backend = settings.astrology_backend
    
    internal_error = None
    external_error = None
    
    # Strategy: INTERNAL only
    if backend == AstrologyBackend.INTERNAL:
        result = await _try_internal(
            year, month, date, hours, minutes, seconds,
            latitude, longitude, timezone, observation_point, ayanamsha
        )
        if result is not None:
            return result, BackendUsed.INTERNAL
        raise AstrologyServiceError("Internal engine failed", internal_error="Calculation error")
    
    # Strategy: EXTERNAL only
    if backend == AstrologyBackend.FREEASTROLOGY:
        result = await _try_external(
            year, month, date, hours, minutes, seconds,
            latitude, longitude, timezone, ayanamsha
        )
        if result is not None:
            return result, BackendUsed.EXTERNAL
        raise AstrologyServiceError("External API failed", external_error="API error")
    
    # Strategy: HYBRID (internal first, fallback to external)
    if backend == AstrologyBackend.HYBRID:
        # Try internal first
        try:
            result = await _try_internal(
                year, month, date, hours, minutes, seconds,
                latitude, longitude, timezone, observation_point, ayanamsha
            )
            if result is not None:
                return result, BackendUsed.INTERNAL
        except Exception as e:
            internal_error = str(e)
            logger.warning(f"Internal engine failed, trying external: {e}")
        
        # Fallback to external
        try:
            result = await _try_external(
                year, month, date, hours, minutes, seconds,
                latitude, longitude, timezone, ayanamsha
            )
            if result is not None:
                logger.info("Successfully used external API as fallback")
                return result, BackendUsed.FALLBACK
        except Exception as e:
            external_error = str(e)
            logger.error(f"External API also failed: {e}")
        
        raise AstrologyServiceError(
            "All backends failed",
            internal_error=internal_error,
            external_error=external_error
        )
    
    # Strategy: MOCK
    return _get_mock_data(), BackendUsed.MOCK


async def _try_internal(
    year: int, month: int, date: int,
    hours: int, minutes: int, seconds: int,
    latitude: float, longitude: float, timezone: float,
    observation_point: str, ayanamsha: str
) -> Optional[Dict[str, Any]]:
    """Try calculating with internal Skyfield engine"""
    try:
        from internal.planetary import calculate_planet_positions, calculate_rahu_ketu
        from internal.houses import (
            calculate_ascendant,
            calculate_houses_whole_sign,
            assign_planets_to_houses,
            datetime_to_julian_date,
            calculate_lahiri_ayanamsha
        )
        from datetime import timedelta
        
        # Build datetime
        local_dt = datetime(year, month, date, hours, minutes, seconds)
        utc_dt = local_dt - timedelta(hours=timezone)
        
        # Calculate chart
        jd = datetime_to_julian_date(utc_dt)
        ayanamsha_value = calculate_lahiri_ayanamsha(jd)
        
        planets = calculate_planet_positions(utc_dt, latitude, longitude, ayanamsha)
        ascendant = calculate_ascendant(utc_dt, latitude, longitude, ayanamsha_value)
        houses = calculate_houses_whole_sign(ascendant)
        planets = assign_planets_to_houses(planets, houses, 'whole_sign')
        
        # Add Rahu/Ketu
        moon = next((p for p in planets if p['name'] == 'Moon'), None)
        if moon:
            rahu, ketu = calculate_rahu_ketu(moon)
            rahu_ketu = assign_planets_to_houses([rahu, ketu], houses, 'whole_sign')
            planets.extend(rahu_ketu)
        
        return {
            "ascendant": ascendant,
            "planets": planets,
            "houses": houses
        }
    except Exception as e:
        logger.error(f"Internal calculation error: {e}", exc_info=True)
        raise


async def _try_external(
    year: int, month: int, date: int,
    hours: int, minutes: int, seconds: int,
    latitude: float, longitude: float, timezone: float,
    ayanamsha: str
) -> Optional[Dict[str, Any]]:
    """Try calculating with external FreeAstrologyAPI"""
    try:
        from freeastrology.client import FreeAstrologyApiClient
        
        client = FreeAstrologyApiClient()
        
        # FreeAstrologyAPI expects specific payload format
        payload = {
            "year": year,
            "month": month,
            "date": date,
            "hours": hours,
            "minutes": minutes,
            "seconds": seconds,
            "latitude": latitude,
            "longitude": longitude,
            "timezone": timezone,
            "ayanamsa": ayanamsha
        }
        
        # Note: This is a simplified call - actual implementation may need adjustment
        result = await client._post("/planets", payload)
        return result
    except Exception as e:
        logger.error(f"External API error: {e}", exc_info=True)
        raise


def _get_mock_data() -> Dict[str, Any]:
    """Return mock data for testing"""
    return {
        "ascendant": 0.0,
        "planets": [],
        "houses": [],
        "_mock": True
    }


async def check_external_api_health() -> bool:
    """Check if external API is available"""
    try:
        import httpx
        settings = get_settings()
        
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{settings.free_api_base_url}/")
            return response.status_code < 500
    except Exception:
        return False
