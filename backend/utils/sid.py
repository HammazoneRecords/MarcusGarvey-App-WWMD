# utils/sid.py
import os
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
STATE_PATH = BASE_DIR / "docs" / "STATE.json"

def get_active_sid() -> str:
    """
    Priority:
    1. RUN_RECORDED_SID (env)
    2. SOLOB_IMPORT_SESSION_ID (env fallback)
    3. docs/STATE.json -> active_session_id
    """
    sid = os.environ.get("RUN_RECORDED_SID") or os.environ.get("SOLOB_IMPORT_SESSION_ID")
    if sid:
        return sid

    if STATE_PATH.exists():
        try:
            data = json.loads(STATE_PATH.read_text(encoding="utf-8"))
            sid = data.get("active_session_id")
            if sid:
                return sid
        except Exception:
            pass

    raise RuntimeError("STOP: Canonical SID witness not found. Run via tools/solob.ps1 record.")
