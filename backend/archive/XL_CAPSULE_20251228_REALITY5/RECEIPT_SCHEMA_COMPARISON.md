# Receipt Schema Comparison: V1 vs V2

**Date**: 2025-12-28  
**Purpose**: Verify V2 schema maintains structural compatibility with V1, adding only ritual metadata fields

---

## Executive Summary

[OK] **VALIDATION RESULT**: V2 is **NOT** structurally identical to V1  
[WARN] **CONCERN**: V2 is a **SIMPLIFIED** ingestion-specific schema, not a full evolution of V1

### Key Differences

| Aspect | V1 (RECEIPT_SCHEMAS.md) | V2 (RECEIPT_SCHEMA_V2.md) |
|--------|-------------------------|---------------------------|
| **Scope** | Universal receipt framework (8 classes, 20+ types) | Ingestion-only receipts |
| **Types** | STATE_TRANSITION, ANCHOR_ADDED, BUNDLE_CREATED, etc. | Focus on INGESTION_COMPLETED |
| **Base Schema** | Full base with actor, integrity, links objects | Simplified metadata fields |
| **Structure** | JSON Schema Draft 2020-12 compliant | Informal specification |
| **Hashing** | Required sha256 for all artifacts | manifest_entry_sha256 only |
| **Audit Chain** | Receipt chaining, previous_receipt_sha256 | No chaining |

---

## V1 Schema (RECEIPT_SCHEMAS.md) - Comprehensive

### 8 Receipt Classes
1. **State & Authority**: STATE_TRANSITION, SESSION_LOCK_CREATED
2. **Anchor Lifecycle**: ANCHOR_ADDED, ANCHOR_UPGRADED, ANCHOR_STATUS_CHANGED
3. **Ingestion & Chunking**: INGESTION_STARTED, INGESTION_COMPLETED, CHUNKING_COMPLETED
4. **Evidence & Index**: EVIDENCE_INDEX_REBUILT, EVIDENCE_BUNDLE_CREATED
5. **Change Control**: CODEBASE_FINGERPRINT_BEFORE/AFTER, CODEBASE_DIFF_CREATED
6. **Interpretation**: DERIVATION_CREATED, SUMMARY_CREATED
7. **Boundary & Epoch**: SEAL_CREATED, EPOCH_DECLARED
8. **Deprecation**: ANCHOR_SUNSET, FEATURE_DEPRECATED, SUBSYSTEM_DECOMMISSIONED

### Base Schema Fields (ALL receipts)
```json
{
  "schema_version": "1.0",
  "receipt_type": "<TYPE>",
  "receipt_id": "R_<UTC>_<TYPE>_<TAG>",
  "session_id": "S_<UTC>_<DESCRIPTOR>",
  "timestamp_utc": "YYYY-MM-DDTHH:MM:SSZ",
  
  "actor": {
    "kind": "human|agent|script|system",
    "name": "...",
    "host": "...",
    "tool_version": "..."
  },
  
  "intent": "human purpose statement",
  
  "links": {
    "related_receipt_ids": [],
    "run_id": "...",
    "manifest_id": "...",
    "anchor_id": "..."
  },
  
  "integrity": {
    "receipt_sha256": "...",
    "previous_receipt_sha256": "...",
    "artifacts": [
      {
        "path": "...",
        "sha256": "...",
        "bytes": 123,
        "mime": "...",
        "role": "..."
      }
    ]
  }
}
```

---

## V2 Schema (RECEIPT_SCHEMA_V2.md) - Ingestion-Specific

### Required Fields (Ingestion Only)
```json
{
  "receipt_version": "V2",
  "intent": "ARTISAN_PDF_PAGE_CHUNK_PILOT",
  "generated_utc": "2025-12-28T18:39:39Z",
  "import_session_id": "S_20251225T075155Z_STATE_RECORD",
  
  "anchor_id": "book_of_solobility_v1",
  "source_path": "anchors/canon/...",
  "manifest_entry_sha256": "...",
  
  "db": {
    "path": "data/memory.db",
    "chunks_before": 2839,
    "chunks_after": 3446,
    "delta": 607
  },
  
  "strict_rules": {
    "chunk_collision": "STOP",
    "missing_anchor": "STOP",
    "manifest_sha_mismatch": "STOP"
  }
}
```

### Missing from V2 (present in V1)
- [ERROR] `receipt_type` enum
- [ERROR] `receipt_id` with standard format
- [ERROR] `actor` object (who/what created it)
- [ERROR] `links` object (related receipts, runs)
- [ERROR] `integrity.artifacts` array with full hashing
- [ERROR] `previous_receipt_sha256` for chaining
- [ERROR] Common schema definitions
- [ERROR] Non-ingestion receipt types

### Present in V2 (not in V1)
- [OK] `receipt_version` (V2 marker)
- [OK] `db.chunks_before/after/delta` (state tracking)
- [OK] `strict_rules` object (prosecutor-grade enforcement)
- [OK] `timestamps.duration_seconds`

---

## Current Receipt Reality Check

Sample current receipt (`RECEIPT_LEXICON_A.json`):
```json
{
  "anchor_id": "lexicon_A",
  "ended_utc": "2025-12-25T04:53:41Z",
  "format_mode": "top_level_dict_entries",
  "import_session_id": "S_20251224T233858Z_LEXICON_AZ_FULL",
  "inserted": 102,
  "letter": "A",
  "row_index_derived": false,
  "source_json": "anchors/canon/...",
  "started_utc": "2025-12-25T04:53:41Z"
}
```

**Analysis**: Current receipts are informal, closer to V2 than V1

---

## Recommendations

### For Reality 5 (Ritual Engine)

**Current Situation**:
- V1 is a comprehensive universal receipt framework (857 lines, 8 classes)
- V2 is a prosecutor-grade ingestion-only spec (275 lines, Reality 4)
- Current receipts are informal, operational

**Option 1: V2+ (Recommended)**
Extend V2 with minimal ritual fields:
```json
{
  "receipt_version": "V2",
  "intent": "RITUAL_LEXICON_IMPORT",
  "ritual_metadata": {
    "ritual_name": "lexicon_import",
    "config_hash": "..."
  },
  // ... rest of V2 fields unchanged
}
```

**Option 2: V1.1**
Add ritual support to comprehensive V1:
```json
{
  "schema_version": "1.1",
  "receipt_type": "INGESTION_COMPLETED",
  "ritual_metadata": {
    "ritual_name": "...",
    "config_hash": "..."
  },
  // ... rest of V1 base fields
}
```

**Recommendation**: **Option 1 (V2+)** 
- Keeps Reality 4 (Prosecutor) stable
- Minimal addition to proven V2 structure
- Doesn't require Court to validate new base schema

---

## Migration Path

### Phase 1: Document Both (DONE)
- [OK] `docs/RECEIPT_SCHEMAS.md` - V1 comprehensive framework
- [OK] `docs/RECEIPT_SCHEMA_V2.md` - V2 prosecutor-grade ingestion

### Phase 2: Extend V2 for Rituals
- Add `ritual_metadata` object to V2 spec
- Fields: `ritual_name`, `config_hash`, `module_version`
- Update `scripts/validate_receipt_v2.py` to accept optional ritual_metadata

### Phase 3: Future Evolution
- Consider migrating V2 -> V1.1 when ready for universal receipts
- Requires Court blessing (Reality 4 validation update)

---

## Conclusion

**V2 is NOT structurally identical to V1** - it's a simplified, focused ingestion schema.

**For Reality 5**: Use V2+ (extend V2 with ritual_metadata) to avoid disturbing Reality 4.

**Long-term**: V1 is the vision, V2 is the current reality. Bridge them when Court is ready.
