#!/usr/bin/env python3
"""
XL Capsule Generator

Automatically creates an XL capsule file with correct local timestamp.
Ensures filename and content timestamps are synchronized.

Usage:
    python scripts/create_xl_capsule.py [--title "Session Title"]
    
Example:
    python scripts/create_xl_capsule.py --title "Reality 5 Planning Session"
"""

import argparse
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
CAPSULE_DIR = BASE_DIR / "ContextCapsuleBOX" / "XL_CAPSULE_BOX"


def generate_xl_capsule(title: str = None) -> Path:
    """Generate XL capsule with correct timestamps"""
    
    # Get current local time (Kingston, UTC-5)
    now = datetime.now()
    
    # Format for content header (ISO 8601 with timezone)
    local_time_iso = now.strftime("%Y-%m-%dT%H:%M:%S-05:00")
    
    # Format for filename (compact: YYYYMMDD_HHMM)
    filename_time = now.strftime("%Y-%m-%d_%H%M")
    
    # Create filename
    capsule_filename = f"AI_XL_CAPSULE_{filename_time}.md"
    capsule_path = CAPSULE_DIR / capsule_filename
    
    # Ensure directory exists
    CAPSULE_DIR.mkdir(parents=True, exist_ok=True)
    
    # Default title if not provided
    if not title:
        title = "[Session Title - Fill This In]"
    
    # Template
    template = f"""# AI XL CAPSULE - {title}
**Date**: {local_time_iso}  
**Session ID**: S_XXXXXXXX_XXXXXXXX  
**Mode**: RECORD  
**Agent**: Antigravity (Google DeepMind)

---

## Executive Summary

[Provide high-level summary of session accomplishments]

**Key Metrics**:
- **[Metric 1]**: [Value]
- **[Metric 2]**: [Value]
- **[Metric 3]**: [Value]

---

## Major Accomplishments

### 1. [Accomplishment 1]

**Problem**: [What was the issue?]

**Solution**: [What did you do?]

**Impact**: [What changed?]

---

### 2. [Accomplishment 2]

**Problem**: [What was the issue?]

**Solution**: [What did you do?]

**Impact**: [What changed?]

---

## Technical Details

[Add technical deep dives here]

---

## Evidence & Verification

**Court Sweep**: [Bundle ID if applicable]

**Verdict**: [PASS/NO-GO]

**Files Modified/Created**: [List key files]

---

## Lessons Learned

### 1. [Lesson 1]
[Explanation]

### 2. [Lesson 2]
[Explanation]

---

## Next Steps

[What comes next?]

---

## Honorable Mentions (16 Bars)

```
[Add 16 bars here if you're feeling creative]
```

---

## Metadata

**Files Created**: N  
**Files Modified**: N  
**Lines of Code**: ~XXX  
**Documentation Pages**: N  
**CHANGELOG Entries**: N  

**Session Duration**: ~XX minutes  
**[Type] Completed**: N  

---

END OF XL CAPSULE
"""
    
    # Write file
    capsule_path.write_text(template, encoding="utf-8")
    
    return capsule_path


def main() -> int:
    ap = argparse.ArgumentParser(description="Generate XL Capsule with correct timestamps")
    ap.add_argument("--title", type=str, help="Session title for the capsule")
    args = ap.parse_args()
    
    capsule_path = generate_xl_capsule(title=args.title)
    
    # Get current time for display
    now = datetime.now()
    local_time_display = now.strftime("%Y-%m-%dT%H:%M:%S-05:00")
    
    print(f"[DONE] XL Capsule created: {capsule_path.relative_to(BASE_DIR)}")
    print(f"[DONE] Local timestamp: {local_time_display}")
    print(f"[DONE] Filename: {capsule_path.name}")
    print(f"\nNext steps:")
    print(f"  1. Fill in the session title")
    print(f"  2. Add Session ID (if applicable)")
    print(f"  3. Complete all [bracketed] sections")
    print(f"  4. Add accomplishments and details")
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
