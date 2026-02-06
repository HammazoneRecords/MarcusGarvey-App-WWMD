import os
import re
import json
import urllib.request
import urllib.error
from pathlib import Path

# Setup paths
BASE_DIR = Path(__file__).resolve().parent.parent
REAL_ENV_PATH = BASE_DIR.parent.parent / "env.local"

def load_key():
    print(f"Reading: {REAL_ENV_PATH}")
    if not REAL_ENV_PATH.exists():
        print("env.local NOT FOUND")
        return None
    
    content = REAL_ENV_PATH.read_text(encoding="utf-8")
    print(f"Content length: {len(content)}")
    
    # Debug print first few chars of lines (masking key)
    for line in content.splitlines():
        if "api key" in line.lower():
            print(f"Found key line: {line.split(':')[0]}: [HIDDEN]")

    match = re.search(r"gemini\s+api\s+key\s*:\s*([A-Za-z0-9\-_]+)", content, re.IGNORECASE)
    if match:
        key = match.group(1)
        print(f"Key parsed length: {len(key)}")
        return key
    print("Regex failed to match key")
    return None

def test_model(api_key, model_name):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    data = {"contents": [{"parts": [{"text": "Hello, explain the number 5."}]}]}
    
    print(f"\nTesting {model_name}...")
    try:
        req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers=headers)
        with urllib.request.urlopen(req) as response:
            print("  SUCCESS!")
            result = json.loads(response.read().decode('utf-8'))
            print("  Response: " + str(result)[:100] + "...")
            return True
    except urllib.error.HTTPError as e:
        print(f"  FAILED: HTTP {e.code}")
        print(f"  Body: {e.read().decode('utf-8')}")
        return False
    except Exception as e:
        print(f"  FAILED: {e}")
        return False

def list_models(api_key):
    # Try v1 instead of v1beta
    url = f"https://generativelanguage.googleapis.com/v1/models?key={api_key}"
    print(f"\nListing models from {url}...")
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            print("AVAILABLE MODELS (v1):")
            for m in result.get('models', []):
                if 'generateContent' in m.get('supportedGenerationMethods', []):
                    print(f" - {m['name']}")
            return True
    except Exception as e:
        print(f"FAILED to list models (v1): {e}")
        return False

def main():
    print("=== GEMINI DEBUG ===")
    key = load_key()
    if not key:
        return
        
    list_models(key)
    
    # Test common models
    models = ["gemini-1.5-flash"]
    for m in models:
        test_model(key, m)

if __name__ == "__main__":
    main()
