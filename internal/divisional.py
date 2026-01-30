"""
Divisional Charts (Varga Charts) Calculator

Calculates various divisional charts used in Vedic astrology:
- D1 (Rashi) - Birth chart
- D9 (Navamsa) - Marriage, destiny, soul purpose
- D10 (Dasamsa) - Career and profession
- D2 (Hora) - Wealth
- D3 (Drekkana) - Siblings
- D7 (Saptamsa) - Children
- D12 (Dwadasamsa) - Parents
"""

from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

# Sign names
SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

# Rashi lords
RASHI_LORDS = {
    1: "Mars", 2: "Venus", 3: "Mercury", 4: "Moon",
    5: "Sun", 6: "Mercury", 7: "Venus", 8: "Mars",
    9: "Jupiter", 10: "Saturn", 11: "Saturn", 12: "Jupiter"
}


def get_d1_position(longitude: float) -> Dict[str, Any]:
    """D1 (Rashi) - Basic birth chart position."""
    rashi = int(longitude / 30) + 1
    degree_in_sign = longitude % 30
    
    return {
        "chart": "D1",
        "rashi": rashi,
        "sign": SIGNS[rashi - 1],
        "degree": round(degree_in_sign, 4),
        "lord": RASHI_LORDS[rashi],
    }


def get_d9_position(longitude: float) -> Dict[str, Any]:
    """D9 (Navamsa) - Divides each sign into 9 parts of 3°20'."""
    rashi = int(longitude / 30) + 1
    degree_in_sign = longitude % 30
    
    # Each navamsa = 3.333... degrees
    navamsa_num = int(degree_in_sign / (30 / 9))  # 0-8
    
    # Starting sign depends on original sign element
    # Fire signs (1,5,9): start from Aries
    # Earth signs (2,6,10): start from Capricorn  
    # Air signs (3,7,11): start from Libra
    # Water signs (4,8,12): start from Cancer
    
    if rashi in [1, 5, 9]:  # Fire
        start_sign = 1
    elif rashi in [2, 6, 10]:  # Earth
        start_sign = 10
    elif rashi in [3, 7, 11]:  # Air
        start_sign = 7
    else:  # Water
        start_sign = 4
    
    d9_rashi = ((start_sign - 1 + navamsa_num) % 12) + 1
    
    return {
        "chart": "D9",
        "rashi": d9_rashi,
        "sign": SIGNS[d9_rashi - 1],
        "lord": RASHI_LORDS[d9_rashi],
        "navamsa_number": navamsa_num + 1,
    }


def get_d10_position(longitude: float) -> Dict[str, Any]:
    """D10 (Dasamsa) - Divides each sign into 10 parts of 3°."""
    rashi = int(longitude / 30) + 1
    degree_in_sign = longitude % 30
    
    # Each dasamsa = 3 degrees
    dasamsa_num = int(degree_in_sign / 3)  # 0-9
    
    # Odd signs: start from same sign
    # Even signs: start from 9th sign from it
    if rashi % 2 == 1:  # Odd
        start_sign = rashi
    else:  # Even
        start_sign = ((rashi - 1 + 8) % 12) + 1  # 9th from it
    
    d10_rashi = ((start_sign - 1 + dasamsa_num) % 12) + 1
    
    return {
        "chart": "D10",
        "rashi": d10_rashi,
        "sign": SIGNS[d10_rashi - 1],
        "lord": RASHI_LORDS[d10_rashi],
        "dasamsa_number": dasamsa_num + 1,
    }


def get_d2_position(longitude: float) -> Dict[str, Any]:
    """D2 (Hora) - Divides each sign into 2 parts of 15°."""
    rashi = int(longitude / 30) + 1
    degree_in_sign = longitude % 30
    
    # First half (0-15): Sun's hora (Leo)
    # Second half (15-30): Moon's hora (Cancer)
    # But varies based on odd/even sign
    
    hora_num = 0 if degree_in_sign < 15 else 1
    
    if rashi % 2 == 1:  # Odd sign
        d2_rashi = 5 if hora_num == 0 else 4  # Leo or Cancer
    else:  # Even sign
        d2_rashi = 4 if hora_num == 0 else 5  # Cancer or Leo
    
    return {
        "chart": "D2",
        "rashi": d2_rashi,
        "sign": SIGNS[d2_rashi - 1],
        "lord": RASHI_LORDS[d2_rashi],
        "hora": "Sun" if d2_rashi == 5 else "Moon",
    }


def get_d3_position(longitude: float) -> Dict[str, Any]:
    """D3 (Drekkana) - Divides each sign into 3 parts of 10°."""
    rashi = int(longitude / 30) + 1
    degree_in_sign = longitude % 30
    
    # Each drekkana = 10 degrees
    drekkana_num = int(degree_in_sign / 10)  # 0-2
    
    # 1st drekkana: same sign
    # 2nd drekkana: 5th sign from it
    # 3rd drekkana: 9th sign from it
    
    if drekkana_num == 0:
        d3_rashi = rashi
    elif drekkana_num == 1:
        d3_rashi = ((rashi - 1 + 4) % 12) + 1
    else:
        d3_rashi = ((rashi - 1 + 8) % 12) + 1
    
    return {
        "chart": "D3",
        "rashi": d3_rashi,
        "sign": SIGNS[d3_rashi - 1],
        "lord": RASHI_LORDS[d3_rashi],
        "drekkana_number": drekkana_num + 1,
    }


def get_d7_position(longitude: float) -> Dict[str, Any]:
    """D7 (Saptamsa) - Divides each sign into 7 parts."""
    rashi = int(longitude / 30) + 1
    degree_in_sign = longitude % 30
    
    # Each saptamsa = 30/7 = 4.2857... degrees
    saptamsa_num = int(degree_in_sign / (30 / 7))  # 0-6
    
    # Odd signs: start from same sign
    # Even signs: start from 7th sign
    if rashi % 2 == 1:
        start_sign = rashi
    else:
        start_sign = ((rashi - 1 + 6) % 12) + 1
    
    d7_rashi = ((start_sign - 1 + saptamsa_num) % 12) + 1
    
    return {
        "chart": "D7",
        "rashi": d7_rashi,
        "sign": SIGNS[d7_rashi - 1],
        "lord": RASHI_LORDS[d7_rashi],
        "saptamsa_number": saptamsa_num + 1,
    }


def get_d12_position(longitude: float) -> Dict[str, Any]:
    """D12 (Dwadasamsa) - Divides each sign into 12 parts of 2°30'."""
    rashi = int(longitude / 30) + 1
    degree_in_sign = longitude % 30
    
    # Each dwadasamsa = 2.5 degrees
    dwadasamsa_num = int(degree_in_sign / 2.5)  # 0-11
    
    # Start from the same sign
    d12_rashi = ((rashi - 1 + dwadasamsa_num) % 12) + 1
    
    return {
        "chart": "D12",
        "rashi": d12_rashi,
        "sign": SIGNS[d12_rashi - 1],
        "lord": RASHI_LORDS[d12_rashi],
        "dwadasamsa_number": dwadasamsa_num + 1,
    }


def calculate_divisional_charts(planets_list: List[Dict], ascendant_lon: float) -> Dict[str, Any]:
    """
    Calculate all major divisional charts for a birth chart.
    
    Args:
        planets_list: List of planet data with name, fullDegree
        ascendant_lon: Ascendant (Lagna) longitude
    
    Returns:
        Dictionary with all divisional chart positions
    """
    charts = {
        "D1": {"name": "Rashi", "purpose": "Physical body, general life"},
        "D2": {"name": "Hora", "purpose": "Wealth and prosperity"},
        "D3": {"name": "Drekkana", "purpose": "Siblings and courage"},
        "D7": {"name": "Saptamsa", "purpose": "Children and progeny"},
        "D9": {"name": "Navamsa", "purpose": "Marriage, spouse, dharma, soul purpose"},
        "D10": {"name": "Dasamsa", "purpose": "Career and profession"},
        "D12": {"name": "Dwadasamsa", "purpose": "Parents and ancestors"},
    }
    
    # Calculate for each chart
    for chart_key in charts:
        charts[chart_key]["positions"] = {}
    
    # Add ascendant to all charts
    asc_positions = {
        "D1": get_d1_position(ascendant_lon),
        "D2": get_d2_position(ascendant_lon),
        "D3": get_d3_position(ascendant_lon),
        "D7": get_d7_position(ascendant_lon),
        "D9": get_d9_position(ascendant_lon),
        "D10": get_d10_position(ascendant_lon),
        "D12": get_d12_position(ascendant_lon),
    }
    
    for chart_key, pos in asc_positions.items():
        charts[chart_key]["positions"]["Ascendant"] = pos
        charts[chart_key]["ascendant_sign"] = pos["sign"]
    
    # Calculate for each planet
    for planet in planets_list:
        name = planet.get("name", "")
        lon = planet.get("fullDegree", planet.get("full_degree", 0))
        
        if not name or lon is None:
            continue
        
        charts["D1"]["positions"][name] = get_d1_position(lon)
        charts["D2"]["positions"][name] = get_d2_position(lon)
        charts["D3"]["positions"][name] = get_d3_position(lon)
        charts["D7"]["positions"][name] = get_d7_position(lon)
        charts["D9"]["positions"][name] = get_d9_position(lon)
        charts["D10"]["positions"][name] = get_d10_position(lon)
        charts["D12"]["positions"][name] = get_d12_position(lon)
    
    return {
        "charts": charts,
        "available_charts": ["D1", "D2", "D3", "D7", "D9", "D10", "D12"],
        "primary_charts": ["D1", "D9", "D10"],
        "backend": "internal",
    }


def get_navamsa_chart(planets_list: List[Dict], ascendant_lon: float) -> Dict[str, Any]:
    """Get D9 (Navamsa) chart specifically."""
    charts = calculate_divisional_charts(planets_list, ascendant_lon)
    return {
        "chart": "D9",
        "name": "Navamsa",
        "purpose": "Marriage, spouse, dharma, soul purpose",
        "positions": charts["charts"]["D9"]["positions"],
        "ascendant_sign": charts["charts"]["D9"]["ascendant_sign"],
        "backend": "internal",
    }


def get_dasamsa_chart(planets_list: List[Dict], ascendant_lon: float) -> Dict[str, Any]:
    """Get D10 (Dasamsa) chart specifically."""
    charts = calculate_divisional_charts(planets_list, ascendant_lon)
    return {
        "chart": "D10",
        "name": "Dasamsa",
        "purpose": "Career and profession",
        "positions": charts["charts"]["D10"]["positions"],
        "ascendant_sign": charts["charts"]["D10"]["ascendant_sign"],
        "backend": "internal",
    }
