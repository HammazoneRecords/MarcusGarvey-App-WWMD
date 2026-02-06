#!/usr/bin/env python3
"""
Comprehensive API key tester - tries multiple endpoints and model formats
"""
import json
import urllib.request
import urllib.error
import sys
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR.parent / "src" / "env.local"

def load_api_key():
    if not ENV_PATH.exists():
        print(f"ERROR: env.local not found at {ENV_PATH}")
        sys.exit(1)
    content = ENV_PATH.read_text(encoding="utf-8")
    matches = re.findall(r'GEMINI_API_KEY\s*=\s*"([^"]+)"', content)
    if matches:
        return matches[-1]
    print("ERROR: Could not parse 'GEMINI_API_KEY' from env.local")
    sys.exit(1)

def test_model(api_key, model_name, api_version="v1beta"):
    """Test a specific model with the API key."""
    url = f"https://generativelanguage.googleapis.com/{api_version}/models/{model_name}:generateContent?key={api_key}"
    
    headers = {"Content-Type": "application/json"}
    data = {
        "contents": [{
            "parts": [{"text": "Say 'API works!' if you can read this."}]
        }]
    }
    
    try:
        req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers=headers)
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            text_response = result['candidates'][0]['content']['parts'][0]['text']
            return True, text_response
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        return False, f"HTTP {e.code}: {error_body[:200]}"
    except Exception as e:
        return False, str(e)

if __name__ == "__main__":
    api_key = load_api_key()
    print(f"Testing API key: {api_key[:15]}...{api_key[-4:]}\n")
    
    # Try different model names and API versions
    test_configs = [
        ("v1beta", "gemini-1.5-flash"),
        ("v1beta", "gemini-1.5-pro"),
        ("v1beta", "gemini-pro"),
        ("v1", "gemini-1.5-flash"),
        ("v1", "gemini-pro"),
    ]
    
    for api_version, model in test_configs:
        print(f"Trying {api_version}/models/{model}...", end=" ")
        success, response = test_model(api_key, model, api_version)
        if success:
            print(f"SUCCESS!")
            print(f"  Response: {response}")
            print(f"\nWORKING CONFIG: {api_version}/models/{model}")
            break
        else:
            print(f"FAILED")
            print(f"  Error: {response[:100]}")
    else:
        print("\nAll configurations failed. Please check:")
        print("1. API key is valid and active")
        print("2. Generative Language API is enabled")
        print("3. Key has proper permissions")
