# AUDIT_TRAIL_PROTOCOL.md - Reality 4 (The Prosecutor)

**Version**: 1.0  
**Status**: CANONICAL  
**Last Updated**: 2025-12-28T16:30:00-05:00

---

## Purpose

This document defines verification procedures for forensic reconstruction of ingestion operations. Every chunk must have a complete, auditable trail back to its source.

---

## Core Principles

1. **Every chunk MUST have a receipt** - No silent ingestion
2. **Receipts MUST be V2-compliant** - Schema validation required
3. **Session IDs MUST be consistent** - Traceability through time
4. **Orphans MUST be detected** - NULL or unreceipted chunks fail audit

---

## Audit Tools

### 1. audit_ingestion_trail.py

**Purpose**: Forensic reconstruction of all chunk ingestion operations

**Usage**:
```bash
python scripts/audit_ingestion_trail.py
```

**Checks**:
- Every chunk has `import_session_id`
- Every session ID has at least one receipt
- Database delta matches receipt claims
- Timeline coherence (created_at vs receipt timestamps)

**Exit Codes**:
- `0` = All chunks accounted for (PASS)
- `1` = Orphans detected (FAIL)
- `2` = Critical error

**Output**:
- Console summary report
- JSON report: `evidence/audits/INGESTION_TRAIL_AUDIT_<timestamp>.json`

---

### 2. Court Sweep: Orphan Detection

**Integration**: `tools/court_sweep.py` includes `audit_orphan_chunks()` check

**Purpose**: Real-time detection of chunks with NULL `import_session_id`

**Query**:
```sql
SELECT chunk_id, anchor_id 
FROM chunks 
WHERE import_session_id IS NULL
```

**Verdict**:
- `PASS` if 0 orphans
- `FAIL` if any orphans detected

---

### 3. Court Sweep: Receipt Validation

**Integration**: `tools/court_sweep.py` includes `audit_receipt_validation()` check

**Purpose**: Validate all V2 receipts in `evidence/` directory

**Process**:
1. Scan `evidence/**/RECEIPTS/RECEIPT_*.json`
2. Run `validate_receipt_v2.py` on each receipt
3. Report invalid receipts

**Verdict**:
- `PASS` if all receipts valid
- `WARN` if no receipts found
- `FAIL` if any receipts invalid

---

## Verification Workflow

### Step 1: Court Sweep (Pre-Flight)
```bash
python tools/cli/mw.py court sweep
```

**Expected Checks**:
- [OK] db_counts
- [OK] state_history_witness
- [OK] evidence_index
- [OK] bundle_uniformity
- [OK] encoding_reports_present
- [OK] receipt_validation
- [OK] orphan_chunks

**Verdict**: Must be `PASS` before proceeding

---

### Step 2: Ingestion Trail Audit (Deep Forensics)
```bash
python scripts/audit_ingestion_trail.py
```

**Expected Output**:
```
Total Chunks:          3446
Receipted Chunks:      3446
Orphan Chunks:         0 (0.00%)
Total Receipts:        XX
Unique Sessions:       XX
Sessions w/ Receipts:  XX

[OK] PASS: All chunks accounted for
```

**Verdict**: Must be `PASS` for Reality 4 compliance

---

### Step 3: Receipt Schema Validation (Spot Check)
```bash
python scripts/validate_receipt_v2.py evidence/<SID>/RECEIPTS/RECEIPT_*.json
```

**Expected Output**:
```
[OK] Receipt is valid
```

**Exit Code**: `0` (valid) or `1` (invalid)

---

## Orphan Remediation

If orphans are detected, follow this protocol:

### Option 1: Retroactive Receipt Generation (Preferred)
1. Identify the ingestion session from chunk metadata
2. Create a V2 receipt for that session
3. Document as "RETROACTIVE_RECEIPT" in receipt intent
4. Include justification in receipt metadata

### Option 2: Quarantine (Last Resort)
1. Move orphan chunks to quarantine table
2. Document in `docs/QUARANTINE_TOMBSTONES.md`
3. Do NOT delete (preserve evidence)

---

## Receipt Schema Requirements

All receipts must conform to **RECEIPT_SCHEMA_V2.md**:

### Required Fields
- `receipt_version`: "V2"
- `intent`: Descriptive intent string
- `generated_utc`: ISO8601 UTC timestamp
- `import_session_id`: Session ID (format: `S_<timestamp>_<descriptor>`)
- `anchor_id`: Anchor identifier
- `source_path`: Relative path to source file
- `db`: Database state (before/after/delta)
- `strict_rules`: All values must be "STOP"

### Validation
```bash
python scripts/validate_receipt_v2.py <receipt_path>
```

---

## Evidence Bundle Structure

Receipts must be stored in session-specific directories:

```
evidence/
  ??? <SESSION_ID>/
  ?   ??? RECEIPTS/
  ?   ?   ??? RECEIPT_CHUNKS_<anchor_id>_<descriptor>.json
  ?   ?   ??? RECEIPT_ANCHORS_<descriptor>.json
  ?   ??? ... (other evidence)
```

---

## Compliance Checklist

Reality 4 (The Prosecutor) requires:

- [ ] All ingestion scripts generate V2 receipts (mandatory)
- [ ] Court Sweep includes receipt validation
- [ ] Court Sweep includes orphan detection
- [ ] `audit_ingestion_trail.py` reports PASS
- [ ] Zero orphan chunks in database
- [ ] All receipts pass V2 schema validation

**Status**: CANONICAL (enforced)

---

## Related Documents

- `docs/RECEIPT_SCHEMA_V2.md` - Receipt specification
- `scripts/validate_receipt_v2.py` - Schema validator
- `scripts/audit_ingestion_trail.py` - Forensic reconstruction
- `tools/court_sweep.py` - Automated audit ritual

---

END OF PROTOCOL
