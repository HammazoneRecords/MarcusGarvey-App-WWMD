# Bootstrap Import Pattern (Constitutional)

## Problem We're Solving

**Ad-hoc sys.path manipulation leads to:**
- [ERROR] Duplicate code in every script
- [ERROR] Inconsistent path logic
- [ERROR] "Quick fix" patterns that become technical debt
- [ERROR] Risk of shadow canons (local re-implementations)

## The Constitutional Pattern

**One file defines the rule:** `scripts/_bootstrap_imports.py`

**Every script follows the pattern:**
```python
# At the very top of any runnable script
from _bootstrap_imports import ensure_repo_root
ensure_repo_root(__file__)

# Now you can import from core/, utils/, etc.
from utils.sid import get_active_sid
from core.chain_constitution import compute_payload_hash
```

## Why This Matters

### Before (Ad-hoc Pattern)
```python
# chunk_tms_pages_pilot.py
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils.sid import get_active_sid

# validate_receipt.py  
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from core.chain_constitution import compute_payload_hash

# another_script.py
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
# ... duplicated everywhere
```

**Problems:**
- Duplicated in N scripts
- If path logic needs to change, must update N files
- Easy to forget in new scripts
- No standard way to handle it

### After (Constitutional Pattern)
```python
# chunk_tms_pages_pilot.py
from _bootstrap_imports import ensure_repo_root
ensure_repo_root(__file__)
from utils.sid import get_active_sid

# validate_receipt.py
from _bootstrap_imports import ensure_repo_root
ensure_repo_root(__file__)
from core.chain_constitution import compute_payload_hash

# another_script.py
from _bootstrap_imports import ensure_repo_root
ensure_repo_root(__file__)
```

**Benefits:**
- [OK] One place to change if logic needs update
- [OK] Explicit and searchable (grep for `ensure_repo_root`)
- [OK] Harder to forget (import fails if you don't bootstrap)
- [OK] Self-documenting (name explains what it does)

## Scripts Updated

**Already using bootstrap:**
- [OK] `scripts/validate_receipt.py`
- [OK] `scripts/chunk_tms_pages_pilot.py` (just fixed)

**Should be updated next:**
- All scripts in `scripts/` that import from `utils/` or `core/`
- Any future scripts

## Template for New Scripts

```python
#!/usr/bin/env python3
"""
Your script description here
"""

from __future__ import annotations

# Bootstrap imports (constitutional pattern - do this FIRST)
from _bootstrap_imports import ensure_repo_root
ensure_repo_root(__file__)

# Now safe to import from repo modules
from utils.sid import get_active_sid
from core.chain_constitution import compute_payload_hash

# Rest of your script...
```

## Benefits Over Ad-hoc

| Aspect | Ad-hoc sys.path | Constitutional Bootstrap |
|--------|----------------|-------------------------|
| **Duplicated code** | Every script | Once (in _bootstrap_imports.py) |
| **Maintainability** | Change N files | Change 1 file |
| **Discoverability** | `grep "sys.path"` (messy) | `grep "ensure_repo_root"` (clean) |
| **Enforcement** | Hope devs remember | Import fails without it |
| **Documentation** | Comments in each file | This doc + function name |

## The Rule

**"If your script imports from `core/` or `utils/`, it must bootstrap first."**

No exceptions. No ad-hoc `sys.path` manipulation.

## Verification

**Check for ad-hoc patterns still lurking:**
```bash
# Find scripts that manually manipulate sys.path
grep -r "sys.path.insert" scripts/
```

**Good (uses bootstrap):**
```python
from _bootstrap_imports import ensure_repo_root
ensure_repo_root(__file__)
```

**Bad (ad-hoc):**
```python
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
```

**Fix:** Replace bad pattern with good pattern.

## Summary

**Constitutional pattern for imports:**
1. One file (`_bootstrap_imports.py`) defines the rule
2. Every script calls `ensure_repo_root(__file__)` at the top
3. No ad-hoc `sys.path` manipulation
4. Easier to maintain, harder to drift

**"Constitutionalize the bootstrap. Don't ad-hoc the import."**
