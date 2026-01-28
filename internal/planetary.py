"""
Planetary Position Calculations

Uses Skyfield library with JPL DE421 ephemeris for accurate planetary positions.
Calculates sidereal (Vedic) positions with Lahiri ayanamsha.
"""

from datetime import datetime, timezone
from typing import List, Dict, Optional
from .signs import longitude_to_sign
from .nakshatras import longitude_to_nakshatra

# Lazy load Skyfield to avoid import errors if not installed
_eph = None
_ts = None
_earth = None
_planets_map = None


def _ensure_ephemeris():
    """Lazy load Skyfield ephemeris data"""
    global _eph, _ts, _earth, _planets_map

    if _eph is not None:
        return

    try:
        import os
        from skyfield.api import load, Loader

        # Get the directory containing this module (internal/)
        module_dir = os.path.dirname(os.path.abspath(__file__))
        # Project root is one level up from internal/
        project_root = os.path.dirname(module_dir)
        
        # Create a loader that looks in the project root for ephemeris files
        loader = Loader(project_root)
        
        # Load ephemeris from project root (where de421.bsp is)
        ephemeris_path = os.path.join(project_root, 'de421.bsp')
        
        if os.path.exists(ephemeris_path):
            _eph = loader('de421.bsp')
        else:
            # Fallback: try to download (not ideal for serverless)
            _eph = load('de421.bsp')
            
        _ts = load.timescale()
        _earth = _eph['earth']

        # Map Vedic planet names to Skyfield bodies
        _planets_map = {
            'Sun': _eph['sun'],
            'Moon': _eph['moon'],
            'Mars': _eph['mars'],
            'Mercury': _eph['mercury'],
            'Jupiter': _eph['jupiter barycenter'],
            'Venus': _eph['venus'],
            'Saturn': _eph['saturn barycenter'],
        }
    except ImportError:
        raise ImportError(
            "Skyfield not installed. Run: pip install skyfield"
        )


def calculate_lahiri_ayanamsha(jd: float) -> float:
    """
    Calculate Lahiri ayanamsha for a given Julian Date

    Uses the standard formula:
    Ayanamsha(t) = 23.85° + 50.26" × (t - 1950.0)

    where t is years since 1950.0

    Args:
        jd: Julian Date

    Returns:
        Ayanamsha value in degrees
    """
    # Julian date for Jan 1, 1950, 0h UT
    jd_1950 = 2433282.5

    # Years since 1950
    years_since_1950 = (jd - jd_1950) / 365.25

    # Lahiri ayanamsha formula
    # Base value at 1950 + annual precession
    ayanamsha = 23.85 + (50.26 / 3600.0) * years_since_1950

    return ayanamsha


def calculate_planet_speed(planet_body, time_obj, ts, interval_days: float = 1.0) -> float:
    """
    Calculate planet's speed in degrees per day

    Args:
        planet_body: Skyfield planet object
        time_obj: Skyfield time object (current time)
        ts: Skyfield timescale object
        interval_days: Days to look back for speed calculation

    Returns:
        Speed in degrees/day (negative if retrograde)
    """
    _ensure_ephemeris()

    # Current position
    pos_now = _earth.at(time_obj).observe(planet_body).apparent().ecliptic_latlon()[1].degrees

    # Position interval_days ago
    t_prev = ts.tt_jd(time_obj.tt - interval_days)
    pos_prev = _earth.at(t_prev).observe(planet_body).apparent().ecliptic_latlon()[1].degrees

    # Calculate speed, handling 360° wraparound
    speed = (pos_now - pos_prev) / interval_days

    # Handle discontinuity at 0°/360°
    if speed > 180:
        speed -= 360
    elif speed < -180:
        speed += 360

    return speed


def calculate_planet_positions(
    dt: datetime,
    latitude: float,
    longitude: float,
    ayanamsha: str = 'lahiri'
) -> List[Dict]:
    """
    Calculate sidereal planetary positions for Vedic astrology

    Args:
        dt: Birth datetime (assumes UTC)
        latitude: Birth latitude in degrees (-90 to 90)
        longitude: Birth longitude in degrees (-180 to 180)
        ayanamsha: Ayanamsha system ('lahiri', 'raman', 'krishnamurti')
                   Currently only 'lahiri' is implemented

    Returns:
        List of planet dictionaries with position, sign, nakshatra, house info
    """
    _ensure_ephemeris()

    from skyfield.api import Topos

    # Create observer location
    observer = _earth + Topos(
        latitude_degrees=latitude,
        longitude_degrees=longitude
    )

    # Create time object (ensure UTC)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        dt = dt.astimezone(timezone.utc)

    t = _ts.from_datetime(dt)

    # Calculate ayanamsha offset
    if ayanamsha.lower() == 'lahiri':
        ayanamsha_value = calculate_lahiri_ayanamsha(t.tt)
    else:
        # TODO: Implement other ayanamsha systems
        ayanamsha_value = calculate_lahiri_ayanamsha(t.tt)

    results = []

    for planet_name, planet_body in _planets_map.items():
        # Get geocentric apparent position
        astrometric = observer.at(t).observe(planet_body)
        apparent = astrometric.apparent()

        # Get ecliptic coordinates
        lat, lon, dist = apparent.ecliptic_latlon()
        tropical_long = lon.degrees

        # Convert tropical to sidereal
        sidereal_long = (tropical_long - ayanamsha_value) % 360

        # Get sign information
        sign_info = longitude_to_sign(sidereal_long)

        # Get nakshatra information
        nakshatra_info = longitude_to_nakshatra(sidereal_long)

        # Calculate speed
        speed = calculate_planet_speed(planet_body, t, _ts)

        results.append({
            'name': planet_name,
            'fullDegree': round(sidereal_long, 6),
            'normDegree': round(sign_info['norm_degree'], 6),
            'speed': round(speed, 6),
            'isRetro': speed < 0,
            'sign': sign_info['sign_name'],
            'signLord': sign_info['sign_lord'],
            'nakshatra': nakshatra_info['nakshatra_name'],
            'nakshatraLord': nakshatra_info['nakshatra_lord'],
            'house': 0  # Will be calculated after ascendant is known
        })

    return results


def calculate_rahu_ketu(moon_position: Dict) -> tuple[Dict, Dict]:
    """
    Calculate Rahu and Ketu positions (lunar nodes)

    Rahu is always exactly 180° opposite to Ketu.
    Simplified calculation: Rahu is approximately Moon's longitude + 180°

    In reality, this requires calculating the Moon's nodes from ephemeris.
    This is a placeholder for MVP.

    Args:
        moon_position: Moon's calculated position dict

    Returns:
        Tuple of (Rahu dict, Ketu dict)
    """
    # TODO: Implement actual lunar node calculation from Skyfield
    # For now, use simplified approximation

    moon_long = moon_position['fullDegree']

    # Rahu is approximately opposite the Moon (simplified)
    rahu_long = (moon_long + 180) % 360
    ketu_long = moon_long  # Ketu opposite to Rahu

    # Get sign and nakshatra for Rahu
    rahu_sign = longitude_to_sign(rahu_long)
    rahu_nakshatra = longitude_to_nakshatra(rahu_long)

    # Get sign and nakshatra for Ketu
    ketu_sign = longitude_to_sign(ketu_long)
    ketu_nakshatra = longitude_to_nakshatra(ketu_long)

    rahu = {
        'name': 'Rahu',
        'fullDegree': round(rahu_long, 6),
        'normDegree': round(rahu_sign['norm_degree'], 6),
        'speed': -0.053,  # Rahu is always retrograde (~3'/day)
        'isRetro': True,
        'sign': rahu_sign['sign_name'],
        'signLord': rahu_sign['sign_lord'],
        'nakshatra': rahu_nakshatra['nakshatra_name'],
        'nakshatraLord': rahu_nakshatra['nakshatra_lord'],
        'house': 0
    }

    ketu = {
        'name': 'Ketu',
        'fullDegree': round(ketu_long, 6),
        'normDegree': round(ketu_sign['norm_degree'], 6),
        'speed': -0.053,  # Ketu is always retrograde
        'isRetro': True,
        'sign': ketu_sign['sign_name'],
        'signLord': ketu_sign['sign_lord'],
        'nakshatra': ketu_nakshatra['nakshatra_name'],
        'nakshatraLord': ketu_nakshatra['nakshatra_lord'],
        'house': 0
    }

    return rahu, ketu
