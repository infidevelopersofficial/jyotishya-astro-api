"""
Horoscope Guidance Text Templates

Rule-based templates for generating horoscope guidance.
Uses planetary transits and aspects to construct meaningful predictions.
"""

from typing import Dict, Any, List
import random

# Seed for consistent daily randomness
def _daily_random(date_str: str, salt: str) -> random.Random:
    """Create a seeded random for consistent daily variation"""
    seed = hash(f"{date_str}:{salt}") % (2**32)
    return random.Random(seed)


# ==============================================================================
# OVERALL GUIDANCE
# ==============================================================================

OVERALL_POSITIVE = [
    "The cosmic energies favor your endeavors today. Trust your instincts and move forward with confidence.",
    "A harmonious day awaits you. The planets align to support your goals and aspirations.",
    "Today brings opportunities for growth and positive change. Embrace new possibilities.",
    "The stars shine favorably upon you. This is an excellent time for important decisions.",
    "Celestial blessings enhance your day. Your efforts are likely to bear fruit.",
]

OVERALL_NEUTRAL = [
    "A balanced day of opportunities and challenges. Navigate with patience and awareness.",
    "Mixed energies surround you today. Focus on what matters most and let go of distractions.",
    "The cosmic tide is calm. Use this time for reflection and planning your next steps.",
    "Neither particularly challenging nor especially favorable, today is what you make of it.",
    "Steady yourself as the planets maintain equilibrium. Consistency is your ally today.",
]

OVERALL_CHALLENGING = [
    "Today requires extra patience and resilience. Challenges are opportunities for growth.",
    "The planetary alignments suggest a need for caution. Think twice before acting.",
    "Cosmic tensions may create obstacles. Stay grounded and trust the process.",
    "A day for careful navigation. What seems like a setback may reveal hidden blessings.",
    "The stars urge patience and perseverance. This too shall pass.",
]


def get_overall_guidance(transits: Dict, sign: str) -> str:
    """Generate overall daily guidance based on transits"""
    
    # Calculate overall sentiment from aspects
    positive_count = sum(1 for t in transits.values() if t.get("aspect") in ["trine", "sextile"])
    negative_count = sum(1 for t in transits.values() if t.get("aspect") in ["square", "opposition"])
    
    if positive_count > negative_count + 1:
        templates = OVERALL_POSITIVE
    elif negative_count > positive_count + 1:
        templates = OVERALL_CHALLENGING
    else:
        templates = OVERALL_NEUTRAL
    
    # Pick based on Sun position for daily variation
    sun_transit = transits.get("Sun", {})
    idx = int(sun_transit.get("degree", 0)) % len(templates)
    
    return templates[idx]


# ==============================================================================
# CAREER GUIDANCE
# ==============================================================================

CAREER_TEMPLATES = {
    "positive": [
        "Professional opportunities abound. Your hard work is being recognized by those who matter.",
        "Career matters flow smoothly today. Consider initiating new projects or discussions.",
        "Leadership energies are strong. Step up and take charge of important matters.",
        "Financial prospects look promising. A good day for business negotiations.",
        "Your expertise shines today. Colleagues and superiors take notice of your contributions.",
    ],
    "neutral": [
        "Maintain your current course at work. Consistency builds long-term success.",
        "Focus on completing existing tasks rather than starting new ventures.",
        "Career energies are stable. A good day for planning and organizing.",
        "Professional matters require steady effort. Avoid major changes for now.",
        "Work within established structures today. Innovation can wait for a better time.",
    ],
    "challenging": [
        "Workplace dynamics may feel tense. Choose your words carefully in professional settings.",
        "Financial decisions need extra scrutiny today. Delay major investments if possible.",
        "Career progress may feel slow. Remember that patience is a virtue.",
        "Avoid confrontations with authority figures. Diplomacy serves you better than defiance.",
        "Workplace challenges are temporary. Focus on what you can control.",
    ],
}


def get_career_guidance(transits: Dict, sign: str) -> str:
    """Generate career guidance based on key planetary transits"""
    
    # Key career planets and their aspects
    sun_aspect = transits.get("Sun", {}).get("aspect", "neutral")
    saturn_aspect = transits.get("Saturn", {}).get("aspect", "neutral")
    jupiter_aspect = transits.get("Jupiter", {}).get("aspect", "neutral")
    
    # Determine sentiment
    positive_aspects = ["trine", "sextile", "conjunction"]
    negative_aspects = ["square", "opposition"]
    
    positive_score = sum(1 for a in [sun_aspect, saturn_aspect, jupiter_aspect] if a in positive_aspects)
    negative_score = sum(1 for a in [sun_aspect, saturn_aspect, jupiter_aspect] if a in negative_aspects)
    
    if positive_score > negative_score:
        category = "positive"
    elif negative_score > positive_score:
        category = "challenging"
    else:
        category = "neutral"
    
    templates = CAREER_TEMPLATES[category]
    idx = int(transits.get("Mercury", {}).get("degree", 0)) % len(templates)
    
    return templates[idx]


# ==============================================================================
# RELATIONSHIP GUIDANCE
# ==============================================================================

RELATIONSHIP_TEMPLATES = {
    "positive": [
        "Love and harmony fill your connections today. Express your feelings openly.",
        "Romantic energies are heightened. Single signs may find interesting encounters.",
        "Existing relationships deepen. It's a beautiful day for quality time together.",
        "Social connections flourish. Networking leads to meaningful relationships.",
        "Venus blesses your interactions. Beauty and grace enhance all communications.",
    ],
    "neutral": [
        "Relationship energies are calm. Enjoy the peace and stability in your connections.",
        "Neither highs nor lows in matters of the heart. Appreciate what you have.",
        "Focus on maintaining existing bonds rather than seeking new connections.",
        "Communication in relationships requires extra clarity today.",
        "Relationship matters call for patience and understanding.",
    ],
    "challenging": [
        "Be mindful of miscommunications in relationships. Listen more than you speak.",
        "Romantic matters may feel complicated. Give each other space when needed.",
        "Avoid making important relationship decisions under today's challenging aspects.",
        "Tensions in partnerships need gentle handling. Compassion heals all wounds.",
        "Past relationship patterns may resurface. Use this as an opportunity for healing.",
    ],
}


def get_relationship_guidance(transits: Dict, sign: str) -> str:
    """Generate relationship guidance based on Venus and Moon transits"""
    
    venus_aspect = transits.get("Venus", {}).get("aspect", "neutral")
    moon_aspect = transits.get("Moon", {}).get("aspect", "neutral")
    mars_aspect = transits.get("Mars", {}).get("aspect", "neutral")
    
    positive_aspects = ["trine", "sextile"]
    negative_aspects = ["square", "opposition"]
    
    # Venus and Moon are more important for relationships
    positive_score = 0
    negative_score = 0
    
    if venus_aspect in positive_aspects:
        positive_score += 2
    if moon_aspect in positive_aspects:
        positive_score += 1
    if venus_aspect in negative_aspects:
        negative_score += 2
    if moon_aspect in negative_aspects:
        negative_score += 1
    if mars_aspect in negative_aspects:
        negative_score += 1
    
    if positive_score > negative_score:
        category = "positive"
    elif negative_score > positive_score:
        category = "challenging"
    else:
        category = "neutral"
    
    templates = RELATIONSHIP_TEMPLATES[category]
    idx = int(transits.get("Venus", {}).get("degree", 0)) % len(templates)
    
    return templates[idx]


# ==============================================================================
# HEALTH GUIDANCE
# ==============================================================================

HEALTH_TEMPLATES = {
    "positive": [
        "Vitality and energy are high. Perfect day for exercise and physical activities.",
        "Your body and mind are in harmony. Listen to what brings you joy.",
        "Health energies support healing and recovery. Trust your body's wisdom.",
        "Physical pursuits are favored. Challenge yourself with new fitness goals.",
        "Solar vitality enhances your well-being. Spend time outdoors if possible.",
    ],
    "neutral": [
        "Maintain your regular health routines. Consistency is key to well-being.",
        "Neither particularly energetic nor lethargic. Honor your body's needs.",
        "A good day for rest and recuperation. Don't push yourself too hard.",
        "Focus on mental health today. Meditation and reflection bring balance.",
        "Health matters require a steady approach. No extremes in diet or exercise.",
    ],
    "challenging": [
        "Take extra care of your physical health today. Rest when needed.",
        "Avoid overexertion. Your body may need more recovery time than usual.",
        "Stress management is crucial today. Practice calming techniques.",
        "Be mindful of what you consume. Your body is more sensitive than usual.",
        "Health challenges are temporary. Focus on self-care and gentle movement.",
    ],
}


def get_health_guidance(transits: Dict, sign: str) -> str:
    """Generate health guidance based on Mars and Sun transits"""
    
    mars_aspect = transits.get("Mars", {}).get("aspect", "neutral")
    sun_aspect = transits.get("Sun", {}).get("aspect", "neutral")
    saturn_aspect = transits.get("Saturn", {}).get("aspect", "neutral")
    
    positive_aspects = ["trine", "sextile"]
    negative_aspects = ["square", "opposition"]
    
    # Mars and Sun are key for vitality
    positive_score = 0
    negative_score = 0
    
    if mars_aspect in positive_aspects:
        positive_score += 1
    if sun_aspect in positive_aspects:
        positive_score += 1
    if mars_aspect in negative_aspects:
        negative_score += 1
    if sun_aspect in negative_aspects:
        negative_score += 1
    if saturn_aspect in negative_aspects:
        negative_score += 1  # Saturn squares/oppositions drain energy
    
    if positive_score > negative_score:
        category = "positive"
    elif negative_score > positive_score:
        category = "challenging"
    else:
        category = "neutral"
    
    templates = HEALTH_TEMPLATES[category]
    idx = int(transits.get("Mars", {}).get("degree", 0)) % len(templates)
    
    return templates[idx]
