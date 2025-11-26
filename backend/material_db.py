"""
Material Database for Aetheria
Maps colors and material types to Poly Haven textures
"""

import colorsys
from typing import List, Dict, Tuple

def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    """Convert hex color to RGB tuple"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hsv(rgb: Tuple[int, int, int]) -> Tuple[float, float, float]:
    """Convert RGB to HSV"""
    r, g, b = [x / 255.0 for x in rgb]
    return colorsys.rgb_to_hsv(r, g, b)

def color_distance(color1: str, color2: str) -> float:
    """Calculate perceptual distance between two hex colors"""
    rgb1 = hex_to_rgb(color1)
    rgb2 = hex_to_rgb(color2)
    
    # Weighted Euclidean distance (perceptual)
    r_mean = (rgb1[0] + rgb2[0]) / 2
    r_diff = rgb1[0] - rgb2[0]
    g_diff = rgb1[1] - rgb2[1]
    b_diff = rgb1[2] - rgb2[2]
    
    weight_r = 2 + r_mean / 256
    weight_g = 4.0
    weight_b = 2 + (255 - r_mean) / 256
    
    return ((weight_r * r_diff * r_diff) + 
            (weight_g * g_diff * g_diff) + 
            (weight_b * b_diff * b_diff)) ** 0.5

# Material categories with representative colors and Poly Haven textures
MATERIAL_DATABASE = {
    'glass_blue': {
        'keywords': ['glass', 'window', 'facade'],
        'colors': ['#87CEEB', '#4682B4', '#5F9EA0', '#B0E0E6'],
        'textures': [
            {
                'name': 'Blue Glass Facade',
                'texture_url': 'https://dl.polyhaven.com/file/ph-assets/Textures/jpg/2k/glass_window/glass_window_diff_2k.jpg',
                'suggestion': 'Reflective Glass',
                'suggestion_url': 'https://dl.polyhaven.com/file/ph-assets/Textures/jpg/2k/glass_window/glass_window_diff_2k.jpg',
                'link': 'https://polyhaven.com/textures/glass'
            }
        ]
    },
    'concrete_gray': {
        'keywords': ['concrete', 'wall', 'building'],
        'colors': ['#808080', '#A9A9A9', '#696969', '#BEBEBE'],
        'textures': [
            {
                'name': 'Concrete Wall',
                'texture_url': 'https://dl.polyhaven.com/file/ph-assets/Textures/jpg/2k/concrete_wall_006/concrete_wall_006_diff_2k.jpg',
                'suggestion': 'Smooth Concrete',
                'suggestion_url': 'https://dl.polyhaven.com/file/ph-assets/Textures/jpg/2k/concrete_floor_02/concrete_floor_02_diff_2k.jpg',
                'link': 'https://polyhaven.com/a/concrete_floor_02'
            }
        ]
    },
    'metal_gray': {
        'keywords': ['metal', 'steel', 'aluminum'],
        'colors': ['#C0C0C0', '#B8B8B8', '#D3D3D3'],
        'textures': [
            {
                'name': 'Brushed Metal',
                'texture_url': 'https://dl.polyhaven.com/file/ph-assets/Textures/jpg/2k/metal_plate/metal_plate_diff_2k.jpg',
                'suggestion': 'Aluminum Panel',
                'suggestion_url': 'https://dl.polyhaven.com/file/ph-assets/Textures/jpg/2k/metal_plate/metal_plate_diff_2k.jpg',
                'link': 'https://polyhaven.com/a/metal_plate'
            }
        ]
    },
    'wood_brown': {
        'keywords': ['wood', 'timber', 'floor'],
        'colors': ['#8B4513', '#A0522D', '#D2691E', '#CD853F'],
        'textures': [
            {
                'name': 'Wood Planks',
                'texture_url': 'https://dl.polyhaven.com/file/ph-assets/Textures/jpg/2k/wood_floor_deck/wood_floor_deck_diff_2k.jpg',
                'suggestion': 'Walnut Veneer',
                'suggestion_url': 'https://dl.polyhaven.com/file/ph-assets/Textures/jpg/2k/walnut_veneer/walnut_veneer_diff_2k.jpg',
                'link': 'https://polyhaven.com/a/walnut_veneer'
            }
        ]
    },
    'brick_red': {
        'keywords': ['brick', 'masonry'],
        'colors': ['#B22222', '#8B0000', '#A52A2A', '#CD5C5C'],
        'textures': [
            {
                'name': 'Red Brick',
                'texture_url': 'https://dl.polyhaven.com/file/ph-assets/Textures/jpg/2k/brick_wall_001/brick_wall_001_diff_2k.jpg',
                'suggestion': 'Weathered Brick',
                'suggestion_url': 'https://dl.polyhaven.com/file/ph-assets/Textures/jpg/2k/brick_wall_001/brick_wall_001_diff_2k.jpg',
                'link': 'https://polyhaven.com/a/brick_wall_001'
            }
        ]
    },
    'plaster_white': {
        'keywords': ['plaster', 'wall', 'ceiling'],
        'colors': ['#FFFFFF', '#F5F5F5', '#FFFAFA', '#F0F0F0'],
        'textures': [
            {
                'name': 'White Plaster',
                'texture_url': 'https://dl.polyhaven.com/file/ph-assets/Textures/jpg/2k/plaster_02/plaster_02_diff_2k.jpg',
                'suggestion': 'Rough Plaster',
                'suggestion_url': 'https://dl.polyhaven.com/file/ph-assets/Textures/jpg/2k/white_rough_plaster/white_rough_plaster_diff_2k.jpg',
                'link': 'https://polyhaven.com/a/white_rough_plaster'
            }
        ]
    },
    'grass_green': {
        'keywords': ['grass', 'lawn', 'vegetation'],
        'colors': ['#228B22', '#32CD32', '#00FF00', '#7CFC00'],
        'textures': [
            {
                'name': 'Grass Ground',
                'texture_url': 'https://dl.polyhaven.com/file/ph-assets/Textures/jpg/2k/grass_001/grass_001_diff_2k.jpg',
                'suggestion': 'Natural Grass',
                'suggestion_url': 'https://dl.polyhaven.com/file/ph-assets/Textures/jpg/2k/grass_001/grass_001_diff_2k.jpg',
                'link': 'https://polyhaven.com/a/grass_001'
            }
        ]
    },
    'sky_blue': {
        'keywords': ['sky', 'atmosphere'],
        'colors': ['#87CEEB', '#00BFFF', '#1E90FF', '#6495ED'],
        'textures': []  # Sky doesn't need texture suggestions
    },
    'marble_white': {
        'keywords': ['marble', 'stone'],
        'colors': ['#F8F8FF', '#FFFAF0', '#FAF0E6'],
        'textures': [
            {
                'name': 'White Marble',
                'texture_url': 'https://dl.polyhaven.com/file/ph-assets/Textures/jpg/2k/marble_01/marble_01_diff_2k.jpg',
                'suggestion': 'Carrara Marble',
                'suggestion_url': 'https://dl.polyhaven.com/file/ph-assets/Textures/jpg/2k/marble_01/marble_01_diff_2k.jpg',
                'link': 'https://polyhaven.com/a/marble_01'
            }
        ]
    },
    'fabric_neutral': {
        'keywords': ['fabric', 'textile', 'upholstery'],
        'colors': ['#F5F5DC', '#FAEBD7', '#FFE4C4', '#DEB887'],
        'textures': [
            {
                'name': 'Fabric Texture',
                'texture_url': 'https://dl.polyhaven.com/file/ph-assets/Textures/jpg/2k/fabric_pattern_07/fabric_pattern_07_col_1_2k.jpg',
                'suggestion': 'Woven Fabric',
                'suggestion_url': 'https://dl.polyhaven.com/file/ph-assets/Textures/jpg/2k/fabric_pattern_05/fabric_pattern_05_col_01_2k.jpg',
                'link': 'https://polyhaven.com/a/fabric_pattern_05'
            }
        ]
    }
}

def find_best_material_match(hex_color: str, position_y: float = 0.5) -> Dict:
    """
    Find the best matching material based on color and vertical position.
    
    Args:
        hex_color: Hex color code (e.g., '#87CEEB')
        position_y: Vertical position in image (0=top, 1=bottom)
    
    Returns:
        Dictionary with material info and texture suggestion
    """
    best_match = None
    best_distance = float('inf')
    best_category = None
    
    # Position-based hints
    # Top of image (sky, ceiling): y < 0.3
    # Middle (walls, facades): 0.3 <= y <= 0.7
    # Bottom (floor, ground): y > 0.7
    
    for category, data in MATERIAL_DATABASE.items():
        for ref_color in data['colors']:
            distance = color_distance(hex_color, ref_color)
            
            # Apply position bias
            if position_y < 0.3 and category in ['sky_blue', 'plaster_white']:
                distance *= 0.7  # Favor sky/ceiling at top
            elif position_y > 0.7 and category in ['grass_green', 'wood_brown', 'concrete_gray']:
                distance *= 0.7  # Favor ground materials at bottom
            elif 0.3 <= position_y <= 0.7 and category in ['glass_blue', 'concrete_gray', 'brick_red']:
                distance *= 0.8  # Favor wall materials in middle
            
            if distance < best_distance:
                best_distance = distance
                best_category = category
                best_match = data
    
    if best_match and best_match['textures']:
        texture = best_match['textures'][0].copy()
        texture['hex'] = hex_color
        texture['category'] = best_category
        return texture
    
    # Fallback for colors without specific textures (like sky)
    return {
        'name': best_category.replace('_', ' ').title() if best_category else 'Unknown Material',
        'hex': hex_color,
        'category': best_category or 'unknown'
    }

def generate_texture_suggestions(palette: List[Dict], image_width: int = 1000, image_height: int = 1000) -> List[Dict]:
    """
    Generate texture suggestions based on color palette.
    
    Args:
        palette: List of color dicts with 'hex' keys
        image_width: Image width for position calculation
        image_height: Image height for position calculation
    
    Returns:
        List of texture suggestion dicts with positions
    """
    suggestions = []
    
    # Distribute palette colors across image regions
    num_colors = len(palette)
    if num_colors == 0:
        return suggestions
    
    for i, color_data in enumerate(palette[:6]):  # Limit to top 6 colors
        hex_color = color_data.get('hex', '#808080')
        
        # Distribute positions intelligently
        # First color: top-left (sky/ceiling)
        # Second color: middle-left (walls)
        # Third color: bottom-left (floor)
        # Etc.
        
        if i == 0:
            x, y = 30, 20  # Top area
        elif i == 1:
            x, y = 50, 50  # Middle
        elif i == 2:
            x, y = 30, 75  # Bottom
        elif i == 3:
            x, y = 70, 30  # Top-right
        elif i == 4:
            x, y = 70, 60  # Middle-right
        else:
            x, y = 50, 80  # Bottom-center
        
        # Find matching material
        material = find_best_material_match(hex_color, y / 100.0)
        
        if material:
            material['x'] = x
            material['y'] = y
            suggestions.append(material)
    
    return suggestions
