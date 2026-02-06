# scripts/run_recorded.py
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path
import json

from hash_utils import sha256_file
from ops_log import log_event
from state_guard import require_allowed

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
SCHEMA_PATH = DATA_DIR / "schema.sql"
DB_PATH = DATA_DIR / "memory.db"
LOGS_DIR = BASE_DIR / "logs"
STATE_PATH = BASE_DIR / "docs" / "STATE.json"


def main() -> int:
    require_allowed("run_script")

    parser = argparse.ArgumentParser()
    parser.add_argument("--intent", required=True, help="Human intent for this run (required).")
    parser.add_argument("script_path", help="Path to the script to run.")
    parser.add_argument("script_args", nargs="*", help="Args passed to the script.")
    args = parser.parse_args()

    script_path = Path(args.script_path).resolve()
    if not script_path.exists():
        raise FileNotFoundError(f"Script not found: {script_path}")

    LOGS_DIR.mkdir(parents=True, exist_ok=True)

    schema_sha = sha256_file(SCHEMA_PATH) if SCHEMA_PATH.exists() else None
    db_sha_before = sha256_file(DB_PATH) if DB_PATH.exists() else None

    cmd = [sys.executable, str(script_path)] + list(args.script_args)
    
    # Load STATE.json to find active_session_id
    try:
        data = json.loads(STATE_PATH.read_text(encoding="utf-8"))
        active_sid = data.get("active_session_id")
    except Exception:
        active_sid = None

    env = os.environ.copy()
    env["SOLOB_RECORDED_RUN"] = "1"
    env["SOLOB_HUMAN_INTENT"] = args.intent
    
    if active_sid:
        env["RUN_RECORDED_SID"] = active_sid
    else:
        # Generate run-local sid
        from datetime import datetime, timezone
        utc_stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        env["RUN_RECORDED_SID"] = f"S_{utc_stamp}_RUN_RECORDED"

    # Force UTF-8 to avoid Windows console encoding issues
    env["PYTHONUTF8"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"

    proc = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=env,
    )

    run_tag = script_path.stem
    out_path = LOGS_DIR / f"{run_tag}.stdout.log"
    err_path = LOGS_DIR / f"{run_tag}.stderr.log"
    out_path.write_text(proc.stdout, encoding="utf-8", errors="replace")
    err_path.write_text(proc.stderr, encoding="utf-8", errors="replace")

    db_sha_after = sha256_file(DB_PATH) if DB_PATH.exists() else None

    log_event(
        action="run_script",
        human_intent=args.intent,
        payload={"cmd": cmd},
        artifacts={
            "exit_code": proc.returncode,
            "stdout_path": str(out_path.as_posix()),
            "stderr_path": str(err_path.as_posix()),
            "schema_sha256": schema_sha,
            "db_sha256_before": db_sha_before,
            "db_sha256_after": db_sha_after,
        },
    )

    # Print back to console (already UTF-8 replaced)
    print(proc.stdout, end="")
    if proc.stderr:
        print(proc.stderr, file=sys.stderr, end="")

    return proc.returncode


if __name__ == "__main__":
    raise SystemExit(main())
