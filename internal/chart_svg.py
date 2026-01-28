"""
Vedic Birth Chart SVG Generator

Generates North Indian (diamond) and South Indian (square) chart visualizations.
"""

from typing import List, Dict, Optional
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ChartStyle(str, Enum):
    NORTH_INDIAN = "north_indian"
    SOUTH_INDIAN = "south_indian"


class ChartTheme(str, Enum):
    LIGHT = "light"
    DARK = "dark"


class ChartSize(str, Enum):
    SMALL = "small"    # 300px
    MEDIUM = "medium"  # 400px
    LARGE = "large"    # 600px


# Size mappings
SIZE_MAP = {
    ChartSize.SMALL: 300,
    ChartSize.MEDIUM: 400,
    ChartSize.LARGE: 600,
}

# Theme color schemes
THEMES = {
    ChartTheme.LIGHT: {
        "background": "#ffffff",
        "border": "#333333",
        "house_fill": "#f8f9fa",
        "text": "#1a1a1a",
        "planet": "#2563eb",
        "retro": "#dc2626",
        "house_number": "#6b7280",
    },
    ChartTheme.DARK: {
        "background": "#1a1a2e",
        "border": "#4a5568",
        "house_fill": "#16213e",
        "text": "#e2e8f0",
        "planet": "#60a5fa",
        "retro": "#f87171",
        "house_number": "#9ca3af",
    },
}

# Planet abbreviations for chart display
PLANET_ABBREV = {
    "Sun": "Su",
    "Moon": "Mo",
    "Mars": "Ma",
    "Mercury": "Me",
    "Jupiter": "Ju",
    "Venus": "Ve",
    "Saturn": "Sa",
    "Rahu": "Ra",
    "Ketu": "Ke",
}


def generate_chart_svg(
    planets: List[Dict],
    houses: List[Dict],
    ascendant: float,
    style: ChartStyle = ChartStyle.NORTH_INDIAN,
    theme: ChartTheme = ChartTheme.LIGHT,
    size: ChartSize = ChartSize.MEDIUM,
) -> str:
    """
    Generate SVG visualization of birth chart.
    
    Args:
        planets: List of planet dictionaries with house assignments
        houses: List of house dictionaries
        ascendant: Ascendant degree
        style: Chart style (north_indian or south_indian)
        theme: Color theme (light or dark)
        size: Chart size (small, medium, large)
        
    Returns:
        SVG string
    """
    if style == ChartStyle.NORTH_INDIAN:
        return _generate_north_indian_chart(planets, houses, ascendant, theme, size)
    else:
        return _generate_south_indian_chart(planets, houses, ascendant, theme, size)


def _generate_north_indian_chart(
    planets: List[Dict],
    houses: List[Dict],
    ascendant: float,
    theme: ChartTheme,
    size: ChartSize,
) -> str:
    """Generate North Indian diamond-style chart"""
    
    px = SIZE_MAP[size]
    colors = THEMES[theme]
    
    # Group planets by house
    planets_by_house = _group_planets_by_house(planets)
    
    # Calculate dimensions
    center = px / 2
    outer_size = px * 0.9
    inner_size = px * 0.45
    
    # Start SVG
    svg_parts = [
        f'<svg width="{px}" height="{px}" viewBox="0 0 {px} {px}" xmlns="http://www.w3.org/2000/svg">',
        f'  <style>',
        f'    .house-border {{ fill: {colors["house_fill"]}; stroke: {colors["border"]}; stroke-width: 1.5; }}',
        f'    .house-number {{ fill: {colors["house_number"]}; font-size: {px * 0.035}px; font-family: sans-serif; }}',
        f'    .planet {{ fill: {colors["planet"]}; font-size: {px * 0.04}px; font-family: sans-serif; font-weight: bold; }}',
        f'    .planet-retro {{ fill: {colors["retro"]}; }}',
        f'    .asc-marker {{ fill: {colors["text"]}; font-size: {px * 0.045}px; font-family: sans-serif; font-weight: bold; }}',
        f'  </style>',
        f'  <rect width="{px}" height="{px}" fill="{colors["background"]}"/>',
    ]
    
    # Draw outer diamond
    outer_points = [
        (center, px * 0.05),                    # Top
        (px * 0.95, center),                    # Right
        (center, px * 0.95),                    # Bottom
        (px * 0.05, center),                    # Left
    ]
    svg_parts.append(f'  <polygon class="house-border" points="{_points_to_string(outer_points)}"/>')
    
    # Draw inner diamond (center)
    inner_offset = px * 0.25
    inner_points = [
        (center, center - inner_offset),       # Top
        (center + inner_offset, center),       # Right
        (center, center + inner_offset),       # Bottom
        (center - inner_offset, center),       # Left
    ]
    svg_parts.append(f'  <polygon class="house-border" points="{_points_to_string(inner_points)}"/>')
    
    # Draw house dividers (lines from outer to inner diamond)
    # Top-left quadrant
    svg_parts.append(f'  <line x1="{outer_points[0][0]}" y1="{outer_points[0][1]}" x2="{inner_points[0][0]}" y2="{inner_points[0][1]}" stroke="{colors["border"]}" stroke-width="1.5"/>')
    svg_parts.append(f'  <line x1="{outer_points[1][0]}" y1="{outer_points[1][1]}" x2="{inner_points[1][0]}" y2="{inner_points[1][1]}" stroke="{colors["border"]}" stroke-width="1.5"/>')
    svg_parts.append(f'  <line x1="{outer_points[2][0]}" y1="{outer_points[2][1]}" x2="{inner_points[2][0]}" y2="{inner_points[2][1]}" stroke="{colors["border"]}" stroke-width="1.5"/>')
    svg_parts.append(f'  <line x1="{outer_points[3][0]}" y1="{outer_points[3][1]}" x2="{inner_points[3][0]}" y2="{inner_points[3][1]}" stroke="{colors["border"]}" stroke-width="1.5"/>')
    
    # Draw cross lines through center
    svg_parts.append(f'  <line x1="{center}" y1="{px * 0.05}" x2="{center}" y2="{px * 0.95}" stroke="{colors["border"]}" stroke-width="1"/>')
    svg_parts.append(f'  <line x1="{px * 0.05}" y1="{center}" x2="{px * 0.95}" y2="{center}" stroke="{colors["border"]}" stroke-width="1"/>')
    
    # House positions for North Indian chart (Ascendant always in top center)
    # Houses are numbered 1-12 starting from Ascendant position
    house_positions = _get_north_indian_house_positions(px, center)
    
    # Draw house numbers and planets
    for house_num in range(1, 13):
        pos = house_positions[house_num]
        
        # Draw house number (small, in corner)
        svg_parts.append(
            f'  <text x="{pos["number_x"]}" y="{pos["number_y"]}" class="house-number" text-anchor="middle">{house_num}</text>'
        )
        
        # Draw planets in this house
        house_planets = planets_by_house.get(house_num, [])
        for i, planet in enumerate(house_planets):
            planet_x = pos["planet_x"]
            planet_y = pos["planet_y"] + (i * px * 0.05)
            
            abbrev = PLANET_ABBREV.get(planet["name"], planet["name"][:2])
            retro_class = " planet-retro" if planet.get("isRetro", False) else ""
            retro_marker = "ᴿ" if planet.get("isRetro", False) else ""
            
            svg_parts.append(
                f'  <text x="{planet_x}" y="{planet_y}" class="planet{retro_class}" text-anchor="middle">{abbrev}{retro_marker}</text>'
            )
    
    # Add ASC marker in first house
    asc_pos = house_positions[1]
    svg_parts.append(
        f'  <text x="{asc_pos["asc_x"]}" y="{asc_pos["asc_y"]}" class="asc-marker" text-anchor="middle">ASC</text>'
    )
    
    svg_parts.append('</svg>')
    
    return '\n'.join(svg_parts)


def _generate_south_indian_chart(
    planets: List[Dict],
    houses: List[Dict],
    ascendant: float,
    theme: ChartTheme,
    size: ChartSize,
) -> str:
    """Generate South Indian square-style chart"""
    
    px = SIZE_MAP[size]
    colors = THEMES[theme]
    cell = px / 4
    
    # Group planets by house
    planets_by_house = _group_planets_by_house(planets)
    
    # South Indian fixed house positions (Aries always top-left of top row)
    # Grid positions: [row, col] for each sign
    sign_positions = {
        1: (0, 1),   # Aries
        2: (0, 0),   # Taurus
        3: (1, 0),   # Gemini
        4: (2, 0),   # Cancer
        5: (3, 0),   # Leo
        6: (3, 1),   # Virgo
        7: (3, 2),   # Libra
        8: (3, 3),   # Scorpio
        9: (2, 3),   # Sagittarius
        10: (1, 3),  # Capricorn
        11: (0, 3),  # Aquarius
        12: (0, 2),  # Pisces
    }
    
    # Determine which sign is the ascendant
    asc_sign = _degree_to_sign_number(ascendant)
    
    svg_parts = [
        f'<svg width="{px}" height="{px}" viewBox="0 0 {px} {px}" xmlns="http://www.w3.org/2000/svg">',
        f'  <style>',
        f'    .cell {{ fill: {colors["house_fill"]}; stroke: {colors["border"]}; stroke-width: 1.5; }}',
        f'    .center {{ fill: {colors["background"]}; stroke: {colors["border"]}; stroke-width: 1.5; }}',
        f'    .sign-name {{ fill: {colors["house_number"]}; font-size: {px * 0.03}px; font-family: sans-serif; }}',
        f'    .planet {{ fill: {colors["planet"]}; font-size: {px * 0.035}px; font-family: sans-serif; font-weight: bold; }}',
        f'    .planet-retro {{ fill: {colors["retro"]}; }}',
        f'    .asc-marker {{ fill: {colors["text"]}; font-size: {px * 0.04}px; font-family: sans-serif; font-weight: bold; }}',
        f'  </style>',
        f'  <rect width="{px}" height="{px}" fill="{colors["background"]}"/>',
    ]
    
    sign_names = ["Ari", "Tau", "Gem", "Can", "Leo", "Vir", "Lib", "Sco", "Sag", "Cap", "Aqu", "Pis"]
    
    # Draw 12 outer cells (4x4 grid without center 2x2)
    for sign_num in range(1, 13):
        row, col = sign_positions[sign_num]
        x = col * cell
        y = row * cell
        
        # Skip center cells (they form the center of the chart)
        if (row, col) in [(1, 1), (1, 2), (2, 1), (2, 2)]:
            continue
            
        svg_parts.append(f'  <rect x="{x}" y="{y}" width="{cell}" height="{cell}" class="cell"/>')
        
        # Sign name
        svg_parts.append(
            f'  <text x="{x + cell * 0.1}" y="{y + cell * 0.2}" class="sign-name">{sign_names[sign_num - 1]}</text>'
        )
        
        # Calculate house number from sign (relative to ascendant)
        house_num = ((sign_num - asc_sign) % 12) + 1
        
        # Mark ASC
        if house_num == 1:
            svg_parts.append(
                f'  <text x="{x + cell * 0.9}" y="{y + cell * 0.2}" class="asc-marker" text-anchor="end">ASC</text>'
            )
        
        # Draw planets
        house_planets = planets_by_house.get(house_num, [])
        for i, planet in enumerate(house_planets):
            planet_x = x + cell * 0.5
            planet_y = y + cell * 0.45 + (i * cell * 0.18)
            
            abbrev = PLANET_ABBREV.get(planet["name"], planet["name"][:2])
            retro_class = " planet-retro" if planet.get("isRetro", False) else ""
            retro_marker = "ᴿ" if planet.get("isRetro", False) else ""
            
            svg_parts.append(
                f'  <text x="{planet_x}" y="{planet_y}" class="planet{retro_class}" text-anchor="middle">{abbrev}{retro_marker}</text>'
            )
    
    # Draw center 2x2 area
    svg_parts.append(f'  <rect x="{cell}" y="{cell}" width="{cell * 2}" height="{cell * 2}" class="center"/>')
    svg_parts.append(f'  <text x="{px / 2}" y="{px / 2}" class="asc-marker" text-anchor="middle" dominant-baseline="middle">Birth Chart</text>')
    
    svg_parts.append('</svg>')
    
    return '\n'.join(svg_parts)


def _group_planets_by_house(planets: List[Dict]) -> Dict[int, List[Dict]]:
    """Group planets by their house number"""
    result = {}
    for planet in planets:
        house = planet.get("house", 1)
        if house not in result:
            result[house] = []
        result[house].append(planet)
    return result


def _points_to_string(points: List[tuple]) -> str:
    """Convert list of (x, y) tuples to SVG points string"""
    return " ".join(f"{x},{y}" for x, y in points)


def _degree_to_sign_number(degree: float) -> int:
    """Convert degree to sign number (1-12)"""
    return int(degree / 30) + 1


def _get_north_indian_house_positions(px: float, center: float) -> Dict[int, Dict[str, float]]:
    """
    Get positions for house numbers and planets in North Indian chart.
    Houses are positioned in the diamond layout.
    """
    # Approximate positions for each house in the diamond
    positions = {}
    
    # House 1 is at top center (Ascendant)
    offset = px * 0.15
    
    positions[1] = {
        "number_x": center, "number_y": px * 0.18,
        "planet_x": center, "planet_y": px * 0.25,
        "asc_x": center, "asc_y": px * 0.12
    }
    
    # House 2 - top right corner
    positions[2] = {
        "number_x": px * 0.75, "number_y": px * 0.18,
        "planet_x": px * 0.75, "planet_y": px * 0.25,
        "asc_x": px * 0.75, "asc_y": px * 0.12
    }
    
    # House 3 - right top
    positions[3] = {
        "number_x": px * 0.85, "number_y": px * 0.35,
        "planet_x": px * 0.78, "planet_y": px * 0.40,
        "asc_x": px * 0.85, "asc_y": px * 0.30
    }
    
    # House 4 - right center
    positions[4] = {
        "number_x": px * 0.82, "number_y": center,
        "planet_x": px * 0.75, "planet_y": center,
        "asc_x": px * 0.88, "asc_y": center
    }
    
    # House 5 - right bottom
    positions[5] = {
        "number_x": px * 0.85, "number_y": px * 0.65,
        "planet_x": px * 0.78, "planet_y": px * 0.60,
        "asc_x": px * 0.85, "asc_y": px * 0.70
    }
    
    # House 6 - bottom right corner
    positions[6] = {
        "number_x": px * 0.75, "number_y": px * 0.82,
        "planet_x": px * 0.75, "planet_y": px * 0.75,
        "asc_x": px * 0.75, "asc_y": px * 0.88
    }
    
    # House 7 - bottom center (opposite to Ascendant)
    positions[7] = {
        "number_x": center, "number_y": px * 0.82,
        "planet_x": center, "planet_y": px * 0.75,
        "asc_x": center, "asc_y": px * 0.88
    }
    
    # House 8 - bottom left corner
    positions[8] = {
        "number_x": px * 0.25, "number_y": px * 0.82,
        "planet_x": px * 0.25, "planet_y": px * 0.75,
        "asc_x": px * 0.25, "asc_y": px * 0.88
    }
    
    # House 9 - left bottom
    positions[9] = {
        "number_x": px * 0.15, "number_y": px * 0.65,
        "planet_x": px * 0.22, "planet_y": px * 0.60,
        "asc_x": px * 0.15, "asc_y": px * 0.70
    }
    
    # House 10 - left center
    positions[10] = {
        "number_x": px * 0.18, "number_y": center,
        "planet_x": px * 0.25, "planet_y": center,
        "asc_x": px * 0.12, "asc_y": center
    }
    
    # House 11 - left top
    positions[11] = {
        "number_x": px * 0.15, "number_y": px * 0.35,
        "planet_x": px * 0.22, "planet_y": px * 0.40,
        "asc_x": px * 0.15, "asc_y": px * 0.30
    }
    
    # House 12 - top left corner
    positions[12] = {
        "number_x": px * 0.25, "number_y": px * 0.18,
        "planet_x": px * 0.25, "planet_y": px * 0.25,
        "asc_x": px * 0.25, "asc_y": px * 0.12
    }
    
    return positions
