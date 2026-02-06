#!/usr/bin/env python3
"""
STATE_HISTORY Format Validator

Validates STATE_HISTORY.md entries against the canonical format specification.
Complements verify_witness_epoch.py by checking format compliance beyond SID markers.

Usage:
    python tools/validate_state_history_format.py [--state-history docs/STATE_HISTORY.md]

Exit Codes:
    0 = All entries compliant
    1 = Format violations found
    2 = Parse error or file not found
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import List, Dict, Any

# Patterns based on STATE_HISTORY_FORMAT_SPEC.md
EPOCH_RE = re.compile(r"witness\s*epoch\s*:\s*([0-9T:\-\.Z]+)", re.IGNORECASE)
SID_RE = re.compile(r"\(sid=([A-Za-z0-9_\-:]+)\)")
TRANSITION_RE = re.compile(r"\b([A-Z_]+)\s*->\s*([A-Z_]+)\b")

# Standard format: - YYYY-MM-DDTHH:MM:SS-05:00 (UTC YYYY-MM-DDTHH:MM:SSZ) - STATE -> STATE - reason (sid=...)
STANDARD_FORMAT_RE = re.compile(
    r"^\s*-\s+"  # Bullet + space
    r"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}-05:00)"  # Local time
    r"\s+\(UTC\s+"  # " (UTC "
    r"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z)"  # UTC time
    r"\)\s+-\s+"  # ") - "
    r"([A-Z_]+)\s*->\s*([A-Z_]+)"  # Transition
    r"\s+-\s+"  # " - "
    r"(.+?)"  # Reason
    r"\s+\(sid=([A-Za-z0-9_\-:]+)\)"  # SID marker
)

# Legacy format: - YYYY-MM-DDTHH:MM:SS-05:00 - STATE -> STATE - reason
LEGACY_FORMAT_RE = re.compile(
    r"^\s*-\s+"  # Bullet + space
    r"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}-05:00)"  # Local time
    r"\s+-\s+"  # " - "
    r"([A-Z_]+)\s*->\s*([A-Z_]+)"  # Transition
    r"\s+-\s+"  # " - "
    r"(.+)"  # Reason (may or may not have SID)
)

# Transitional format: - YYYY-MM-DDTHH:MM:SS-05:00 (UTC YYYY-MM-DDTHH:MM:SSZ) - STATE -> STATE - reason
TRANSITIONAL_FORMAT_RE = re.compile(
    r"^\s*-\s+"  # Bullet + space
    r"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}-05:00)"  # Local time
    r"\s+\(UTC\s+"  # " (UTC "
    r"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z)"  # UTC time
    r"\)\s+-\s+"  # ") - "
    r"([A-Z_]+)\s*->\s*([A-Z_]+)"  # Transition
    r"\s+-\s+"  # " - "
    r"(.+?)"  # Reason
    r"(?!\s+\(sid=)"  # Negative lookahead for sid
)

VALID_STATES = {"OBSERVE", "RECORD", "EXECUTE", "REPAIR"}


def validate_format(lines: List[str]) -> Dict[str, Any]:
    """Validate STATE_HISTORY.md format compliance"""
    
    violations = []
    warnings = []
    entry_count = 0
    standard_count = 0
    legacy_count = 0
    
    # Find epoch
    epoch_ts = "2025-12-25T07:51:59Z"
    epoch_line = None
    for line in lines:
        match = EPOCH_RE.search(line)
        if match:
            epoch_line = line
            epoch_ts = match.group(1)
            break
    
    if not epoch_line:
        violations.append({
            "type": "missing_epoch",
            "message": "Missing 'Witness Epoch:' declaration in file header"
        })
    
    # Check each line for state transitions
    for idx, line in enumerate(lines, start=1):
        line = line.strip()
        
        # Skip empty lines and headers
        if not line or line.startswith("#"):
            continue
        
        # Check if line contains a transition
        if not TRANSITION_RE.search(line):
            continue
        
        entry_count += 1
        
        # Try to match standard format first
        standard_match = STANDARD_FORMAT_RE.match(line)
        if standard_match:
            standard_count += 1
            local_time, utc_time, from_state, to_state, reason, sid = standard_match.groups()
            
            # Validate states
            if from_state not in VALID_STATES:
                violations.append({
                    "line": idx,
                    "type": "invalid_state",
                    "message": f"Invalid FROM state: {from_state} (valid: {VALID_STATES})"
                })
            if to_state not in VALID_STATES:
                violations.append({
                    "line": idx,
                    "type": "invalid_state",
                    "message": f"Invalid TO state: {to_state} (valid: {VALID_STATES})"
                })
            
            # Validate SID format
            if not sid.startswith("S_"):
                warnings.append({
                    "line": idx,
                    "type": "sid_format",
                    "message": f"SID doesn't start with 'S_': {sid}"
                })
            
            continue

        # Try transitional format (Standard but no SID)
        transitional_match = TRANSITIONAL_FORMAT_RE.match(line)
        if transitional_match:
            # Check if this is post-epoch
            local_time, utc_time, from_state, to_state, reason = transitional_match.groups()
            
            if utc_time >= epoch_ts:
                violations.append({
                    "line": idx,
                    "type": "missing_sid",
                    "message": f"Post-epoch entry missing SID (Epoch: {epoch_ts}, Entry: {utc_time})"
                })
            else:
                standard_count += 1 # Count as standard for metrics
            
            continue
        
        # Try legacy format
        legacy_match = LEGACY_FORMAT_RE.match(line)
        if legacy_match:
            legacy_count += 1
            local_time, from_state, to_state, reason = legacy_match.groups()
            
            # Check if it has SID (legacy with SID is acceptable)
            has_sid = SID_RE.search(reason)
            
            # Validate states
            if from_state not in VALID_STATES:
                violations.append({
                    "line": idx,
                    "type": "invalid_state",
                    "message": f"Invalid FROM state: {from_state}"
                })
            if to_state not in VALID_STATES:
                violations.append({
                    "line": idx,
                    "type": "invalid_state",
                    "message": f"Invalid TO state: {to_state}"
                })
            
            # Warn if missing UTC timestamp (legacy format)
            if not has_sid:
                # Pre-epoch legacy is OK
                warnings.append({
                    "line": idx,
                    "type": "legacy_format",
                    "message": "Legacy format (missing UTC timestamp) - acceptable for pre-epoch"
                })
            else:
                # Has SID but missing UTC - should upgrade
                warnings.append({
                    "line": idx,
                    "type": "missing_utc",
                    "message": "Has SID but missing UTC timestamp (consider upgrading to standard format)"
                })
            
            continue
        
        # If we get here, format doesn't match any known pattern
        if TRANSITION_RE.search(line):
            violations.append({
                "line": idx,
                "type": "format_mismatch",
                "message": f"Transition found but format doesn't match spec: {line[:80]}"
            })
    
    return {
        "total_entries": entry_count,
        "standard_format": standard_count,
        "legacy_format": legacy_count,
        "violations": violations,
        "warnings": warnings
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Validate STATE_HISTORY.md format compliance")
    ap.add_argument(
        "--state-history",
        default="docs/STATE_HISTORY.md",
        help="Path to STATE_HISTORY.md (default: docs/STATE_HISTORY.md)"
    )
    args = ap.parse_args()
    
    state_history_path = Path(args.state_history)
    
    if not state_history_path.exists():
        print(f"[ERROR] File not found: {state_history_path}", file=sys.stderr)
        return 2
    
    try:
        lines = state_history_path.read_text(encoding="utf-8").splitlines()
    except Exception as e:
        print(f"[ERROR] Failed to read file: {e}", file=sys.stderr)
        return 2
    
    result = validate_format(lines)
    
    # Report results
    print(f"STATE_HISTORY Format Validation")
    print(f"=" * 50)
    print(f"Total entries: {result['total_entries']}")
    print(f"Standard format: {result['standard_format']}")
    print(f"Legacy format: {result['legacy_format']}")
    print()
    
    if result['violations']:
        print(f"[FAIL] VIOLATIONS: {len(result['violations'])}")
        print()
        for v in result['violations']:
            line_info = f"L{v['line']}: " if 'line' in v else ""
            print(f"  - {line_info}{v['type']}: {v['message']}")
        print()
    
    if result['warnings']:
        print(f"[WARN] WARNINGS: {len(result['warnings'])}")
        print()
        for w in result['warnings'][:10]:  # Show first 10
            line_info = f"L{w['line']}: " if 'line' in w else ""
            print(f"  - {line_info}{w['type']}: {w['message']}")
        if len(result['warnings']) > 10:
            print(f"  ... and {len(result['warnings']) - 10} more warnings")
        print()
    
    # Exit code
    if result['violations']:
        print("[FAIL] Format violations detected")
        return 1
    elif result['warnings']:
        print("[PASS with warnings] All entries valid, but consider format upgrades")
        return 0
    else:
        print("[PASS] All entries compliant")
        return 0


if __name__ == "__main__":
    sys.exit(main())
