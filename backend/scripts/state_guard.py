# scripts/state_guard.py
from __future__ import annotations

import json
from pathlib import Path
from typing import Literal

BASE_DIR = Path(__file__).resolve().parent.parent
STATE_PATH = BASE_DIR / "docs" / "STATE.json"

State = Literal["OBSERVE", "RECORD", "EXECUTE"]

ALLOWED_ACTIONS = {
    "OBSERVE": set(),
    "RECORD": {"snapshot_anchors", "run_script"},
    "EXECUTE": {"snapshot_anchors", "run_script"},
}


def get_state() -> State:
    if not STATE_PATH.exists():
        raise RuntimeError(f"STATE is undeclared. Missing: {STATE_PATH}")

    data = json.loads(STATE_PATH.read_text(encoding="utf-8"))
    state = data.get("state")
    if state not in ("OBSERVE", "RECORD", "EXECUTE"):
        raise RuntimeError(f"Invalid state in STATE.json: {state}")
    return state  # type: ignore[return-value]


def require_allowed(action: str) -> None:
    state = get_state()
    allowed = ALLOWED_ACTIONS.get(state, set())
    if action not in allowed:
        raise RuntimeError(
            f"Blocked by STGRAIL. Current state={state}. Action='{action}' not allowed."
        )
