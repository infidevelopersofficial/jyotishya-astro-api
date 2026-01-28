"""
Daily Horoscope Generator

Calculates planetary transits and generates horoscope guidance
based on current planetary positions and their aspects to natal signs.
"""

from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from enum import Enum
import logging

logger = logging.getLogger(__name__)


# Zodiac signs in order
ZODIAC_SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer",
    "Leo", "Virgo", "Libra", "Scorpio",
    "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

# Sign to index mapping
SIGN_INDEX = {sign.lower(): i for i, sign in enumerate(ZODIAC_SIGNS)}


class AspectType(str, Enum):
    """Planetary aspects in Vedic astrology"""
    CONJUNCTION = "conjunction"  # Same sign (strong)
    OPPOSITION = "opposition"    # 7th from (challenging)
    TRINE = "trine"              # 5th/9th from (harmonious)
    SQUARE = "square"            # 4th/10th from (tension)
    SEXTILE = "sextile"          # 3rd/11th from (supportive)
    NEUTRAL = "neutral"          # No major aspect


# Aspect definitions (house positions that form aspects)
ASPECTS = {
    AspectType.CONJUNCTION: [0],
    AspectType.OPPOSITION: [6],
    AspectType.TRINE: [4, 8],
    AspectType.SQUARE: [3, 9],
    AspectType.SEXTILE: [2, 10],
}


def calculate_daily_transits(
    date: datetime,
    latitude: float = 28.6139,
    longitude: float = 77.209,
) -> List[Dict[str, Any]]:
    """
    Calculate planetary positions for a given date.
    Uses the existing planetary calculation engine.
    
    Args:
        date: Date for transit calculation (UTC)
        latitude: Default latitude for calculations
        longitude: Default longitude for calculations
        
    Returns:
        List of planet dictionaries with positions
    """
    try:
        from .planetary import calculate_planet_positions, calculate_rahu_ketu
        
        # Use noon on the given date for transits
        transit_dt = datetime(
            date.year, date.month, date.day,
            12, 0, 0, tzinfo=timezone.utc
        )
        
        planets = calculate_planet_positions(
            transit_dt, latitude, longitude, "lahiri"
        )
        
        # Add Rahu/Ketu
        moon = next((p for p in planets if p['name'] == 'Moon'), None)
        if moon:
            rahu, ketu = calculate_rahu_ketu(moon)
            planets.extend([rahu, ketu])
        
        return planets
        
    except Exception as e:
        logger.error(f"Error calculating transits: {e}", exc_info=True)
        raise


def get_aspect_to_sign(transit_sign_idx: int, natal_sign_idx: int) -> AspectType:
    """
    Determine the aspect between a transiting planet's sign and natal sign.
    
    Args:
        transit_sign_idx: Index of the sign the planet is transiting
        natal_sign_idx: Index of the natal sign being aspected
        
    Returns:
        AspectType enum value
    """
    # Calculate the distance from natal to transit
    distance = (transit_sign_idx - natal_sign_idx) % 12
    
    for aspect_type, positions in ASPECTS.items():
        if distance in positions:
            return aspect_type
    
    return AspectType.NEUTRAL


def generate_daily_horoscope(
    sign: str,
    date: datetime,
    transits: Optional[List[Dict]] = None,
) -> Dict[str, Any]:
    """
    Generate daily horoscope for a zodiac sign.
    
    Args:
        sign: Zodiac sign (e.g., "aries", "taurus")
        date: Date for horoscope
        transits: Pre-calculated transits (optional, will calculate if not provided)
        
    Returns:
        Horoscope dictionary with transits, guidance, and ratings
    """
    sign_lower = sign.lower()
    if sign_lower not in SIGN_INDEX:
        raise ValueError(f"Invalid sign: {sign}")
    
    natal_sign_idx = SIGN_INDEX[sign_lower]
    sign_name = ZODIAC_SIGNS[natal_sign_idx]
    
    # Calculate transits if not provided
    if transits is None:
        transits = calculate_daily_transits(date)
    
    # Analyze transits relative to this sign
    transit_aspects = {}
    for planet in transits:
        planet_sign = planet.get("sign", "").lower()
        if planet_sign in SIGN_INDEX:
            planet_sign_idx = SIGN_INDEX[planet_sign]
            aspect = get_aspect_to_sign(planet_sign_idx, natal_sign_idx)
            
            # Convert numpy types to native Python types
            norm_degree = planet.get("normDegree", 0)
            is_retro = planet.get("isRetro", False)
            
            # Handle numpy types
            if hasattr(norm_degree, 'item'):
                norm_degree = norm_degree.item()
            if hasattr(is_retro, 'item'):
                is_retro = is_retro.item()
            
            transit_aspects[planet["name"]] = {
                "sign": planet.get("sign"),
                "degree": round(float(norm_degree), 2),
                "aspect": aspect.value,
                "is_retro": bool(is_retro),
            }
    
    # Generate guidance based on transits
    guidance = generate_guidance(transit_aspects, sign_name)
    
    # Calculate ratings based on aspects
    ratings = calculate_ratings(transit_aspects)
    
    return {
        "sign": sign_name,
        "date": date.strftime("%Y-%m-%d"),
        "backend": "internal",
        "transits": transit_aspects,
        "guidance": guidance,
        "ratings": ratings,
    }


def generate_guidance(transits: Dict, sign: str) -> Dict[str, str]:
    """
    Generate horoscope guidance text based on transits.
    Uses rule-based templates for MVP.
    
    Args:
        transits: Dictionary of planet transits with aspects
        sign: The zodiac sign name
        
    Returns:
        Dictionary with guidance for different life areas
    """
    from .templates import (
        get_overall_guidance,
        get_career_guidance,
        get_relationship_guidance,
        get_health_guidance,
    )
    
    return {
        "overall": get_overall_guidance(transits, sign),
        "career": get_career_guidance(transits, sign),
        "relationships": get_relationship_guidance(transits, sign),
        "health": get_health_guidance(transits, sign),
    }


def calculate_ratings(transits: Dict) -> Dict[str, int]:
    """
    Calculate 1-5 star ratings for different life areas.
    
    Rating logic:
    - Trines add points
    - Squares subtract points
    - Retrograde planets reduce impact
    """
    # Base scores
    scores = {"overall": 3, "career": 3, "love": 3, "health": 3}
    
    # Key planets for each area
    career_planets = ["Sun", "Saturn", "Jupiter", "Mercury"]
    love_planets = ["Venus", "Moon", "Mars"]
    health_planets = ["Mars", "Sun", "Saturn"]
    
    for planet_name, transit in transits.items():
        aspect = transit.get("aspect", "neutral")
        is_retro = transit.get("is_retro", False)
        
        # Aspect point modifiers
        if aspect == "trine":
            points = 1
        elif aspect == "sextile":
            points = 0.5
        elif aspect == "square":
            points = -0.5
        elif aspect == "opposition":
            points = -1
        elif aspect == "conjunction":
            # Conjunctions can be positive or negative depending on planet
            points = 0.5 if planet_name in ["Venus", "Jupiter"] else -0.3
        else:
            points = 0
        
        # Retrograde reduces impact
        if is_retro:
            points *= 0.5
        
        # Apply to relevant areas
        scores["overall"] += points * 0.5
        
        if planet_name in career_planets:
            scores["career"] += points
        if planet_name in love_planets:
            scores["love"] += points
        if planet_name in health_planets:
            scores["health"] += points
    
    # Clamp and round to 1-5
    return {
        area: max(1, min(5, round(score)))
        for area, score in scores.items()
    }


def generate_batch_horoscopes(
    date: datetime,
) -> Dict[str, Dict[str, Any]]:
    """
    Generate horoscopes for all 12 zodiac signs.
    Efficient: calculates transits once and reuses.
    
    Args:
        date: Date for horoscopes
        
    Returns:
        Dictionary with all 12 sign horoscopes
    """
    # Calculate transits once
    transits = calculate_daily_transits(date)
    
    result = {}
    for sign in ZODIAC_SIGNS:
        result[sign.lower()] = generate_daily_horoscope(
            sign=sign,
            date=date,
            transits=transits,
        )
    
    return result
