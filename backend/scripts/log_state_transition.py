#!/usr/bin/env python3
"""
State History Transition Logger (Helper)
Ensures every entry in STATE_HISTORY.md follows the canonical V1.0 spec.
Automatically fetches the current SID from STATE.json.
"""
import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
STATE_JSON_PATH = BASE_DIR / 'docs' / 'STATE.json'
STATE_HISTORY_PATH = BASE_DIR / 'docs' / 'STATE_HISTORY.md'

def get_current_sid():
    """Load active session ID from STATE.json."""
    try:
        if STATE_JSON_PATH.exists():
            with open(STATE_JSON_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('active_session_id', 'NO_SID_FOUND')
    except Exception:
        pass
    return "UNKNOWN_SID"

def format_timestamps():
    """Generate local (-05:00) and UTC (Z) timestamps."""
    now_utc = datetime.now(timezone.utc)
    # Local Kingston time is UTC-5
    from datetime import timedelta
    now_local = now_utc - timedelta(hours=5)
    
    ts_local = now_local.strftime('%Y-%m-%dT%H:%M:%S-05:00')
    ts_utc = now_utc.strftime('%Y-%m-%dT%H:%M:%S%Z').replace('UTC', 'Z')
    if not ts_utc.endswith('Z'): # Fallback
         ts_utc = now_utc.strftime('%Y-%m-%dT%H:%M:%SZ')
    
    return ts_local, ts_utc

def log_transition(from_state, to_state, reason, sid=None, is_note=False):
    """Append a formatted entry to STATE_HISTORY.md."""
    ts_local, ts_utc = format_timestamps()
    if not sid:
        sid = get_current_sid()
    
    if is_note:
        entry = f"- {ts_local} (UTC {ts_utc})  NOTE  {reason}"
    else:
        entry = f"- {ts_local} (UTC {ts_utc}) - {from_state} -> {to_state} - {reason} (sid={sid})"
    
    with open(STATE_HISTORY_PATH, 'a', encoding='utf-8') as f:
        f.write(f"\n{entry}")
    
    return entry

def main():
    parser = argparse.ArgumentParser(description="Log a state transition or note to STATE_HISTORY.md")
    parser.add_argument("--note", help="Log as a NOTE entry rather than a transition.")
    parser.add_argument("--from", dest="from_state", help="The source state (e.g., OBSERVE).")
    parser.add_argument("--to", dest="to_state", help="The target state (e.g., RECORD).")
    parser.add_argument("--reason", help="The reason for the transition/note.")
    parser.add_argument("--sid", help="Override the SID (optional).")

    args = parser.parse_args()

    if args.note:
        entry = log_transition(None, None, args.note, is_note=True)
    elif args.from_state and args.to_state and args.reason:
        entry = log_transition(args.from_state.upper(), args.to_state.upper(), args.reason, sid=args.sid)
    else:
        parser.print_help()
        print("\nError: Must provide --note OR (--from, --to, --reason)")
        return 1

    print(f"Logged: {entry}")
    return 0

if __name__ == "__main__":
    exit(main())
