import requests
import os
import json
from dotenv import load_dotenv

load_dotenv()

# Key from .env
API_KEY = os.getenv("OPENROUTER_API_KEY")

def test_openrouter():
    if not API_KEY:
        print("Error: OPENROUTER_API_KEY not found in .env")
        return

    print(f"Testing API Key: {API_KEY[:10]}...")
    
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:5001", 
        "X-Title": "Aetheria Debug"
    }
    
    # Test 1: List models (to check auth)
    data = {
        "model": "google/gemini-2.0-flash-exp:free",
        "messages": [
            {"role": "user", "content": "Hello, are you working?"}
        ]
    }
    
    try:
        print(f"Sending request to {data['model']}...")
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("SUCCESS: API Key and Model are working.")
            print(f"Response preview: {response.text[:100]}...")
        else:
            print(f"FAILURE: API Error {response.status_code}.")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    test_openrouter()
