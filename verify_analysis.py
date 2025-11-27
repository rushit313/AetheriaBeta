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
    
    # Test without AI first (should get stats)
    print("Testing Basic Analysis (No AI)...")
    try:
        resp = requests.post(url, files=files, data={'ai': '0'})
        if resp.status_code == 200:
            data = resp.json()
            print("Success!")
            print(f"Stats: {data.get('analysis')}")
            # Verify stats are not the mock values
            # Mock was: exposure 120.8, contrast 52.2
            # Our solid color image should have 0 contrast
            contrast = data['analysis']['contrast_std']
            print(f"Contrast: {contrast}")
            if contrast < 1.0:
                print("PASS: Real stats are working (low contrast for solid image)")
            else:
                print("FAIL: Contrast seems too high for solid image, might be using mock data?")
        else:
            print(f"Failed: {resp.status_code} - {resp.text}")
    except Exception as e:
        print(f"Error connecting to backend: {e}")
        print("Make sure the backend is running!")

if __name__ == "__main__":
    test_analysis()
