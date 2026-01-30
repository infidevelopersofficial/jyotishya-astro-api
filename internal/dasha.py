"""
Vimsottari Dasha Calculator

Calculates Hindu astrological planetary periods based on Moon's nakshatra at birth.
The Vimsottari system spans 120 years total.

Dasha order: Ketu → Venus → Sun → Moon → Mars → Rahu → Jupiter → Saturn → Mercury
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

# Dasha periods in years
DASHA_YEARS = {
    "Ketu": 7,
    "Venus": 20,
    "Sun": 6,
    "Moon": 10,
    "Mars": 7,
    "Rahu": 18,
    "Jupiter": 16,
    "Saturn": 19,
    "Mercury": 17,
}

# Total cycle length
TOTAL_DASHA_YEARS = 120

# Dasha sequence
DASHA_SEQUENCE = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]

# Nakshatra lords (each nakshatra ruled by a planet)
# The pattern repeats every 9 nakshatras
NAKSHATRA_LORDS = [
    "Ketu",      # 1. Ashwini
    "Venus",     # 2. Bharani
    "Sun",       # 3. Krittika
    "Moon",      # 4. Rohini
    "Mars",      # 5. Mrigashira
    "Rahu",      # 6. Ardra
    "Jupiter",   # 7. Punarvasu
    "Saturn",    # 8. Pushya
    "Mercury",   # 9. Ashlesha
    "Ketu",      # 10. Magha
    "Venus",     # 11. Purva Phalguni
    "Sun",       # 12. Uttara Phalguni
    "Moon",      # 13. Hasta
    "Mars",      # 14. Chitra
    "Rahu",      # 15. Swati
    "Jupiter",   # 16. Vishakha
    "Saturn",    # 17. Anuradha
    "Mercury",   # 18. Jyeshtha
    "Ketu",      # 19. Mula
    "Venus",     # 20. Purva Ashadha
    "Sun",       # 21. Uttara Ashadha
    "Moon",      # 22. Shravana
    "Mars",      # 23. Dhanishtha
    "Rahu",      # 24. Shatabhisha
    "Jupiter",   # 25. Purva Bhadrapada
    "Saturn",    # 26. Uttara Bhadrapada
    "Mercury",   # 27. Revati
]

NAKSHATRA_NAMES = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira",
    "Ardra", "Punarvasu", "Pushya", "Ashlesha", "Magha",
    "Purva Phalguni", "Uttara Phalguni", "Hasta", "Chitra", "Swati",
    "Vishakha", "Anuradha", "Jyeshtha", "Mula", "Purva Ashadha",
    "Uttara Ashadha", "Shravana", "Dhanishtha", "Shatabhisha",
    "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
]


def calculate_vimsottari_dasha(
    moon_longitude: float,
    birth_date: datetime,
    years_to_calculate: int = 100
) -> Dict[str, Any]:
    """
    Calculate Vimsottari Dasha periods from birth.
    
    Args:
        moon_longitude: Moon's sidereal longitude (0-360 degrees)
        birth_date: Birth date/time
        years_to_calculate: How many years of dasha to calculate
    
    Returns:
        Dictionary with Mahadasha and Antardasha periods
    """
    try:
        # Calculate nakshatra (each spans 13°20' = 13.3333°)
        nakshatra_span = 360 / 27  # 13.3333 degrees
        nakshatra_num = int(moon_longitude / nakshatra_span)
        nakshatra_name = NAKSHATRA_NAMES[nakshatra_num]
        
        # Position within nakshatra (0 to 1)
        progress_in_nakshatra = (moon_longitude % nakshatra_span) / nakshatra_span
        
        # Get the ruling planet of this nakshatra
        first_dasha_lord = NAKSHATRA_LORDS[nakshatra_num]
        first_dasha_years = DASHA_YEARS[first_dasha_lord]
        
        # Calculate elapsed portion of first Mahadasha
        # (based on how far Moon has progressed through nakshatra)
        elapsed_years = progress_in_nakshatra * first_dasha_years
        remaining_years = first_dasha_years - elapsed_years
        
        # Calculate Mahadasha periods
        mahadashas = []
        current_date = birth_date
        
        # Find index of first dasha lord in sequence
        dasha_index = DASHA_SEQUENCE.index(first_dasha_lord)
        
        # First Mahadasha (partial)
        first_end_date = current_date + timedelta(days=remaining_years * 365.25)
        mahadashas.append({
            "planet": first_dasha_lord,
            "start_date": current_date.strftime("%Y-%m-%d"),
            "end_date": first_end_date.strftime("%Y-%m-%d"),
            "duration_years": round(remaining_years, 2),
            "is_current": is_current_period(current_date, first_end_date),
            "antardashas": calculate_antardashas(
                first_dasha_lord, current_date, first_end_date
            ),
        })
        
        current_date = first_end_date
        years_calculated = remaining_years
        
        # Subsequent Mahadashas
        while years_calculated < years_to_calculate:
            dasha_index = (dasha_index + 1) % 9
            dasha_lord = DASHA_SEQUENCE[dasha_index]
            dasha_years = DASHA_YEARS[dasha_lord]
            
            end_date = current_date + timedelta(days=dasha_years * 365.25)
            
            mahadashas.append({
                "planet": dasha_lord,
                "start_date": current_date.strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d"),
                "duration_years": dasha_years,
                "is_current": is_current_period(current_date, end_date),
                "antardashas": calculate_antardashas(
                    dasha_lord, current_date, end_date
                ),
            })
            
            current_date = end_date
            years_calculated += dasha_years
        
        # Find current Mahadasha and Antardasha
        current_maha = None
        current_antar = None
        for maha in mahadashas:
            if maha["is_current"]:
                current_maha = maha["planet"]
                for antar in maha["antardashas"]:
                    if antar["is_current"]:
                        current_antar = antar["planet"]
                        break
                break
        
        return {
            "birth_nakshatra": nakshatra_name,
            "nakshatra_lord": first_dasha_lord,
            "moon_longitude": round(moon_longitude, 4),
            "current_mahadasha": current_maha,
            "current_antardasha": current_antar,
            "mahadashas": mahadashas,
            "total_years_calculated": years_to_calculate,
            "backend": "internal",
        }
        
    except Exception as e:
        logger.error(f"Error calculating Vimsottari Dasha: {e}", exc_info=True)
        raise


def calculate_antardashas(
    mahadasha_lord: str,
    maha_start: datetime,
    maha_end: datetime
) -> List[Dict[str, Any]]:
    """
    Calculate Antardasha (sub-periods) within a Mahadasha.
    
    Antardasha duration = (Mahadasha years × Antardasha planet years) / 120
    Sequence starts from the Mahadasha lord itself.
    """
    antardashas = []
    maha_duration_days = (maha_end - maha_start).days
    
    # Start sequence from Mahadasha lord
    start_index = DASHA_SEQUENCE.index(mahadasha_lord)
    current_date = maha_start
    
    for i in range(9):
        antar_index = (start_index + i) % 9
        antar_lord = DASHA_SEQUENCE[antar_index]
        
        # Antardasha proportion
        antar_proportion = DASHA_YEARS[antar_lord] / TOTAL_DASHA_YEARS
        antar_days = maha_duration_days * antar_proportion
        
        end_date = current_date + timedelta(days=antar_days)
        
        antardashas.append({
            "planet": antar_lord,
            "start_date": current_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "duration_days": int(antar_days),
            "is_current": is_current_period(current_date, end_date),
        })
        
        current_date = end_date
    
    return antardashas


def is_current_period(start: datetime, end: datetime) -> bool:
    """Check if current date falls within this period."""
    now = datetime.now()
    
    # Handle string dates
    if isinstance(start, str):
        start = datetime.strptime(start, "%Y-%m-%d")
    if isinstance(end, str):
        end = datetime.strptime(end, "%Y-%m-%d")
    
    return start <= now <= end


def get_dasha_from_birth_chart(
    year: int, month: int, day: int,
    hours: int, minutes: int, seconds: int,
    latitude: float, longitude: float,
    timezone: float,
    ayanamsha: str = "lahiri",
    years_to_calculate: int = 100
) -> Dict[str, Any]:
    """
    Calculate Vimsottari Dasha from birth chart details.
    First calculates Moon position, then derives Dasha periods.
    """
    try:
        from .planetary import (
            _ensure_ephemeris,
            calculate_lahiri_ayanamsha
        )
        from .houses import datetime_to_julian_date
        from datetime import timezone as tz
        
        # Ensure ephemeris is loaded
        _ensure_ephemeris()
        
        from . import planetary
        ts = planetary._ts
        eph = planetary._eph
        
        # Create birth datetime
        birth_dt = datetime(year, month, day, hours, minutes, seconds)
        
        # Convert to UTC for ephemeris calculation
        utc_offset = timedelta(hours=timezone)
        utc_dt = birth_dt - utc_offset
        
        # Get Skyfield time
        t = ts.utc(utc_dt.year, utc_dt.month, utc_dt.day,
                   utc_dt.hour, utc_dt.minute, utc_dt.second)
        
        # Calculate Moon position
        earth = eph['earth']
        moon = eph['moon']
        
        astrometric = earth.at(t).observe(moon)
        ecliptic = astrometric.apparent().ecliptic_latlon()
        moon_lon = ecliptic[1].degrees
        
        # Apply ayanamsha for sidereal position
        jd = datetime_to_julian_date(utc_dt)
        ayanamsha_value = calculate_lahiri_ayanamsha(jd)
        moon_sidereal = (moon_lon - ayanamsha_value) % 360
        
        # Calculate Dasha
        result = calculate_vimsottari_dasha(
            moon_longitude=moon_sidereal,
            birth_date=birth_dt,
            years_to_calculate=years_to_calculate
        )
        
        result["ayanamsha"] = ayanamsha
        result["ayanamsha_value"] = round(ayanamsha_value, 4)
        
        return result
        
    except Exception as e:
        logger.error(f"Error getting dasha from birth chart: {e}", exc_info=True)
        raise
