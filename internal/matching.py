"""
Ashtakoot Kundli Matching Calculator

Calculates marriage compatibility using the 8-point (Ashtakoot) system:
1. Varna (1 point) - Spiritual/ego compatibility
2. Vashya (2 points) - Mutual attraction and control
3. Tara (3 points) - Health and longevity
4. Yoni (4 points) - Physical/sexual compatibility
5. Graha Maitri (5 points) - Mental compatibility
6. Gana (6 points) - Temperament match
7. Bhakoot (7 points) - Love and family harmony
8. Nadi (8 points) - Health of offspring

Total: 36 points
"""

from typing import Dict, Any, Tuple
import logging

logger = logging.getLogger(__name__)

# Nakshatra to number mapping (1-27)
NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira",
    "Ardra", "Punarvasu", "Pushya", "Ashlesha", "Magha",
    "Purva Phalguni", "Uttara Phalguni", "Hasta", "Chitra", "Swati",
    "Vishakha", "Anuradha", "Jyeshtha", "Mula", "Purva Ashadha",
    "Uttara Ashadha", "Shravana", "Dhanishtha", "Shatabhisha",
    "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
]

# Rashi (Zodiac sign) numbers
RASHIS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

# Varna (caste) of each nakshatra (Brahmin=1, Kshatriya=2, Vaishya=3, Shudra=4)
NAKSHATRA_VARNA = [
    2, 3, 1, 4, 4, 3, 1, 2, 4, 3,  # 1-10
    1, 2, 4, 3, 1, 2, 4, 3, 4, 1,  # 11-20
    2, 4, 3, 4, 1, 2, 3             # 21-27
]

# Rashi Varna
RASHI_VARNA = {
    "Cancer": 1, "Scorpio": 1, "Pisces": 1,        # Brahmin
    "Aries": 2, "Leo": 2, "Sagittarius": 2,        # Kshatriya
    "Taurus": 3, "Virgo": 3, "Capricorn": 3,       # Vaishya
    "Gemini": 4, "Libra": 4, "Aquarius": 4         # Shudra
}

# Vashya categories
VASHYA_CATEGORIES = {
    "Aries": "Chatushpada",
    "Taurus": "Chatushpada", 
    "Leo": "Vanachara",
    "Capricorn": "Chatushpada",
    "Sagittarius": "Chatushpada",  # First half human, second half Chatushpada
    "Cancer": "Keet",
    "Scorpio": "Keet",
    "Pisces": "Jalchar",
    "Gemini": "Manava",
    "Virgo": "Manava",
    "Libra": "Manava",
    "Aquarius": "Manava"
}

# Yoni (animal symbol) for each nakshatra
NAKSHATRA_YONI = [
    "Horse", "Elephant", "Sheep", "Snake", "Snake",     # 1-5
    "Dog", "Cat", "Sheep", "Cat", "Rat",                # 6-10
    "Rat", "Cow", "Buffalo", "Tiger", "Buffalo",        # 11-15
    "Tiger", "Deer", "Deer", "Dog", "Monkey",           # 16-20
    "Mongoose", "Monkey", "Lion", "Horse", "Lion",      # 21-25
    "Cow", "Elephant"                                    # 26-27
]

# Yoni compatibility (enemies get 0, friendly get 4)
YONI_ENEMIES = [
    ("Horse", "Buffalo"), ("Elephant", "Lion"), ("Sheep", "Monkey"),
    ("Snake", "Mongoose"), ("Dog", "Deer"), ("Cat", "Rat"),
    ("Tiger", "Cow")
]

# Gana (temperament)
NAKSHATRA_GANA = [
    "Deva", "Manushya", "Rakshasa", "Manushya", "Deva",     # 1-5
    "Manushya", "Deva", "Deva", "Rakshasa", "Rakshasa",     # 6-10
    "Manushya", "Manushya", "Deva", "Rakshasa", "Deva",     # 11-15
    "Rakshasa", "Deva", "Rakshasa", "Rakshasa", "Manushya", # 16-20
    "Manushya", "Deva", "Rakshasa", "Rakshasa", "Manushya", # 21-25
    "Manushya", "Deva"                                       # 26-27
]

# Nadi (pulse/health)
NAKSHATRA_NADI = [
    "Vata", "Pitta", "Kapha", "Kapha", "Pitta",     # 1-5
    "Vata", "Vata", "Pitta", "Kapha", "Kapha",     # 6-10
    "Pitta", "Vata", "Vata", "Pitta", "Kapha",     # 11-15
    "Kapha", "Pitta", "Vata", "Vata", "Pitta",     # 16-20
    "Kapha", "Kapha", "Pitta", "Vata", "Vata",     # 21-25
    "Pitta", "Kapha"                                # 26-27
]

# Rashi lords
RASHI_LORDS = {
    "Aries": "Mars", "Taurus": "Venus", "Gemini": "Mercury",
    "Cancer": "Moon", "Leo": "Sun", "Virgo": "Mercury",
    "Libra": "Venus", "Scorpio": "Mars", "Sagittarius": "Jupiter",
    "Capricorn": "Saturn", "Aquarius": "Saturn", "Pisces": "Jupiter"
}

# Planet friendships for Graha Maitri
PLANET_FRIENDS = {
    "Sun": ["Moon", "Mars", "Jupiter"],
    "Moon": ["Sun", "Mercury"],
    "Mars": ["Sun", "Moon", "Jupiter"],
    "Mercury": ["Sun", "Venus"],
    "Jupiter": ["Sun", "Moon", "Mars"],
    "Venus": ["Mercury", "Saturn"],
    "Saturn": ["Mercury", "Venus"]
}

PLANET_ENEMIES = {
    "Sun": ["Venus", "Saturn"],
    "Moon": [],
    "Mars": ["Mercury"],
    "Mercury": ["Moon"],
    "Jupiter": ["Mercury", "Venus"],
    "Venus": ["Sun", "Moon"],
    "Saturn": ["Sun", "Moon", "Mars"]
}


def get_nakshatra_from_moon(moon_longitude: float) -> Tuple[int, str]:
    """Get nakshatra number and name from Moon longitude."""
    nakshatra_span = 360 / 27
    nakshatra_num = int(moon_longitude / nakshatra_span)
    return nakshatra_num + 1, NAKSHATRAS[nakshatra_num]


def get_rashi_from_moon(moon_longitude: float) -> Tuple[int, str]:
    """Get rashi number and name from Moon longitude."""
    rashi_num = int(moon_longitude / 30)
    return rashi_num + 1, RASHIS[rashi_num]


def calculate_varna(bride_rashi: str, groom_rashi: str) -> Dict[str, Any]:
    """Calculate Varna (spiritual compatibility) - Max 1 point."""
    bride_varna = RASHI_VARNA.get(bride_rashi, 1)
    groom_varna = RASHI_VARNA.get(groom_rashi, 1)
    
    # Groom's varna should be equal or higher than bride's
    if groom_varna <= bride_varna:
        score = 1
        description = "Compatible varnas"
    else:
        score = 0
        description = "Varna mismatch"
    
    return {
        "name": "Varna",
        "max_score": 1,
        "score": score,
        "bride_value": bride_varna,
        "groom_value": groom_varna,
        "description": description
    }


def calculate_vashya(bride_rashi: str, groom_rashi: str) -> Dict[str, Any]:
    """Calculate Vashya (mutual attraction) - Max 2 points."""
    bride_vashya = VASHYA_CATEGORIES.get(bride_rashi, "Manava")
    groom_vashya = VASHYA_CATEGORIES.get(groom_rashi, "Manava")
    
    if bride_vashya == groom_vashya:
        score = 2
        description = "Same Vashya type - excellent mutual attraction"
    elif bride_rashi == groom_rashi:
        score = 2
        description = "Same rashi - good compatibility"
    else:
        # Partial compatibility
        score = 1
        description = "Partial Vashya compatibility"
    
    return {
        "name": "Vashya",
        "max_score": 2,
        "score": score,
        "bride_value": bride_vashya,
        "groom_value": groom_vashya,
        "description": description
    }


def calculate_tara(bride_nakshatra: int, groom_nakshatra: int) -> Dict[str, Any]:
    """Calculate Tara (health compatibility) - Max 3 points."""
    # Count from bride to groom
    diff1 = ((groom_nakshatra - bride_nakshatra) % 27) + 1
    tara1 = ((diff1 - 1) % 9) + 1
    
    # Count from groom to bride
    diff2 = ((bride_nakshatra - groom_nakshatra) % 27) + 1
    tara2 = ((diff2 - 1) % 9) + 1
    
    # Auspicious taras: 1, 2, 4, 6, 8, 9
    # Inauspicious: 3, 5, 7
    auspicious = {1, 2, 4, 6, 8, 9}
    
    score = 0
    if tara1 in auspicious:
        score += 1.5
    if tara2 in auspicious:
        score += 1.5
    
    return {
        "name": "Tara",
        "max_score": 3,
        "score": score,
        "bride_tara": tara1,
        "groom_tara": tara2,
        "description": f"Tara positions: {tara1}, {tara2}"
    }


def calculate_yoni(bride_nakshatra: int, groom_nakshatra: int) -> Dict[str, Any]:
    """Calculate Yoni (physical compatibility) - Max 4 points."""
    bride_yoni = NAKSHATRA_YONI[bride_nakshatra - 1]
    groom_yoni = NAKSHATRA_YONI[groom_nakshatra - 1]
    
    if bride_yoni == groom_yoni:
        score = 4
        description = "Same Yoni - excellent compatibility"
    else:
        # Check if enemies
        is_enemy = False
        for pair in YONI_ENEMIES:
            if (bride_yoni in pair and groom_yoni in pair):
                is_enemy = True
                break
        
        if is_enemy:
            score = 0
            description = f"Enemy Yonis ({bride_yoni} vs {groom_yoni})"
        else:
            score = 2
            description = f"Neutral Yonis ({bride_yoni}, {groom_yoni})"
    
    return {
        "name": "Yoni",
        "max_score": 4,
        "score": score,
        "bride_value": bride_yoni,
        "groom_value": groom_yoni,
        "description": description
    }


def calculate_graha_maitri(bride_rashi: str, groom_rashi: str) -> Dict[str, Any]:
    """Calculate Graha Maitri (mental compatibility) - Max 5 points."""
    bride_lord = RASHI_LORDS.get(bride_rashi, "Sun")
    groom_lord = RASHI_LORDS.get(groom_rashi, "Sun")
    
    if bride_lord == groom_lord:
        score = 5
        description = "Same lord - excellent mental harmony"
    elif groom_lord in PLANET_FRIENDS.get(bride_lord, []) and bride_lord in PLANET_FRIENDS.get(groom_lord, []):
        score = 5
        description = "Mutual friends - very good harmony"
    elif groom_lord in PLANET_FRIENDS.get(bride_lord, []) or bride_lord in PLANET_FRIENDS.get(groom_lord, []):
        score = 4
        description = "One-sided friendship - good harmony"
    elif groom_lord in PLANET_ENEMIES.get(bride_lord, []) and bride_lord in PLANET_ENEMIES.get(groom_lord, []):
        score = 0
        description = "Mutual enemies - challenging relationship"
    elif groom_lord in PLANET_ENEMIES.get(bride_lord, []) or bride_lord in PLANET_ENEMIES.get(groom_lord, []):
        score = 1
        description = "One-sided enmity - some challenges"
    else:
        score = 2.5
        description = "Neutral relationship"
    
    return {
        "name": "Graha Maitri",
        "max_score": 5,
        "score": score,
        "bride_lord": bride_lord,
        "groom_lord": groom_lord,
        "description": description
    }


def calculate_gana(bride_nakshatra: int, groom_nakshatra: int) -> Dict[str, Any]:
    """Calculate Gana (temperament) - Max 6 points."""
    bride_gana = NAKSHATRA_GANA[bride_nakshatra - 1]
    groom_gana = NAKSHATRA_GANA[groom_nakshatra - 1]
    
    if bride_gana == groom_gana:
        score = 6
        description = f"Same Gana ({bride_gana}) - excellent match"
    elif bride_gana == "Deva" and groom_gana == "Manushya":
        score = 5
        description = "Deva-Manushya - good compatibility"
    elif bride_gana == "Manushya" and groom_gana == "Deva":
        score = 5
        description = "Manushya-Deva - good compatibility"
    elif "Rakshasa" in [bride_gana, groom_gana] and bride_gana != groom_gana:
        score = 0
        description = f"Rakshasa with non-Rakshasa - not recommended"
    else:
        score = 3
        description = f"Partial Gana match ({bride_gana}, {groom_gana})"
    
    return {
        "name": "Gana",
        "max_score": 6,
        "score": score,
        "bride_value": bride_gana,
        "groom_value": groom_gana,
        "description": description
    }


def calculate_bhakoot(bride_rashi_num: int, groom_rashi_num: int) -> Dict[str, Any]:
    """Calculate Bhakoot (love/family harmony) - Max 7 points."""
    # Position from bride to groom
    diff = ((groom_rashi_num - bride_rashi_num) % 12) + 1
    
    # Inauspicious combinations: 2-12, 5-9, 6-8
    inauspicious = [(2, 12), (5, 9), (6, 8)]
    
    is_inauspicious = False
    for pair in inauspicious:
        if diff in pair:
            reverse_diff = ((bride_rashi_num - groom_rashi_num) % 12) + 1
            if reverse_diff in pair:
                is_inauspicious = True
                break
    
    if is_inauspicious:
        score = 0
        description = f"Bhakoot Dosha present (position {diff})"
    else:
        score = 7
        description = "No Bhakoot Dosha - harmonious"
    
    return {
        "name": "Bhakoot",
        "max_score": 7,
        "score": score,
        "position": diff,
        "description": description
    }


def calculate_nadi(bride_nakshatra: int, groom_nakshatra: int) -> Dict[str, Any]:
    """Calculate Nadi (health of offspring) - Max 8 points."""
    bride_nadi = NAKSHATRA_NADI[bride_nakshatra - 1]
    groom_nadi = NAKSHATRA_NADI[groom_nakshatra - 1]
    
    if bride_nadi == groom_nadi:
        score = 0
        description = f"Same Nadi ({bride_nadi}) - Nadi Dosha present"
    else:
        score = 8
        description = "Different Nadis - excellent for progeny"
    
    return {
        "name": "Nadi",
        "max_score": 8,
        "score": score,
        "bride_value": bride_nadi,
        "groom_value": groom_nadi,
        "description": description
    }


def calculate_compatibility(
    bride_moon_longitude: float,
    groom_moon_longitude: float,
    bride_name: str = "Bride",
    groom_name: str = "Groom"
) -> Dict[str, Any]:
    """
    Calculate complete Ashtakoot compatibility.
    
    Args:
        bride_moon_longitude: Bride's Moon sidereal longitude (0-360)
        groom_moon_longitude: Groom's Moon sidereal longitude (0-360)
        bride_name: Name of bride
        groom_name: Name of groom
    
    Returns:
        Complete compatibility report with all 8 koots
    """
    # Get nakshatra and rashi for both
    bride_nakshatra_num, bride_nakshatra = get_nakshatra_from_moon(bride_moon_longitude)
    groom_nakshatra_num, groom_nakshatra = get_nakshatra_from_moon(groom_moon_longitude)
    
    bride_rashi_num, bride_rashi = get_rashi_from_moon(bride_moon_longitude)
    groom_rashi_num, groom_rashi = get_rashi_from_moon(groom_moon_longitude)
    
    # Calculate all 8 koots
    koots = [
        calculate_varna(bride_rashi, groom_rashi),
        calculate_vashya(bride_rashi, groom_rashi),
        calculate_tara(bride_nakshatra_num, groom_nakshatra_num),
        calculate_yoni(bride_nakshatra_num, groom_nakshatra_num),
        calculate_graha_maitri(bride_rashi, groom_rashi),
        calculate_gana(bride_nakshatra_num, groom_nakshatra_num),
        calculate_bhakoot(bride_rashi_num, groom_rashi_num),
        calculate_nadi(bride_nakshatra_num, groom_nakshatra_num),
    ]
    
    # Calculate totals
    total_score = sum(k["score"] for k in koots)
    max_score = 36
    percentage = round((total_score / max_score) * 100, 1)
    
    # Determine verdict
    if total_score >= 25:
        verdict = "Excellent Match"
        recommendation = "Highly recommended for marriage"
    elif total_score >= 18:
        verdict = "Good Match"
        recommendation = "Recommended with minor considerations"
    elif total_score >= 12:
        verdict = "Average Match"
        recommendation = "Can proceed with remedies"
    else:
        verdict = "Below Average Match"
        recommendation = "Careful consideration advised"
    
    return {
        "bride": {
            "name": bride_name,
            "nakshatra": bride_nakshatra,
            "nakshatra_number": bride_nakshatra_num,
            "rashi": bride_rashi,
            "rashi_number": bride_rashi_num,
            "moon_longitude": round(bride_moon_longitude, 4),
        },
        "groom": {
            "name": groom_name,
            "nakshatra": groom_nakshatra,
            "nakshatra_number": groom_nakshatra_num,
            "rashi": groom_rashi,
            "rashi_number": groom_rashi_num,
            "moon_longitude": round(groom_moon_longitude, 4),
        },
        "koots": koots,
        "total_score": total_score,
        "max_score": max_score,
        "percentage": percentage,
        "verdict": verdict,
        "recommendation": recommendation,
        "backend": "internal",
    }
