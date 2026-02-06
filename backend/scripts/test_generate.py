import os
import json
import requests
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

API_KEY = os.getenv("GEMINI_API_KEY") or ""
MODEL  = os.getenv("GEMINI_MODEL") or "gemini-2.5-flash"  # fallback guess

if not API_KEY:
    raise SystemExit("Missing GEMINI_API_KEY env var")

# Mask key for security
masked_key = f"{API_KEY[:10]}...{API_KEY[-4:]}" if len(API_KEY) > 14 else "****"
print(f"Using API key: {masked_key}")
print(f"Testing model: {MODEL}\n")

url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"
payload = {
    "contents": [
        {"role": "user", "parts": [{"text": "What is economic independence? Answer in 4 bullets."}]}
    ]
}

r = requests.post(url, params={"key": API_KEY}, json=payload, timeout=60)

print("HTTP:", r.status_code)
print(r.text[:3000])

# If you want to hard-fail on non-200:
r.raise_for_status()

data = r.json()
print("\nParsed OK. Top-level keys:", list(data.keys()))
