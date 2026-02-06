# Pre-Flight Balance Check - User Guide

## Overview

**Script:** `scripts/preflight_balance_check.py`

**Purpose:** Verify system balance before progression - ensures constitution integrity, import stability, database coherence, and receipt validation.

**Returns:**
- Exit code 0 (GO) - All checks pass
- Exit code 1 (NO-GO) - Issues found

---

## Usage

### Run Full Check

```bash
python scripts/preflight_balance_check.py
```

### Check Sections

The script validates:

**[A] Constitution + Drift Tripwires**
- Verifies `core/chain_constitution.py` exists
- Checks identity lock (direct aliases)
- Runs drift detection tests

**[B] Import Stability**
- Scans for ad-hoc `sys.path.insert` usage
- Verifies bootstrap pattern adoption
- Lists non-compliant scripts

**[C] Database Coherence**
- Confirms canonical DB (`data/memory.db`)
- Checks anchor/chunk counts
- Detects ghost DB files

**[D] Receipt Schema Compliance**
- Finds all receipts in `evidence/**/*.json`
- Validates each receipt
- Reports pass/fail counts

**[E] Balanced Level Summary**
- Aggregates all results
- Provides GO/NO-GO decision

---

## Output Examples

### GO (All Passed)

```
======================================================================
PRE-FLIGHT BALANCE CHECK
======================================================================

[A] Constitution + Drift Tripwires
----------------------------------------------------------------------
[OK] Constitution: All exports present
[OK] Identity Lock: Direct aliases verified
[OK] Drift Tests: Tripwire passing

[B] Import Stability
----------------------------------------------------------------------
[WARN] Imports: 9 scripts with ad-hoc sys.path
  - scripts/test_receipt_chain_optional.py:31
  - scripts/test_hash_consistency.py:29
  - scripts/emit_receipt.py:263
  ... and 6 more

[C] Database Coherence
----------------------------------------------------------------------
[OK] Database: 31/31 canon anchors, 3,383 chunks, 0 orphans

[D] Receipt Schema Compliance
----------------------------------------------------------------------
[OK] Receipts: 145/145 valid

======================================================================
DECISION: GO - System balanced
======================================================================
```

**Exit Code:** 0

---

### NO-GO (Issues Found)

```
======================================================================
PRE-FLIGHT BALANCE CHECK
======================================================================

[A] Constitution + Drift Tripwires
----------------------------------------------------------------------
[FAIL] Constitution:
  - Cannot import chain_constitution: No module named 'core'

[B] Import Stability
----------------------------------------------------------------------
[WARN] Imports: 9 scripts with ad-hoc sys.path

[C] Database Coherence
----------------------------------------------------------------------
[FAIL] Database:
  - Canon anchors without chunks: 1 (expected 0)
  - Ghost DB file: data/solob.db (non-canonical, should be in orphans/)

[D] Receipt Schema Compliance
----------------------------------------------------------------------
[FAIL] Receipts: 130/145 valid (15 failed)
  - evidence/S_XYZ/RECEIPTS/R_BAD.json
    Error: Missing required field: integrity.receipt_sha256
  ... and 14 more failures

======================================================================
DECISION: NO-GO - Fix issues before proceeding
======================================================================
```

**Exit Code:** 1

---

## What Each Section Checks

### Constitution (Critical)

[OK] **Pass Criteria:**
- `core/chain_constitution.py` exists
- All required exports present (CHAIN_SPEC_VERSION, PAYLOAD_HASH_MODE, etc.)
- Identity lock verified (`receipt_chain.X is constitution.X`)
- Tripwire test passes

[ERROR] **Failure Examples:**
- Constitution file missing
- Missing exports
- Hash drift detected
- Wrapper functions instead of aliases

### Imports (Warning Level)

[WARN] **Warning Criteria:**
- Scripts using ad-hoc `sys.path.insert`
- Should use `ensure_repo_root(__file__)` pattern

**Note:** This generates warnings, not failures. The system can proceed with import warnings, but should be fixed for long-term stability.

### Database (Critical)

[OK] **Pass Criteria:**
- `data/memory.db` exists
- All canon anchors have chunks (0 without)
- No orphaned chunks
- No ghost DB files outside checkpoints/orphans

[ERROR] **Failure Examples:**
- Missing canonical DB
- Canon anchors without chunks
- Orphaned chunks (not linked to anchors)
- Ghost DB files in data/ root

### Receipts (Critical)

[OK] **Pass Criteria:**
- All receipts validate against schema
- Chain fields (if present) complete and valid
- No JSON parsing errors

[ERROR] **Failure Examples:**
- Invalid JSON
- Missing required fields
- Chain validation errors
- Schema violations

---

## Common Issues & Fixes

### Issue: Hash Drift Detected

**Symptom:**
```
[FAIL] Identity Lock:
  - CRITICAL: Hash drift detected!
```

**Fix:**
1. Check `utils/receipt_chain.py` for local hash implementations
2. Replace with direct aliases:
   ```python
   from core.chain_constitution import compute_payload_hash
   ```
3. Re-run tripwire test

### Issue: Import Stability Warnings

**Symptom:**
```
[WARN] Imports: 9 scripts with ad-hoc sys.path
```

**Fix:**
1. Update each script to use bootstrap:
   ```python
   from _bootstrap_imports import ensure_repo_root
   ensure_repo_root(__file__)
   ```
2. Remove ad-hoc `sys.path.insert` lines

### Issue: Canon Anchors Without Chunks

**Symptom:**
```
[FAIL] Database:
  - Canon anchors without chunks: 1
```

**Fix:**
1. Run coherence audit:
   ```bash
   python scripts/audit_anchor_coherence.py
   ```
2. Identify missing anchor
3. Ingest chunks for that anchor

### Issue: Receipt Validation Failures

**Symptom:**
```
[FAIL] Receipts: 130/145 valid (15 failed)
```

**Fix:**
1. Review first failing receipt path
2. Check validation error message
3. Fix receipt schema or regenerate receipt
4. Re-validate

---

## Integration with Workflow

**When to Run:**

1. **Before major operations**
   - Before ingesting new anchors
   - Before schema migrations
   - Before production deployment

2. **After system changes**
   - After updating constitution
   - After modifying scripts
   - After receipt schema changes

3. **Periodic verification**
   - Weekly/monthly health checks
   - After long development sessions
   - Before archiving work

**Exit Codes:**
- `0` = GO -> Safe to proceed
- `1` = NO-GO -> Fix issues first

---

## Developer Notes

### ASCII-Only Output

All output uses ASCII markers (`[OK]`, `[FAIL]`, `[WARN]`) instead of emoji to avoid Windows cp1252 encoding issues.

### Read-Only

The balance check never modifies:
- Database
- Receipts
- Configuration files

Safe to run repeatedly.

### Performance

**Expected runtime:** <10 seconds

**Bottlenecks:**
- Receipt validation (scans all evidence files)
- Drift tests (runs subprocess)

**Optimization:** Run critical checks first (constitution, DB) before slower receipt validation.

---

## Summary

**Use this script before any major system state change.**

**GO** = System balanced, safe to proceed  
**NO-GO** = Fix issues, then re-check

**ASCII-only, read-only, comprehensive.**
