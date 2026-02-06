#!/usr/bin/env python3
"""
STATE_HISTORY Auto-Formatter (Human-Run Only)

IMPORTANT: This tool MUST be run explicitly by a human operator.
It modifies STATE_HISTORY.md, which is an append-only governance log.

Purpose:
- Upgrades legacy entries to standard format (adds UTC timestamps)
- Fixes common spacing/formatting issues
- Preserves all semantic content

Safety:
- Creates backup before modification (.bak file)
- Dry-run mode by default (preview changes)
- Requires --apply flag to actually modify file
- Logs all changes for audit trail

Usage:
    # Preview changes (safe, no modifications)
    python tools/format_state_history.py
    
    # Apply changes (requires explicit --apply flag)
    python tools/format_state_history.py --apply

Exit Codes:
    0 = Success (or dry-run completed)
    1 = Formatting errors
    2 = File not found or parse error
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import List, Tuple

# Patterns
STANDARD_FORMAT_RE = re.compile(
    r"^(\s*-\s+)"  # Prefix
    r"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}-05:00)"  # Local time
    r"(\s+\(UTC\s+)"  # " (UTC "
    r"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z)"  # UTC time
    r"(\)\s+-\s+)"  # ") - "
    r"(.+)"  # Rest of line
)

LEGACY_FORMAT_RE = re.compile(
    r"^(\s*-\s+)"  # Prefix
    r"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}-05:00)"  # Local time
    r"(\s+-\s+)"  # " - "
    r"(.+)"  # Rest of line
)


def local_to_utc(local_time_str: str) -> str:
    """Convert Kingston local time (UTC-5) to UTC"""
    try:
        # Parse local time (assumes Kingston UTC-5)
        local_dt = datetime.fromisoformat(local_time_str.replace("-05:00", ""))
        
        # Add 5 hours to convert to UTC
        utc_dt = local_dt + timedelta(hours=5)
        
        # Format as UTC
        return utc_dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    except Exception as e:
        print(f"Warning: Failed to convert time {local_time_str}: {e}", file=sys.stderr)
        return "YYYY-MM-DDTHH:MM:SSZ"


def format_entry(line: str) -> Tuple[str, bool]:
    """
    Format a single entry line.
    Returns: (formatted_line, was_changed)
    """
    # Skip non-entry lines
    if not line.strip() or line.strip().startswith("#"):
        return line, False
    
    # Already in standard format
    if STANDARD_FORMAT_RE.match(line):
        return line, False
    
    # Try to upgrade legacy format
    legacy_match = LEGACY_FORMAT_RE.match(line)
    if legacy_match:
        prefix, local_time, separator, rest = legacy_match.groups()
        
        # Convert local to UTC
        utc_time = local_to_utc(local_time)
        
        # Rebuild in standard format
        formatted = f"{prefix}{local_time} (UTC {utc_time}) - {rest}"
        return formatted, True
    
    # Not a recognizable entry format
    return line, False


def format_state_history(input_path: Path, dry_run: bool = True) -> Tuple[List[str], int]:
    """
    Format STATE_HISTORY.md entries.
    Returns: (formatted_lines, change_count)
    """
    try:
        lines = input_path.read_text(encoding="utf-8").splitlines(keepends=True)
    except Exception as e:
        print(f"[ERROR] Failed to read file: {e}", file=sys.stderr)
        return [], 0
    
    formatted_lines = []
    change_count = 0
    
    for idx, line in enumerate(lines, start=1):
        formatted, changed = format_entry(line.rstrip("\r\n"))
        
        # Preserve original line endings
        if line.endswith("\r\n"):
            formatted += "\r\n"
        elif line.endswith("\n"):
            formatted += "\n"
        
        formatted_lines.append(formatted)
        
        if changed:
            change_count += 1
            if dry_run:
                print(f"[PREVIEW] Line {idx} would be changed:")
                print(f"  Before: {line.rstrip()}")
                print(f"  After:  {formatted.rstrip()}")
                print()
    
    return formatted_lines, change_count


def main() -> int:
    ap = argparse.ArgumentParser(description="Format STATE_HISTORY.md (human-run only)")
    ap.add_argument(
        "--state-history",
        default="docs/STATE_HISTORY.md",
        help="Path to STATE_HISTORY.md (default: docs/STATE_HISTORY.md)"
    )
    ap.add_argument(
        "--apply",
        action="store_true",
        help="Apply changes (default: dry-run preview only)"
    )
    args = ap.parse_args()
    
    state_history_path = Path(args.state_history)
    
    if not state_history_path.exists():
        print(f"[ERROR] File not found: {state_history_path}", file=sys.stderr)
        return 2
    
    print("STATE_HISTORY Auto-Formatter")
    print("=" * 50)
    print(f"File: {state_history_path}")
    print(f"Mode: {'APPLY (will modify file)' if args.apply else 'DRY-RUN (preview only)'}")
    print()
    
    # Format
    formatted_lines, change_count = format_state_history(state_history_path, dry_run=not args.apply)
    
    if change_count == 0:
        print("[OK] No changes needed - all entries already in standard format")
        return 0
    
    print(f"Changes detected: {change_count} entries")
    print()
    
    if not args.apply:
        print("[DRY-RUN] No files modified. Run with --apply to make changes.")
        print()
        print("To apply changes:")
        print(f"  python {Path(__file__).name} --apply")
        return 0
    
    # Create backup
    backup_path = state_history_path.with_suffix(".md.bak")
    try:
        shutil.copy2(state_history_path, backup_path)
        print(f"[BACKUP] Created: {backup_path}")
    except Exception as e:
        print(f"[ERROR] Failed to create backup: {e}", file=sys.stderr)
        return 1
    
    # Write formatted file
    try:
        state_history_path.write_text("".join(formatted_lines), encoding="utf-8")
        print(f"[APPLIED] {change_count} entries formatted")
        print(f"[OK] {state_history_path} updated")
        print()
        print("Backup preserved at: {backup_path}")
        return 0
    except Exception as e:
        print(f"[ERROR] Failed to write file: {e}", file=sys.stderr)
        print(f"[RECOVERY] Backup available at: {backup_path}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
