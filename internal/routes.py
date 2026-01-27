"""
FastAPI Routes for Internal Astrology Engine

Implements the same API contract as FreeAstrologyAPI to allow
drop-in replacement without frontend changes.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from datetime import datetime
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


@router.post("/horoscope-chart-svg-code")
async def get_chart_svg(request: AstrologyRequest):
    """
    Generate SVG chart visualization

    Matches FreeAstrologyAPI endpoint: POST /horoscope-chart-svg-code

    For MVP, returns a placeholder response. Full SVG generation
    can be implemented later or handled client-side.
    """
    try:
        # Calculate basic chart data
        birth_chart = await get_birth_chart(request)

        # TODO: Generate actual SVG visualization
        # For now, return placeholder
        svg_placeholder = f"""
        <svg width="400" height="400" xmlns="http://www.w3.org/2000/svg">
            <text x="200" y="200" text-anchor="middle">
                Chart visualization coming soon
            </text>
            <text x="200" y="230" text-anchor="middle">
                Ascendant: {birth_chart.ascendant:.2f}°
            </text>
        </svg>
        """

        return {
            "statusCode": 200,
            "output": svg_placeholder.strip()
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


# Additional endpoints can be added here to match FreeAstrologyAPI:
# - POST /panchang - Calculate Panchang
# - POST /match-making - Compatibility
# - POST /vimsottari-maha-dasa - Dasa periods
# - POST /planets-d9, /planets-d10, etc. - Divisional charts

# For MVP, we'll implement these as needed
