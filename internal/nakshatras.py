"""
Nakshatras (Lunar Mansions)

27 Nakshatras divide the zodiac into 27 equal parts of 13°20' each.
Each nakshatra has a ruling planet (lord).
"""

from typing import Dict

# 27 Nakshatras
NAKSHATRAS = [
    'Ashwini',          # 0° - 13°20' Aries
    'Bharani',          # 13°20' - 26°40' Aries
    'Krittika',         # 26°40' Aries - 10° Taurus
    'Rohini',           # 10° - 23°20' Taurus
    'Mrigashira',       # 23°20' Taurus - 6°40' Gemini
    'Ardra',            # 6°40' - 20° Gemini
    'Punarvasu',        # 20° Gemini - 3°20' Cancer
    'Pushya',           # 3°20' - 16°40' Cancer
    'Ashlesha',         # 16°40' - 30° Cancer
    'Magha',            # 0° - 13°20' Leo
    'Purva Phalguni',   # 13°20' - 26°40' Leo
    'Uttara Phalguni',  # 26°40' Leo - 10° Virgo
    'Hasta',            # 10° - 23°20' Virgo
    'Chitra',           # 23°20' Virgo - 6°40' Libra
    'Swati',            # 6°40' - 20° Libra
    'Vishakha',         # 20° Libra - 3°20' Scorpio
    'Anuradha',         # 3°20' - 16°40' Scorpio
    'Jyeshtha',         # 16°40' - 30° Scorpio
    'Mula',             # 0° - 13°20' Sagittarius
    'Purva Ashadha',    # 13°20' - 26°40' Sagittarius
    'Uttara Ashadha',   # 26°40' Sagittarius - 10° Capricorn
    'Shravana',         # 10° - 23°20' Capricorn
    'Dhanishta',        # 23°20' Capricorn - 6°40' Aquarius
    'Shatabhisha',      # 6°40' - 20° Aquarius
    'Purva Bhadrapada', # 20° Aquarius - 3°20' Pisces
    'Uttara Bhadrapada',# 3°20' - 16°40' Pisces
    'Revati'            # 16°40' - 30° Pisces
]

# Nakshatra Lords (Planetary Rulers)
# Pattern: Ketu, Venus, Sun, Moon, Mars, Rahu, Jupiter, Saturn, Mercury (repeats 3 times)
NAKSHATRA_LORDS = [
    'Ketu',    # Ashwini
    'Venus',   # Bharani
    'Sun',     # Krittika
    'Moon',    # Rohini
    'Mars',    # Mrigashira
    'Rahu',    # Ardra
    'Jupiter', # Punarvasu
    'Saturn',  # Pushya
    'Mercury', # Ashlesha
    'Ketu',    # Magha
    'Venus',   # Purva Phalguni
    'Sun',     # Uttara Phalguni
    'Moon',    # Hasta
    'Mars',    # Chitra
    'Rahu',    # Swati
    'Jupiter', # Vishakha
    'Saturn',  # Anuradha
    'Mercury', # Jyeshtha
    'Ketu',    # Mula
    'Venus',   # Purva Ashadha
    'Sun',     # Uttara Ashadha
    'Moon',    # Shravana
    'Mars',    # Dhanishta
    'Rahu',    # Shatabhisha
    'Jupiter', # Purva Bhadrapada
    'Saturn',  # Uttara Bhadrapada
    'Mercury'  # Revati
]

# Nakshatra Deities
NAKSHATRA_DEITIES = [
    'Ashwini Kumaras',  # Ashwini
    'Yama',             # Bharani
    'Agni',             # Krittika
    'Brahma',           # Rohini
    'Soma',             # Mrigashira
    'Rudra',            # Ardra
    'Aditi',            # Punarvasu
    'Brihaspati',       # Pushya
    'Sarpa',            # Ashlesha
    'Pitris',           # Magha
    'Bhaga',            # Purva Phalguni
    'Aryaman',          # Uttara Phalguni
    'Savitar',          # Hasta
    'Tvashtar',         # Chitra
    'Vayu',             # Swati
    'Indra-Agni',       # Vishakha
    'Mitra',            # Anuradha
    'Indra',            # Jyeshtha
    'Nirriti',          # Mula
    'Apas',             # Purva Ashadha
    'Vishve Devas',     # Uttara Ashadha
    'Vishnu',           # Shravana
    'Vasus',            # Dhanishta
    'Varuna',           # Shatabhisha
    'Aja Ekapada',      # Purva Bhadrapada
    'Ahir Budhnya',     # Uttara Bhadrapada
    'Pushan'            # Revati
]


def get_nakshatra_name(nakshatra_num: int) -> str:
    """
    Get nakshatra name from nakshatra number (0-26)

    Args:
        nakshatra_num: Nakshatra number (0 = Ashwini, 26 = Revati)

    Returns:
        Nakshatra name
    """
    return NAKSHATRAS[nakshatra_num % 27]


def get_nakshatra_lord(nakshatra_num: int) -> str:
    """
    Get ruling planet for a nakshatra

    Args:
        nakshatra_num: Nakshatra number (0-26)

    Returns:
        Planet name (e.g., "Ketu" for Ashwini)
    """
    return NAKSHATRA_LORDS[nakshatra_num % 27]


def get_nakshatra_deity(nakshatra_num: int) -> str:
    """Get deity for a nakshatra"""
    return NAKSHATRA_DEITIES[nakshatra_num % 27]


def longitude_to_nakshatra(longitude: float) -> Dict[str, any]:
    """
    Convert ecliptic longitude to nakshatra information

    Each nakshatra spans 13°20' (13.333...°)

    Args:
        longitude: Ecliptic longitude in degrees (0-360)

    Returns:
        Dict with nakshatra_num, name, lord, pada, degree_in_nakshatra
    """
    # Each nakshatra is 13°20' = 13.333... degrees
    nakshatra_span = 360.0 / 27.0  # 13.333...

    nakshatra_num = int(longitude / nakshatra_span) % 27
    degree_in_nakshatra = longitude % nakshatra_span

    # Pada (quarter of nakshatra, each 3°20')
    pada_span = nakshatra_span / 4.0  # 3.333... degrees
    pada = int(degree_in_nakshatra / pada_span) + 1  # 1-4

    return {
        'nakshatra_num': nakshatra_num,
        'nakshatra_name': get_nakshatra_name(nakshatra_num),
        'nakshatra_lord': get_nakshatra_lord(nakshatra_num),
        'deity': get_nakshatra_deity(nakshatra_num),
        'pada': pada,
        'degree_in_nakshatra': degree_in_nakshatra
    }
