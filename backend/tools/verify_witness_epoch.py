#!/usr/bin/env python3
"""
verify_witness_epoch.py
Purpose:
  Enforce SID Witness Policy after witness epoch:
  Every transition block after the epoch must contain a "(sid=...)" marker.

Exit codes:
  0 = OK
  2 = violations found
  3 = input missing / parse failure
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from datetime import datetime

EPOCH_RE = re.compile(r"witness\s*epoch\s*:\s*([0-9T:\-\.Z]+)", re.IGNORECASE)
SID_RE = re.compile(r"\(sid=[A-Za-z0-9_\-:]+\)")
# Heuristic: a "transition block" is any line that looks like "STATE_A -> STATE_B"
TRANSITION_RE = re.compile(r"\b([A-Z_]+)\s*->\s*([A-Z_]+)\b")


def parse_epoch(text: str) -> str | None:
    for line in text.splitlines():
        m = EPOCH_RE.search(line)
        if m:
            return m.group(1).strip()
    return None


def iso_to_dt(iso: str) -> datetime:
    # Accept "2025-12-25T07:51:59Z" and also fractional seconds
    if iso.endswith("Z"):
        iso = iso[:-1] + "+00:00"
    return datetime.fromisoformat(iso)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--state-history", default="docs/STATE_HISTORY.md", help="Path to STATE_HISTORY.md")
    ap.add_argument("--epoch-override", default="", help="Override epoch ISO (if file lacks it)")
    ap.add_argument("--show-context", action="store_true", help="Print offending lines with nearby context")
    args = ap.parse_args()

    p = Path(args.state_history)
    if not p.exists():
        print(f"[ERROR] missing file: {p}")
        return 3

    text = p.read_text(encoding="utf-8", errors="replace")

    epoch_iso = args.epoch_override.strip() or parse_epoch(text)
    if not epoch_iso:
        print("[ERROR] witness epoch not found. Add a line like: 'Witness Epoch: 2025-12-25T07:51:59Z'")
        return 3

    try:
        epoch_dt = iso_to_dt(epoch_iso)
    except Exception as e:
        print(f"[ERROR] invalid epoch format: {epoch_iso} ({e})")
        return 3

    lines = text.splitlines()
    violations: list[dict] = []

    # Heuristic: find blocks after epoch by scanning for timestamps in lines.
    # If your STATE_HISTORY format uses lines like: "2025-12-28T03:58:00-05:00 | OBSERVE -> RECORD | ..."
    # we treat anything with an ISO-ish timestamp that parses > epoch_dt as "post-epoch".
    TS_RE = re.compile(r"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})?)")

    for idx, line in enumerate(lines, start=1):
        tsm = TS_RE.search(line)
        trm = TRANSITION_RE.search(line)
        if not (tsm and trm):
            continue

        ts_iso = tsm.group(1)
        try:
            ts_dt = iso_to_dt(ts_iso)
        except Exception:
            # If timestamp is unparseable, skip rather than false-failing.
            continue

        if ts_dt <= epoch_dt:
            continue

        # Post-epoch transition lines must contain SID marker
        if not SID_RE.search(line):
            violations.append({
                "line": idx,
                "timestamp": ts_iso,
                "transition": f"{trm.group(1)} -> {trm.group(2)}",
                "text": line.strip(),
            })

    if violations:
        print(f"[FAIL] witness epoch: {epoch_iso}")
        print(f"[FAIL] violations: {len(violations)}")
        for v in violations:
            print(f"  - L{v['line']}: {v['timestamp']} | {v['transition']} | missing (sid=...)")
            if args.show_context:
                start = max(1, v["line"] - 2)
                end = min(len(lines), v["line"] + 2)
                for j in range(start, end + 1):
                    prefix = ">>" if j == v["line"] else "  "
                    print(f"{prefix} L{j}: {lines[j-1]}")
                print("")
        return 2

    print(f"[OK] witness epoch: {epoch_iso}")
    print("[OK] zero violations")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
