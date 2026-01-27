"""
Zodiac Signs and Rulerships

Vedic astrology uses 12 signs (rashis) in the sidereal zodiac.
"""

from typing import Dict

# 12 Zodiac Signs (Rashis)
SIGNS = [
    'Aries',       # Mesha
    'Taurus',      # Vrishabha
    'Gemini',      # Mithuna
    'Cancer',      # Karka
    'Leo',         # Simha
    'Virgo',       # Kanya
    'Libra',       # Tula
    'Scorpio',     # Vrishchika
    'Sagittarius', # Dhanu
    'Capricorn',   # Makara
    'Aquarius',    # Kumbha
    'Pisces'       # Meena
]

# Sign Lords (Ruling Planets)
SIGN_LORDS = [
    'Mars',    # Aries
    'Venus',   # Taurus
    'Mercury', # Gemini
    'Moon',    # Cancer
    'Sun',     # Leo
    'Mercury', # Virgo
    'Venus',   # Libra
    'Mars',    # Scorpio
    'Jupiter', # Sagittarius
    'Saturn',  # Capricorn
    'Saturn',  # Aquarius
    'Jupiter'  # Pisces
]

# Sign Elements
SIGN_ELEMENTS = [
    'Fire',  # Aries
    'Earth', # Taurus
    'Air',   # Gemini
    'Water', # Cancer
    'Fire',  # Leo
    'Earth', # Virgo
    'Air',   # Libra
    'Water', # Scorpio
    'Fire',  # Sagittarius
    'Earth', # Capricorn
    'Air',   # Aquarius
    'Water'  # Pisces
]

# Sign Qualities
SIGN_QUALITIES = [
    'Cardinal', # Aries
    'Fixed',    # Taurus
    'Mutable',  # Gemini
    'Cardinal', # Cancer
    'Fixed',    # Leo
    'Mutable',  # Virgo
    'Cardinal', # Libra
    'Fixed',    # Scorpio
    'Mutable',  # Sagittarius
    'Cardinal', # Capricorn
    'Fixed',    # Aquarius
    'Mutable'   # Pisces
]


def get_sign_name(sign_num: int) -> str:
    """
    Get sign name from sign number (0-11)

    Args:
        sign_num: Sign number (0 = Aries, 11 = Pisces)

    Returns:
        Sign name (e.g., "Aries")
    """
    return SIGNS[sign_num % 12]


def get_sign_lord(sign_num: int) -> str:
    """
    Get ruling planet for a sign

    Args:
        sign_num: Sign number (0-11)

    Returns:
        Planet name (e.g., "Mars" for Aries)
    """
    return SIGN_LORDS[sign_num % 12]


def get_sign_element(sign_num: int) -> str:
    """Get element for a sign (Fire, Earth, Air, Water)"""
    return SIGN_ELEMENTS[sign_num % 12]


def get_sign_quality(sign_num: int) -> str:
    """Get quality for a sign (Cardinal, Fixed, Mutable)"""
    return SIGN_QUALITIES[sign_num % 12]


def longitude_to_sign(longitude: float) -> Dict[str, any]:
    """
    Convert ecliptic longitude to sign information

    Args:
        longitude: Ecliptic longitude in degrees (0-360)

    Returns:
        Dict with sign_num, sign_name, sign_lord, norm_degree
    """
    sign_num = int(longitude / 30) % 12
    norm_degree = longitude % 30

    return {
        'sign_num': sign_num,
        'sign_name': get_sign_name(sign_num),
        'sign_lord': get_sign_lord(sign_num),
        'norm_degree': norm_degree,
        'element': get_sign_element(sign_num),
        'quality': get_sign_quality(sign_num)
    }
