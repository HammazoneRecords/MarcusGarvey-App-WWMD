# PROPOSAL: Evidence Bundle V2 Migration Plan

## Problem Statement
The recent Court Sweep identified 32 legacy (V1) bundles in `evidence/bundles/`. While these contain historical evidence, they lack the `INDEX.json` and `REPORT.md` files required by the V2 specification, leading to a `[WARN]` status in audits.

## Objective
Standardize all historical evidence bundles to the V2 specification without modifying the underlying evidence files.

## Proposed Workflow

### 1. Script Development
Create `scripts/prosecutor_upgrade_bundles_v2.py`. This script will:
- Traverse `evidence/bundles/`.
- Identify folders lacking `INDEX.json`.
- Extract metadata (Session ID, Timestamp, Descriptor) from the folder name.
- Look for `BATCH_RECEIPT.json` to recover any internal metadata.

### 2. Backfill Logic
For each legacy bundle, generate:
- **INDEX.json**:
  ```json
  {
    "type": "grandfathered_v1",
    "ts_utc": "TIMESTAMP_FROM_DIR",
    "bundle_version": "V2",
    "migration_note": "Upgraded from V1 via prosecutor_upgrade_bundles_v2.py",
    "files": [...]
  }
  ```
- **REPORT.md**:
  A standard markdown report summarizing the migration and the assumed validity of the historical bundle.

### 3. Execution (Staged)
- **Dry Run**: Print the list of bundles to be modified and the proposed metadata.
- **Commit**: Execute the write operations.

### 4. Verification
Run `python tools/court_sweep.py` to ensure the `bundle_layout` check moves from `[WARN]` to `[PASS]`.

---

## Next Steps
1. Approve this plan.
2. I will implement and run the migration script.
