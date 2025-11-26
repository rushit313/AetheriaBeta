"""
AI Vision Module for Aetheria
Uses OpenRouter API to detect objects and materials in architectural renders
"""

import os
import base64
import requests
from typing import List, Dict, Optional
import io
from PIL import Image

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
        
        # Prepare prompt for architectural analysis
        prompt = """Analyze this architectural render image and identify:

1. **Materials visible** (e.g., glass, concrete, wood, metal, brick, plaster)
2. **Objects/Elements** (e.g., windows, doors, walls, floors, furniture, vegetation)
3. **Approximate positions** (top/middle/bottom, left/center/right)

For each material/object detected, provide:
- Name (e.g., "Glass Facade", "Concrete Wall")
- Type (glass/concrete/wood/metal/brick/plaster/fabric/stone/vegetation/sky)
- Position (as percentage: x: 0-100, y: 0-100 where 0,0 is top-left)
- Dominant color (hex code if possible)

Format your response as a structured list. Be specific about architectural materials."""

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
    
    This is a simple parser - you may want to make it more robust
    based on the actual response format from the AI.
    """
    materials = []
    
    # Simple parsing logic
    # Look for material mentions and try to extract structured data
    # This is a basic implementation - can be enhanced
    
    lines = response_text.split('\n')
    current_material = {}
    
    for line in lines:
        line = line.strip()
        if not line:
            if current_material:
                materials.append(current_material)
                current_material = {}
            continue
        
        # Try to extract material info
        # This is simplified - actual parsing depends on AI response format
        if 'glass' in line.lower():
            current_material['type'] = 'glass'
        elif 'concrete' in line.lower():
            current_material['type'] = 'concrete'
        elif 'wood' in line.lower():
            current_material['type'] = 'wood'
        elif 'metal' in line.lower():
            current_material['type'] = 'metal'
        elif 'brick' in line.lower():
            current_material['type'] = 'brick'
        
        # Extract name if present
        if ':' in line and 'name' in line.lower():
            current_material['name'] = line.split(':', 1)[1].strip()
    
    if current_material:
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
        'fabric': 'fabric_neutral'
    }
    return mapping.get(material_type.lower(), 'concrete_gray')
