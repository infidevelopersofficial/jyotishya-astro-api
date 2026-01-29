"""
Panchang Calculator

Calculates Hindu almanac elements:
- Tithi (Lunar day)
- Nakshatra (Lunar mansion)
- Yoga (Sun-Moon combination)
- Karana (Half-tithi)
- Sunrise/Sunset times
"""

from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional
import logging
import math

logger = logging.getLogger(__name__)

# Tithi names (30 tithis in a lunar month)
TITHIS = [
    "Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami",
    "Shashthi", "Saptami", "Ashtami", "Navami", "Dashami",
    "Ekadashi", "Dwadashi", "Trayodashi", "Chaturdashi", "Purnima",
    "Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami",
    "Shashthi", "Saptami", "Ashtami", "Navami", "Dashami",
    "Ekadashi", "Dwadashi", "Trayodashi", "Chaturdashi", "Amavasya"
]

# Nakshatra names (27 nakshatras)
NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira",
    "Ardra", "Punarvasu", "Pushya", "Ashlesha", "Magha",
    "Purva Phalguni", "Uttara Phalguni", "Hasta", "Chitra", "Swati",
    "Vishakha", "Anuradha", "Jyeshtha", "Mula", "Purva Ashadha",
    "Uttara Ashadha", "Shravana", "Dhanishtha", "Shatabhisha",
    "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
]

# Yoga names (27 yogas)
YOGAS = [
    "Vishkambha", "Priti", "Ayushman", "Saubhagya", "Shobhana",
    "Atiganda", "Sukarma", "Dhriti", "Shoola", "Ganda",
    "Vriddhi", "Dhruva", "Vyaghata", "Harshana", "Vajra",
    "Siddhi", "Vyatipata", "Variyan", "Parigha", "Shiva",
    "Siddha", "Sadhya", "Shubha", "Shukla", "Brahma",
    "Indra", "Vaidhriti"
]

# Karana names (11 karanas, some repeat)
KARANAS = [
    "Bava", "Balava", "Kaulava", "Taitila", "Gara",
    "Vanija", "Vishti", "Shakuni", "Chatushpada", "Naga", "Kimstughna"
]


def calculate_panchang(
    date: datetime,
    latitude: float = 28.6139,  # Delhi default
    longitude: float = 77.209,
    timezone_hours: float = 5.5,
    ayanamsha: str = "lahiri"
) -> Dict[str, Any]:
    """
    Calculate Panchang for a given date and location.
    
    Args:
        date: Date for Panchang calculation
        latitude: Location latitude
        longitude: Location longitude
        timezone_hours: Timezone offset in hours
        ayanamsha: Ayanamsha system (lahiri, krishnamurti, raman)
    
    Returns:
        Dictionary with all Panchang elements
    """
    try:
        from .planetary import load_ephemeris, get_ayanamsha_value
        
        ts, eph = load_ephemeris()
        
        # Use noon for calculations
        noon_dt = datetime(
            date.year, date.month, date.day,
            12, 0, 0, tzinfo=timezone.utc
        )
        t = ts.utc(noon_dt)
        
        # Get Sun and Moon positions
        earth = eph['earth']
        sun = eph['sun']
        moon = eph['moon']
        
        sun_astrometric = earth.at(t).observe(sun)
        moon_astrometric = earth.at(t).observe(moon)
        
        sun_ecliptic = sun_astrometric.apparent().ecliptic_latlon()
        moon_ecliptic = moon_astrometric.apparent().ecliptic_latlon()
        
        sun_lon = sun_ecliptic[1].degrees
        moon_lon = moon_ecliptic[1].degrees
        
        # Apply ayanamsha for sidereal positions
        ayanamsha_value = get_ayanamsha_value(t, ayanamsha)
        sun_sidereal = (sun_lon - ayanamsha_value) % 360
        moon_sidereal = (moon_lon - ayanamsha_value) % 360
        
        # Calculate Tithi (0-29)
        moon_sun_diff = (moon_sidereal - sun_sidereal) % 360
        tithi_num = int(moon_sun_diff / 12)
        tithi_name = TITHIS[tithi_num]
        tithi_paksha = "Shukla Paksha" if tithi_num < 15 else "Krishna Paksha"
        
        # Calculate Nakshatra (0-26)
        nakshatra_num = int(moon_sidereal / (360 / 27))
        nakshatra_name = NAKSHATRAS[nakshatra_num]
        nakshatra_pada = int((moon_sidereal % (360 / 27)) / (360 / 27 / 4)) + 1
        
        # Calculate Yoga (0-26)
        yoga_value = (sun_sidereal + moon_sidereal) % 360
        yoga_num = int(yoga_value / (360 / 27))
        yoga_name = YOGAS[yoga_num]
        
        # Calculate Karana (0-10, but cycles through)
        karana_value = moon_sun_diff / 6
        karana_num = int(karana_value) % 11
        karana_name = KARANAS[karana_num]
        
        # Calculate approximate sunrise/sunset
        sunrise, sunset = calculate_sun_times(date, latitude, longitude, timezone_hours)
        
        # Determine Vara (day of week)
        vara_names = ["Ravivara", "Somavara", "Mangalavara", "Budhavara", 
                      "Guruvara", "Shukravara", "Shanivara"]
        vara = vara_names[date.weekday()]
        
        # Determine Ritu (season) - approximate based on month
        month = date.month
        if month in [3, 4]:
            ritu = "Vasanta (Spring)"
        elif month in [5, 6]:
            ritu = "Grishma (Summer)"
        elif month in [7, 8]:
            ritu = "Varsha (Monsoon)"
        elif month in [9, 10]:
            ritu = "Sharad (Autumn)"
        elif month in [11, 12]:
            ritu = "Hemanta (Pre-Winter)"
        else:
            ritu = "Shishira (Winter)"
        
        return {
            "date": date.strftime("%Y-%m-%d"),
            "vara": vara,
            "tithi": {
                "name": tithi_name,
                "number": tithi_num + 1,
                "paksha": tithi_paksha,
            },
            "nakshatra": {
                "name": nakshatra_name,
                "number": nakshatra_num + 1,
                "pada": nakshatra_pada,
            },
            "yoga": {
                "name": yoga_name,
                "number": yoga_num + 1,
            },
            "karana": {
                "name": karana_name,
                "number": karana_num + 1,
            },
            "sunrise": sunrise,
            "sunset": sunset,
            "ritu": ritu,
            "moon_sign": NAKSHATRAS[int(moon_sidereal / 30) % 12].split()[0],
            "sun_sign": NAKSHATRAS[int(sun_sidereal / 30) % 12].split()[0],
            "ayanamsha": ayanamsha,
            "ayanamsha_value": round(ayanamsha_value, 4),
            "backend": "internal",
        }
        
    except Exception as e:
        logger.error(f"Error calculating panchang: {e}", exc_info=True)
        raise


def calculate_sun_times(
    date: datetime,
    latitude: float,
    longitude: float,
    timezone_hours: float
) -> tuple:
    """
    Calculate approximate sunrise and sunset times.
    Uses a simplified algorithm for quick calculation.
    """
    try:
        # Day of year
        day_of_year = date.timetuple().tm_yday
        
        # Solar declination (approximate)
        declination = 23.45 * math.sin(math.radians((360 / 365) * (day_of_year - 81)))
        
        # Hour angle
        lat_rad = math.radians(latitude)
        dec_rad = math.radians(declination)
        
        cos_hour_angle = -math.tan(lat_rad) * math.tan(dec_rad)
        
        # Clamp to valid range
        cos_hour_angle = max(-1, min(1, cos_hour_angle))
        
        hour_angle = math.degrees(math.acos(cos_hour_angle))
        
        # Solar noon in hours (approximate)
        solar_noon = 12 - (longitude / 15) + timezone_hours
        
        # Sunrise and sunset
        sunrise_hours = solar_noon - (hour_angle / 15)
        sunset_hours = solar_noon + (hour_angle / 15)
        
        # Convert to time strings
        def hours_to_time(h):
            h = h % 24
            hours = int(h)
            minutes = int((h - hours) * 60)
            return f"{hours:02d}:{minutes:02d}"
        
        return hours_to_time(sunrise_hours), hours_to_time(sunset_hours)
        
    except Exception as e:
        logger.warning(f"Error calculating sun times: {e}")
        return "06:00", "18:00"  # Fallback
