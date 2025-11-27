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
            'error': 'No API key provided. Set OPENROUTER_API_KEY in environment variables.',
            'materials': [],
            'objects': []
        }
    
    try:
        # Encode image
        base64_image = encode_image_to_base64(image_bytes)
        
        # Prepare prompt for comprehensive architectural analysis
        prompt = """Analyze this architectural render image in detail. Act as an expert architectural visualizer and critic.

Please provide a comprehensive analysis including:
1.  **Materials**: Identify all visible materials (facade, ground, vegetation, etc.).
2.  **Critique**: Provide a professional critique of the render, focusing on lighting, composition, realism, and material quality.
3.  **Score**: Rate the photorealism/quality on a scale of 0-100.
4.  **Suggestions**: Provide 2-3 specific, actionable suggestions to improve the render.

Return your response as a VALID JSON object with this exact structure:
{
  "materials": [
    {
      "name": "Glass Facade",
      "type": "glass",
      "x": 50,
      "y": 40,
      "color": "#87CEEB"
    }
  ],
  "critique": "The render shows a good sense of scale, but the lighting feels a bit flat...",
  "score": 75,
  "suggestions": [
    "Increase the contrast to add depth.",
    "Add some imperfections to the concrete texture for realism."
  ]
}

For materials, use types: glass, concrete, wood, metal, brick, plaster, grass, vegetation, sky, stone, asphalt, fabric.
"""

        # Call OpenRouter API with retry logic
        max_retries = 3
        retry_delay = 2  # Start with 2 seconds
        
        for attempt in range(max_retries):
            try:
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
                    timeout=45
                )
                
                # Handle rate limiting (429)
                if response.status_code == 429:
                    if attempt < max_retries - 1:
                        import time
                        wait_time = retry_delay * (2 ** attempt)  # Exponential backoff
                        print(f"Rate limit hit (429). Retrying in {wait_time}s... (attempt {attempt + 1}/{max_retries})")
                        time.sleep(wait_time)
                        continue
                    else:
                        return {
                            'error': f'Rate limit exceeded. Please wait a few minutes and try again.',
                            'materials': [],
                            'objects': []
                        }
                
                if response.status_code != 200:
                    return {
                        'error': f'API error: {response.status_code}',
                        'materials': [],
                        'objects': []
                    }
                
                # Success - break out of retry loop
                break
                
            except requests.exceptions.Timeout:
                if attempt < max_retries - 1:
                    import time
                    print(f"Request timeout. Retrying... (attempt {attempt + 1}/{max_retries})")
                    time.sleep(retry_delay)
                    continue
                else:
                    return {
                        'error': 'Request timeout after multiple retries',
                        'materials': [],
                        'objects': []
                    }
        
        result = response.json()
        ai_response = result['choices'][0]['message']['content']
        
        # Parse AI response into structured data
        parsed_data = parse_ai_response(ai_response)
        
        return {
            'success': True,
            'materials': parsed_data.get('materials', []),
            'critique': parsed_data.get('critique', 'Analysis complete.'),
            'score': parsed_data.get('score', 0),
            'suggestions': parsed_data.get('suggestions', []),
            'raw_response': ai_response
        }
        
    except Exception as e:
        print(f"AI Analysis Error: {e}")
        return {
            'error': str(e),
            'materials': [],
            'objects': []
        }

def parse_ai_response(response_text: str) -> Dict:
    """
    Parse AI response text into structured data.
    Handles JSON extraction and fallback.
    """
    try:
        # Try to extract JSON object from response
        # Look for the first '{' and the last '}'
        json_match = re.search(r'\{[\s\S]*\}', response_text)
        if json_match:
            json_str = json_match.group(0)
            data = json.loads(json_str)
            
            # Normalize materials if present
            if 'materials' in data:
                normalized_materials = []
                for mat in data['materials']:
                    if isinstance(mat, dict) and 'type' in mat:
                        normalized_materials.append({
                            'name': mat.get('name', 'Unknown Material'),
                            'type': mat.get('type', 'unknown').lower(),
                            'x': int(mat.get('x', 50)),
                            'y': int(mat.get('y', 50)),
                            'color': mat.get('color', '#808080')
                        })
                data['materials'] = normalized_materials
            
            return data
            
    except (json.JSONDecodeError, ValueError) as e:
        print(f"JSON parsing failed: {e}, falling back to text parsing")
    
    # Fallback: minimal structure
    return {
        'materials': [],
        'critique': "Could not parse detailed AI analysis. " + response_text[:100] + "...",
        'score': 50,
        'suggestions': []
    }

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
