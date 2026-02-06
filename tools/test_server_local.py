import urllib.request
import urllib.error
import json
import sys
import time
import os

BASE_URL = os.environ.get("WWMD_API_BASE", "http://localhost:5050/api").strip().rstrip('/')

def make_request(url, method='GET', data=None):
    headers = {'Content-Type': 'application/json'}
    req = urllib.request.Request(url, method=method, headers=headers)
    if data:
        req.data = json.dumps(data).encode('utf-8')
        
    try:
        with urllib.request.urlopen(req) as response:
            return response.status, json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()
    except Exception as e:
        return 0, str(e)

def test_health():
    status, data = make_request(f"{BASE_URL}/health")
    if status == 200 and isinstance(data, dict) and data.get("status") == "ok":
        print("[PASS] /api/health")
        return True
    else:
        print(f"[FAIL] /api/health: {status} {data}")
        return False

def test_chat():
    payload = {"query": "What is the meaning of life?", "debug": "strict"}
    status, data = make_request(f"{BASE_URL}/chat", method='POST', data=payload)
    
    if status == 200 and isinstance(data, dict):
        if "answer" in data and "citations" in data:
            print("[PASS] /api/chat")
            return True
        else:
            print(f"[FAIL] /api/chat: Invalid contract {data.keys()}")
            return False
    else:
        print(f"[FAIL] /api/chat: {status} {data}")
        return False

if __name__ == "__main__":
    print("Waiting for server (2s)...")
    time.sleep(2)
    current_health = test_health()
    current_chat = test_chat()
    
    if current_health and current_chat:
        print("\nALL SYSTEMS GO")
        sys.exit(0)
    else:
        print("\nSYSTEM FAILURE")
        sys.exit(1)
