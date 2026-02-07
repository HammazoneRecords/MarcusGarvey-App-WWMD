from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import sqlite3
import sys
import os
from pathlib import Path

# Add ragbox/scripts and backend to path so we can import modules
BASE_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BASE_DIR.parent
SESSIONS_DIR = PROJECT_ROOT / "sessions"
DB_PATH = BASE_DIR / "data" / "memory.db"
TESTING_PANEL_DB_PATH = BASE_DIR / "data" / "testing_panel.db"
RAG_SCRIPTS_DIR = BASE_DIR / "ragbox" / "scripts"
sys.path.insert(0, str(BASE_DIR))
sys.path.append(str(RAG_SCRIPTS_DIR))

try:
    from api.nodes_db import get_library
except ImportError:
    try:
        from nodes_db import get_library
    except ImportError:
        get_library = None

try:
    from wwmd_ask_hybrid import ask_marcus, ask_marcus_lens
except ImportError as e:
    print(f"Error importing RAG modules: {e}")
    sys.exit(1)

SERVER_HOST = os.environ.get("ARK_API_HOST", "0.0.0.0")
SERVER_PORT = int(os.environ.get("ARK_API_PORT", os.environ.get("PORT", "5050")))

# CORS: in production set CORS_ORIGINS to comma-separated allowed origins (e.g. https://app.example.com)
CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "").strip()
app = Flask(__name__)
if CORS_ORIGINS:
    origins = [o.strip() for o in CORS_ORIGINS.split(",") if o.strip()]
    CORS(app, origins=origins, supports_credentials=False)
else:
    CORS(app)  # allow all (dev default)

# Input limits for public API
WWMD_SITUATION_MAX_LEN = int(os.environ.get("WWMD_SITUATION_MAX_LEN", "4000"))
CHAT_QUERY_MAX_LEN = int(os.environ.get("CHAT_QUERY_MAX_LEN", "2000"))

@app.route('/api/wwmd', methods=['POST'])
def wwmd_lens():
    data = request.json
    if not data or 'situation' not in data:
        return jsonify({"error": "Missing situation"}), 400
    
    situation = data['situation']
    if not isinstance(situation, str):
        return jsonify({"error": "situation must be a string"}), 400
    situation = situation.strip()
    if len(situation) > WWMD_SITUATION_MAX_LEN:
        return jsonify({"error": f"situation must be at most {WWMD_SITUATION_MAX_LEN} characters"}), 400
    mode = data.get('mode', 'Personal')
    
    try:
        # Generate structured analysis
        response = ask_marcus_lens(situation, mode=mode)
        return jsonify(response)
    except Exception as e:
        print(f"Error processing WWMD request: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    if not data or 'query' not in data:
        return jsonify({"error": "Missing query"}), 400
    
    query = data['query']
    if not isinstance(query, str):
        return jsonify({"error": "query must be a string"}), 400
    query = query.strip()
    if len(query) > CHAT_QUERY_MAX_LEN:
        return jsonify({"error": f"query must be at most {CHAT_QUERY_MAX_LEN} characters"}), 400
    debug_mode = data.get('debug', 'expand')
    
    try:
        response = ask_marcus(query, debug_mode=debug_mode)
        return jsonify(response)
    except Exception as e:
        print(f"Error processing query: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/latest', methods=['GET'])
def get_latest_session():
    """Get the most recent session JSON from the vault."""
    try:
        if not SESSIONS_DIR.exists():
            return jsonify({"error": "No sessions found"}), 404
        # Find all session files
        all_sessions = []
        for date_dir in SESSIONS_DIR.iterdir():
            if date_dir.is_dir():
                for session_file in date_dir.glob("*.json"):
                    all_sessions.append(session_file)
        
        if not all_sessions:
            return jsonify({"error": "No sessions found"}), 404
            
        # Sort by modification time
        latest_file = max(all_sessions, key=os.path.getmtime)
        return jsonify(json.loads(latest_file.read_text(encoding="utf-8")))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/history', methods=['GET'])
def get_history():
    """List all sessions organized by date."""
    history = []
    try:
        if SESSIONS_DIR.exists():
            for date_dir in sorted(SESSIONS_DIR.iterdir(), reverse=True):
                if date_dir.is_dir():
                    sessions = []
                    for s in sorted(date_dir.glob("*.json"), reverse=True):
                        # Lightweight preview
                        try:
                            content = json.loads(s.read_text(encoding="utf-8"))
                            sessions.append({
                                "filename": s.name,
                                "date": date_dir.name,
                                "query": content.get("query", "Unknown"),
                                "timestamp": content.get("meta", {}).get("timestamp")
                            })
                        except:
                            continue
                    if sessions:
                        history.extend(sessions)
        return jsonify(history)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/session', methods=['GET'])
def get_session():
    """Get a specific session by filename (searches all date dirs)."""
    filename = request.args.get('file')
    if not filename:
        return jsonify({"error": "Missing file parameter"}), 400
        
    try:
        for date_dir in SESSIONS_DIR.iterdir():
            if date_dir.is_dir():
                target = date_dir / filename
                if target.exists():
                    return jsonify(json.loads(target.read_text(encoding="utf-8")))
        return jsonify({"error": "Session not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def _init_testing_panel_db():
    """Create testing_panel.db and table if missing."""
    if not TESTING_PANEL_DB_PATH.parent.exists():
        TESTING_PANEL_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    schema_path = BASE_DIR / "data" / "testing_panel_schema.sql"
    if schema_path.exists():
        conn = sqlite3.connect(str(TESTING_PANEL_DB_PATH))
        conn.executescript(schema_path.read_text(encoding="utf-8"))
        conn.close()


@app.route('/api/testing-panel', methods=['GET'])
def get_testing_panel():
    """Get testing panel state for a storage_key. Returns { checked: string[], notes: string[] }."""
    storage_key = request.args.get('storage_key')
    if not storage_key:
        return jsonify({"error": "Missing storage_key"}), 400
    try:
        _init_testing_panel_db()
        conn = sqlite3.connect(str(TESTING_PANEL_DB_PATH))
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            "SELECT checked_json, notes_json FROM testing_panel_state WHERE storage_key = ?",
            (storage_key,)
        ).fetchone()
        conn.close()
        if not row:
            return jsonify({"checked": [], "notes": []})
        return jsonify({
            "checked": json.loads(row["checked_json"]) if row["checked_json"] else [],
            "notes": json.loads(row["notes_json"]) if row["notes_json"] else [],
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/testing-panel', methods=['POST'])
def save_testing_panel():
    """Upsert testing panel state. Body: { storage_key, checked?: string[], notes?: string[] }."""
    data = request.json
    if not data or 'storage_key' not in data:
        return jsonify({"error": "Missing storage_key"}), 400
    storage_key = data["storage_key"]
    checked = data.get("checked")
    notes = data.get("notes")
    if checked is None and notes is None:
        return jsonify({"error": "Provide at least one of checked or notes"}), 400
    from datetime import datetime
    updated_at = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    try:
        _init_testing_panel_db()
        conn = sqlite3.connect(str(TESTING_PANEL_DB_PATH))
        existing = conn.execute(
            "SELECT checked_json, notes_json FROM testing_panel_state WHERE storage_key = ?",
            (storage_key,)
        ).fetchone()
        if existing:
            checked_json = json.dumps(checked) if checked is not None else existing[0]
            notes_json = json.dumps(notes) if notes is not None else existing[1]
        else:
            checked_json = json.dumps(checked if checked is not None else [])
            notes_json = json.dumps(notes if notes is not None else [])
        conn.execute(
            """INSERT INTO testing_panel_state (storage_key, checked_json, notes_json, updated_at)
               VALUES (?, ?, ?, ?)
               ON CONFLICT(storage_key) DO UPDATE SET
                 checked_json = excluded.checked_json,
                 notes_json = excluded.notes_json,
                 updated_at = excluded.updated_at""",
            (storage_key, checked_json, notes_json, updated_at)
        )
        conn.commit()
        conn.close()
        # Also persist to a JSON file so progress can be resumed by external chains/tools.
        try:
            state_dir = PROJECT_ROOT / "sessions" / "testing_panel"
            state_dir.mkdir(parents=True, exist_ok=True)
            state_path = state_dir / f"{storage_key}.json"
            payload = {
                "storageKey": storage_key,
                "checked": json.loads(checked_json),
                "notes": json.loads(notes_json),
                "updatedAt": updated_at,
            }
            state_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        except Exception:
            # File persistence is best-effort; DB state is the primary store.
            pass
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def _page_locator_from(locator):
    """Derive page-level locator from a line or chunk locator so we fetch the full page chunk.
    e.g. pdf:page:0010:line:5 -> pdf:page:0010; pdf:page:0010 -> pdf:page:0010
    """
    if not locator or ":" not in locator:
        return locator
    parts = locator.split(":")
    # Chunks table uses page-level locators like "pdf:page:0010" (3 parts)
    if len(parts) >= 3:
        return ":".join(parts[:3])
    return locator


@app.route('/api/source/<anchor_id>', methods=['GET'])
def get_source_section(anchor_id):
    """Return source metadata and PAGE chunk content (full page) for an anchor (and optional locator).
    If locator is line-level (e.g. pdf:page:0010:line:5), we derive the page locator to return the full page.
    """
    locator = request.args.get('locator')
    if not anchor_id:
        return jsonify({"error": "Missing anchor_id"}), 400
    if not DB_PATH.exists():
        return jsonify({"error": "Database not available"}), 503
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        # Resolve anchor title (V2 schema: title, canonical_path)
        cursor = conn.execute(
            "SELECT anchor_id, title, canonical_path FROM anchors WHERE anchor_id = ? LIMIT 1",
            (anchor_id,)
        )
        row = cursor.fetchone()
        if not row:
            conn.close()
            return jsonify({"error": "Anchor not found"}), 404
        title = row["title"] or anchor_id
        canonical_path = row["canonical_path"] or ""
        # Always fetch PAGE chunk (full page), not line chunk: derive page locator from receipt locator
        page_locator = _page_locator_from(locator) if locator else None
        if page_locator:
            cursor = conn.execute(
                "SELECT content FROM chunks WHERE anchor_id = ? AND anchor_locator = ? LIMIT 1",
                (anchor_id, page_locator)
            )
            chunk = cursor.fetchone()
            if not chunk and page_locator != locator:
                cursor = conn.execute(
                    "SELECT content FROM chunks WHERE anchor_id = ? AND anchor_locator = ? LIMIT 1",
                    (anchor_id, locator)
                )
                chunk = cursor.fetchone()
        else:
            cursor = conn.execute(
                "SELECT content FROM chunks WHERE anchor_id = ? ORDER BY anchor_locator LIMIT 1",
                (anchor_id,)
            )
            chunk = cursor.fetchone()
        section_content = chunk["content"] if chunk else ""
        conn.close()
        # Page label from locator e.g. pdf:page:0010 -> 10
        page_label = ""
        if (page_locator or locator) and ":" in (page_locator or locator or ""):
            pl = (page_locator or locator or "").split(":")
            if len(pl) >= 3:
                page_label = pl[2].lstrip("0") or "0"
        return jsonify({
            "anchorId": anchor_id,
            "title": title,
            "locator": locator or None,
            "sectionContent": section_content,
            "pageLabel": page_label or None,
            "canonicalPath": canonical_path or None,
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/library', methods=['GET'])
def library():
    """Library: sources + facts (nodes DB, seeded from db.json). Supports ?search= &category= &confidence="""
    if get_library is None:
        return jsonify({"error": "Nodes DB not available"}), 503
    try:
        filters = {
            "search": request.args.get("search"),
            "category": request.args.get("category"),
            "confidence": request.args.get("confidence"),
        }
        data = get_library(filters)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/library/facts/<fact_id>', methods=['GET'])
def library_fact_by_id(fact_id):
    """Single fact by id (external_id)."""
    if get_library is None:
        return jsonify({"error": "Nodes DB not available"}), 503
    try:
        data = get_library()
        for f in data.get("facts", []):
            if f.get("id") == fact_id:
                return jsonify(f)
        return jsonify({"error": "Fact not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "service": "WhirlwindDB ARK Connect"})

if __name__ == '__main__':
    print(f"Starting WWMD RAG Server on port {SERVER_PORT}...")
    app.run(host=SERVER_HOST, port=SERVER_PORT, debug=True)
