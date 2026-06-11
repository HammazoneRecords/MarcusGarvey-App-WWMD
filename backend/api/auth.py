"""Homegrown magic-link authentication + user-data sync.

Replaces Supabase auth/data tables with SQLite tables in the same DB
server.py already uses (DB_PATH = backend/data/memory.db).

All routes built on top of this module are optional: if a request has
no Authorization header, callers should fall back to the existing
session_id anonymous identity flow.
"""

import os
import re
import json
import sqlite3
import secrets
from pathlib import Path
from datetime import datetime, timedelta, timezone

import jwt

# backend/api/auth.py -> backend/api -> backend -> MarcusGarvey-App-WWMD
BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent.parent
ARK_CONFIG_PATH = PROJECT_ROOT / ".ark"

JWT_ALGORITHM = "HS256"
JWT_EXPIRY_DAYS = 30
MAGIC_LINK_EXPIRY_MINUTES = 15
MAGIC_LINK_COOLDOWN_SECONDS = 60


def load_ark_config(key_name):
    """Read a config value: env var first, then .ark file."""
    env_val = os.environ.get(key_name)
    if env_val and env_val.strip():
        return env_val.strip()
    if ARK_CONFIG_PATH.exists():
        content = ARK_CONFIG_PATH.read_text(encoding="utf-8")
        matches = re.findall(rf'{key_name}\s*=\s*"?([^"\n]+)"?', content)
        if matches:
            return matches[-1].strip()
    return None


def _persist_to_ark(key_name, value):
    """Append a key=value line to .ark, creating the file if needed."""
    line = f'{key_name}="{value}"\n'
    if ARK_CONFIG_PATH.exists():
        content = ARK_CONFIG_PATH.read_text(encoding="utf-8")
        if not content.endswith("\n"):
            content += "\n"
        content += line
        ARK_CONFIG_PATH.write_text(content, encoding="utf-8")
    else:
        ARK_CONFIG_PATH.write_text(line, encoding="utf-8")


def get_jwt_secret():
    """Get JWT_SECRET, generating and persisting one to .ark if absent."""
    secret = load_ark_config("JWT_SECRET")
    if secret:
        return secret
    secret = secrets.token_hex(32)
    _persist_to_ark("JWT_SECRET", secret)
    return secret


def get_resend_api_key():
    return load_ark_config("RESEND_API_KEY")


def get_resend_from_email():
    return load_ark_config("RESEND_FROM_EMAIL") or "Marcus Garvey ARK <onboarding@resend.dev>"


def get_frontend_url():
    return load_ark_config("FRONTEND_URL") or "http://localhost:5175"


# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------

def init_auth_tables(db_path):
    conn = sqlite3.connect(str(db_path))
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS magic_links (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            token TEXT UNIQUE NOT NULL,
            expires_at TEXT NOT NULL,
            used INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS user_saved_facts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            fact_id TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            UNIQUE(user_id, fact_id)
        );

        CREATE TABLE IF NOT EXISTS user_lens_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            result_id TEXT NOT NULL,
            payload TEXT NOT NULL,
            checked_action_step_ids TEXT NOT NULL DEFAULT '[]',
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            UNIQUE(user_id, result_id)
        );

        CREATE TABLE IF NOT EXISTS user_toolkit_edits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            template_id TEXT NOT NULL,
            markdown TEXT NOT NULL,
            updated_at TEXT NOT NULL DEFAULT (datetime('now')),
            UNIQUE(user_id, template_id)
        );

        CREATE TABLE IF NOT EXISTS tts_leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            source TEXT,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        );
    """)
    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# Magic link request / verify
# ---------------------------------------------------------------------------

def send_magic_link_email(email, link):
    """Send the magic link via Resend, or log it to the console if no API key."""
    api_key = get_resend_api_key()
    if not api_key:
        print(f"\n[AUTH] Magic link for {email}:\n  {link}\n")
        return True, None

    import requests
    try:
        resp = requests.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "from": get_resend_from_email(),
                "to": [email],
                "subject": "Your Marcus Garvey ARK sign-in link",
                "html": (
                    f"<p>Click below to sign in:</p>"
                    f'<p><a href="{link}">{link}</a></p>'
                    f"<p>This link expires in {MAGIC_LINK_EXPIRY_MINUTES} minutes.</p>"
                ),
            },
            timeout=10,
        )
        if resp.status_code >= 400:
            return False, f"Resend API error: {resp.status_code}"
        return True, None
    except Exception as e:
        return False, str(e)


def request_magic_link(email, db_path):
    email = email.strip().lower()
    if not email or "@" not in email:
        return False, "Invalid email address"

    conn = sqlite3.connect(str(db_path))

    last_row = conn.execute(
        "SELECT created_at FROM magic_links WHERE email = ? ORDER BY id DESC LIMIT 1",
        (email,),
    ).fetchone()
    if last_row:
        # created_at is stored via SQLite's datetime('now'), e.g. "2026-06-10 19:35:00" (UTC, naive)
        last_created = datetime.strptime(last_row[0], "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
        if datetime.now(timezone.utc) - last_created < timedelta(seconds=MAGIC_LINK_COOLDOWN_SECONDS):
            conn.close()
            return False, "Please wait a minute before requesting another sign-in link"

    token = secrets.token_urlsafe(32)
    expires_at = (datetime.now(timezone.utc) + timedelta(minutes=MAGIC_LINK_EXPIRY_MINUTES)).isoformat()

    conn.execute(
        "INSERT INTO magic_links (email, token, expires_at) VALUES (?, ?, ?)",
        (email, token, expires_at),
    )
    conn.commit()
    conn.close()

    link = f"{get_frontend_url().rstrip('/')}/auth/verify?token={token}"
    ok, err = send_magic_link_email(email, link)
    if not ok:
        return False, err
    return True, None


def verify_magic_link(token, db_path):
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    row = conn.execute(
        "SELECT * FROM magic_links WHERE token = ? LIMIT 1", (token,)
    ).fetchone()

    if not row:
        conn.close()
        return None, "Invalid or expired link"
    if row["used"]:
        conn.close()
        return None, "This link has already been used"
    expires_at = datetime.fromisoformat(row["expires_at"])
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if datetime.now(timezone.utc) > expires_at:
        conn.close()
        return None, "This link has expired"

    email = row["email"]
    conn.execute("UPDATE magic_links SET used = 1 WHERE id = ?", (row["id"],))

    user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    if not user:
        conn.execute("INSERT INTO users (email) VALUES (?)", (email,))
        conn.commit()
        user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    else:
        conn.commit()

    user_dict = {"id": user["id"], "email": user["email"]}
    conn.close()
    return user_dict, None


# ---------------------------------------------------------------------------
# JWT
# ---------------------------------------------------------------------------

def generate_jwt(user_id, email):
    payload = {
        "sub": str(user_id),
        "email": email,
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(days=JWT_EXPIRY_DAYS),
    }
    return jwt.encode(payload, get_jwt_secret(), algorithm=JWT_ALGORITHM)


def decode_jwt(token):
    try:
        return jwt.decode(token, get_jwt_secret(), algorithms=[JWT_ALGORITHM])
    except jwt.PyJWTError:
        return None


def get_user_from_request(request):
    """Returns {id, email} if a valid Bearer token is present, else None."""
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None
    token = auth_header[len("Bearer "):].strip()
    payload = decode_jwt(token)
    if not payload:
        return None
    return {"id": int(payload["sub"]), "email": payload["email"]}


# ---------------------------------------------------------------------------
# User data sync
# ---------------------------------------------------------------------------

def get_user_data_snapshot(user_id, db_path):
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row

    fact_rows = conn.execute(
        "SELECT fact_id FROM user_saved_facts WHERE user_id = ? ORDER BY created_at ASC",
        (user_id,),
    ).fetchall()
    saved_fact_ids = [r["fact_id"] for r in fact_rows]

    lens_rows = conn.execute(
        "SELECT result_id, payload, checked_action_step_ids FROM user_lens_results "
        "WHERE user_id = ? ORDER BY created_at DESC",
        (user_id,),
    ).fetchall()
    saved_lens_results = []
    saved_action_steps = {}
    for r in lens_rows:
        payload = json.loads(r["payload"])
        payload["id"] = r["result_id"]
        payload.setdefault("query", r["result_id"])
        saved_lens_results.append(payload)
        saved_action_steps[r["result_id"]] = json.loads(r["checked_action_step_ids"])

    edit_rows = conn.execute(
        "SELECT template_id, markdown FROM user_toolkit_edits WHERE user_id = ?",
        (user_id,),
    ).fetchall()
    toolkit_edits = {r["template_id"]: r["markdown"] for r in edit_rows}

    conn.close()
    return {
        "savedFactIds": saved_fact_ids,
        "savedLensResults": saved_lens_results,
        "savedActionSteps": saved_action_steps,
        "toolkitEdits": toolkit_edits,
    }


def add_saved_fact(user_id, fact_id, db_path):
    conn = sqlite3.connect(str(db_path))
    conn.execute(
        "INSERT OR IGNORE INTO user_saved_facts (user_id, fact_id) VALUES (?, ?)",
        (user_id, fact_id),
    )
    conn.commit()
    conn.close()


def remove_saved_fact(user_id, fact_id, db_path):
    conn = sqlite3.connect(str(db_path))
    conn.execute(
        "DELETE FROM user_saved_facts WHERE user_id = ? AND fact_id = ?",
        (user_id, fact_id),
    )
    conn.commit()
    conn.close()


def upsert_lens_result(user_id, result_id, payload, checked_action_step_ids, db_path):
    conn = sqlite3.connect(str(db_path))
    conn.execute(
        """INSERT INTO user_lens_results (user_id, result_id, payload, checked_action_step_ids)
           VALUES (?, ?, ?, ?)
           ON CONFLICT(user_id, result_id) DO UPDATE SET
             payload = excluded.payload,
             checked_action_step_ids = excluded.checked_action_step_ids""",
        (user_id, result_id, json.dumps(payload), json.dumps(checked_action_step_ids)),
    )
    conn.commit()
    conn.close()


def upsert_toolkit_edit(user_id, template_id, markdown, db_path):
    conn = sqlite3.connect(str(db_path))
    conn.execute(
        """INSERT INTO user_toolkit_edits (user_id, template_id, markdown, updated_at)
           VALUES (?, ?, ?, datetime('now'))
           ON CONFLICT(user_id, template_id) DO UPDATE SET
             markdown = excluded.markdown,
             updated_at = excluded.updated_at""",
        (user_id, template_id, markdown),
    )
    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# TTS early-access leads
# ---------------------------------------------------------------------------

def add_tts_lead(email, db_path, source=None):
    email = email.strip().lower()
    if not email or "@" not in email:
        return False, "Invalid email address"
    conn = sqlite3.connect(str(db_path))
    conn.execute(
        "INSERT OR IGNORE INTO tts_leads (email, source) VALUES (?, ?)",
        (email, source),
    )
    conn.commit()
    conn.close()
    return True, None
