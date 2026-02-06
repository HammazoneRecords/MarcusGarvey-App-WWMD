# RECEIPT EXAMPLES (Teaching Surface)
**Version:** 1.0  
**Status:** Active  
**Last Updated:** 2025-12-26  
**Reality Bridge:** Reality 5 -> Reality 6

---

## Purpose

This document is the **teaching surface** for the Solob receipt system.

Examples are how rules survive:
- **Training** ? new operators learn by pattern
- **Forking** ? other systems can adopt the model
- **Pressure** ? under audit, examples prove intent

> **Examples are how rules survive migration.**

---

## Receipt Format Overview

Every receipt shares a base structure:

```json
{
  "schema_version": "1.0",
  "receipt_type": "<TYPE>",
  "receipt_id": "R_<YYYYMMDDTHHMMSSZ>_<TYPE>_<tag>",
  "session_id": "S_<YYYYMMDDTHHMMSSZ>_<CONTEXT>",
  "timestamp_utc": "YYYY-MM-DDTHH:MM:SSZ",
  
  "actor": {
    "kind": "human | agent | script | system",
    "name": "<operator or tool name>",
    "host": "<machine identifier>"
  },
  
  "intent": "<human-readable purpose>",
  
  "links": {
    "related_receipt_ids": [],
    "anchor_id": "<if applicable>",
    "manifest_id": "<if applicable>"
  },
  
  "integrity": {
    "artifacts": [
      {
        "path": "<relative path>",
        "sha256": "<64 hex chars>",
        "bytes": 1234,
        "role": "<anchor | archive | source | output>"
      }
    ]
  },
  
  "<type-specific fields>": "..."
}
```

---

## 1?? ANCHOR_ADDED ? Reality 1 (Monk)

**When:** A new canonical source is registered in the system.

**Reality posture:** Monk ? inputs only, no interpretation.

```json
{
  "schema_version": "1.0",
  "receipt_type": "ANCHOR_ADDED",
  "receipt_id": "R_20251219T143022Z_ANCHOR_ADDED_waiinv",
  "session_id": "S_20251219T140000Z_ANCHOR_REGISTRATION",
  "timestamp_utc": "2025-12-19T14:30:22Z",
  
  "actor": {
    "kind": "human",
    "name": "Ovando",
    "host": "dev-workstation"
  },
  
  "intent": "Register Wrapper Anchor Invariants (WAI) as canonical governance anchor",
  
  "anchor": {
    "anchor_id": "wai_invariants",
    "role": "governance",
    "source_path": "anchors/wrapper_anchor_invariants/WAI.md",
    "sha256": "89c5b5d294d10e99aa055866ad4b21a093f72ebfb2b50856b656f3a24b4457a8",
    "status": "canon",
    "added_reason": "Constitutional document defining what may never break in the anchor system"
  },
  
  "links": {
    "manifest_id": "anchors_manifest_20251219T143022Z.json"
  },
  
  "integrity": {
    "artifacts": [
      {
        "path": "anchors/wrapper_anchor_invariants/WAI.md",
        "sha256": "89c5b5d294d10e99aa055866ad4b21a093f72ebfb2b50856b656f3a24b4457a8",
        "bytes": 4243,
        "role": "anchor"
      }
    ]
  }
}
```

### Key Elements:
- **anchor.status**: `"canon"` ? this is source-of-truth
- **anchor.added_reason**: Why this anchor exists
- **integrity.artifacts**: Hash proves content at registration time

---

## 2?? ANCHOR_UPGRADED ? Reality 2 (Cartographer)

**When:** An anchor is updated with a new version (old version archived).

**Reality posture:** Cartographer ? mapping change, not interpreting it.

```json
{
  "schema_version": "1.0",
  "receipt_type": "ANCHOR_UPGRADED",
  "receipt_id": "R_20251226T052432Z_ANCHOR_UPGRADED_wai",
  "session_id": "S_20251226T052432Z_WAI_UPGRADE",
  "timestamp_utc": "2025-12-26T05:24:32Z",
  
  "actor": {
    "kind": "human",
    "name": "Ovando",
    "host": "dev-workstation",
    "tool_version": "Antigravity IDE"
  },
  
  "intent": "Upgrade WAI to v1.1: Add INVARIANT 14 (Archive Rule) + enhance PDF extraction guidance",
  
  "anchor": {
    "anchor_id": "wai_invariants"
  },
  
  "previous": {
    "path": "anchors/wrapper_anchor_invariants/WAI.md",
    "sha256": "89c5b5d294d10e99aa055866ad4b21a093f72ebfb2b50856b656f3a24b4457a8",
    "version": "v1.0"
  },
  
  "next": {
    "path": "anchors/wrapper_anchor_invariants/WAI.md",
    "sha256": "d749677b1e4b8136af48cf754e15cc46050733696178a92d6971269649196628",
    "version": "v1.1"
  },
  
  "archive": {
    "path": "anchors/wrapper_anchor_invariants/archive/WAI_v1.0_2025-12-19.md",
    "sha256": "89c5b5d294d10e99aa055866ad4b21a093f72ebfb2b50856b656f3a24b4457a8"
  },
  
  "upgrade_reason": "Added INVARIANT 14 (versioning protocol for invariant files) and enhanced INVARIANT 12 (PDF/text extraction must preserve source fidelity)",
  
  "links": {
    "manifest_id": "anchors_manifest_20251226T052432Z.json",
    "anchor_id": "wai_invariants",
    "related_receipt_ids": ["R_20251219T143022Z_ANCHOR_ADDED_waiinv"]
  },
  
  "integrity": {
    "artifacts": [
      {
        "path": "anchors/wrapper_anchor_invariants/WAI.md",
        "sha256": "d749677b1e4b8136af48cf754e15cc46050733696178a92d6971269649196628",
        "bytes": 7281,
        "role": "anchor"
      },
      {
        "path": "anchors/wrapper_anchor_invariants/archive/WAI_v1.0_2025-12-19.md",
        "sha256": "89c5b5d294d10e99aa055866ad4b21a093f72ebfb2b50856b656f3a24b4457a8",
        "bytes": 4243,
        "role": "archive"
      }
    ]
  }
}
```

### Key Elements:
- **previous + next**: Both versions hashed
- **archive**: Old version preserved, never deleted
- **upgrade_reason**: Explicit rationale
- **links.related_receipt_ids**: Chain to original ANCHOR_ADDED

---

## 3?? INGESTION_COMPLETED ? Reality 3 (Prosecutor)

**When:** Chunks are extracted from an anchor and inserted into the database.

**Reality posture:** Prosecutor ? verifying and recording evidence of transformation.

```json
{
  "schema_version": "1.0",
  "receipt_type": "INGESTION_COMPLETED",
  "receipt_id": "R_20251225T045341Z_INGESTION_COMPLETED_lexa",
  "session_id": "S_20251224T233858Z_LEXICON_AZ_FULL",
  "timestamp_utc": "2025-12-25T04:53:41Z",
  
  "actor": {
    "kind": "script",
    "name": "import_lexicon_chunks_v1_1.py",
    "host": "dev-workstation",
    "tool_version": "v1.1"
  },
  
  "intent": "Ingest Lexicon A entries into database as chunks",
  
  "anchor_id": "lexicon_A",
  
  "source_artifact": {
    "path": "anchors/canon/definitions/Lexical Canon Anchors/A/A.json",
    "sha256": "88cdf371e82e59e7c2e097e99bf38e76b805c0031e5953f20470141b998cd95c",
    "bytes": 45678,
    "role": "anchor"
  },
  
  "output_artifacts": [
    {
      "path": "data/memory.db",
      "sha256": "db_state_hash_placeholder",
      "role": "database"
    }
  ],
  
  "stats": {
    "chunks_count": 102,
    "format_mode": "top_level_dict_entries",
    "row_index_derived": false,
    "started_utc": "2025-12-25T04:53:41Z",
    "ended_utc": "2025-12-25T04:53:42Z",
    "duration_ms": 1200
  },
  
  "links": {
    "anchor_id": "lexicon_A",
    "manifest_id": "anchors_manifest_20251225T045341Z.json"
  },
  
  "integrity": {
    "artifacts": [
      {
        "path": "anchors/canon/definitions/Lexical Canon Anchors/A/A.json",
        "sha256": "88cdf371e82e59e7c2e097e99bf38e76b805c0031e5953f20470141b998cd95c",
        "role": "source"
      }
    ]
  }
}
```

### Key Elements:
- **stats.chunks_count**: Verifiable output count
- **source_artifact**: What was consumed
- **output_artifacts**: What was produced
- **stats.format_mode**: How the source was parsed

---

## 4?? EVIDENCE_INDEX_REBUILT ? Reality 4 (Artisan)

**When:** The evidence index is regenerated to reflect current state.

**Reality posture:** Artisan ? building surfaces without changing truth.

```json
{
  "schema_version": "1.0",
  "receipt_type": "EVIDENCE_INDEX_REBUILT",
  "receipt_id": "R_20251225T210000Z_EVIDENCE_INDEX_REBUILT_full",
  "session_id": "S_20251225T075155Z_STATE_RECORD",
  "timestamp_utc": "2025-12-25T21:00:00Z",
  
  "actor": {
    "kind": "script",
    "name": "evidence_index.py",
    "host": "dev-workstation",
    "tool_version": "v2.0"
  },
  
  "intent": "Rebuild evidence index after Lexicon A-Z ingestion + bundle consolidation",
  
  "evidence_root": "evidence",
  
  "index_artifact": {
    "path": "evidence/INDEX.json",
    "sha256": "index_hash_placeholder",
    "bytes": 12456,
    "role": "index"
  },
  
  "stats": {
    "sessions_indexed": 5,
    "receipts_indexed": 58,
    "bundles_indexed": 2,
    "orphans_found": 0
  },
  
  "links": {
    "related_receipt_ids": [
      "R_20251225T045341Z_INGESTION_COMPLETED_lexa",
      "R_20251225T071209Z_EVIDENCE_BUNDLE_CREATED_supreme"
    ]
  },
  
  "integrity": {
    "artifacts": [
      {
        "path": "evidence/INDEX.json",
        "sha256": "index_hash_placeholder",
        "role": "index"
      }
    ]
  }
}
```

### Key Elements:
- **stats**: What was indexed
- **evidence_root**: Where the index covers
- **orphans_found**: Integrity check

---

## 5?? SEAL_CREATED ? Reality 5 (Court)

**When:** An epoch or reality milestone is declared complete and immutable.

**Reality posture:** Court ? judgment that freezes interpretation.

```json
{
  "schema_version": "1.0",
  "receipt_type": "SEAL_CREATED",
  "receipt_id": "R_20251225T210654Z_SEAL_CREATED_reality5",
  "session_id": "S_20251225T075155Z_STATE_RECORD",
  "timestamp_utc": "2025-12-25T21:06:54Z",
  
  "actor": {
    "kind": "human",
    "name": "Ovando",
    "host": "dev-workstation"
  },
  
  "intent": "Seal Reality 5: Front-door coherence achieved (all anchors mapped, all receipts indexed, witness epoch enforced)",
  
  "seal": {
    "epoch": "Reality 5",
    "milestone": "Front-Door Coherence",
    "reason": "All lexicon A-Z ingested (1625 chunks), evidence index complete, witness epoch active since 2025-12-25T07:51:59Z",
    "sealed_receipts": [
      "R_20251225T045341Z_INGESTION_COMPLETED_lexa",
      "R_20251225T071209Z_EVIDENCE_BUNDLE_CREATED_supreme",
      "R_20251225T210000Z_EVIDENCE_INDEX_REBUILT_full"
    ],
    "sealed_at_utc": "2025-12-25T21:06:54Z"
  },
  
  "links": {
    "related_receipt_ids": [
      "R_20251225T045341Z_INGESTION_COMPLETED_lexa",
      "R_20251225T071209Z_EVIDENCE_BUNDLE_CREATED_supreme"
    ]
  },
  
  "integrity": {
    "artifacts": [
      {
        "path": "evidence/S_20251225T075155Z_STATE_RECORD/RECEIPT_LEXICON_AZ_COVERAGE_LEDGER.json",
        "sha256": "ledger_hash_placeholder",
        "role": "ledger"
      },
      {
        "path": "evidence/INDEX.json",
        "sha256": "index_hash_placeholder",
        "role": "index"
      }
    ]
  }
}
```

### Key Elements:
- **seal.epoch**: Which reality is being sealed
- **seal.milestone**: Human-readable achievement
- **seal.reason**: Evidence supporting the seal
- **seal.sealed_receipts**: What is now immutable
- **sealed_at_utc**: Timestamp of finalization

---

## 6?? EPOCH_DECLARED ? Boundary Marker

**When:** A new operational epoch begins (witness epoch, rule change, etc.).

**Reality posture:** Court ? establishing new regime.

```json
{
  "schema_version": "1.0",
  "receipt_type": "EPOCH_DECLARED",
  "receipt_id": "R_20251225T075159Z_EPOCH_DECLARED_witness",
  "session_id": "S_20251225T075155Z_STATE_RECORD",
  "timestamp_utc": "2025-12-25T07:51:59Z",
  
  "actor": {
    "kind": "human",
    "name": "Ovando",
    "host": "dev-workstation"
  },
  
  "intent": "Declare Witness Epoch: All state transitions from this point forward require canonical SID",
  
  "epoch": {
    "name": "Witness Epoch",
    "effective_from_utc": "2025-12-25T07:51:59Z",
    "rules": [
      "All state transitions must include session_id (SID)",
      "Legacy transitions documented in STATE_HISTORY_LEGACY_SID_ADDENDUM.json",
      "No unsigned state changes permitted"
    ],
    "supersedes": null,
    "reason": "Establish provenance-first discipline for all future operations"
  },
  
  "links": {},
  
  "integrity": {
    "artifacts": [
      {
        "path": "docs/STATE_HISTORY_LEGACY_SID_ADDENDUM.json",
        "sha256": "addendum_hash_placeholder",
        "role": "legacy_documentation"
      }
    ]
  }
}
```

### Key Elements:
- **epoch.effective_from_utc**: When the new rules take effect
- **epoch.rules**: What the epoch enforces
- **epoch.supersedes**: What epoch this replaces (if any)

---

## 7?? RECEIPT_SUPERSEDES ? Correction Without Erasure

**When:** A previous receipt needs to be replaced (not deleted).

**Reality posture:** Court ? judgment without destruction.

```json
{
  "schema_version": "1.0",
  "receipt_type": "ANCHOR_ADDED",
  "receipt_id": "R_20251226T080000Z_ANCHOR_ADDED_fixed",
  "session_id": "S_20251226T075000Z_CORRECTION",
  "timestamp_utc": "2025-12-26T08:00:00Z",
  
  "actor": {
    "kind": "human",
    "name": "Ovando"
  },
  
  "intent": "Correct anchor registration: previous receipt had incorrect hash",
  
  "supersedes": {
    "receipt_hash": "abc123def456...",
    "receipt_id": "R_20251226T070000Z_ANCHOR_ADDED_wrong",
    "reason": "correction",
    "superseded_at_utc": "2025-12-26T08:00:00Z",
    "explanation": "Original receipt contained hash computed before file was finalized. This receipt supersedes with correct hash."
  },
  
  "anchor": {
    "anchor_id": "example_anchor",
    "role": "canon",
    "source_path": "anchors/example.md",
    "sha256": "correct_hash_here_64_hex_chars_0123456789abcdef01234567890",
    "status": "canon",
    "added_reason": "Corrected registration"
  },
  
  "links": {
    "related_receipt_ids": ["R_20251226T070000Z_ANCHOR_ADDED_wrong"]
  },
  
  "integrity": {
    "artifacts": [
      {
        "path": "anchors/example.md",
        "sha256": "correct_hash_here_64_hex_chars_0123456789abcdef01234567890",
        "role": "anchor"
      }
    ]
  }
}
```

### Key Elements:
- **supersedes.receipt_hash**: Hash of the receipt being superseded
- **supersedes.reason**: Why supersession is needed
- **supersedes.explanation**: Human context
- **Original receipt remains untouched** ? history preserved

---

## 8?? RECEIPT_ADDENDUM ? Clarification Without Invalidation

**When:** Additional context is needed for an existing receipt.

**Reality posture:** Cartographer ? adding to the map, not redrawing it.

```json
{
  "schema_version": "1.0",
  "receipt_type": "RECEIPT_ADDENDUM",
  "receipt_id": "R_20251226T090000Z_ADDENDUM_context",
  "session_id": "S_20251226T085000Z_DOCUMENTATION",
  "timestamp_utc": "2025-12-26T09:00:00Z",
  
  "actor": {
    "kind": "human",
    "name": "Ovando"
  },
  
  "intent": "Add context to WAI upgrade receipt: clarify why INVARIANT 14 was added",
  
  "addendum": {
    "extends_receipt_id": "R_20251226T052432Z_ANCHOR_UPGRADED_wai",
    "extends_receipt_hash": "original_receipt_hash_placeholder",
    "does_not_invalidate": true,
    "clarification": "INVARIANT 14 was added to prevent future WAI updates from losing traceability. The archive protocol ensures every version remains accessible for audit."
  },
  
  "links": {
    "related_receipt_ids": ["R_20251226T052432Z_ANCHOR_UPGRADED_wai"]
  },
  
  "integrity": {
    "artifacts": []
  }
}
```

### Key Elements:
- **addendum.extends_receipt_id**: What receipt this adds to
- **addendum.does_not_invalidate**: Explicitly states original remains valid
- **addendum.clarification**: The additional context

---

## Reality Constraints Summary

| Reality | Posture | Allowed Receipt Types | Sealed Required? |
|---------|---------|----------------------|------------------|
| **Monk** | Inputs only | ANCHOR_ADDED, NOTE | [OK] |
| **Cartographer** | Mapping | ANCHOR_UPGRADED, INDEX_REBUILT, ADDENDUM | [OK] |
| **Prosecutor** | Verification | INGESTION_*, VALIDATION, REJECTION | [OK] |
| **Artisan** | Building | EMISSION, DERIVATION, SUMMARY | [WARN] Optional |
| **Court** | Judgment | SEAL_CREATED, EPOCH_DECLARED, SUPERSEDES | [OK] |

---

## Validation Checklist for Examples

Every example receipt above passes:

- [ ] `schema_version` = "1.0"
- [ ] `receipt_type` in valid enumeration
- [ ] `receipt_id` matches `R_<YYYYMMDDTHHMMSSZ>_<TYPE>_<tag>`
- [ ] `session_id` matches `S_<YYYYMMDDTHHMMSSZ>_<CONTEXT>`
- [ ] `timestamp_utc` is ISO8601 UTC with Z suffix
- [ ] `actor.kind` in {human, agent, script, system}
- [ ] `actor.name` is non-empty
- [ ] `intent` is at least 3 characters
- [ ] `integrity.artifacts[].sha256` is 64 hex chars
- [ ] Type-specific required fields present

---

## Philosophy Encoded

Every receipt embeds discipline:

| Field | What It Encodes |
|-------|-----------------|
| `intent` | **Meaning** ? why this action matters |
| `reality` | **Epistemic posture** ? under what rules |
| `integrity.artifacts` | **Proof** ? verifiable hashes |
| `sealed` | **Finality** ? no retroactive lies |
| `supersedes` | **Continuity** ? change without erasure |

---

## Why Examples Matter

This document exists because:

1. **Training**: New operators learn by copying patterns
2. **Forking**: Other systems can adopt the model
3. **Pressure**: Under audit, examples prove intent
4. **Migration**: When schemas evolve, examples bridge versions

> **Examples are how rules survive migration.**

---

## Related Documents

- [RECEIPT_SCHEMAS.md](./RECEIPT_SCHEMAS.md) ? Formal schemas
- [RECEIPT_LIFECYCLE_RULES.md](./RECEIPT_LIFECYCLE_RULES.md) ? Governance
- [The 7 Classes of Receipts](./The%207%20Classes%20Of%20Receipts.md) ? Taxonomy
- [TIMEZONE_REFERENCE.md](./TIMEZONE_REFERENCE.md) ? Timestamp conventions
- [v1-scope.md](./v1-scope.md) ? V1 workflow

---

END OF RECEIPT EXAMPLES ? V1.0
