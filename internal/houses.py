"""
House System Calculations

Implements house cusp calculations and ascendant determination.
Supports Whole Sign and Placidus house systems.
"""

import math
from datetime import datetime, timezone
from typing import List, Dict
from .signs import get_sign_name


def datetime_to_julian_date(dt: datetime) -> float:
    """
    Convert datetime to Julian Date

    Args:
        dt: Datetime object (UTC)

    Returns:
        Julian Date as float
    """
    # Ensure UTC
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        dt = dt.astimezone(timezone.utc)

    # Julian Date calculation
    year = dt.year
    month = dt.month
    day = dt.day

    # Adjust for January/February
    if month <= 2:
        year -= 1
        month += 12

    a = int(year / 100)
    b = 2 - a + int(a / 4)

    jd = int(365.25 * (year + 4716)) + int(30.6001 * (month + 1)) + day + b - 1524.5

    # Add time fraction
    time_fraction = (dt.hour + dt.minute / 60.0 + dt.second / 3600.0) / 24.0
    jd += time_fraction

    return jd


def calculate_greenwich_sidereal_time(dt: datetime) -> float:
    """
    Calculate Greenwich Sidereal Time in hours (0-24)

    Args:
        dt: Datetime object (UTC)

    Returns:
        Greenwich Sidereal Time in hours
    """
    jd = datetime_to_julian_date(dt)

    # J2000.0 epoch (Jan 1, 2000, 12:00 UT)
    jd2000 = 2451545.0

    # Days since J2000
    d = jd - jd2000

    # Mean sidereal time at Greenwich (simplified formula)
    # GST at 0h UT = 18.697374558 + 24.06570982441908 * D
    gst = 18.697374558 + 24.06570982441908 * d

    # Normalize to 0-24 hours
    gst = gst % 24.0

    return gst


def calculate_local_sidereal_time(dt: datetime, longitude: float) -> float:
    """
    Calculate Local Sidereal Time in hours (0-24)

    Args:
        dt: Datetime object (UTC)
        longitude: Observer's longitude in degrees (East is positive)

    Returns:
        Local Sidereal Time in hours
    """
    # Greenwich Sidereal Time
    gst = calculate_greenwich_sidereal_time(dt)

    # Longitude correction: 1 degree = 4 minutes of time = 1/15 hour
    longitude_hours = longitude / 15.0

    # Local Sidereal Time
    lst = (gst + longitude_hours) % 24.0

    return lst


def calculate_ascendant(
    dt: datetime,
    latitude: float,
    longitude: float,
    ayanamsha: float
) -> float:
    """
    Calculate ascendant (rising sign) using Placidus system

    The ascendant is the degree of the ecliptic rising on the eastern horizon
    at the moment and place of birth.

    Args:
        dt: Birth datetime (UTC)
        latitude: Birth latitude in degrees (-90 to 90)
        longitude: Birth longitude in degrees (-180 to 180)
        ayanamsha: Ayanamsha value in degrees (for sidereal conversion)

    Returns:
        Sidereal ascendant longitude in degrees (0-360)
    """
    # Local Sidereal Time
    lst = calculate_local_sidereal_time(dt, longitude)

    # Convert LST to degrees (RAMC - Right Ascension of Midheaven)
    ramc = lst * 15.0  # hours to degrees

    # Obliquity of the ecliptic (Earth's axial tilt)
    # Mean obliquity for epoch J2000.0: 23.4392911°
    # For better accuracy, should adjust for date, but this is close enough for MVP
    epsilon = 23.4397

    # Convert to radians
    ramc_rad = math.radians(ramc)
    lat_rad = math.radians(latitude)
    eps_rad = math.radians(epsilon)

    # Ascendant formula (Placidus/standard method)
    # tan(Asc) = -cos(RAMC) / (sin(RAMC) * cos(ε) + tan(lat) * sin(ε))

    numerator = -math.cos(ramc_rad)
    denominator = (
        math.sin(ramc_rad) * math.cos(eps_rad) +
        math.tan(lat_rad) * math.sin(eps_rad)
    )

    # Calculate ascendant in ecliptic longitude (tropical)
    asc_tropical_rad = math.atan2(numerator, denominator)
    asc_tropical = math.degrees(asc_tropical_rad)

    # Normalize to 0-360
    asc_tropical = asc_tropical % 360

    # Convert tropical to sidereal
    asc_sidereal = (asc_tropical - ayanamsha) % 360

    return asc_sidereal


def calculate_midheaven(
    dt: datetime,
    longitude: float,
    ayanamsha: float
) -> float:
    """
    Calculate Midheaven (MC - Medium Coeli)

    MC is the point where the ecliptic crosses the meridian.

    Args:
        dt: Birth datetime (UTC)
        longitude: Birth longitude in degrees
        ayanamsha: Ayanamsha value in degrees

    Returns:
        Sidereal MC longitude in degrees (0-360)
    """
    # Local Sidereal Time
    lst = calculate_local_sidereal_time(dt, longitude)

    # RAMC in degrees
    ramc = lst * 15.0

    # Obliquity of ecliptic
    epsilon = 23.4397

    # MC calculation (simplified)
    # For a more accurate formula, we'd use:
    # tan(MC) = tan(RAMC) / cos(ε)

    ramc_rad = math.radians(ramc)
    eps_rad = math.radians(epsilon)

    mc_tropical_rad = math.atan2(math.tan(ramc_rad), math.cos(eps_rad))
    mc_tropical = math.degrees(mc_tropical_rad) % 360

    # Convert to sidereal
    mc_sidereal = (mc_tropical - ayanamsha) % 360

    return mc_sidereal


def calculate_houses_whole_sign(ascendant: float) -> List[Dict]:
    """
    Calculate house cusps using Whole Sign house system

    In Whole Sign houses, each house spans exactly one sign (30°).
    The 1st house cusp is the beginning of the sign containing the ascendant.

    Args:
        ascendant: Sidereal ascendant longitude in degrees

    Returns:
        List of 12 house dictionaries with house number, sign, and cusp degree
    """
    houses = []

    # Determine which sign contains the ascendant
    asc_sign_num = int(ascendant / 30)

    for house_num in range(1, 13):
        # Each house starts at a new sign
        sign_num = (asc_sign_num + house_num - 1) % 12
        sign_name = get_sign_name(sign_num)

        # Cusp is at the beginning of the sign
        cusp_degree = sign_num * 30

        houses.append({
            'house': house_num,
            'sign': sign_name,
            'degree': round(cusp_degree, 6)
        })

    return houses


def calculate_houses_placidus(
    ascendant: float,
    mc: float,
    latitude: float
) -> List[Dict]:
    """
    Calculate house cusps using Placidus house system

    Placidus is the most commonly used house system in Western astrology.
    It divides the time it takes for a degree to travel from the IC to MC
    into thirds.

    Args:
        ascendant: Sidereal ascendant longitude
        mc: Sidereal Midheaven longitude
        latitude: Birth latitude

    Returns:
        List of 12 house dictionaries

    Note: This is a simplified implementation. Full Placidus requires
    iterative calculations. For MVP, we'll use a hybrid approach.
    """
    houses = []

    # Houses 1, 4, 7, 10 are the angular houses (exact)
    house_1 = ascendant
    house_10 = mc
    house_7 = (ascendant + 180) % 360  # Descendant
    house_4 = (mc + 180) % 360  # IC

    # For MVP, use equal division between angular houses
    # (True Placidus is more complex and requires iterative calculation)

    house_cusps = {
        1: house_1,
        2: (house_1 + (house_4 - house_1) / 3) % 360,
        3: (house_1 + 2 * (house_4 - house_1) / 3) % 360,
        4: house_4,
        5: (house_4 + (house_7 - house_4) / 3) % 360,
        6: (house_4 + 2 * (house_7 - house_4) / 3) % 360,
        7: house_7,
        8: (house_7 + (house_10 - house_7) / 3) % 360,
        9: (house_7 + 2 * (house_10 - house_7) / 3) % 360,
        10: house_10,
        11: (house_10 + (house_1 - house_10) / 3) % 360,
        12: (house_10 + 2 * (house_1 - house_10) / 3) % 360,
    }

    for house_num in range(1, 13):
        cusp = house_cusps[house_num]
        sign_num = int(cusp / 30) % 12
        sign_name = get_sign_name(sign_num)

        houses.append({
            'house': house_num,
            'sign': sign_name,
            'degree': round(cusp, 6)
        })

    return houses


def assign_planets_to_houses(
    planets: List[Dict],
    houses: List[Dict],
    house_system: str = 'whole_sign'
) -> List[Dict]:
    """
    Assign each planet to its house based on the house system

    Args:
        planets: List of planet position dictionaries
        houses: List of house cusp dictionaries
        house_system: 'whole_sign' or 'placidus'

    Returns:
        Updated planets list with 'house' field populated
    """
    for planet in planets:
        planet_long = planet['fullDegree']

        if house_system == 'whole_sign':
            # In whole sign, house = sign offset from 1st house sign
            planet_sign = int(planet_long / 30)
            first_house_sign = int(houses[0]['degree'] / 30)
            house = ((planet_sign - first_house_sign) % 12) + 1
        else:
            # Placidus: find which house the planet falls into
            house = 1
            for i in range(12):
                cusp_this = houses[i]['degree']
                cusp_next = houses[(i + 1) % 12]['degree']

                # Handle wraparound at 0°/360°
                if cusp_next < cusp_this:
                    # House crosses 0° Aries
                    if planet_long >= cusp_this or planet_long < cusp_next:
                        house = i + 1
                        break
                else:
                    if cusp_this <= planet_long < cusp_next:
                        house = i + 1
                        break

        planet['house'] = house

    return planets
