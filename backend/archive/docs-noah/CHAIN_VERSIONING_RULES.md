# Chain Constitution Versioning Rules

## Core Principle

**"Canon changes only by version bump; old validators must continue to validate old payload modes."**

---

## Current Versions (LOCKED)

- **CHAIN_SPEC_VERSION:** `"chain/1.0"`
- **PAYLOAD_HASH_MODE:** `"payload_v1"`

These are **IMMUTABLE**. The payload_v1 hash algorithm is frozen forever.

---

## Why Versioning Matters

**Without versioning:**
```python
# Someone "optimizes" the serializer
json.dumps(obj, ensure_ascii=True)  # Changed from False

# RESULT: Every historical chain now fails validation
# All existing receipts show "TAMPERED" even though they're valid
# Court rejects legitimate evidence
```

**With versioning:**
```python
# Old: payload_v1 uses ensure_ascii=False (still works)
# New: payload_v2 uses ensure_ascii=True (new receipts only)
# Validator checks payload_hash_mode and uses correct function
# Historical chains remain valid [OK]
```

---

## Version Bump Rules

### Rule 1: Any Canon Change Requires New Version

**Changes that require version bump:**
- Modifying `canonical_json_bytes()` parameters
- Adding/removing fields from `HASH_EXCLUDE_TOPLEVEL`
- Changing hash algorithm (SHA256 -> SHA3)
- Modifying `CHAIN_FIELDS_TOPLEVEL`
- Changing how `payload_view` is computed

**Example - Need different JSON serialization:**
```python
# [ERROR] WRONG - Silent mutation breaks history
def canonical_json_bytes(obj):
    return json.dumps(obj, indent=2).encode("utf-8")  # BREAKS ALL OLD CHAINS

# [OK] CORRECT - Version bump
PAYLOAD_HASH_MODE_V2 = "payload_v2"

def canonical_json_bytes_v2(obj):
    return json.dumps(obj, indent=2).encode("utf-8")

def compute_payload_hash_v2(receipt):
    view = compute_payload_view(receipt)
    return hashlib.sha256(canonical_json_bytes_v2(view)).hexdigest()
```

### Rule 2: Old Logic Must Coexist (Never Replace)

**[ERROR] WRONG:**
```python
# Replacing old function
def compute_payload_hash(receipt):  # Now uses v2 logic
    # This breaks validation of ALL historical receipts
    ...
```

**[OK] CORRECT:**
```python
# Keep old function unchanged
def compute_payload_hash(receipt):  # Still payload_v1
    view = compute_payload_view(receipt)
    return hashlib.sha256(canonical_json_bytes(view)).hexdigest()

# Add new function alongside
def compute_payload_hash_v2(receipt):  # New payload_v2
    view = compute_payload_view_v2(receipt)
    return hashlib.sha256(canonical_json_bytes_v2(view)).hexdigest()
```

### Rule 3: Validator Must Support All Versions

```python
def validate_chain_fields(receipt):
    payload_mode = receipt.get("payload_hash_mode")
    
    if payload_mode == "payload_v1":
        expected = compute_payload_hash(receipt)  # Use v1 logic
    elif payload_mode == "payload_v2":
        expected = compute_payload_hash_v2(receipt)  # Use v2 logic
    else:
        raise ValidationError(f"Unknown payload_hash_mode: {payload_mode}")
    
    if receipt["payload_hash"] != expected:
        raise ValidationError("payload_hash mismatch (TAMPERED)")
```

---

## Protected Functions (DO NOT MODIFY)

### [WARN] These Functions Are FROZEN for payload_v1

**In `core/chain_constitution.py`:**

1. **`canonical_json_bytes(obj)`**
   - Parameters are constitutional
   - Any change breaks ALL historical chains
   - To modify: Create `canonical_json_bytes_v2()`

2. **`compute_payload_view(receipt)`**
   - Exclusion set is constitutional
   - Cannot customize via parameters
   - To modify: Create `compute_payload_view_v2()`

3. **`compute_payload_hash(receipt)`**
   - Entire algorithm is locked
   - Used by ALL payload_v1 receipts
   - To modify: Create `compute_payload_hash_v2()`

4. **`HASH_EXCLUDE_TOPLEVEL`**
   - Frozenset is immutable
   - Cannot add/remove fields
   - To modify: Create `HASH_EXCLUDE_TOPLEVEL_V2`

---

## exclude_keys Parameter (DEPRECATED & LOCKED)

**In `receipt_chain.py`:**

```python
def compute_payload_view(receipt, *, exclude_keys=None):
    """
    exclude_keys parameter is IGNORED.
    payload_v1 exclusions are CONSTITUTIONAL.
    """
    if exclude_keys is not None and exclude_keys != DEFAULT_HASH_EXCLUDE:
        raise ValueError("Cannot customize exclusions for payload_v1")
    
    return _compute_payload_view_constitution(receipt)
```

**Why this matters:**
- Old API accepted `exclude_keys` parameter
- Looks configurable but isn't (for payload_v1)
- Now explicitly raises error if you try to customize it
- Prevents accidental "helpful refactor" that breaks chains

---

## Migration Path (When You Need payload_v2)

### Step 1: Create New Functions

```python
# In core/chain_constitution.py

PAYLOAD_HASH_MODE_V2 = "payload_v2"

HASH_EXCLUDE_TOPLEVEL_V2 = frozenset({
    "receipt_id",
    "timestamp_utc",
    *CHAIN_FIELDS_TOPLEVEL,
    "new_volatile_field",  # Your new exclusion
})

def canonical_json_bytes_v2(obj):
    # Your new serialization logic
    return json.dumps(obj, indent=2).encode("utf-8")

def compute_payload_view_v2(receipt):
    return {k: v for k, v in receipt.items() if k not in HASH_EXCLUDE_TOPLEVEL_V2}

def compute_payload_hash_v2(receipt):
    view = compute_payload_view_v2(receipt)
    return hashlib.sha256(canonical_json_bytes_v2(view)).hexdigest()
```

### Step 2: Update Emitter

```python
# In receipt_chain.py - add_chain_fields()

r["payload_hash_mode"] = PAYLOAD_HASH_MODE_V2  # Use v2 for new receipts
r["payload_hash"] = compute_payload_hash_v2(r)  # Compute with v2 logic
```

### Step 3: Update Validator

```python
# In validate_receipt.py - validate_chain_fields()

payload_mode = receipt.get("payload_hash_mode")

if payload_mode == "payload_v1":
    expected_hash = compute_payload_hash(receipt)
elif payload_mode == "payload_v2":
    expected_hash = compute_payload_hash_v2(receipt)
else:
    raise ValidationError(f"Unknown payload_hash_mode: {payload_mode}")
```

### Step 4: Keep Old Logic FOREVER

- [OK] payload_v1 functions stay in constitution
- [OK] payload_v2 functions added alongside  
- [OK] Historical receipts validate with v1
- [OK] New receipts validate with v2

---

## Test Requirements

**Before deploying payload_v2:**

1. [OK] All existing tests still pass with v1
2. [OK] New v2 tests pass
3. [OK] Validator correctly routes v1 -> v1 logic, v2 -> v2 logic
4. [OK] Historical receipts still validate correctly

---

## Forbidden Patterns

### [ERROR] Silent Mutation
```python
# DON'T modify existing functions
def canonical_json_bytes(obj):
    return json.dumps(obj, indent=2).encode("utf-8")  # BREAKS HISTORY
```

### [ERROR] Parameter Customization
```python
# DON'T make exclusions configurable
def compute_payload_view(receipt, exclude_keys):
    return {k: v for k, v in receipt.items() if k not in exclude_keys}
```

### [ERROR] Replacing Old Logic
```python
# DON'T remove old functions
# def compute_payload_hash(receipt):  # [ERROR] Commented out - breaks v1 validation
#     ...

def compute_payload_hash_v2(receipt):  # Only v2 exists now - WRONG
    ...
```

---

## Enforcement

1. **Code Review Rule:** Any PR touching `chain_constitution.py` must justify why
2. **Test Rule:** `test_hash_consistency.py` must pass before merge
3. **Documentation Rule:** Version bumps require update to this file

**"If you're modifying the canon, you're probably doing it wrong.  
If you're adding a new version, document the migration path."**

---

## Summary

[OK] payload_v1 is LOCKED  
[OK] Changes require NEW version (payload_v2)  
[OK] Old validators must validate old modes  
[OK] Never silently mutate canon  
[OK] `exclude_keys` parameter is deprecated & enforced  

**"A constitution is not code you refactor. It's code you version."**
