# scripts/ops_log.py
from __future__ import annotations

import json
import os
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

BASE_DIR = Path(__file__).resolve().parent.parent
LOGS_DIR = BASE_DIR / "logs"
LEDGER_PATH = LOGS_DIR / "ops_ledger.jsonl"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def append_jsonl(path: Path, obj: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False, sort_keys=True) + "\n")


def log_event(
    action: str,
    *,
    human_intent: str,
    payload: Dict[str, Any],
    artifacts: Optional[Dict[str, Any]] = None,
) -> None:
    evt = {
        "ts_utc": utc_now_iso(),
        "action": action,
        "human_intent": human_intent,
        "payload": payload,
        "artifacts": artifacts or {},
        "env": {
            "python": sys.version.split()[0],
            "platform": platform.platform(),
            "cwd": str(Path.cwd()),
            "user": os.environ.get("USERNAME") or os.environ.get("USER") or "unknown",
        },
    }
    append_jsonl(LEDGER_PATH, evt)
