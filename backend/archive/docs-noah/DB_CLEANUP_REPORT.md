# Database Cleanup Report

## Issue Identified

**Two database files exist:**
1. [OK] `data/memory.db` - **Active database** (31 anchors, 2,999 chunks)
2. [ERROR] `data/solob.db` - **Empty/uninitialized** (no tables)

## Root Cause Analysis

**Code grep results:**
- [OK] **All scripts use `memory.db`** (30+ references found)
- [ERROR] **Zero references to `solob.db`** in codebase

**Conclusion:** `solob.db` was created accidentally (possibly by a script
that defaulted to this name before the codebase standardized on `memory.db`).

---

## Canonical Database: `memory.db`

**Evidence from schema.sql:**
```sql
-- Solob Wrapper V1.1 ? Canonical SQLite Schema
-- Database role: Index + provenance ledger (NOT source of truth)
```

**Evidence from codebase:**
All 30+ scripts reference `data/memory.db`:
- `scripts/init_db.py`
- `scripts/sanity_check.py`
- `scripts/register_anchors_from_registry.py`
- `scripts/audit_anchor_coherence.py`
- All ingestion/audit/prosecutor scripts
- PowerShell harnesses (`mw_full_proof.ps1`, etc.)

---

## Current Database Status (memory.db)

**From audit:**
```
Anchors: 31 total
  - Status: canon
  - Types: lexicon (26), book (4), letter (1)

Chunks: 2,999 total
  - Anchors with chunks: 30
  - Anchors without chunks: 1
    -> to_my_son_v1 (PDF exists, 5,256,436 bytes)
      This is NOT a system failure - it's a missing ingestion event
```

---

## Recommended Action: Remove solob.db

### Process to Enter RECORD State

Per `docs/v1-scope.md` and STGRAIL discipline:

```powershell
# 1. Enter RECORD state (write-enabled)
.\tools\solob.ps1 record -note "cleanup: remove empty solob.db ghost file"

# 2. Remove the empty database
Remove-Item data\solob.db

# 3. Verify it's gone
Test-Path data\solob.db  # Should return False

# 4. Return to OBSERVE state
.\tools\solob.ps1 observe -note "cleanup complete: removed empty solob.db"
```

### Why This Is Safe

1. **No code references it** - Nothing will break
2. **It's empty** - No data loss
3 **memory.db is canonical** - All operations use the correct DB
4. **STGRAIL witnessed** - State transition is logged

---

## Prevention: Add Validation

To prevent ghost DBs in the future, consider adding to `sanity_check.py`:

```python
def check_for_ghost_dbs():
    """Warn if non-canonical DB files exist."""
    data_dir = Path("data")
    db_files = list(data_dir.glob("*.db"))
    
    canonical = data_dir / "memory.db"
    ghosts = [f for f in db_files if f != canonical]
    
    if ghosts:
        print(f"[WARN]  Ghost database files found: {ghosts}")
        print(f"   Only {canonical} should exist")
        return False
    return True
```

---

## Summary

**Action Required:**
1. Enter RECORD state
2. Remove `data/solob.db`
3. Return to OBSERVE state

**No Code Changes Needed:** All scripts already use correct database.

**Impact:** Zero (file is empty and unused)

**Status:** Ready for cleanup when you enter next RECORD window.
