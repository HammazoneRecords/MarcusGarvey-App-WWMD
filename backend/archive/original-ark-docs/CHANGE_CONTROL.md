# CHANGE CONTROL (V1)

## Philosophy
In a system without git-based change auditing (e.g. relying on manual backups or untracked folders), we must enforce **Change Control** through artifacts.

We do not trust ourselves to "remember what changed." We generate **receipts**.

## The Chain of Receipts

### 1. Session Lock (`SESSION_LOCK.json`)
- **What**: A snapshot of the *data* state (DB, anchors, schema, manifest, ledger).
- **When**: At the start of an implementation batch.
- **Why**: Proves the starting point was clean, consistent, and identical to the last SEAL.

### 2. Codebase Fingerprint (`CODEBASE_BEFORE.json`)
- **What**: A SHA256 map of the *code* (scripts, docs, tools).
- **When**: Immediately after Session Lock, *before* touching code.
- **Why**: Proves state of the code logic before intervention.

### 3. Implementation (The Work)
- You edit scripts, add features, or run migrations.

### 4. Codebase Fingerprint (`CODEBASE_AFTER.json`)
- **What**: A SHA256 map of the *code* after work is done.
- **When**: Immediately after edits are complete and verified.

### 5. Diff Report (`CODEBASE_DIFF.json`)
- **What**: A computed difference between BEFORE and AFTER.
- **Why**: Lists exactly which files were added, removed, or modified.
- **Audit**: If a file is in the Diff Report but wasn't part of the plan, it is a violation.

## How to Run

```powershell
# 1. Establish Baseline
python scripts/run_recorded.py --intent "BASELINE" scripts/codebase_fingerprint.py -- --out evidence/S_001/CODEBASE_BEFORE.json

# 2. Do Work
# ... edit files ...

# 3. Establish New State
python scripts/run_recorded.py --intent "POST_WORK" scripts/codebase_fingerprint.py -- --out evidence/S_001/CODEBASE_AFTER.json

# 4. Generate Diff
python scripts/run_recorded.py --intent "DIFF_REPORT" scripts/codebase_diff_report.py -- --before evidence/S_001/CODEBASE_BEFORE.json --after evidence/S_001/CODEBASE_AFTER.json --out evidence/S_001/CODEBASE_DIFF.json

# 5. Rebuild Evidence Index
.\tools\solob.ps1 run `
  -intent "EVIDENCE: rebuild index sid=$SID" `
  -script scripts/evidence_index.py `
  -args @("--root","evidence","--out","evidence/INDEX.json")
```
