import requests
import os
import sys
import time
import threading
from flask import Flask
import sys

# Add backend to path to import app
sys.path.append(os.path.join(os.getcwd(), 'backend'))

try:
    from app import app
except ImportError:
    print("Could not import app from backend. Make sure you are in the root directory.")
    sys.exit(1)

def run_server():
    app.run(port=5002, use_reloader=False)

def test_endpoints():
    base_url = "http://127.0.0.1:5002"
    
    # Wait for server to start
    time.sleep(2)
    
    print("Testing /api/ping...")
    try:
        r = requests.get(f"{base_url}/api/ping")
        if r.status_code == 200 and r.json().get("ok"):
            print("PASS: /api/ping")
        else:
            print(f"FAIL: /api/ping - {r.status_code} {r.text}")
    except Exception as e:
        print(f"FAIL: /api/ping - {e}")

    print("\nTesting /api/analyze_render (no files)...")
    try:
        r = requests.post(f"{base_url}/api/analyze_render")
        if r.status_code == 400:
            print("PASS: /api/analyze_render (no files) correctly returned 400")
        else:
            print(f"FAIL: /api/analyze_render (no files) - {r.status_code}")
    except Exception as e:
        print(f"FAIL: /api/analyze_render (no files) - {e}")

    # Create dummy image for testing
    print("\nTesting /api/analyze_render (with file)...")
    dummy_img_path = "test_image.png"
    # Create a simple 1x1 PNG
    with open(dummy_img_path, "wb") as f:
        # 1x1 pixel transparent png
        f.write(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82')

    try:
        with open(dummy_img_path, "rb") as img:
            files = {'render': img}
            r = requests.post(f"{base_url}/api/analyze_render", files=files)
            if r.status_code == 200:
                data = r.json()
                if "analysis" in data:
                    print("PASS: /api/analyze_render (with file)")
                    print("Analysis keys:", data["analysis"].keys())
                else:
                    print("FAIL: /api/analyze_render response missing 'analysis'")
            else:
                print(f"FAIL: /api/analyze_render (with file) - {r.status_code} {r.text}")
    except Exception as e:
        print(f"FAIL: /api/analyze_render (with file) - {e}")
    finally:
        if os.path.exists(dummy_img_path):
            os.remove(dummy_img_path)

if __name__ == "__main__":
    # Start server in a separate thread
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    test_endpoints()
    print("\nTests complete.")
