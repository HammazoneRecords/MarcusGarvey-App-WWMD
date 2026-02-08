import os
import json

# Ensure the project path is importable
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Set a dummy env var for testing
os.environ.pop('GEMINI_API_KEY', None)
# Enable DIAGNOSTIC_MODE for this test run so server will start without full RAG modules
os.environ['DIAGNOSTIC_MODE'] = '1'

import importlib.util
from pathlib import Path

# Load server module by filepath to avoid import path issues
server_path = Path(__file__).resolve().parents[1] / 'api' / 'server.py'
spec = importlib.util.spec_from_file_location('wwmd_server', str(server_path))
server = importlib.util.module_from_spec(spec)
spec.loader.exec_module(server)

app = server.app

with app.test_client() as client:
    print('=== No keys set ===')
    r = client.post('/api/key-diagnostic', json={})
    print(r.status_code, json.dumps(r.get_json(), indent=2))

    print('\n=== Env key present ===')
    os.environ['GEMINI_API_KEY'] = 'env_dummy_key'
    r = client.post('/api/key-diagnostic', json={})
    print(r.status_code, json.dumps(r.get_json(), indent=2))

    print('\n=== User key provided ===')
    payload = {'apiConfig': {'geminiApiKey': 'user_dummy_key'}}
    r = client.post('/api/key-diagnostic', json=payload)
    print(r.status_code, json.dumps(r.get_json(), indent=2))

    print('\n=== Both present (user should take precedence) ===')
    os.environ['GEMINI_API_KEY'] = 'env_dummy_key'
    payload = {'apiConfig': {'geminiApiKey': 'user_dummy_key'}}
    r = client.post('/api/key-diagnostic', json=payload)
    print(r.status_code, json.dumps(r.get_json(), indent=2))
