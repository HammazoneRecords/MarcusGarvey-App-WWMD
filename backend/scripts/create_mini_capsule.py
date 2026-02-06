#!/usr/bin/env python3
"""
Mini Capsule Generator

Creates mini capsule files with synchronized local timestamps.
Mini capsules are smaller summary documents for quick session snapshots.

Usage:
    python scripts/create_mini_capsule.py --title "Session Summary"
    python scripts/create_mini_capsule.py  # Uses default title
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone, timedelta
from pathlib import Path

# Repository root
BASE_DIR = Path(__file__).resolve().parent.parent

# Mini capsule output directory
MINI_CAPSULE_DIR = BASE_DIR / "ContextCapsuleBOX" / "MINI CAPSULE BOX" / "MINI CAPSULE BOX"

# Kingston timezone (UTC-5)
KINGSTON_TZ = timezone(timedelta(hours=-5))


def get_local_timestamp() -> tuple[str, str]:
    """
    Get current local time in Kingston (UTC-5).
    
    Returns:
        Tuple of (iso_timestamp, filename_timestamp)
        - iso_timestamp: 2025-12-28T19:14:00-05:00
        - filename_timestamp: 2025-12-28_1914
    """
    now = datetime.now(KINGSTON_TZ)
    iso_ts = now.strftime("%Y-%m-%dT%H:%M:%S") + now.strftime("%z")[:3] + ":" + now.strftime("%z")[3:]
    file_ts = now.strftime("%Y-%m-%d_%H%M")
    return iso_ts, file_ts


def generate_mini_capsule(title: str = "Session Summary") -> Path:
    """
    Generate a new mini capsule file.
    
    Args:
        title: Title for the mini capsule
    
    Returns:
        Path to the created file
    """
    iso_ts, file_ts = get_local_timestamp()
    
    # Ensure directory exists
    MINI_CAPSULE_DIR.mkdir(parents=True, exist_ok=True)
    
    filename = f"AI_MINI_CAPSULE_{file_ts}.md"
    filepath = MINI_CAPSULE_DIR / filename
    
    # Template content
    content = f"""# AI Mini Capsule - {title}

**Date**: {iso_ts}  
**Session ID**: [FILL_IN_SID]  
**Type**: [SESSION_SUMMARY|MILESTONE|CHECKPOINT]

---

## Summary

[Brief 1-2 sentence summary of what was accomplished]

---

## Key Accomplishments

- [ ] Item 1
- [ ] Item 2
- [ ] Item 3

---

## Files Modified

- `path/to/file1` - Description
- `path/to/file2` - Description

---

## Next Steps

- [ ] Next task 1
- [ ] Next task 2

---

## Notes

[Any additional context or observations]

---

END OF CAPSULE
"""
    
    filepath.write_text(content, encoding="utf-8")
    return filepath


def main() -> int:
    ap = argparse.ArgumentParser(description="Generate Mini Capsule")
    ap.add_argument("--title", type=str, default="Session Summary",
                    help="Title for the mini capsule")
    args = ap.parse_args()
    
    filepath = generate_mini_capsule(title=args.title)
    
    print(f"[OK] Mini capsule created: {filepath}")
    print(f"   Relative: {filepath.relative_to(BASE_DIR)}")
    print()
    print("Next: Open the file and fill in the template sections.")
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
