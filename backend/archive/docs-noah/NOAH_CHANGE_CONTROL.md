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


# CHANGE CONTROL (V2)
## Witnessed, Artifact-Driven Governance

---

## 0. Why Change Control Exists (Updated)

In environments without reliable git-based auditing  
(or where backups, folders, or tools may drift),

**we do not rely on memory, intention, or trust.**

We rely on:
- Witnesses
- Receipts
- Deterministic artifacts
- Cross-layer proof

This system treats **change itself as an auditable event**.

---

## 1. Core Principle

> If a change cannot explain **when**, **why**, **by whom**, and **from what state** it occurred ?  
> it is not a valid change.

Change Control is enforced **without rewriting history**.

---

## 2. Canonical Concepts (Reality 5)

### 2.1 Witness Epoch

All state-changing operations occur within a **Witness Epoch**:
- A continuous period where every transition carries a canonical `active_session_id`
- Enforced via STGRAIL + SID propagation
- Sealed explicitly when complete

Legacy gaps are documented via **addendum**, never erased.

---

### 2.2 Front-Door Rule

All mutations must pass through:
- `solob.ps1 record`
- `run_recorded.py`
- State guards
- Evidence emission

Back-door edits are considered **corruption**, even if well-intended.

---

## 3. The Chain of Receipts (Expanded)

Change Control is enforced through a **linked receipt chain**.

### 3.1 Session Lock  
`SESSION_LOCK.json`

- **What**: Snapshot of *data state*
  - DB schema + counts
  - Anchors
  - Evidence index
  - Manifests
- **When**: At the start of an implementation batch
- **Why**: Proves the starting point was clean, coherent, and sealed

This establishes the **?before? reality**.

---

### 3.2 Codebase Fingerprint (Before)  
`CODEBASE_BEFORE.json`

- **What**: SHA256 fingerprint of:
  - `scripts/`
  - `tools/`
  - `docs/`
- **When**: Immediately after Session Lock
- **Why**: Freezes the logic layer before intervention

---

### 3.3 Implementation (The Work)

Permitted actions:
- Script edits
- Tool additions
- Schema migrations (via recorder)
- Evidence rebuilds

Forbidden actions:
- Silent file edits
- Manual DB writes
- History rewrites
- Deleting evidence

---

### 3.4 Codebase Fingerprint (After)  
`CODEBASE_AFTER.json`

- **What**: SHA256 fingerprint after work is complete
- **Why**: Defines the new logic reality

---

### 3.5 Diff Report  
`CODEBASE_DIFF.json`

- **What**: Deterministic diff between BEFORE and AFTER
- **Why**: Enumerates *exactly* what changed

**Rule:**
> If a file appears in the diff and was not part of the declared intent, it is a violation.

---

### 3.6 Evidence Index Rebuild  
`INDEX.json`

- Recomputed after any change batch
- Ensures:
  - Receipts are discoverable
  - Bundles are counted
  - Cross-layer integrity holds

---

## 4. State Discipline (STGRAIL)

| State     | Allowed Actions                                  |
|----------|--------------------------------------------------|
| OBSERVE  | Read-only audits, inspection, proofs             |
| RECORD   | Writes, ingestion, migrations, indexing           |

Sanity checks may run in OBSERVE **only** when explicitly flagged as read-only.

---

## 5. Enforcement Mechanisms

Change Control is enforced by:

- **State Guards** (hard STOP)
- **Session IDs** (no anonymous writes)
- **Append-only evidence**
- **Cross-layer verification**
  - DB ? Evidence ? Manifests ? History
- **Proof Harness**
  - `prove.ps1`
  - `court_sweep.ps1`
  - `mw_full_proof.ps1`

---

## 6. Legacy Handling

Pre-Witness Epoch changes are:
- Cataloged
- Mapped
- Sealed via `STATE_HISTORY_LEGACY_SID_ADDENDUM.json`

They are:
- **Acknowledged**
- **Not rewritten**
- **Not silently ignored**

This preserves historical honesty.

---

## 7. How to Run (Canonical Flow)

```powershell
# 0. Enter RECORD
.\tools\solob.ps1 record -note "CHANGE: <intent>"

# 1. Session Lock
python scripts/run_recorded.py --intent "SESSION_LOCK" scripts/session_lock.py

# 2. Codebase Fingerprint (Before)
python scripts/run_recorded.py --intent "CODEBASE_BEFORE" `
  scripts/codebase_fingerprint.py -- `
  --out evidence/$SID/CODEBASE_BEFORE.json

# 3. Do Work
# (edit scripts / tools / docs)

# 4. Codebase Fingerprint (After)
python scripts/run_recorded.py --intent "CODEBASE_AFTER" `
  scripts/codebase_fingerprint.py -- `
  --out evidence/$SID/CODEBASE_AFTER.json

# 5. Diff Report
python scripts/run_recorded.py --intent "CODEBASE_DIFF" `
  scripts/codebase_diff_report.py -- `
  --before evidence/$SID/CODEBASE_BEFORE.json `
  --after  evidence/$SID/CODEBASE_AFTER.json `
  --out    evidence/$SID/CODEBASE_DIFF.json

# 6. Evidence Index
.\tools\solob.ps1 run `
  -intent "EVIDENCE: rebuild index" `
  -script scripts/evidence_index.py `
  -args @("--root","evidence","--out","evidence/INDEX.json")

# 7. Seal
.\tools\solob.ps1 observe -note "CHANGE SEAL: <summary>"
