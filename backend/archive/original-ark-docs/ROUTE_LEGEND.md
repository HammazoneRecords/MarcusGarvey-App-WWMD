# ROUTE LEGEND (V1)

## Purpose
This document explains the ?front door? scripts, what they do, and which state allows them.
No side doors: **clean entry or no entry**.

---

## States
- **OBSERVE**: read-only posture. No recorded runs permitted.
- **RECORD**: recorded runs permitted via the front door.
- **EXECUTE**: reserved (disabled in V1).

---

## Front Door (Canonical)
### scripts/run_recorded.py
- Role: only allowed execution wrapper for state-changing scripts
- Guarantees:
  - sets `SOLOB_RECORDED_RUN=1`
  - captures stdout/stderr into `logs/`
  - appends an immutable event into `logs/ops_ledger.jsonl`
- Pattern:
  - Always pass child script args after `--`
  - Example:
    `python scripts/run_recorded.py --intent "..." scripts/some_script.py -- --arg1 X`

### tools/cli/mw.py (The "mw" CLI)
- Role: Unified ergonomic wrapper for all operations:
  - `mw state` (view current state)
  - `mw observe --note "..."` (state transition to OBSERVE)
  - `mw record --note "..."` (state transition to RECORD)
  - `mw run --intent "..." --script <script> -- [args]` (recorded execution)
  - `mw audit ...` (run audits)
- Guarantees:
  - Routes state transitions through `scripts/state_transition.py`
  - Routes execution through `scripts/run_recorded.py`
  - Enforces confirmation latches ("YES_I_MEAN_IT")
  - Manages Session IDs (SIDs) automatically

### scripts/state_guard.py
- Role: blocks actions not allowed in the current state

### scripts/state_transition.py
- Role: changes `docs/STATE.json` and appends to `docs/STATE_HISTORY.md`

---

## Script Map

| Script | Purpose | Inputs | Outputs | Required State |
|:---|:---|:---|:---|:---|
| **Core** | | | | |
| `snapshot_anchors.py` | Create baseline of anchors | anchors dir | `data/snapshots/anchors_manifest_*.json` | RECORD |
| `init_db.py` | Initialize SQLite | schema.sql | `data/memory.db` | RECORD |
| `sanity_check.py` | Verify empty DB state | DB | stdout | RECORD |
| `session_lock.py` | Capture implementation baseline | DB, anchors, ledger | `evidence/<SID>/SESSION_LOCK.json` | RECORD |
| **Audit & Maps** | | | | |
| `pre_ingestion_audit_ext.py` | Check manifest/DB/schema before chunks | DB, manifest | stdout | RECORD/OBSERVE |
| `cartographer_emit_anchors_map.py` | Visual map of anchors | DB | `docs/ANCHORS_MAP.md` | RECORD |
| `naming_guard.py` | Enforce file/folder naming | anchors dir | stdout (or `ALLOWLIST.json`) | RECORD |
| **Ingestion** | | | | |
| `import_lexicon_chunks_v1_1.py` | Import chunks from raw | raw json | DB chunks | RECORD |
| `lexicon_stamp_row_index.py` | Add row_index to raw | raw json | modified json, orphan backup | RECORD |
| `post_ingestion_audit_ext.py` | Verify chunks integrity | DB | stdout | RECORD |
| **Evidence** | | | | |
| `prosecutor_emit_evidence_bundle.py` | Gather proofs | DB, logs | `evidence/<SID>/` | RECORD |
| `prosecutor_verify_evidence_bundle.py` | Verify proofs | evidence dir | stdout | RECORD/OBSERVE |
| `prosecutor_db_checkpoint.py` | Snapshot DB state | DB | `evidence/<SID>/db_checkpoint.db` | RECORD |
| `evidence_index.py` | Index all evidence | evidence dir | `evidence/INDEX.json` | RECORD |
| **Code Receipts** | | | | |
| `codebase_fingerprint.py` | Hash current codebase state | codebase | JSON receipt | RECORD |
| `codebase_diff_report.py` | Compare two fingerprints | 2x JSON receipts | JSON diff report | RECORD |
| **Ritual Engine (Reality 5)** | | | | |
| `ritual_engine.py` | Config-driven ingestion | ritual config JSON | DB chunks + V2 receipt | RECORD |
| `mw ritual list` | List available rituals | - | stdout | OBSERVE/RECORD |
| `mw ritual run --config <path>` | Execute ritual | ritual config | DB + receipt | RECORD |
| `mw ritual validate --config <path>` | Dry-run validation | ritual config | stdout | OBSERVE/RECORD |

---

## Canonical V1 Sequences

### A) Anchors-Only (Monk / Pre-Ingestion)
1) `snapshot_anchors.py` -> `data/snapshots/anchors_manifest_*.json`
2) `init_db.py` -> `data/memory.db`
3) `register_anchors_from_registry.py` -> anchors table only
4) `sanity_check.py` -> verifies empty DB coherence
5) `pre_ingestion_audit_ext.py` -> checks manifest + DB + schema + ledger coherence
6) `cartographer_emit_anchors_map.py` -> `docs/ANCHORS_MAP*.md`
7) `session_lock.py` -> baseline for evidence

### B) Code Change Workflow
1) `codebase_fingerprint.py` (BEFORE)
2) Make edits
3) `codebase_fingerprint.py` (AFTER)
4) `codebase_diff_report.py` (DIFF)
5) Rebuild Index:
   ```bash
   python tools/cli/mw.py run \
     --intent "EVIDENCE: rebuild index sid=$SID" \
     --script scripts/evidence_index.py \
     -- --root evidence --out evidence/INDEX.json
   ```

### C) Ingestion Pilot
1) `post_ingestion_audit_ext.py` -> confirms DB integrity + no duplicates + no orphans
2) `import_lexicon_chunks_v1_1.py` -> deterministic chunks only (no interpretation)
3) Resnap:
   - new `anchors_manifest_*.json`
   - re-emit `docs/ANCHORS_MAP*.md`
   - Rebuild Index:
     ```bash
     python tools/cli/mw.py run \
       --intent "EVIDENCE: rebuild index sid=$SID" \
       --script scripts/evidence_index.py \
       -- --root evidence --out evidence/INDEX.json
     ```
4) Seal -> OBSERVE

---

## Rule
If a script can mutate reality, it must:
1) be blocked outside RECORD, and
2) be blocked without `SOLOB_RECORDED_RUN=1`, and
3) leave logs + ledger evidence.
