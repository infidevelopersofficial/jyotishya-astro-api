"""
Transit Predictions Calculator

Calculates the effects of current planetary transits on a natal birth chart.
Analyzes aspects between transiting planets and natal planet positions.
"""

from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

# Aspect definitions with orbs and effects
ASPECTS = {
    "conjunction": {"angle": 0, "orb": 8, "nature": "intense"},
    "opposition": {"angle": 180, "orb": 8, "nature": "challenging"},
    "trine": {"angle": 120, "orb": 6, "nature": "harmonious"},
    "square": {"angle": 90, "orb": 6, "nature": "challenging"},
    "sextile": {"angle": 60, "orb": 4, "nature": "harmonious"},
}

# Planet significations for interpretation
PLANET_SIGNIFICATIONS = {
    "Sun": ["self", "vitality", "authority", "career", "father"],
    "Moon": ["mind", "emotions", "mother", "public", "comfort"],
    "Mars": ["energy", "action", "courage", "conflict", "siblings"],
    "Mercury": ["communication", "intellect", "business", "education"],
    "Jupiter": ["wisdom", "luck", "expansion", "spirituality", "guru"],
    "Venus": ["love", "beauty", "wealth", "arts", "relationships"],
    "Saturn": ["discipline", "karma", "delays", "structure", "lessons"],
    "Rahu": ["desires", "obsession", "unconventional", "foreign"],
    "Ketu": ["spirituality", "detachment", "past karma", "liberation"],
}

# Transit effects based on nature
TRANSIT_EFFECTS = {
    "harmonious": {
        "Sun": "Positive energy boost for self-expression and authority",
        "Moon": "Emotional harmony and mental peace",
        "Mars": "Constructive action and healthy competition",
        "Mercury": "Clear communication and good decisions",
        "Jupiter": "Growth opportunities and good fortune",
        "Venus": "Love, beauty, and financial gains",
        "Saturn": "Productive discipline and lasting achievements",
        "Rahu": "Unconventional opportunities that work out well",
        "Ketu": "Spiritual insights and letting go gracefully",
    },
    "challenging": {
        "Sun": "Ego conflicts and need to prove yourself",
        "Moon": "Emotional turbulence and mental stress",
        "Mars": "Impulsive actions and potential conflicts",
        "Mercury": "Miscommunication and hasty decisions",
        "Jupiter": "Overconfidence and missed opportunities",
        "Venus": "Relationship tensions and overspending",
        "Saturn": "Obstacles, delays, and hard lessons",
        "Rahu": "Confusion and unhealthy desires",
        "Ketu": "Detachment anxiety and loss of direction",
    },
    "intense": {
        "Sun": "Powerful transformation of self-identity",
        "Moon": "Intensified emotions and new beginnings",
        "Mars": "Surge of energy for major initiatives",
        "Mercury": "Important communications and new ideas",
        "Jupiter": "Major expansion and life-changing luck",
        "Venus": "Significant relationships and financial changes",
        "Saturn": "Major karmic events and restructuring",
        "Rahu": "Obsessive focus on new desires",
        "Ketu": "Deep spiritual awakening or release",
    },
}

# Transiting planets to consider
TRANSIT_PLANETS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]

# Slow planets (their transits are more significant)
SLOW_PLANETS = ["Jupiter", "Saturn", "Rahu", "Ketu"]


def calculate_aspect(transit_lon: float, natal_lon: float) -> Dict[str, Any]:
    """Check if there's an aspect between transit and natal position."""
    diff = abs(transit_lon - natal_lon)
    if diff > 180:
        diff = 360 - diff
    
    for aspect_name, aspect_data in ASPECTS.items():
        angle = aspect_data["angle"]
        orb = aspect_data["orb"]
        
        if abs(diff - angle) <= orb:
            exactness = 1 - (abs(diff - angle) / orb)
            return {
                "aspect": aspect_name,
                "angle": angle,
                "actual_angle": round(diff, 2),
                "orb": round(abs(diff - angle), 2),
                "exactness": round(exactness, 2),
                "nature": aspect_data["nature"],
            }
    
    return None


def get_current_transits(timezone_hours: float = 5.5) -> Dict[str, float]:
    """
    Get current planetary positions for transit calculation.
    Uses the planetary module for real-time positions.
    """
    try:
        from .planetary import (
            _ensure_ephemeris,
            calculate_lahiri_ayanamsha,
        )
        from .houses import datetime_to_julian_date
        
        _ensure_ephemeris()
        
        from . import planetary
        ts = planetary._ts
        eph = planetary._eph
        
        # Get current time
        now = datetime.now(timezone.utc)
        t = ts.utc(now)
        
        earth = eph['earth']
        
        # Calculate ayanamsha
        jd = datetime_to_julian_date(now)
        ayanamsha = calculate_lahiri_ayanamsha(jd)
        
        transits = {}
        
        # True planets
        planet_keys = {
            "Sun": "sun",
            "Moon": "moon", 
            "Mars": "mars",
            "Mercury": "mercury",
            "Jupiter": "jupiter barycenter",
            "Venus": "venus",
            "Saturn": "saturn barycenter",
        }
        
        for planet_name, eph_key in planet_keys.items():
            planet = eph[eph_key]
            astrometric = earth.at(t).observe(planet)
            ecliptic = astrometric.apparent().ecliptic_latlon()
            tropical_lon = ecliptic[1].degrees
            sidereal_lon = (tropical_lon - ayanamsha) % 360
            transits[planet_name] = round(sidereal_lon, 4)
        
        # Calculate mean Rahu (North Node)
        # Rahu/Ketu move retrograde, roughly 19.3° per year
        # Using a reference point and calculating
        # Reference: Rahu was at ~0° Aries on Jan 1, 2000
        days_since_2000 = (now - datetime(2000, 1, 1, tzinfo=timezone.utc)).days
        rahu_movement = (days_since_2000 / 365.25) * 19.3
        rahu_lon = (0 - rahu_movement) % 360  # Retrograde
        ketu_lon = (rahu_lon + 180) % 360
        
        transits["Rahu"] = round(rahu_lon, 4)
        transits["Ketu"] = round(ketu_lon, 4)
        
        return transits
        
    except Exception as e:
        logger.error(f"Error getting current transits: {e}", exc_info=True)
        raise


def calculate_transit_effects(
    natal_planets: Dict[str, float],
    transit_time: datetime = None
) -> Dict[str, Any]:
    """
    Calculate transit effects on natal chart.
    
    Args:
        natal_planets: Dict of planet name -> sidereal longitude
        transit_time: Time for transit calculation (default: now)
    
    Returns:
        Transit analysis with aspects and interpretations
    """
    try:
        # Get current transits
        current_transits = get_current_transits()
        
        # Analyze each transit planet against each natal planet
        active_transits = []
        
        for transit_planet, transit_lon in current_transits.items():
            for natal_planet, natal_lon in natal_planets.items():
                aspect_data = calculate_aspect(transit_lon, natal_lon)
                
                if aspect_data:
                    # Get interpretation
                    nature = aspect_data["nature"]
                    effect = TRANSIT_EFFECTS.get(nature, {}).get(transit_planet, "Significant transit")
                    
                    # Determine significance
                    is_slow = transit_planet in SLOW_PLANETS
                    significance = "major" if is_slow else "minor"
                    if aspect_data["exactness"] > 0.8:
                        significance = "critical" if is_slow else "notable"
                    
                    active_transits.append({
                        "transit_planet": transit_planet,
                        "transit_longitude": transit_lon,
                        "natal_planet": natal_planet,
                        "natal_longitude": natal_lon,
                        "aspect": aspect_data["aspect"],
                        "nature": nature,
                        "exactness": aspect_data["exactness"],
                        "orb": aspect_data["orb"],
                        "effect": effect,
                        "significance": significance,
                        "significations": PLANET_SIGNIFICATIONS.get(transit_planet, []),
                    })
        
        # Sort by significance and exactness
        priority_order = {"critical": 0, "major": 1, "notable": 2, "minor": 3}
        active_transits.sort(key=lambda x: (priority_order.get(x["significance"], 4), -x["exactness"]))
        
        # Generate summary
        major_transits = [t for t in active_transits if t["significance"] in ["critical", "major"]]
        challenging = [t for t in major_transits if t["nature"] == "challenging"]
        harmonious = [t for t in major_transits if t["nature"] == "harmonious"]
        
        if len(challenging) > len(harmonious):
            overall_tone = "challenging"
            summary = "Current transits indicate a period requiring patience and careful action."
        elif len(harmonious) > len(challenging):
            overall_tone = "favorable"
            summary = "Current transits support positive developments and opportunities."
        else:
            overall_tone = "mixed"
            summary = "Current transits bring a mix of opportunities and challenges."
        
        return {
            "transit_time": datetime.now(timezone.utc).isoformat(),
            "current_positions": current_transits,
            "active_transits": active_transits,
            "summary": {
                "total_aspects": len(active_transits),
                "major_transits": len(major_transits),
                "challenging_count": len(challenging),
                "harmonious_count": len(harmonious),
                "overall_tone": overall_tone,
                "interpretation": summary,
            },
            "backend": "internal",
        }
        
    except Exception as e:
        logger.error(f"Error calculating transit effects: {e}", exc_info=True)
        raise
