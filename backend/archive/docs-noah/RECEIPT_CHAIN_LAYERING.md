# RECEIPT CHAIN LAYERING

**Status:** Active  
**Version:** 1.0  
**Last Updated:** 2025-12-26

---

## Purpose

This document explains **when and how** to use Merkle chains in the receipt system.

**Core principle:**  
Chains are **OPTIONAL** and reserved for Court/Epoch layer receipts only.

---

## The Problem This Solves

Early receipt systems made chaining mandatory, creating unnecessary overhead:
- Normal receipts (ingestion, anchors, etc.) don't need cryptographic linkage
- Chain fields add complexity without proportional value for routine operations
- Validation became slow and brittle

**Solution:**  
Move Merkle chaining to a **lower layer** ? make it **opt-in** for critical receipts only.

---

## When to Use Chains

### [OK] Chain-Enabled Receipt Types (Court/Epoch Layer)

These receipts **should** use chains:

| Receipt Type | Why Chain? |
|--------------|-----------|
| `SEAL_CREATED` | Marks epoch boundaries; must be tamper-evident |
| `EPOCH_DECLARED` | Governance change; forms audit trail |
| `EVIDENCE_BUNDLE_CREATED` | Bundle finalization; cryptographic proof |
| `EVIDENCE_INDEX_REBUILT` | Index snapshot; integrity check |

### [ERROR] Chain-Free Receipt Types (Normal Operations)

These receipts **should NOT** use chains:

| Receipt Type | Why No Chain? |
|--------------|---------------|
| `ANCHOR_ADDED` | Standalone anchor registration |
| `INGESTION_COMPLETED` | Ingestion events are independent |
| `CHUNKING_COMPLETED` | Chunk creation doesn't need linkage |
| `DERIVATION_CREATED` | Interpretations are derivative, not canonical |

---

## Chain Fields Reference

When `--chain` flag is used, these fields are added:

| Field | Type | Description |
|-------|------|-------------|
| `chain_id` | string | Chain identifier (e.g., `"epoch_seals"`) |
| `sequence` | integer | Position in chain (0-indexed) |
| `payload_hash` | sha256 | Hash of receipt payload (pre-signature) |
| `sealed` | boolean | Always `true` for chained receipts |
| `integrity.previous_receipt_hash` | sha256 | Links to previous receipt in chain |

---

## Usage Examples

### 1?? Normal Receipt (No Chain)

```bash
# Emit an ANCHOR_ADDED receipt (no chain)
python scripts/emit_receipt.py \
  --type ANCHOR_ADDED \
  --intent "Register new anchor" \
  --file payload.json
```

**Result:**
```json
{
  "schema_version": "1.0",
  "receipt_type": "ANCHOR_ADDED",
  "receipt_id": "R_20251226T100000Z_ANCHOR_ADDED_test",
  "session_id": "S_20251226T093000Z_MILESTONE",
  "timestamp_utc": "2025-12-26T10:00:00Z",
  "actor": {...},
  "intent": "Register new anchor",
  "links": {},
  "integrity": {"artifacts": [...]},
  "anchor": {...}
}
```

**Note:** No `chain_id`, `sequence`, or `payload_hash` fields.

---

### 2?? Chain-Enabled Receipt (Seal)

```bash
# Emit a SEAL_CREATED receipt WITH chain
python scripts/emit_receipt.py \
  --type SEAL_CREATED \
  --intent "Seal Reality 6" \
  --file seal_payload.json \
  --chain \
  --chain-id "epoch_seals"
```

**Result:**
```json
{
  "schema_version": "1.0",
  "receipt_type": "SEAL_CREATED",
  "receipt_id": "R_20251226T100000Z_SEAL_CREATED_r6",
  "session_id": "S_20251226T093000Z_MILESTONE",
  "timestamp_utc": "2025-12-26T10:00:00Z",
  "actor": {...},
  "intent": "Seal Reality 6",
  "links": {},
  "integrity": {
    "artifacts": [...],
    "previous_receipt_hash": "abc123..."
  },
  "chain_id": "epoch_seals",
  "sequence": 0,
  "payload_hash": "def456...",
  "sealed": true,
  "seal": {...}
}
```

**Note:** Chain fields present. This receipt is now part of a verifiable chain.

---

### 3?? Chain With Explicit Previous Receipt

```bash
# Emit second seal in chain, explicitly linking to previous
python scripts/emit_receipt.py \
  --type SEAL_CREATED \
  --intent "Seal Reality 7" \
  --file seal_payload.json \
  --chain \
  --chain-id "epoch_seals" \
  --previous-receipt evidence/S_20251226.../R_20251226T100000Z_SEAL_CREATED_r6.json
```

**Result:** `sequence: 1`, `integrity.previous_receipt_hash` points to R6 seal

---

## Validation Behavior

### Without Chain Fields (Default)
```python
# Validates:
# - Base schema
# - Type-specific fields
# - Integrity artifacts
# - Actor/intent/timestamps

# Does NOT require:
# - chain_id
# - sequence
# - payload_hash
```

### With Chain Fields (Optional)
```python
# Validates everything above, PLUS:
# - chain_id is non-empty string
# - sequence is non-negative integer
# - payload_hash is valid sha256
# - sealed is boolean
# - previous_receipt_hash is valid sha256 (if present)
```

**Backward compatibility:** Old receipts without chain fields still validate.

---

## Chain Verification

Use `utils/receipt_chain.py` to verify chain integrity:

```python
from pathlib import Path
from utils.receipt_chain import verify_chain, load_receipt

# Load all seals in a chain
seal_paths = sorted(Path("evidence").rglob("*SEAL_CREATED*.json"))
seals = [load_receipt(p) for p in seal_paths if 'chain_id' in load_receipt(p)]

# Verify chain
errors = verify_chain(seals, strict=False)

if errors:
    print("Chain errors:", errors)
else:
    print("Chain verified [OK]")
```

---

## Design Decisions

### Why Optional?

1. **Performance:** Validation is faster when not checking chains
2. **Simplicity:** Most receipts don't need cryptographic linkage
3. **Separation of concerns:** Routine operations vs governance milestones
4. **Backward compatibility:** Old receipts remain valid

### Why Opt-In With Flag?

- **Explicit intent:** Operator must consciously enable chaining
- **Self-documenting:** `--chain` flag signals "this is critical"
- **Mistake prevention:** Prevents accidental chaining of routine receipts

### Why These4 Receipt Types?

These are **epoch boundaries** and **bundle finalizations** ? the moments when:
- Governance changes occur
- Evidence is sealed
- Audit trails become immutable
- External parties may verify integrity

---

## Migration Path

### Existing Receipts (No Chains)
[OK] **No action needed.** They validate as-is.

### Future Seals/Bundles
? **Use `--chain` flag** when emitting Court/Epoch receipts.

### Gradual Adoption
- Phase 1: Add `--chain` to new seals only
- Phase 2: Backfill critical receipts (optional)
- Phase 3: Enforce chain for specific types (future)

---

## Summary

| Aspect | Normal Receipts | Chain-Enabled Receipts |
|--------|----------------|------------------------|
| **Flag** | None | `--chain` |
| **Validation** | Base + type-specific | Base + type + chain |
| **Fields** | Standard only | Standard + chain |
| **Use cases** | Daily operations | Milestones, seals, bundles |
| **Performance** | Fast | Slightly slower |

**Remember:**  
Chains are for **Court**, not **Cartographer**.  
Most receipts don't need them.

---

## Related Documents

- [RECEIPT_SCHEMAS.md](./RECEIPT_SCHEMAS.md) ? Base schema reference
- [RECEIPT_LIFECYCLE_RULES.md](./RECEIPT_LIFECYCLE_RULES.md) ? Lifecycle governance
- [The 7 Classes Of Receipts](./The%207%20Classes%20Of%20Recipts.md) ? Receipt taxonomy
- [EVIDENCE_BUNDLE_SPEC.md](./EVIDENCE_BUNDLE_SPEC.md) ? Bundle structure

---

END OF RECEIPT CHAIN LAYERING
