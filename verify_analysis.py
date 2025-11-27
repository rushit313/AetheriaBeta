import requests
import base64
import os

# Create a simple test image (solid color)
from PIL import Image
import io

def create_test_image(color=(100, 150, 200), size=(100, 100)):
    img = Image.new('RGB', size, color)
    buf = io.BytesIO()
    img.save(buf, format='JPEG')
    return buf.getvalue()

def test_analysis():
    url = "http://127.0.0.1:5001/api/analyze_render"
    
    # Create a test image
    img_bytes = create_test_image()
    
    files = {
        'render': ('test.jpg', img_bytes, 'image/jpeg')
    }
    
    # Test WITH AI
    print("Testing AI Analysis (ai=1)...")
    try:
        resp = requests.post(url, files=files, data={'ai': '1'})
        if resp.status_code == 200:
            data = resp.json()
            print("Success!")
            print(f"Score: {data.get('score')}")
            print(f"Critique: {data.get('critique')}")
            
            if data.get('score') > 0:
                print("PASS: AI Analysis returned a score.")
            else:
                print("FAIL: Score is 0, AI might have failed.")
        else:
            print(f"Failed: {resp.status_code} - {resp.text}")
    except Exception as e:
        print(f"Error connecting to backend: {e}")
        print("Make sure the backend is running!")

if __name__ == "__main__":
    test_analysis()
