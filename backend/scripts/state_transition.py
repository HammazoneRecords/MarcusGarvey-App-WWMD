from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
STATE_PATH = BASE_DIR / "docs" / "STATE.json"
HISTORY_PATH = BASE_DIR / "docs" / "STATE_HISTORY.md"

VALID_STATES = {"OBSERVE", "RECORD", "EXECUTE"}


def parse_offset_ts(ts: str) -> datetime:
    """
    Accepts:
      - 2025-12-21T22:49:50-05:00
      - 2025-12-22T03:49:50Z
    Returns timezone-aware datetime.
    """
    ts = ts.strip()
    if ts.endswith("Z"):
        ts = ts[:-1] + "+00:00"
    dt = datetime.fromisoformat(ts)
    if dt.tzinfo is None:
        raise ValueError("Timestamp must include timezone offset, e.g. -05:00, or end with Z.")
    return dt


def now_local_offset() -> datetime:
    return datetime.now().astimezone()


def utc_z(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def read_state() -> dict:
    if not STATE_PATH.exists():
        raise FileNotFoundError(f"Missing {STATE_PATH}")
    return json.loads(STATE_PATH.read_text(encoding="utf-8"))


def write_state(d: dict) -> None:
    STATE_PATH.write_text(
        json.dumps(d, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def append_history(line: str, add_heading: bool) -> None:
    HISTORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not HISTORY_PATH.exists():
        HISTORY_PATH.write_text("### Notes\n", encoding="utf-8")

    with HISTORY_PATH.open("a", encoding="utf-8") as f:
        if add_heading:
            f.write("\n\n### Notes\n")
        f.write("\n" + line)


def main() -> int:
    ap = argparse.ArgumentParser(description="Change STGRAIL state + append STATE_HISTORY entry.")
    ap.add_argument("--to", required=True, help="Target state: OBSERVE | RECORD | EXECUTE")
    ap.add_argument("--note", required=True, help="Why this transition happened (human-readable).")
    ap.add_argument(
        "--at",
        default=None,
        help="Optional explicit timestamp (offset-style), e.g. 2025-12-21T22:49:50-05:00",
    )
    ap.add_argument(
        "--heading",
        action="store_true",
        help='Optional: insert a "### Notes" separator before appending the line.',
    )
    ap.add_argument(
        "--confirm",
        required=True,
        help='Safety latch. Must be EXACTLY: YES_I_MEAN_IT',
    )
    args = ap.parse_args()

    if args.confirm != "YES_I_MEAN_IT":
        raise SystemExit("Blocked: --confirm must be exactly YES_I_MEAN_IT")

    to_state = args.to.strip().upper()
    if to_state not in VALID_STATES:
        raise SystemExit(f"Blocked: --to must be one of {sorted(VALID_STATES)}")

    # NOTE MUST NOT BE BLANK (prevents meaningless / AI-abusable transitions)
    note = (args.note or "").strip()
    if not note:
        raise SystemExit("Blocked: --note is required and cannot be blank.")

    d = read_state()
    from_state = str(d.get("state", "UNKNOWN")).upper()

    dt_local = parse_offset_ts(args.at) if args.at else now_local_offset()
    local_str = dt_local.isoformat(timespec="seconds")
    utc_str = utc_z(dt_local)

    # Update STATE.json
    d["state"] = to_state
    write_state(d)

    # Append STATE_HISTORY (using ASCII-safe symbols to prevent encoding ghosts)
    line = f"- {local_str} (UTC {utc_str}) - {from_state} -> {to_state} - {note}"
    append_history(line, add_heading=args.heading)

    print("STATE =>", to_state)
    print("STATE_HISTORY appended:")
    print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
