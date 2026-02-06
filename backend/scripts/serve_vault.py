#!/usr/bin/env python3
"""
Vault Server - The "Gliding" Bridge
Serves the latest WWMD session JSON to the frontend.
Usage: python backend/scripts/serve_vault.py
"""
import os
import json
import glob
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler

# Configuration
PORT = 5000
BASE_DIR = Path(__file__).resolve().parent.parent.parent
SESSIONS_DIR = BASE_DIR / "sessions"

class VaultHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        # Enable CORS for local dev
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET')
        self.send_header('Content-Type', 'application/json')
        self.end_headers()

        if self.path == '/api/latest':
            self.serve_latest()
        elif self.path == '/api/history':
            self.serve_history()
        elif self.path.startswith('/api/session'):
            self.serve_session()
        else:
            self.wfile.write(b'{"status": "ok", "message": "WWMD Vault Server Online"}')

    def serve_session(self):
        """Serve a specific session file by filename."""
        from urllib.parse import urlparse, parse_qs
        query = parse_qs(urlparse(self.path).query)
        filename = query.get('file', [None])[0]
        
        if not filename:
            self.wfile.write(b'{"error": "No file specified"}')
            return

        # Security check: prevent directory traversal
        if '..' in filename or '/' in filename or '\\' in filename:
            self.wfile.write(b'{"error": "Invalid filename"}')
            return
            
        # Search for the file in all subdirectories
        files = glob.glob(str(SESSIONS_DIR / "**" / filename), recursive=True)
        if not files:
             self.wfile.write(b'{"error": "File not found"}')
             return
             
        try:
            with open(files[0], 'rb') as f:
                self.wfile.write(f.read())
        except Exception as e:
            err = {"error": str(e)}
            self.wfile.write(json.dumps(err).encode('utf-8'))

    def serve_latest(self):
        """Find the most recent JSON in sessions/ and serve it."""
        try:
            # Recursive glob to find all .json files in subdirectories of sessions/
            files = glob.glob(str(SESSIONS_DIR / "**/*.json"), recursive=True)
            if not files:
                self.wfile.write(b'{"error": "No sessions found"}')
                return

            # Sort by modification time (newest first)
            latest_file = max(files, key=os.path.getmtime)
            
            with open(latest_file, 'rb') as f:
                self.wfile.write(f.read())
                
        except Exception as e:
            err = {"error": str(e)}
            self.wfile.write(json.dumps(err).encode('utf-8'))

    def serve_history(self):
        """List all available session files."""
        try:
            files = glob.glob(str(SESSIONS_DIR / "**/*.json"), recursive=True)
            # Create summary list
            history = []
            for f in sorted(files, key=os.path.getmtime, reverse=True):
                path = Path(f)
                history.append({
                    "filename": path.name,
                    "date": path.parent.name,
                    "timestamp": os.path.getmtime(f)
                })
            
            self.wfile.write(json.dumps(history).encode('utf-8'))
            
        except Exception as e:
            err = {"error": str(e)}
            self.wfile.write(json.dumps(err).encode('utf-8'))

def run(server_class=HTTPServer, handler_class=VaultHandler):
    server_address = ('', PORT)
    httpd = server_class(server_address, handler_class)
    print(f"🚀 WWMD Vault Server running on http://localhost:{PORT}")
    print(f"📂 Watching: {SESSIONS_DIR}")
    print("endpoints:")
    print(f"  - GET /api/latest  (Most recent answer)")
    print(f"  - GET /api/history (List of all answers)")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped.")

if __name__ == "__main__":
    run()
