"""
FastAPI Routes for Internal Astrology Engine

Implements the same API contract as FreeAstrologyAPI to allow
drop-in replacement without frontend changes.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
from typing import Optional, List, Dict
import logging

from .planetary import (
    calculate_planet_positions,
    calculate_lahiri_ayanamsha,
    calculate_rahu_ketu
)
from .houses import (
    calculate_ascendant,
    calculate_midheaven,
    calculate_houses_whole_sign,
    assign_planets_to_houses,
    datetime_to_julian_date
)

logger = logging.getLogger(__name__)

router = APIRouter()


# Request Models (matching FreeAstrologyAPI)
class AstrologyRequest(BaseModel):
    """Birth details request matching FreeAstrologyAPI format"""
    year: int = Field(..., ge=1800, le=2200)
    month: int = Field(..., ge=1, le=12)
    date: int = Field(..., ge=1, le=31)
    hours: int = Field(..., ge=0, le=23)
    minutes: int = Field(..., ge=0, le=59)
    seconds: int = Field(0, ge=0, le=59)
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    timezone: float = Field(..., ge=-12, le=14)
    observation_point: str = Field("topocentric", pattern="^(topocentric|geocentric)$")
    ayanamsha: str = Field("lahiri", pattern="^(lahiri|raman|krishnamurti|thirukanitham)$")


# Response Models
class PlanetPosition(BaseModel):
    name: str
    fullDegree: float
    normDegree: float
    speed: float
    isRetro: bool
    sign: str
    signLord: str
    nakshatra: str
    nakshatraLord: str
    house: int


class HouseInfo(BaseModel):
    house: int
    sign: str
    degree: float


class BirthChartResponse(BaseModel):
    input: AstrologyRequest
    ascendant: float
    planets: List[PlanetPosition]
    houses: List[HouseInfo]


@router.post("/planets", response_model=BirthChartResponse)
async def get_birth_chart(request: AstrologyRequest):
    """
    Calculate birth chart with planetary positions

    Matches FreeAstrologyAPI endpoint: POST /planets
    """
    try:
        logger.info(f"Calculating birth chart for {request.year}-{request.month}-{request.date}")

        # Convert to UTC datetime
        # Subtract timezone offset to get UTC
        local_dt = datetime(
            request.year,
            request.month,
            request.date,
            request.hours,
            request.minutes,
            request.seconds
        )

        # Convert local time to UTC by subtracting timezone offset
        from datetime import timedelta
        utc_dt = local_dt - timedelta(hours=request.timezone)

        # Calculate ayanamsha
        jd = datetime_to_julian_date(utc_dt)
        ayanamsha_value = calculate_lahiri_ayanamsha(jd)

        # Calculate planetary positions
        planets = calculate_planet_positions(
            utc_dt,
            request.latitude,
            request.longitude,
            request.ayanamsha
        )

        # Calculate ascendant
        ascendant = calculate_ascendant(
            utc_dt,
            request.latitude,
            request.longitude,
            ayanamsha_value
        )

        # Calculate houses (use Whole Sign for simplicity in MVP)
        houses = calculate_houses_whole_sign(ascendant)

        # Assign planets to houses
        planets = assign_planets_to_houses(planets, houses, 'whole_sign')

        # Add Rahu and Ketu (shadow planets)
        moon = next((p for p in planets if p['name'] == 'Moon'), None)
        if moon:
            rahu, ketu = calculate_rahu_ketu(moon)
            # Assign houses to Rahu/Ketu
            rahu_ketu_list = [rahu, ketu]
            rahu_ketu_list = assign_planets_to_houses(rahu_ketu_list, houses, 'whole_sign')
            planets.extend(rahu_ketu_list)

        logger.info(f"Birth chart calculated successfully. Ascendant: {ascendant:.2f}°")

        return BirthChartResponse(
            input=request,
            ascendant=ascendant,
            planets=[PlanetPosition(**p) for p in planets],
            houses=[HouseInfo(**h) for h in houses]
        )

    except Exception as e:
        logger.error(f"Error calculating birth chart: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to calculate birth chart: {str(e)}"
        )


class ChartSvgRequest(AstrologyRequest):
    """Extended request with chart styling options"""
    chart_style: str = Field("north_indian", pattern="^(north_indian|south_indian)$")
    theme: str = Field("light", pattern="^(light|dark)$")
    size: str = Field("medium", pattern="^(small|medium|large)$")


@router.post("/horoscope-chart-svg-code")
async def get_chart_svg(request: ChartSvgRequest):
    """
    Generate SVG chart visualization

    Matches FreeAstrologyAPI endpoint: POST /horoscope-chart-svg-code
    
    Supports:
    - chart_style: north_indian (diamond) | south_indian (square)
    - theme: light | dark
    - size: small (300px) | medium (400px) | large (600px)
    """
    try:
        from .chart_svg import generate_chart_svg, ChartStyle, ChartTheme, ChartSize
        
        # Calculate birth chart data first
        birth_chart = await get_birth_chart(request)
        
        # Convert string params to enums
        style = ChartStyle.NORTH_INDIAN if request.chart_style == "north_indian" else ChartStyle.SOUTH_INDIAN
        theme = ChartTheme.LIGHT if request.theme == "light" else ChartTheme.DARK
        size_map = {"small": ChartSize.SMALL, "medium": ChartSize.MEDIUM, "large": ChartSize.LARGE}
        size = size_map.get(request.size, ChartSize.MEDIUM)
        
        # Convert planet models back to dicts for SVG generator
        planets = [p.model_dump() for p in birth_chart.planets]
        houses = [h.model_dump() for h in birth_chart.houses]
        
        # Generate SVG
        svg_code = generate_chart_svg(
            planets=planets,
            houses=houses,
            ascendant=birth_chart.ascendant,
            style=style,
            theme=theme,
            size=size,
        )
        
        logger.info(f"Generated {request.chart_style} chart SVG ({request.size}, {request.theme})")
        
        return {
            "statusCode": 200,
            "output": svg_code,
            "chart_style": request.chart_style,
            "theme": request.theme,
            "size": request.size
        }

    except Exception as e:
        logger.error(f"Error generating chart SVG: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate chart SVG: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "source": "internal_astrology_engine",
        "version": "1.0.0"
    }


# ==============================================================================
# DAILY HOROSCOPE ENDPOINTS
# ==============================================================================

class DailyHoroscopeRequest(BaseModel):
    """Request for single sign daily horoscope"""
    sign: str = Field(..., pattern="^(aries|taurus|gemini|cancer|leo|virgo|libra|scorpio|sagittarius|capricorn|aquarius|pisces)$")
    date: Optional[str] = Field(None, pattern=r"^\d{4}-\d{2}-\d{2}$")  # YYYY-MM-DD format
    timezone: str = Field("Asia/Kolkata")


class BatchHoroscopeRequest(BaseModel):
    """Request for all 12 signs daily horoscope"""
    date: Optional[str] = Field(None, pattern=r"^\d{4}-\d{2}-\d{2}$")
    timezone: str = Field("Asia/Kolkata")


@router.post("/horoscope/daily")
async def get_daily_horoscope(request: DailyHoroscopeRequest):
    """
    Get daily horoscope for a single zodiac sign.
    
    Args:
        sign: Zodiac sign (lowercase)
        date: Date in YYYY-MM-DD format (default: today)
        timezone: Timezone name (default: Asia/Kolkata)
    
    Returns:
        Horoscope with transits, guidance, and ratings
    """
    try:
        from .horoscope import generate_daily_horoscope
        from datetime import datetime, timezone as tz
        from zoneinfo import ZoneInfo
        
        # Parse date
        if request.date:
            try:
                target_date = datetime.strptime(request.date, "%Y-%m-%d")
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
        else:
            # Use today in the requested timezone
            try:
                zone = ZoneInfo(request.timezone)
                target_date = datetime.now(zone)
            except Exception:
                target_date = datetime.now(tz.utc)
        
        # Generate horoscope
        horoscope = generate_daily_horoscope(
            sign=request.sign,
            date=target_date,
        )
        
        logger.info(f"Generated daily horoscope for {request.sign}")
        
        return horoscope
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error generating daily horoscope: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate daily horoscope: {str(e)}"
        )


@router.post("/horoscope/daily/batch")
async def get_batch_horoscopes(request: BatchHoroscopeRequest):
    """
    Get daily horoscopes for all 12 zodiac signs.
    
    Efficient: calculates planetary transits once and generates
    all 12 horoscopes from the same data.
    
    Args:
        date: Date in YYYY-MM-DD format (default: today)
        timezone: Timezone name (default: Asia/Kolkata)
    
    Returns:
        Dictionary with all 12 sign horoscopes
    """
    try:
        from .horoscope import generate_batch_horoscopes
        from datetime import datetime, timezone as tz
        from zoneinfo import ZoneInfo
        
        # Parse date
        if request.date:
            try:
                target_date = datetime.strptime(request.date, "%Y-%m-%d")
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
        else:
            try:
                zone = ZoneInfo(request.timezone)
                target_date = datetime.now(zone)
            except Exception:
                target_date = datetime.now(tz.utc)
        
        # Generate all horoscopes
        horoscopes = generate_batch_horoscopes(date=target_date)
        
        logger.info(f"Generated batch horoscopes for {target_date.strftime('%Y-%m-%d')}")
        
        return {
            "date": target_date.strftime("%Y-%m-%d"),
            "backend": "internal",
            "horoscopes": horoscopes,
        }
        
    except Exception as e:
        logger.error(f"Error generating batch horoscopes: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate batch horoscopes: {str(e)}"
        )


# ==============================================================================
# PANCHANG ENDPOINTS
# ==============================================================================

class PanchangRequest(BaseModel):
    """Request for Panchang calculation"""
    date: Optional[str] = Field(None, pattern=r"^\d{4}-\d{2}-\d{2}$")  # YYYY-MM-DD
    latitude: float = Field(28.6139, ge=-90, le=90)
    longitude: float = Field(77.209, ge=-180, le=180)
    timezone: float = Field(5.5, ge=-12, le=14)
    ayanamsha: str = Field("lahiri", pattern="^(lahiri|raman|krishnamurti)$")


@router.get("/panchang/today")
async def get_today_panchang(
    latitude: float = 28.6139,
    longitude: float = 77.209,
    timezone: float = 5.5,
    locale: str = "en"
):
    """
    Get Panchang for today.
    
    Returns Tithi, Nakshatra, Yoga, Karana, Sunrise, Sunset, Vara, Ritu.
    """
    try:
        from .panchang import calculate_panchang
        from datetime import datetime, timezone as tz
        from zoneinfo import ZoneInfo
        
        # Get today in the specified timezone
        try:
            tz_offset = timedelta(hours=timezone)
            today = datetime.now(tz.utc) + tz_offset
        except Exception:
            today = datetime.now(tz.utc)
        
        panchang = calculate_panchang(
            date=today,
            latitude=latitude,
            longitude=longitude,
            timezone_hours=timezone,
        )
        
        logger.info(f"Generated Panchang for {panchang['date']}")
        
        return panchang
        
    except Exception as e:
        logger.error(f"Error calculating today's panchang: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to calculate Panchang: {str(e)}"
        )


@router.post("/panchang")
async def get_panchang(request: PanchangRequest):
    """
    Calculate Panchang for a specific date.
    
    Args:
        date: Date in YYYY-MM-DD format (default: today)
        latitude: Location latitude (default: Delhi)
        longitude: Location longitude (default: Delhi)
        timezone: Timezone offset in hours (default: IST +5.5)
        ayanamsha: Ayanamsha system (default: lahiri)
    
    Returns:
        Complete Panchang with Tithi, Nakshatra, Yoga, Karana, etc.
    """
    try:
        from .panchang import calculate_panchang
        from datetime import datetime, timezone as tz
        
        # Parse date or use today
        if request.date:
            try:
                target_date = datetime.strptime(request.date, "%Y-%m-%d")
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
        else:
            tz_offset = timedelta(hours=request.timezone)
            target_date = datetime.now(tz.utc) + tz_offset
        
        panchang = calculate_panchang(
            date=target_date,
            latitude=request.latitude,
            longitude=request.longitude,
            timezone_hours=request.timezone,
            ayanamsha=request.ayanamsha,
        )
        
        logger.info(f"Generated Panchang for {panchang['date']}")
        
        return panchang
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating panchang: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to calculate Panchang: {str(e)}"
        )


# ==============================================================================
# VIMSOTTARI DASHA ENDPOINTS
# ==============================================================================

class DashaRequest(BaseModel):
    """Request for Vimsottari Dasha calculation"""
    year: int = Field(..., ge=1800, le=2200)
    month: int = Field(..., ge=1, le=12)
    date: int = Field(..., ge=1, le=31)
    hours: int = Field(..., ge=0, le=23)
    minutes: int = Field(..., ge=0, le=59)
    seconds: int = Field(0, ge=0, le=59)
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    timezone: float = Field(..., ge=-12, le=14)
    ayanamsha: str = Field("lahiri", pattern="^(lahiri|raman|krishnamurti)$")
    years_to_calculate: int = Field(100, ge=10, le=150)


@router.post("/vimsottari-dasha")
async def calculate_dasha(request: DashaRequest):
    """
    Calculate Vimsottari Dasha periods from birth details.
    
    Returns:
        - birth_nakshatra: Moon's nakshatra at birth
        - current_mahadasha: Currently running major period
        - current_antardasha: Currently running sub-period
        - mahadashas: List of all Mahadasha periods with Antardashas
    """
    try:
        from .dasha import get_dasha_from_birth_chart
        
        result = get_dasha_from_birth_chart(
            year=request.year,
            month=request.month,
            day=request.date,
            hours=request.hours,
            minutes=request.minutes,
            seconds=request.seconds,
            latitude=request.latitude,
            longitude=request.longitude,
            timezone=request.timezone,
            ayanamsha=request.ayanamsha,
            years_to_calculate=request.years_to_calculate,
        )
        
        logger.info(f"Generated Vimsottari Dasha for {request.year}-{request.month}-{request.date}")
        
        return result
        
    except Exception as e:
        logger.error(f"Error calculating Vimsottari Dasha: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to calculate Vimsottari Dasha: {str(e)}"
        )


class DashaFromMoonRequest(BaseModel):
    """Request for Dasha from Moon longitude (already calculated)"""
    moon_longitude: float = Field(..., ge=0, lt=360, description="Moon's sidereal longitude")
    birth_date: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$", description="Birth date YYYY-MM-DD")
    years_to_calculate: int = Field(100, ge=10, le=150)


@router.post("/vimsottari-dasha/from-moon")
async def calculate_dasha_from_moon(request: DashaFromMoonRequest):
    """
    Calculate Vimsottari Dasha from pre-calculated Moon longitude.
    
    Useful when you already have the birth chart and just need Dasha periods.
    """
    try:
        from .dasha import calculate_vimsottari_dasha
        
        birth_dt = datetime.strptime(request.birth_date, "%Y-%m-%d")
        
        result = calculate_vimsottari_dasha(
            moon_longitude=request.moon_longitude,
            birth_date=birth_dt,
            years_to_calculate=request.years_to_calculate,
        )
        
        logger.info(f"Generated Vimsottari Dasha from Moon longitude {request.moon_longitude}")
        
        return result
        
    except Exception as e:
        logger.error(f"Error calculating Dasha from Moon: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to calculate Dasha: {str(e)}"
        )


# ==============================================================================
# KUNDLI MATCHING ENDPOINTS
# ==============================================================================

class MatchingFromMoonRequest(BaseModel):
    """Request for matching from Moon longitudes"""
    bride_moon_longitude: float = Field(..., ge=0, lt=360, description="Bride's sidereal Moon longitude")
    groom_moon_longitude: float = Field(..., ge=0, lt=360, description="Groom's sidereal Moon longitude")
    bride_name: str = Field("Bride", max_length=100)
    groom_name: str = Field("Groom", max_length=100)


@router.post("/match-making")
async def calculate_match_from_moon(request: MatchingFromMoonRequest):
    """
    Calculate Ashtakoot compatibility from Moon longitudes.
    
    Returns 8 compatibility factors (koots) with total score out of 36.
    """
    try:
        from .matching import calculate_compatibility
        
        result = calculate_compatibility(
            bride_moon_longitude=request.bride_moon_longitude,
            groom_moon_longitude=request.groom_moon_longitude,
            bride_name=request.bride_name,
            groom_name=request.groom_name,
        )
        
        logger.info(f"Generated match for {request.bride_name} & {request.groom_name}: {result['total_score']}/36")
        
        return result
        
    except Exception as e:
        logger.error(f"Error calculating match: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to calculate match: {str(e)}"
        )


class MatchingFromBirthRequest(BaseModel):
    """Request for matching from birth details"""
    bride: DashaRequest = Field(..., description="Bride's birth details")
    groom: DashaRequest = Field(..., description="Groom's birth details")
    bride_name: str = Field("Bride", max_length=100)
    groom_name: str = Field("Groom", max_length=100)


@router.post("/match-making/birth-details")
async def calculate_match_from_birth(request: MatchingFromBirthRequest):
    """
    Calculate Ashtakoot compatibility from full birth details.
    
    Calculates Moon positions for both, then runs compatibility check.
    """
    try:
        from .dasha import get_dasha_from_birth_chart
        from .matching import calculate_compatibility
        
        # Get Moon longitudes for both
        bride_dasha = get_dasha_from_birth_chart(
            year=request.bride.year,
            month=request.bride.month,
            day=request.bride.date,
            hours=request.bride.hours,
            minutes=request.bride.minutes,
            seconds=request.bride.seconds,
            latitude=request.bride.latitude,
            longitude=request.bride.longitude,
            timezone=request.bride.timezone,
            years_to_calculate=10,  # Just need Moon position
        )
        
        groom_dasha = get_dasha_from_birth_chart(
            year=request.groom.year,
            month=request.groom.month,
            day=request.groom.date,
            hours=request.groom.hours,
            minutes=request.groom.minutes,
            seconds=request.groom.seconds,
            latitude=request.groom.latitude,
            longitude=request.groom.longitude,
            timezone=request.groom.timezone,
            years_to_calculate=10,
        )
        
        bride_moon = bride_dasha["moon_longitude"]
        groom_moon = groom_dasha["moon_longitude"]
        
        result = calculate_compatibility(
            bride_moon_longitude=bride_moon,
            groom_moon_longitude=groom_moon,
            bride_name=request.bride_name,
            groom_name=request.groom_name,
        )
        
        # Add birth nakshatras from dasha calculation
        result["bride"]["birth_nakshatra_from_dasha"] = bride_dasha["birth_nakshatra"]
        result["groom"]["birth_nakshatra_from_dasha"] = groom_dasha["birth_nakshatra"]
        
        logger.info(f"Generated match from birth details: {result['total_score']}/36")
        
        return result
        
    except Exception as e:
        logger.error(f"Error calculating match from birth: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to calculate match: {str(e)}"
        )


# ==============================================================================
# TRANSIT PREDICTIONS ENDPOINTS
# ==============================================================================

class TransitRequest(BaseModel):
    """Request for transit predictions"""
    natal_planets: Dict[str, float] = Field(
        ..., 
        description="Dict of planet name to sidereal longitude (0-360)"
    )


@router.post("/transits")
async def get_transits(request: TransitRequest):
    """
    Calculate current transit effects on natal chart.
    
    Analyzes aspects between current planetary positions and natal planets.
    Returns active transits with interpretations and significance levels.
    """
    try:
        from .transits import calculate_transit_effects
        
        result = calculate_transit_effects(
            natal_planets=request.natal_planets
        )
        
        logger.info(f"Generated transit predictions: {result['summary']['total_aspects']} aspects found")
        
        return result
        
    except Exception as e:
        logger.error(f"Error calculating transits: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to calculate transits: {str(e)}"
        )


@router.get("/transits/current")
async def get_current_positions():
    """
    Get current planetary positions for transits.
    
    Returns real-time sidereal positions of all planets.
    """
    try:
        from .transits import get_current_transits
        
        positions = get_current_transits()
        
        return {
            "timestamp": datetime.now().isoformat(),
            "positions": positions,
            "ayanamsha": "lahiri",
            "backend": "internal",
        }
        
    except Exception as e:
        logger.error(f"Error getting current positions: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get positions: {str(e)}"
        )


class TransitFromBirthRequest(BaseModel):
    """Request for transit predictions from birth details"""
    year: int = Field(..., ge=1800, le=2200)
    month: int = Field(..., ge=1, le=12)
    date: int = Field(..., ge=1, le=31)
    hours: int = Field(..., ge=0, le=23)
    minutes: int = Field(..., ge=0, le=59)
    seconds: int = Field(0, ge=0, le=59)
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    timezone: float = Field(..., ge=-12, le=14)


@router.post("/transits/birth-chart")
async def get_transits_from_birth(request: TransitFromBirthRequest):
    """
    Calculate transit effects from birth details.
    
    First calculates natal chart, then analyzes current transits.
    """
    try:
        from .planetary import calculate_planet_positions
        from .transits import calculate_transit_effects
        from datetime import datetime, timedelta, timezone as tz
        
        # Construct datetime from request
        utc_offset = timedelta(hours=request.timezone)
        birth_tz = tz(utc_offset)
        birth_dt = datetime(
            year=request.year,
            month=request.month,
            day=request.date,
            hour=request.hours,
            minute=request.minutes,
            second=request.seconds,
            tzinfo=birth_tz
        )
        
        # Calculate natal chart
        natal_planets_list = calculate_planet_positions(
            dt=birth_dt,
            latitude=request.latitude,
            longitude=request.longitude,
        )
        
        # Extract natal planet longitudes
        natal_planets = {}
        for planet in natal_planets_list:
            name = planet.get("name", "")
            lon = planet.get("fullDegree", planet.get("full_degree", 0))
            if name and lon:
                natal_planets[name] = lon
        
        # Calculate transits
        result = calculate_transit_effects(natal_planets=natal_planets)
        
        # Add natal data to response
        result["natal_data"] = {
            "birth_date": f"{request.year}-{request.month:02d}-{request.date:02d}",
            "planets": natal_planets,
        }
        
        logger.info(f"Generated transit predictions from birth chart")
        
        return result
        
    except Exception as e:
        logger.error(f"Error calculating transits from birth: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to calculate transits: {str(e)}"
        )


# ==============================================================================
# YOGAS (PLANETARY COMBINATIONS) ENDPOINTS
# ==============================================================================

class YogasRequest(BaseModel):
    """Request for yoga detection"""
    planets: List[Dict[str, Any]] = Field(
        ..., description="List of planet data with name and fullDegree"
    )
    ascendant_longitude: float = Field(
        ..., ge=0, le=360, description="Ascendant longitude"
    )


@router.post("/yogas")
async def detect_yogas_endpoint(request: YogasRequest):
    """Detect yogas (planetary combinations) in a birth chart."""
    try:
        from .yogas import detect_yogas
        
        result = detect_yogas(
            planets_list=request.planets,
            ascendant_lon=request.ascendant_longitude
        )
        
        logger.info(f"Detected {result['summary']['total_yogas']} yogas")
        return result
        
    except Exception as e:
        logger.error(f"Error detecting yogas: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to detect yogas: {str(e)}"
        )


class YogasFromBirthRequest(BaseModel):
    """Request for yoga detection from birth details"""
    year: int = Field(..., ge=1800, le=2200)
    month: int = Field(..., ge=1, le=12)
    date: int = Field(..., ge=1, le=31)
    hours: int = Field(..., ge=0, le=23)
    minutes: int = Field(..., ge=0, le=59)
    seconds: int = Field(0, ge=0, le=59)
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    timezone: float = Field(..., ge=-12, le=14)


@router.post("/yogas/birth-chart")
async def detect_yogas_from_birth(request: YogasFromBirthRequest):
    """Detect yogas from birth details."""
    try:
        from .planetary import calculate_planet_positions, calculate_lahiri_ayanamsha, _ensure_ephemeris, _ts
        from .houses import calculate_ascendant
        from .yogas import detect_yogas
        from datetime import datetime, timedelta, timezone as tz
        
        # Construct datetime from request
        utc_offset = timedelta(hours=request.timezone)
        birth_tz = tz(utc_offset)
        birth_dt = datetime(
            year=request.year,
            month=request.month,
            day=request.date,
            hour=request.hours,
            minute=request.minutes,
            second=request.seconds,
            tzinfo=birth_tz
        )
        
        # Calculate planets
        planets_list = calculate_planet_positions(
            dt=birth_dt,
            latitude=request.latitude,
            longitude=request.longitude,
        )
        
        # Calculate ayanamsha
        _ensure_ephemeris()
        t = _ts.from_datetime(birth_dt)
        ayanamsha_value = calculate_lahiri_ayanamsha(t.tt)
        
        # Calculate ascendant (returns float)
        asc_lon = calculate_ascendant(
            dt=birth_dt,
            latitude=request.latitude,
            longitude=request.longitude,
            ayanamsha=ayanamsha_value
        )
        
        result = detect_yogas(
            planets_list=planets_list,
            ascendant_lon=asc_lon
        )
        
        result["birth_data"] = {
            "birth_date": f"{request.year}-{request.month:02d}-{request.date:02d}",
            "ascendant_longitude": asc_lon,
        }
        
        logger.info(f"Detected {result['summary']['total_yogas']} yogas from birth chart")
        return result
        
    except Exception as e:
        logger.error(f"Error detecting yogas from birth: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to detect yogas: {str(e)}"
        )


# ==============================================================================
# DIVISIONAL CHARTS ENDPOINTS
# ==============================================================================

class DivisionalRequest(BaseModel):
    """Request for divisional charts"""
    planets: List[Dict[str, Any]] = Field(
        ..., description="List of planet data with name and fullDegree"
    )
    ascendant_longitude: float = Field(
        ..., ge=0, le=360, description="Ascendant longitude"
    )


@router.post("/divisional-charts")
async def get_divisional_charts(request: DivisionalRequest):
    """Calculate all divisional charts (D1 through D12)."""
    try:
        from .divisional import calculate_divisional_charts
        
        result = calculate_divisional_charts(
            planets_list=request.planets,
            ascendant_lon=request.ascendant_longitude
        )
        
        logger.info(f"Calculated {len(result['available_charts'])} divisional charts")
        return result
        
    except Exception as e:
        logger.error(f"Error calculating divisional charts: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to calculate divisional charts: {str(e)}"
        )


class DivisionalFromBirthRequest(BaseModel):
    """Request for divisional charts from birth details"""
    year: int = Field(..., ge=1800, le=2200)
    month: int = Field(..., ge=1, le=12)
    date: int = Field(..., ge=1, le=31)
    hours: int = Field(..., ge=0, le=23)
    minutes: int = Field(..., ge=0, le=59)
    seconds: int = Field(0, ge=0, le=59)
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    timezone: float = Field(..., ge=-12, le=14)
    chart: Optional[str] = Field(None, description="Specific chart: D1, D9, D10, etc.")


@router.post("/divisional-charts/birth-chart")
async def get_divisional_from_birth(request: DivisionalFromBirthRequest):
    """Calculate divisional charts from birth details."""
    try:
        from .planetary import calculate_planet_positions, calculate_lahiri_ayanamsha, _ensure_ephemeris, _ts
        from .houses import calculate_ascendant
        from .divisional import calculate_divisional_charts, get_navamsa_chart, get_dasamsa_chart
        from datetime import datetime, timedelta, timezone as tz
        
        # Construct datetime from request
        utc_offset = timedelta(hours=request.timezone)
        birth_tz = tz(utc_offset)
        birth_dt = datetime(
            year=request.year,
            month=request.month,
            day=request.date,
            hour=request.hours,
            minute=request.minutes,
            second=request.seconds,
            tzinfo=birth_tz
        )
        
        # Calculate planets
        planets_list = calculate_planet_positions(
            dt=birth_dt,
            latitude=request.latitude,
            longitude=request.longitude,
        )
        
        # Calculate ayanamsha
        _ensure_ephemeris()
        t = _ts.from_datetime(birth_dt)
        ayanamsha_value = calculate_lahiri_ayanamsha(t.tt)
        
        # Calculate ascendant (returns float)
        asc_lon = calculate_ascendant(
            dt=birth_dt,
            latitude=request.latitude,
            longitude=request.longitude,
            ayanamsha=ayanamsha_value
        )
        
        # Return specific chart if requested
        if request.chart:
            if request.chart.upper() == "D9":
                result = get_navamsa_chart(planets_list, asc_lon)
            elif request.chart.upper() == "D10":
                result = get_dasamsa_chart(planets_list, asc_lon)
            else:
                all_charts = calculate_divisional_charts(planets_list, asc_lon)
                chart_key = request.chart.upper()
                if chart_key in all_charts["charts"]:
                    result = {
                        "chart": chart_key,
                        **all_charts["charts"][chart_key]
                    }
                else:
                    raise ValueError(f"Chart {chart_key} not available")
        else:
            result = calculate_divisional_charts(planets_list, asc_lon)
        
        result["birth_data"] = {
            "birth_date": f"{request.year}-{request.month:02d}-{request.date:02d}",
            "ascendant_longitude": asc_lon,
        }
        
        logger.info("Calculated divisional charts from birth")
        return result
        
    except Exception as e:
        logger.error(f"Error calculating divisional from birth: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to calculate divisional charts: {str(e)}"
        )


# Additional endpoints to implement:
# - POST /planetary-strength - Shadbala calculations
