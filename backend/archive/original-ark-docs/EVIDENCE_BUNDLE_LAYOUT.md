# EVIDENCE_BUNDLE_LAYOUT.md - Reality 4 (The Prosecutor)

**Version**: 2.0  
**Status**: CANONICAL  
**Last Updated**: 2025-12-28T16:53:00-05:00

---

## Purpose

This document defines the canonical evidence bundle layout for all bundle types in the Solob Wrapper system. Standardized layouts enable automation, validation, and forensic reconstruction.

---

## Core Principles

1. **Every bundle MUST have INDEX.json** - Machine-readable metadata
2. **Every bundle MUST have REPORT.md** - Human-readable summary
3. **Structure is uniform** - Same layout regardless of bundle type
4. **Legacy bundles are grandfathered** - V1 bundles remain valid but deprecated

---

## Canonical Bundle Structure

```
evidence/bundles/<BUNDLE_ID>/
??? INDEX.json          (REQUIRED - bundle metadata)
??? REPORT.md           (REQUIRED - human-readable summary)
??? RECEIPTS/           (OPTIONAL - ingestion receipts)
?   ??? RECEIPT_*.json
??? LEDGER_SUBSET.jsonl (OPTIONAL - relevant ledger events)
??? MANIFESTS/          (OPTIONAL - copied manifests)
    ??? *.json
```

---

## Required Files

### INDEX.json

**Purpose**: Machine-readable bundle metadata

**Required Fields**:
```json
{
  "bundle_version": "V2",
  "bundle_type": "court_sweep" | "ingestion" | "weekly_aggregate",
  "bundle_id": "<BUNDLE_ID>",
  "generated_utc": "2025-12-28T16:53:00Z",
  "import_session_id": "<SID>" (for ingestion bundles),
  "summary": {
    // Type-specific summary fields
  }
}
```

**Bundle Types**:

**1. Court Sweep Bundles** (`bundle_type`: `"court_sweep"`):
```json
{
  "bundle_version": "V2",
  "bundle_type": "court_sweep",
  "bundle_id": "S_20251228T165300Z_COURT_SWEEP",
  "generated_utc": "2025-12-28T16:53:00Z",
  "summary": {
    "checks_run": 7,
    "checks_passed": 6,
    "verdict": "NO-GO"
  },
  "checks": {
    "db_counts": {...},
    "state_history_witness": {...},
    // ... other checks
  }
}
```

**2. Ingestion Bundles** (`bundle_type`: `"ingestion"`):
```json
{
  "bundle_version": "V2",
  "bundle_type": "ingestion",
  "bundle_id": "<SESSION_ID>",
  "generated_utc": "2025-12-28T16:53:00Z",
  "import_session_id": "S_20251225T075155Z_STATE_RECORD",
  "summary": {
    "anchors_in_batch": 31,
    "receipts_written": 31,
    "ledger_events_matched": 5
  },
  "db_sha256": "<hash>",
  "manifest_sha256": "<hash>"
}
```

**3. Weekly Aggregate Bundles** (`bundle_type`: `"weekly_aggregate"`):
```json
{
  "bundle_version": "V2",
  "bundle_type": "weekly_aggregate",
  "bundle_id": "WEEKLY_20251222_TO_20251228",
  "generated_utc": "2025-12-28T16:53:00Z",
  "period": {
    "start_date": "2025-12-22",
    "end_date": "2025-12-28"
  },
  "summary": {
    "court_sweeps": 12,
    "ingestion_bundles": 3,
    "total_chunks_added": 607
  }
}
```

---

### REPORT.md

**Purpose**: Human-readable summary for quick review

**Format**:
```markdown
# <Bundle Type> Report

**Bundle ID**: <BUNDLE_ID>  
**Generated**: <UTC_TIMESTAMP>  
**Verdict**: PASS/NO-GO/INFO

## Summary

<High-level overview>

## Key Metrics

- Metric 1: Value
- Metric 2: Value

## Details

<Detailed information>
```

---

## Optional Directories

### RECEIPTS/

**Purpose**: Store ingestion receipts (V2 schema)

**Contents**:
- `RECEIPT_ANCHOR_<anchor_id>.json` - Per-anchor receipts (ingestion bundles)
- `RECEIPT_CHUNKS_<anchor_id>_<descriptor>.json` - Chunk ingestion receipts
- `RECEIPT_*.json` - Other receipt types

**Naming Convention**: `RECEIPT_<TYPE>_<IDENTIFIER>.json`

---

### LEDGER_SUBSET.jsonl

**Purpose**: Relevant ops_ledger events for this bundle

**Format**: JSONL (one JSON object per line)

**Example**:
```json
{"ts_utc": "2025-12-28T16:53:00Z", "event": "anchor_registered", "anchor_id": "book_of_solobility_v1"}
{"ts_utc": "2025-12-28T16:54:00Z", "event": "chunks_ingested", "count": 607}
```

---

### MANIFESTS/

**Purpose**: Copies of relevant manifest files for portability

**Contents**:
- `anchors_manifest_<timestamp>.json`
- Other manifest files referenced in INDEX.json

---

## Bundle Types

### Court Sweep Bundles

**Bundle ID Format**: `S_<TIMESTAMP>Z_COURT_SWEEP`

**Required Files**:
- `INDEX.json` (with audit results)
- `REPORT.md` (human-readable summary)

**Optional Files**: None (Court Sweep is read-only audit)

---

### Ingestion Bundles

**Bundle ID Format**: `<SESSION_ID>` (e.g., `S_20251225T075155Z_STATE_RECORD`)

**Required Files**:
- `INDEX.json` (with ingestion metadata)
- `REPORT.md` (ingestion summary)

**Optional Files**:
- `RECEIPTS/RECEIPT_ANCHOR_*.json` (per-anchor receipts)
- `LEDGER_SUBSET.jsonl` (ledger events for this session)
- `MANIFESTS/anchors_manifest_*.json` (copy of manifest)

---

### Weekly Aggregate Bundles

**Bundle ID Format**: `WEEKLY_<START_DATE>_TO_<END_DATE>`

**Required Files**:
- `INDEX.json` (with aggregation metadata)
- `REPORT.md` (weekly summary)

**Optional Files**:
- References to other bundles (via INDEX.json `references` field)

---

## Validation

### Court Sweep Check: `audit_bundle_layout()`

**Purpose**: Validate bundle structure compliance

**Process**:
1. Scan `evidence/bundles/*`
2. Check for `INDEX.json` (REQUIRED)
3. Check for `REPORT.md` (REQUIRED)
4. Validate INDEX.json schema
5. Check bundle_version field

**Verdict**:
- `PASS` - All bundles compliant
- `WARN` - V1 bundles found (deprecated but valid)
- `FAIL` - Missing required files or invalid INDEX.json

---

## Migration from V1

### V1 Bundle Structures

**Ingestion Bundles (V1)**:
- `BATCH_RECEIPT.json` -> Migrate to `INDEX.json`
- `anchors_receipts/*.json` -> Move to `RECEIPTS/RECEIPT_ANCHOR_*.json`
- `ops_ledger_subset.jsonl` -> Rename to `LEDGER_SUBSET.jsonl`
- `anchors_manifest_*.json` -> Move to `MANIFESTS/`
- Add `REPORT.md`

**Court Sweep Bundles**: Already V2-compliant (use `INDEX.json` and `REPORT.md`)

### Migration Strategy

1. **New bundles**: Must use V2 layout
2. **Legacy bundles**: Leave unchanged (grandfathered)
3. **Court Sweep**: WARN for V1, FAIL for missing required files
4. **Optional**: Migration script to upgrade V1 -> V2

---

## Quick Reference

| Bundle Type | Bundle ID Format | Required Files | Optional Directories |
|-------------|------------------|----------------|----------------------|
| Court Sweep | `S_<TS>Z_COURT_SWEEP` | INDEX.json, REPORT.md | None |
| Ingestion | `<SESSION_ID>` | INDEX.json, REPORT.md | RECEIPTS/, LEDGER_SUBSET.jsonl, MANIFESTS/ |
| Weekly Aggregate | `WEEKLY_<START>_TO_<END>` | INDEX.json, REPORT.md | None (references only) |

---

## Related Documents

- `docs/RECEIPT_SCHEMA_V2.md` - Receipt specification
- `docs/AUDIT_TRAIL_PROTOCOL.md` - Audit procedures
- `scripts/prosecutor_emit_evidence_bundle.py` - Bundle generation
- `tools/court_sweep.py` - Bundle validation

---

END OF SPECIFICATION
