"""
AI Vision Module for Aetheria
Uses OpenRouter API to detect objects and materials in architectural renders
"""

import os
import base64
import json
import re
import requests
from typing import List, Dict, Optional

def encode_image_to_base64(image_bytes: bytes) -> str:
    """Convert image bytes to base64 string"""
    return base64.b64encode(image_bytes).decode('utf-8')

def analyze_image_with_ai(image_bytes: bytes, api_key: Optional[str] = None) -> Dict:
    """
    Analyze architectural render using OpenRouter's vision models.
    
    Args:
        image_bytes: Image data as bytes
        api_key: OpenRouter API key (defaults to env var)
    
    Returns:
        Dict with detected materials, objects, and suggestions
    """
    if not api_key:
        api_key = os.getenv('OPENROUTER_API_KEY')
    
    if not api_key:
        return {
            'error': 'No API key provided',
            'materials': [],
            'objects': []
        }
    
    try:
        # Encode image
        base64_image = encode_image_to_base64(image_bytes)
        
        # Prepare prompt for comprehensive architectural analysis
        prompt = """Analyze this architectural render image in detail and identify ALL visible materials and elements.

Please provide a comprehensive analysis including:
- Building facade materials (glass, metal panels, concrete, brick, etc.)
- Ground/road surfaces (asphalt, pavement, grass, etc.)
- Vegetation (trees, plants, landscaping)
- Sky and atmospheric elements
- Lighting conditions (sunlight, shadows, time of day)
- Any other visible materials or textures

For EACH material/element detected, provide:
1. A descriptive name (e.g., "Glass Curtain Wall", "Asphalt Road", "Green Vegetation")
2. Material type (glass/concrete/wood/metal/brick/plaster/asphalt/grass/vegetation/sky/stone)
3. Approximate position in the image (x: 0-100, y: 0-100 where 0,0 is top-left)
4. Dominant color as hex code (e.g., #87CEEB)

Return your response as a JSON array with this exact format:
[
  {
    "name": "Glass Facade",
    "type": "glass",
    "x": 50,
    "y": 40,
    "color": "#87CEEB"
  },
  {
    "name": "Asphalt Road",
    "type": "asphalt",
    "x": 50,
    "y": 85,
    "color": "#3C3C3C"
  }
]

Analyze thoroughly and include at least 5-10 different materials/elements."""

        # Call OpenRouter API
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "google/gemini-2.0-flash-exp:free",  # Free vision model
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ]
            },
            timeout=30
        )
        
        if response.status_code != 200:
            return {
                'error': f'API error: {response.status_code}',
                'materials': [],
                'objects': []
            }
        
        result = response.json()
        ai_response = result['choices'][0]['message']['content']
        
        # Parse AI response into structured data
        materials = parse_ai_response(ai_response)
        
        return {
            'success': True,
            'materials': materials,
            'raw_response': ai_response
        }
        
    except Exception as e:
        return {
            'error': str(e),
            'materials': [],
            'objects': []
        }

def parse_ai_response(response_text: str) -> List[Dict]:
    """
    Parse AI response text into structured material data.
    Handles both JSON array format and fallback text parsing.
    """
    materials = []
    
    try:
        # Try to extract JSON array from response
        json_match = re.search(r'\[[\s\S]*\]', response_text)
        if json_match:
            json_str = json_match.group(0)
            parsed_materials = json.loads(json_str)
            
            # Validate and normalize the parsed materials
            for mat in parsed_materials:
                if isinstance(mat, dict) and 'type' in mat:
                    materials.append({
                        'name': mat.get('name', 'Unknown Material'),
                        'type': mat.get('type', 'unknown').lower(),
                        'x': int(mat.get('x', 50)),
                        'y': int(mat.get('y', 50)),
                        'color': mat.get('color', '#808080')
                    })
            
            if materials:
                return materials
    except (json.JSONDecodeError, ValueError) as e:
        print(f"JSON parsing failed: {e}, falling back to text parsing")
    
    # Fallback: text-based parsing
    lines = response_text.split('\n')
    current_material = {}
    
    for line in lines:
        line = line.strip()
        if not line:
            if current_material and 'type' in current_material:
                materials.append(current_material)
                current_material = {}
            continue
        
        # Try to extract material type from common keywords
        line_lower = line.lower()
        if any(keyword in line_lower for keyword in ['glass', 'window', 'facade']):
            current_material['type'] = 'glass'
            current_material['name'] = line.split(':')[0] if ':' in line else 'Glass Element'
        elif any(keyword in line_lower for keyword in ['concrete', 'cement']):
            current_material['type'] = 'concrete'
            current_material['name'] = line.split(':')[0] if ':' in line else 'Concrete Element'
        elif any(keyword in line_lower for keyword in ['wood', 'timber']):
            current_material['type'] = 'wood'
            current_material['name'] = line.split(':')[0] if ':' in line else 'Wood Element'
        elif any(keyword in line_lower for keyword in ['metal', 'steel', 'aluminum']):
            current_material['type'] = 'metal'
            current_material['name'] = line.split(':')[0] if ':' in line else 'Metal Element'
        elif any(keyword in line_lower for keyword in ['brick', 'masonry']):
            current_material['type'] = 'brick'
            current_material['name'] = line.split(':')[0] if ':' in line else 'Brick Element'
        elif any(keyword in line_lower for keyword in ['grass', 'lawn', 'vegetation', 'tree', 'plant']):
            current_material['type'] = 'grass'
            current_material['name'] = line.split(':')[0] if ':' in line else 'Vegetation'
        elif any(keyword in line_lower for keyword in ['road', 'asphalt', 'pavement']):
            current_material['type'] = 'asphalt'
            current_material['name'] = line.split(':')[0] if ':' in line else 'Road Surface'
        elif 'sky' in line_lower:
            current_material['type'] = 'sky'
            current_material['name'] = 'Sky'
        
        # Set default position if not set
        if 'type' in current_material and 'x' not in current_material:
            current_material['x'] = 50
            current_material['y'] = 50
            current_material['color'] = '#808080'
    
    if current_material and 'type' in current_material:
        materials.append(current_material)
    
    return materials

def get_material_category(material_type: str) -> str:
    """Map AI-detected material type to our material database categories"""
    mapping = {
        'glass': 'glass_blue',
        'concrete': 'concrete_gray',
        'wood': 'wood_brown',
        'metal': 'metal_gray',
        'brick': 'brick_red',
        'plaster': 'plaster_white',
        'grass': 'grass_green',
        'vegetation': 'grass_green',
        'sky': 'sky_blue',
        'marble': 'marble_white',
        'stone': 'marble_white',
        'fabric': 'fabric_neutral',
        'asphalt': 'concrete_gray'
    }
    return mapping.get(material_type.lower(), 'concrete_gray')
