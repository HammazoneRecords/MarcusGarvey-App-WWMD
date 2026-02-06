# Chain Constitution Implementation Summary

## Date: 2025-12-26

## What Was Built

A **constitutional chain implementation** for the Solob Wrapper receipt system, layering optional Merkle chains on top of the existing receipt infrastructure with strict anti-drift guarantees.

---

## Core Philosophy

**"Proof is for skeptics. Receipts are for participants."**

Chains are **optional** (most receipts don't use them), but when present, they are **strict** (complete and verified). The system optimizes for continuity rather than persuasion.

**"A Merkle chain is a scar, not a tattoo."** - Chains aren't decorative proof. They're recorded participation.

---

## Three-Layer Anti-Drift Protection

### 1. Single Source of Truth (`core/chain_constitution.py`)
- [OK] ONE canonical implementation for payload_v1
- [OK] Immutable hash algorithm (frozen)
- [OK] Both emitter and validator import from same source
- [OK] No duplicate logic anywhere

### 2. Import Stability (`scripts/_bootstrap_imports.py`)
- [OK] Works from any CWD (repo root or scripts/)
- [OK] Prevents "import failed -> quick fix with local copy" pattern
- [OK] No temptation to duplicate functions

### 3. Versioning Discipline (Enforced Rules)
- [OK] `exclude_keys` parameter raises error if misused
- [OK] Explicit "DO NOT MODIFY" warnings in code
- [OK] Version bump rules documented
- [OK] Migration path defined for payload_v2

---

## Constitutional Lock (payload_v1)

### Frozen Functions
These cannot be modified without creating payload_v2:

1. `canonical_json_bytes()` - JSON serialization is constitutional
2. `compute_payload_view()` - Exclusion set is locked  
3. `compute_payload_hash()` - Hash algorithm is immutable
4. `HASH_EXCLUDE_TOPLEVEL` - Frozenset cannot change

**Attempting customization:**
```python
compute_payload_view(receipt, exclude_keys=custom)
# Raises: ValueError("Cannot customize exclusions for payload_v1")
```

---

## Chain Specification (chain/1.0)

### Required Fields (All-or-Nothing)
- `chain_id`: Chain identifier
- `chain_spec`: "chain/1.0" (version lock)
- `sequence`: Position in chain (0 = genesis)
- `payload_hash`: SHA256 of canonical payload view
- `payload_hash_mode`: "payload_v1" (algorithm lock)
- `sealed`: Must be `true`

### Genesis Purity (Strictest Enforcement)
- **sequence == 0:** Must NOT have `integrity.previous_receipt_sha256` key (not even as decoration)
- **sequence > 0:** MUST have valid `integrity.previous_receipt_sha256` (64-char hex)

### Payload Hash (payload_v1 Contract)
**Excludes (top-level only):**
- `receipt_id`, `timestamp_utc` (volatile)
- All chain fields: `chain_id`, `chain_spec`, `sequence`, `payload_hash`, `payload_hash_mode`, `sealed`

**Includes:**
- `integrity.previous_receipt_sha256` (linkage is semantic)
- Everything else in receipt

This makes `payload_hash` represent: **"this payload as-linked in this chain position"**

---

## Validator Hardening (4 Critical Fixes)

### 1. Strengthened `has_previous` Logic
```python
# Before: Just checked key existence
has_previous = "previous_receipt_sha256" in integrity

# After: Ensures non-empty string
has_previous = isinstance(prev_hash, str) and len(prev_hash) > 0
```

### 2. Eliminated ImportError Bypass
```python
# Before: Silent bypass if import fails
try:
    from receipt_chain import compute_payload_hash
except ImportError:
    pass  # ?? Hash verification skipped!

# After: Always validates (sovereign implementation)
from core.chain_constitution import compute_payload_hash
# Import guaranteed by bootstrap
```

### 3. Strictest Genesis Purity
```python
# Before: Only rejected truthy values
if has_previous:  # Allowed key with empty string

# After: Rejects key existence at all
if "previous_receipt_sha256" in integrity:  # Even as decoration
    raise ValidationError("fake genesis attack blocked")
```

### 4. Fixed Indentation Bug
Corrected spacing on `# Validate payload_hash_mode` comment.

---

## Test Coverage

### Hash Consistency (3/3 PASS)
- [OK] Exclusion sets match (constitution vs implementations)
- [OK] Hash implementations identical (all three produce same output)
- [OK] CHAIN_FIELDS constants match

### Chain Tests (6/6 PASS)
1. [OK] Normal receipt (no chain)
2. [OK] Chain-enabled receipt (with chain)
3. [OK] Chain linkage verification
4. [OK] Backward compatibility (old receipts work)
5. [OK] Incomplete chain rejected
6. [OK] Fake genesis rejected (genesis purity enforced)

---

## Documentation Created

1. **`core/chain_constitution.py`**
   - Single canonical implementation
   - Versioning rules in docstring
   - DO NOT MODIFY warnings

2. **`docs/CHAIN_VERSIONING_RULES.md`**
   - Version bump requirements
   - Migration path to payload_v2  
   - Forbidden patterns
   - Coexistence rules

3. **`docs/IMPORT_STABILITY.md`**
   - Bootstrap usage guide
   - Anti-drift strategy
   - Pattern for new scripts

4. **`docs/RECEIPT_CHAIN_LAYERING.md`** *(existing, updated)*
   - Chain philosophy
   - Optional-but-strict principle

5. **`docs/RECEIPT_CHAIN_IMPLEMENTATION.md`** *(existing, updated)*
   - Implementation summary
   - Test results

6. **`docs/v1-scope.md`** *(updated)*
   - Added chain constitution to guarantees
   - Added `core/` folder to navigation
   - Added chain docs to governance section

---

## Files Modified

### Core Implementation
- `core/chain_constitution.py` - Created (constitutional canon)
- `utils/receipt_chain.py` - Now delegates to constitution
- `scripts/validate_receipt.py` - Imports from constitution, removed local hash

### Bootstrap
- `scripts/_bootstrap_imports.py` - Created (import stability)

### Tests
- `scripts/test_hash_consistency.py` - Updated to verify constitution
- `scripts/test_receipt_chain_optional.py` - All 6 tests pass

### Documentation
- `docs/CHAIN_VERSIONING_RULES.md` - Created
- `docs/IMPORT_STABILITY.md` - Created  
- `docs/v1-scope.md` - Updated with chain constitution

---

## Enforcement Mechanisms

### Code Level
1. **Frozensets** - CHAIN_FIELDS_TOPLEVEL and HASH_EXCLUDE_TOPLEVEL are immutable
2. **Parameter Validation** - exclude_keys raises ValueError if misused
3. **Import Bootstrap** - Prevents path-dependent failures
4. **Single Source** - No duplicate implementations exist

### Test Level
1. **Hash Consistency Tests** - Catch drift immediately
2. **Chain Tests** - Verify all rules enforced
3. **Import Tests** - Works from any directory

### Documentation Level
1. **Explicit Warnings** - "DO NOT MODIFY THIS FUNCTION"
2. **Version Bump Rules** - Documented migration path
3. **Forbidden Patterns** - Listed with examples

---

## Key Principles

1. **"Optional but strict"** - Chains are optional, but when present, all rules enforced
2. **"Constitution, not Configuration"** - payload_v1 is locked, not customizable  
3. **"Version, don't mutate"** - Changes require payload_v2, never silent edits
4. **"One canon, two delegators"** - Constitution is truth, others just import it
5. **"Scar, not tattoo"** - Chains record participation, not decoration

---

## Status

[OK] **COMPLETE**

- Constitutional implementation frozen
- Anti-drift protection active
- Tests passing (9/9)
- Documentation comprehensive
- v1-scope.md updated

**"The constitution is physical law. You don't refactor physics. You version to physics_v2."**

---

## Next Steps (Future)

When payload_v2 is needed:
1. Create new functions in `chain_constitution.py` (coexist, don't replace)
2. Update emitter to use v2 for new receipts
3. Update validator to route based on `payload_hash_mode`
4. Keep v1 logic FOREVER (historical validation)

**Historical chains are sacred. They stay valid forever.**
