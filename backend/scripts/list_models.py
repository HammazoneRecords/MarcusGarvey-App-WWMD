import os
import requests

# Windows console safety
import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

API_KEY = os.getenv("GEMINI_API_KEY") or ""
if not API_KEY:
    raise SystemExit("Missing GEMINI_API_KEY env var")

# Mask key for security
masked_key = f"{API_KEY[:10]}...{API_KEY[-4:]}" if len(API_KEY) > 14 else "****"
print(f"Using API key: {masked_key}\n")

url = "https://generativelanguage.googleapis.com/v1beta/models"
r = requests.get(url, params={"key": API_KEY}, timeout=30)

print("HTTP:", r.status_code)
print(r.text[:2000])  # print first chunk safely

r.raise_for_status()
data = r.json()

models = data.get("models", [])
print("\nFound models:", len(models))

# Show a compact list + supported methods
for m in models[:30]:
    name = m.get("name")
    methods = m.get("supportedGenerationMethods", [])
    print(f"- {name} | methods={methods}")
