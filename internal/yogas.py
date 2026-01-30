"""
Yogas (Planetary Combinations) Detector

Identifies special planetary combinations in a birth chart that indicate
specific life effects according to Vedic astrology.
"""

from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

# Rashi lords mapping
RASHI_LORDS = {
    1: "Mars", 2: "Venus", 3: "Mercury", 4: "Moon",
    5: "Sun", 6: "Mercury", 7: "Venus", 8: "Mars",
    9: "Jupiter", 10: "Saturn", 11: "Saturn", 12: "Jupiter"
}

# Exaltation signs
EXALTATION = {
    "Sun": 1, "Moon": 2, "Mars": 10, "Mercury": 6,
    "Jupiter": 4, "Venus": 12, "Saturn": 7
}

# Debilitation signs
DEBILITATION = {
    "Sun": 7, "Moon": 8, "Mars": 4, "Mercury": 12,
    "Jupiter": 10, "Venus": 6, "Saturn": 1
}

# Kendra houses (angular)
KENDRAS = [1, 4, 7, 10]

# Trikona houses (trinal)
TRIKONAS = [1, 5, 9]

# Dusthanas (malefic houses)
DUSTHANAS = [6, 8, 12]

# Natural benefics and malefics
BENEFICS = ["Jupiter", "Venus", "Moon", "Mercury"]
MALEFICS = ["Sun", "Mars", "Saturn", "Rahu", "Ketu"]


def get_rashi_from_lon(longitude: float) -> int:
    """Get rashi number (1-12) from longitude."""
    return int(longitude / 30) + 1


def get_house_from_lon(planet_lon: float, asc_lon: float) -> int:
    """Get house number (1-12) from planet and ascendant longitude."""
    diff = (planet_lon - asc_lon) % 360
    return int(diff / 30) + 1


def is_exalted(planet: str, rashi: int) -> bool:
    """Check if planet is in exaltation sign."""
    return EXALTATION.get(planet) == rashi


def is_debilitated(planet: str, rashi: int) -> bool:
    """Check if planet is in debilitation sign."""
    return DEBILITATION.get(planet) == rashi


def detect_raj_yogas(planets: Dict[str, Dict], asc_rashi: int) -> List[Dict]:
    """Detect Raja Yogas (combinations for power and authority)."""
    yogas = []
    
    # Get lords of kendras and trikonas
    kendra_lords = set()
    trikona_lords = set()
    
    for house in KENDRAS:
        rashi = ((asc_rashi - 1 + house - 1) % 12) + 1
        lord = RASHI_LORDS[rashi]
        kendra_lords.add(lord)
    
    for house in TRIKONAS:
        rashi = ((asc_rashi - 1 + house - 1) % 12) + 1
        lord = RASHI_LORDS[rashi]
        trikona_lords.add(lord)
    
    # Raja Yoga: Kendra lord + Trikona lord conjunction or mutual aspect
    for kl in kendra_lords:
        for tl in trikona_lords:
            if kl == tl:
                continue
            kl_data = planets.get(kl, {})
            tl_data = planets.get(tl, {})
            
            if not kl_data or not tl_data:
                continue
            
            kl_rashi = kl_data.get("rashi", 0)
            tl_rashi = tl_data.get("rashi", 0)
            
            # Check conjunction (same sign)
            if kl_rashi == tl_rashi:
                yogas.append({
                    "name": f"Raja Yoga ({kl}-{tl})",
                    "type": "raja",
                    "planets": [kl, tl],
                    "description": f"Kendra lord {kl} conjunct Trikona lord {tl}",
                    "effect": "Rise in status, power, authority, and recognition",
                    "strength": "strong"
                })
    
    return yogas


def detect_dhana_yogas(planets: Dict[str, Dict], asc_rashi: int) -> List[Dict]:
    """Detect Dhana Yogas (combinations for wealth)."""
    yogas = []
    
    # 2nd and 11th house lords for wealth
    second_rashi = ((asc_rashi - 1 + 1) % 12) + 1
    eleventh_rashi = ((asc_rashi - 1 + 10) % 12) + 1
    
    second_lord = RASHI_LORDS[second_rashi]
    eleventh_lord = RASHI_LORDS[eleventh_rashi]
    
    # Check if 2nd and 11th lords are together or in kendras
    sl_data = planets.get(second_lord, {})
    el_data = planets.get(eleventh_lord, {})
    
    if sl_data and el_data:
        sl_house = sl_data.get("house", 0)
        el_house = el_data.get("house", 0)
        
        if sl_data.get("rashi") == el_data.get("rashi"):
            yogas.append({
                "name": "Dhana Yoga (2nd-11th)",
                "type": "dhana",
                "planets": [second_lord, eleventh_lord],
                "description": f"2nd lord {second_lord} conjunct 11th lord {eleventh_lord}",
                "effect": "Accumulation of wealth and prosperity",
                "strength": "strong"
            })
        elif sl_house in KENDRAS and el_house in KENDRAS:
            yogas.append({
                "name": "Dhana Yoga (Kendra)",
                "type": "dhana",
                "planets": [second_lord, eleventh_lord],
                "description": f"2nd and 11th lords in Kendras",
                "effect": "Good financial growth and stability",
                "strength": "moderate"
            })
    
    # Jupiter in 2nd, 5th, 9th, or 11th
    jupiter_data = planets.get("Jupiter", {})
    if jupiter_data:
        jup_house = jupiter_data.get("house", 0)
        if jup_house in [2, 5, 9, 11]:
            yogas.append({
                "name": "Jupiter Wealth Yoga",
                "type": "dhana",
                "planets": ["Jupiter"],
                "description": f"Jupiter in house {jup_house}",
                "effect": "Natural abundance and good fortune with money",
                "strength": "moderate"
            })
    
    return yogas


def detect_gaja_kesari(planets: Dict[str, Dict]) -> List[Dict]:
    """Detect Gaja Kesari Yoga (Jupiter-Moon combination)."""
    yogas = []
    
    moon_data = planets.get("Moon", {})
    jupiter_data = planets.get("Jupiter", {})
    
    if not moon_data or not jupiter_data:
        return yogas
    
    moon_rashi = moon_data.get("rashi", 0)
    jup_rashi = jupiter_data.get("rashi", 0)
    
    # Check if Moon and Jupiter are in kendra from each other (1, 4, 7, 10)
    diff = abs(moon_rashi - jup_rashi)
    if diff == 0:
        diff = 1
    else:
        diff = ((jup_rashi - moon_rashi) % 12) + 1
    
    if diff in [1, 4, 7, 10]:
        yogas.append({
            "name": "Gaja Kesari Yoga",
            "type": "prosperity",
            "planets": ["Moon", "Jupiter"],
            "description": "Jupiter in kendra from Moon",
            "effect": "Fame, wisdom, good memory, learning ability, and respected status",
            "strength": "strong" if diff == 1 else "moderate"
        })
    
    return yogas


def detect_pancha_mahapurusha(planets: Dict[str, Dict], asc_rashi: int) -> List[Dict]:
    """Detect Pancha Mahapurusha Yogas (5 great person yogas)."""
    yogas = []
    
    mahapurusha = {
        "Mars": ("Ruchaka", "Courage, leadership, authority in military/police"),
        "Mercury": ("Bhadra", "Intelligence, eloquence, business acumen"),
        "Jupiter": ("Hamsa", "Wisdom, spirituality, teaching ability"),
        "Venus": ("Malavya", "Beauty, luxury, artistic talents, pleasures"),
        "Saturn": ("Shasha", "Power through discipline, longevity, success through hard work")
    }
    
    for planet, (yoga_name, effect) in mahapurusha.items():
        p_data = planets.get(planet, {})
        if not p_data:
            continue
        
        p_house = p_data.get("house", 0)
        p_rashi = p_data.get("rashi", 0)
        own_signs = [i for i, lord in RASHI_LORDS.items() if lord == planet]
        exalt_sign = EXALTATION.get(planet)
        
        # Must be in kendra and in own sign or exaltation
        if p_house in KENDRAS:
            if p_rashi in own_signs or p_rashi == exalt_sign:
                yogas.append({
                    "name": f"{yoga_name} Yoga",
                    "type": "mahapurusha",
                    "planets": [planet],
                    "description": f"{planet} in kendra in own sign/exaltation",
                    "effect": effect,
                    "strength": "very strong"
                })
    
    return yogas


def detect_neecha_bhanga(planets: Dict[str, Dict]) -> List[Dict]:
    """Detect Neecha Bhanga Raja Yoga (cancellation of debilitation)."""
    yogas = []
    
    for planet_name, p_data in planets.items():
        if planet_name in ["Rahu", "Ketu"]:
            continue
        
        p_rashi = p_data.get("rashi", 0)
        
        # Check if debilitated
        if not is_debilitated(planet_name, p_rashi):
            continue
        
        # Cancellation: Lord of debilitation sign in kendra from Moon or Ascendant
        debil_lord = RASHI_LORDS.get(p_rashi)
        if debil_lord:
            lord_data = planets.get(debil_lord, {})
            if lord_data:
                lord_house = lord_data.get("house", 0)
                if lord_house in KENDRAS:
                    yogas.append({
                        "name": "Neecha Bhanga Raja Yoga",
                        "type": "raja",
                        "planets": [planet_name, debil_lord],
                        "description": f"{planet_name}'s debilitation cancelled by {debil_lord} in kendra",
                        "effect": "Tremendous rise after initial struggles, turning weakness to strength",
                        "strength": "strong"
                    })
    
    return yogas


def detect_yogas(planets_list: List[Dict], ascendant_lon: float) -> Dict[str, Any]:
    """
    Detect all yogas in a birth chart.
    
    Args:
        planets_list: List of planet data with name, fullDegree, etc.
        ascendant_lon: Ascendant (Lagna) longitude
    
    Returns:
        Dictionary with detected yogas and summary
    """
    # Convert planets list to dict with house/rashi info
    asc_rashi = get_rashi_from_lon(ascendant_lon)
    
    planets = {}
    for p in planets_list:
        name = p.get("name", "")
        lon = p.get("fullDegree", p.get("full_degree", 0))
        
        if not name or not lon:
            continue
        
        rashi = get_rashi_from_lon(lon)
        house = get_house_from_lon(lon, ascendant_lon)
        
        planets[name] = {
            "longitude": lon,
            "rashi": rashi,
            "house": house,
            "is_exalted": is_exalted(name, rashi),
            "is_debilitated": is_debilitated(name, rashi),
        }
    
    # Collect all yogas
    all_yogas = []
    
    # Pancha Mahapurusha (most powerful)
    all_yogas.extend(detect_pancha_mahapurusha(planets, asc_rashi))
    
    # Raja Yogas
    all_yogas.extend(detect_raj_yogas(planets, asc_rashi))
    
    # Gaja Kesari
    all_yogas.extend(detect_gaja_kesari(planets))
    
    # Dhana Yogas
    all_yogas.extend(detect_dhana_yogas(planets, asc_rashi))
    
    # Neecha Bhanga
    all_yogas.extend(detect_neecha_bhanga(planets))
    
    # Categorize by type
    yoga_categories = {}
    for yoga in all_yogas:
        yoga_type = yoga.get("type", "other")
        if yoga_type not in yoga_categories:
            yoga_categories[yoga_type] = []
        yoga_categories[yoga_type].append(yoga)
    
    # Count by strength
    strength_count = {"very strong": 0, "strong": 0, "moderate": 0, "weak": 0}
    for yoga in all_yogas:
        strength = yoga.get("strength", "moderate")
        strength_count[strength] = strength_count.get(strength, 0) + 1
    
    return {
        "ascendant_rashi": asc_rashi,
        "planets": planets,
        "yogas": all_yogas,
        "categories": yoga_categories,
        "summary": {
            "total_yogas": len(all_yogas),
            "by_strength": strength_count,
            "has_mahapurusha": len(yoga_categories.get("mahapurusha", [])) > 0,
            "has_raja_yoga": len(yoga_categories.get("raja", [])) > 0,
            "has_dhana_yoga": len(yoga_categories.get("dhana", [])) > 0,
        },
        "backend": "internal",
    }
