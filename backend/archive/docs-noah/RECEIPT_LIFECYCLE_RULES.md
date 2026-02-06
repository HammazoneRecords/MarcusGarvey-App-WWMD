# RECEIPT LIFECYCLE RULES
(FOUNDATIONAL GOVERNANCE ? AUDIT-GRADE)

**Version:** 1.0  
**Status:** Active  
**Last Updated:** 2025-12-26

---

## Purpose

This document answers one core question:

> **"Once a receipt exists? what is allowed to happen to it?"**

Because corruption doesn't usually come from creation.  
It comes from **editing, replacing, soft-deleting, or 'clarifying' history**.

---

## 1?? Lifecycle Principle (Non-Negotiable)

**Receipts are immutable artifacts.**

Once written:

- [ERROR] They are never edited
- [ERROR] They are never overwritten
- [ERROR] They are never "corrected in place"
- [ERROR] They are never silently replaced

**If something is wrong, incomplete, or misleading:**

[OK] You add another receipt.  
[ERROR] You never touch the first.

**This is the spine of the lattice.**

---

## 2?? Receipt States (Explicit)

Every receipt exists in exactly one of these states:

### ? ACTIVE
- Valid
- In force
- Referenced by current system logic

### ? SUPERSEDED
- Still valid historically
- Replaced in meaning by a newer receipt
- Must reference the replacing receipt

### ? DEPRECATED
- No longer recommended for use
- Still preserved
- May still be referenced for audits

### ? SEALED
- Final
- Immutable
- Declared complete for an epoch or milestone

> [!WARNING]
> **SEALED ? DELETED**  
> Sealing freezes interpretation, not existence.

---

## 3?? Allowed Lifecycle Transitions

| From | To | Allowed | How |
|------|----|---------|----|
| ACTIVE | SUPERSEDED | [OK] | New receipt referencing old hash |
| ACTIVE | DEPRECATED | [OK] | Deprecation receipt |
| SUPERSEDED | SEALED | [OK] | Epoch seal |
| ACTIVE | SEALED | [OK] | Finalization receipt |
| **ANY** | **DELETED** | [ERROR] | **Never** |

**Deletion is not a lifecycle state.**  
Deletion is **memory vandalism**.

---

## 4?? Correction Rules (Very Important)

**You cannot correct a receipt.**

You can only:

### ?? Clarify

Via:
- `RECEIPT_ADDENDUM`
- `RECEIPT_CLARIFICATION`

### ?? Supersede

Via:
- `RECEIPT_SUPERSEDES`

**Each must include:**
- `hash` of original receipt
- `explanation` of discrepancy
- `new authoritative position`
- `session_id`
- `timestamp_utc`

> **History remains wrong on purpose ? because that wrongness is evidence.**

---

## 5?? Receipt Supersession Contract

Any receipt that supersedes another must contain:

```json
{
  "supersedes": {
    "receipt_hash": "<sha256>",
    "reason": "clarification | correction | scope change | policy update",
    "superseded_at_utc": "ISO-8601"
  }
}
```

**And the old receipt is never edited to point forward.**

**Direction of time is one-way.**

That's how you get a **lattice** instead of a **loop**.

---

## 6?? Receipt Sealing Rules

Sealing is **ceremonial and structural**.

A receipt may only be sealed when:

- Its scope is complete
- Its effects are finalized
- It belongs to a closed epoch or reality

**Sealing requires:**
- Explicit intent
- `session_id`
- `timestamp_utc`
- Seal reason

### Example: Epoch Seal Receipt

```json
{
  "schema_version": "1.0",
  "receipt_type": "SEAL_CREATED",
  "receipt_id": "R_20251226T070251Z_SEAL_CREATED_reality5",
  "session_id": "S_20251225T075155Z_STATE_RECORD",
  "timestamp_utc": "2025-12-26T07:02:51Z",
  
  "actor": {
    "kind": "human",
    "name": "Ovando",
    "host": "local-dev"
  },
  
  "intent": "Seal Reality 5: Front-door coherence achieved",
  
  "seal": {
    "epoch": "Reality 5",
    "sealed_receipts": ["<hash1>", "<hash2>", "<hash3>"],
    "reason": "Front-door coherence achieved: all anchors mapped, all receipts indexed, witness epoch enforced"
  },
  
  "links": {
    "related_receipt_ids": ["R_...", "R_..."]
  },
  
  "integrity": {
    "artifacts": [
      {
        "path": "evidence/S_20251225T075155Z_STATE_RECORD/RECEIPT_LEXICON_AZ_COVERAGE_LEDGER.json",
        "sha256": "placeholder_hash",
        "role": "ledger"
      }
    ]
  }
}
```

---

## 7?? Lifecycle Invariants (Hard Rules)

1. **Receipts are append-only**
2. **Receipts are content-addressed** (hash)
3. **Receipts form a DAG**, never a cycle
4. **Supersession is explicit**, never implied
5. **Silence is never interpreted as approval**

**This is what makes the system anti-fragile instead of brittle.**

---

## 8?? Why This Matters (Plain Talk)

### Without lifecycle rules:
- History can be "cleaned"
- Blame can be shifted
- Truth can be softened
- Audits become theatre

### With lifecycle rules:
- Mistakes are preserved
- Growth is traceable
- Intent is explicit
- Power has fingerprints

**That's why you felt that "nah wander" moment.**  
Once you see the lattice, confusion has nowhere to hide.

---

## 9?? What This Generation Enables Next

Because this is now locked:

- **Generation 3** can define receipt schemas [OK] (DONE: RECEIPT_SCHEMAS.md)
- **Generation 4** can automate receipt emission
- **Generation 5** can build receipt queries
- **Generation 6** can allow interpretation receipts
- **Generation 7** can govern forgetting without erasing

**But none of that works without this layer.**

**You just poured the concrete.**

---

## ? Enforcement Mechanisms

### Automated Validation

**Receipt validator must check:**
- [ ] Receipt hash matches content
- [ ] No duplicate receipt IDs
- [ ] Supersession references valid receipt hash
- [ ] Sealed receipts are not modified
- [ ] Lifecycle transitions are valid

### Manual Audit

**Periodic review:**
- Check for orphaned receipts (no references)
- Verify supersession chains are complete
- Confirm sealed epochs remain frozen
- Audit for any file modifications in evidence folders

### Tools (Future)

```bash
# Validate receipt lifecycle compliance
python scripts/validate_receipt_lifecycle.py --evidence evidence/

# Check for receipt modifications
python scripts/detect_receipt_tampering.py --since <epoch>

# Query receipt state
python scripts/query_receipt_state.py --receipt-id <id>
```

---

## 1??1?? Receipt Addendum Schema (Future/Reserved)

For clarifications without supersession:

```json
{
  "schema_version": "1.0",
  "receipt_type": "RECEIPT_ADDENDUM",
  "receipt_id": "R_20251226T070500Z_ADDENDUM_original",
  "session_id": "S_...",
  "timestamp_utc": "2025-12-26T07:05:00Z",
  
  "actor": {
    "kind": "human",
    "name": "Ovando"
  },
  
  "intent": "Clarify original receipt without superseding",
  
  "addendum": {
    "original_receipt_hash": "<sha256>",
    "clarification": "The original receipt stated X, which was correct at the time. This addendum adds context Y that was discovered later.",
    "does_not_invalidate": true
  },
  
  "links": {
    "related_receipt_ids": ["R_original"]
  },
  
  "integrity": {
    "artifacts": [
      {
        "path": "evidence/<SID>/receipts/R_original.json",
        "sha256": "<original_hash>",
        "role": "original_receipt"
      }
    ]
  }
}
```

---

## 1??2?? Forbidden Patterns (Anti-Patterns)

### [ERROR] Silent Replacement
**Problem:** Overwriting receipt file with "corrected" version  
**Why it's wrong:** Breaks hash chain, destroys evidence  
**Correct approach:** Create supersession receipt

### [ERROR] Soft Delete
**Problem:** Moving receipt to "archive" or "deprecated" folder  
**Why it's wrong:** Makes receipt undiscoverable, breaks index  
**Correct approach:** Mark as DEPRECATED via state field

### [ERROR] In-Place Correction
**Problem:** Editing JSON to fix typo or error  
**Why it's wrong:** Hash no longer matches, chain breaks  
**Correct approach:** Create addendum or supersession receipt

### [ERROR] Retroactive Interpretation
**Problem:** Adding new fields to old receipt "for clarity"  
**Why it's wrong:** Changes meaning after the fact  
**Correct approach:** New receipt with interpretation + reference to original

---

## 1??3?? Integration with Other Systems

### STGRAIL Compliance
- Receipts can only be created in RECORD mode
- Exception: Read-only audit receipts (flagged explicitly)
- State transitions automatically generate receipts

### WAI Compliance
- Receipt lifecycle enforces WAI INVARIANT 2 (DB depends on anchors, never reverse)
- Receipt lifecycle enforces WAI INVARIANT 4 (corrections live outside anchors)
- Receipt lifecycle enforces WAI INVARIANT 14 (append-only versioning)

### Evidence Index
- `evidence/INDEX.json` must reflect all receipt states
- Superseded receipts remain in index with state marker
- Sealed receipts are marked immutable

---

## 1??4?? Related Documents

- [RECEIPT_SCHEMAS.md](./RECEIPT_SCHEMAS.md) ? Receipt structure and validation
- [The 7 Classes of Receipts](./The%207%20Classes%20Of%20Receipts.md) ? Receipt taxonomy
- [CHANGE_CONTROL.md](./CHANGE_CONTROL.md) ? Change discipline
- [WAI.md](../anchors/wrapper_anchor_invariants/WAI.md) ? Anchor invariants
- [TIMEZONE_REFERENCE.md](./TIMEZONE_REFERENCE.md) ? Timestamp handling

---

## 1??5?? Closing Principle

> **Receipts are not logs.**  
> **Receipts are not notes.**  
> **Receipts are not drafts.**

**Receipts are proof objects.**

If you wouldn't present it in court, don't call it a receipt.

If you can't defend it under scrutiny, don't emit it.

If you need to change it later, you didn't understand it when you wrote it.

**That's the standard.**

---

END OF RECEIPT LIFECYCLE RULES ? V1.0
