from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
STATE_PATH = BASE_DIR / "docs" / "STATE.json"
HISTORY_PATH = BASE_DIR / "docs" / "STATE_HISTORY.md"


def now_local_offset() -> str:
    # Example: 2025-12-21T20:47:00-05:00
    return datetime.now().astimezone().isoformat(timespec="seconds")


def now_utc_z() -> str:
    # Example: 2025-12-22T01:47:00Z
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def current_state() -> str:
    if not STATE_PATH.exists():
        return "UNKNOWN"
    d = json.loads(STATE_PATH.read_text(encoding="utf-8"))
    return str(d.get("state", "UNKNOWN")).upper()


def ensure_header_exists() -> None:
    HISTORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not HISTORY_PATH.exists():
        HISTORY_PATH.write_text("### Notes\n", encoding="utf-8")


def append_line(line: str) -> None:
    ensure_header_exists()
    with HISTORY_PATH.open("a", encoding="utf-8") as f:
        f.write("\n" + line)


def main() -> int:
    ap = argparse.ArgumentParser(description="Append a note to STATE_HISTORY.md (no state change).")
    ap.add_argument("--note", required=True, help="The note text to append.")
    ap.add_argument("--from", dest="from_state", default=None, help="Optional: explicit FROM state label.")
    ap.add_argument("--to", dest="to_state", default=None, help="Optional: explicit TO state label.")
    args = ap.parse_args()

    ts_local = now_local_offset()
    ts_utc = now_utc_z()

    frm = (args.from_state or current_state()).upper()
    to = (args.to_state or frm).upper()  # default: no transition, just a note

    note = args.note.strip()
    line = f"- {ts_local} (UTC {ts_utc}) ? {frm} -> {to} ? {note}"

    append_line(line)
    print("STATE_HISTORY appended:")
    print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())