---
trigger: always_on
---

## IDE Agent Rules (Solob Wrapper Governance Protocol)

### 1) Logging is mandatory

* **No direct edits to logs by hand.**
* Agent must use a **scripted logger** (or append-only audit writer) for:

  * every run
  * every file mutation
  * every quarantine/tombstone
  * every “decision” that changes system state

### 2) UTF-8 is law (end-to-end)

* All reads/writes must specify encoding explicitly: `encoding="utf-8"`.
* Any generated file must be UTF-8.
* Any CLI output capture should be UTF-8 safe (`PYTHONUTF8=1`, `PYTHONIOENCODING=utf-8`).
* If encoding ambiguity appears → **stop and ask** (don’t “fix” by guessing).

### 3) Single execution surface

* Run everything from the **IDE terminal** (your chosen environment) to avoid cross-contamination.
* If PowerShell is used, it must be:

  * run inside IDE terminal
  * invoked via repo tools (e.g., `tools/*.ps1`), not random one-offs
  * logged with an evidence/audit file

### 4) Script State Protocol is enforced

* Agent must read `docs/SCRIPT_STATE_PROTOCOL.md` + registry first.
* Default state for unknown files = **OBSERVE**.
* **STABLE**: ask permission before editing.
* **FROZEN**: never edit; propose a new file/version.

### 5) “No silent mutation”

Before modifying anything, agent must output:

* list of files to change (grouped by state)
* why each change is required
* what evidence will be produced after change (audit file name + location)

### 6) Evidence-first behavior

Any meaningful action must emit at least one:

* audit report in `evidence/audits/`
* or bundle in `evidence/bundles/SID_*`
* or receipt validation proof

If it can’t produce evidence → it must say so and ask what to do.

### 7) Deterministic reruns are a requirement

* Every tool must be runnable twice with same inputs → same outputs (or explain why not).
* If nondeterminism detected → log it as a defect and stop.

### 8) Roadblock protocol (your new rule)

If the agent hits **4 consecutive roadblocks**, it must:

* stop automation
* summarize the 4 blockers in plain language
* provide 2–3 resolution options
* ask you for the decision

*(Roadblock = same failure class repeating: missing file, encoding error, permission denied, inconsistent paths, etc.)*

### 9) Never “assume DB state”

* DB is **UNTRUSTED** until verified by explicit queries (counts, schema version).
* Agent must not claim ingestion happened unless receipts/bundles prove it.

### 10) “Quarantine, don’t gamble”

If corruption or uncertainty is detected:

* quarantine with timestamped suffix
* tombstone entry in `docs/QUARANTINE_TOMBSTONES.md`
* recreate clean only when needed

### 11) Path discipline

* Always resolve repo root reliably.
* Never hardcode your Windows user path inside logic.
* Normalize separators + use `Pathlib`.

### 12) Time + SID discipline

* Every run must have:

  * UTC -5 timestamp (Kingston)
  * SID in filenames for bundles where applicable
* Any state transition must be SID-witnessed.

### 13) No truncated error logs

* Any failure must write **full traceback** to an audit file.
* The summary can be short, but the evidence must be complete.

### 14) Small changes, small blast radius

* Prefer creating new tools/scripts over editing settled ones.
* Keep commits/changesets minimal and reversible (even though we’re “forward only”, we still want traceability).

### 15) “Implementation Delta” stays current

* Agent must update or generate an **Implementation Delta checklist** after changes:

  * DONE / PARTIAL / OPEN
  * evidence link(s) for each DONE claim

---

Copy this into the top of your IDE agent prompt:

```text
OPERATING RULES (HARD):
1) Use scripts to add logs; never hand-edit logs. Every action emits evidence in evidence/audits or evidence/bundles.
2) UTF-8 everywhere: explicit encoding on all read/write; keep PYTHONUTF8 and PYTHONIOENCODING enforced.
3) Run all commands ONLY in the IDE terminal (single execution surface). No external shell runs unless scripted + logged.
4) Enforce SCRIPT_STATE_PROTOCOL + SCRIPT_STATE_REGISTRY: unknown files default OBSERVE; STABLE requires user consent; FROZEN never edited (new version instead).
5) No silent mutation: before edits, list files to change grouped by state + evidence to produce.
6) DB is UNTRUSTED until verified by explicit queries + receipts.
7) If 4 consecutive roadblocks occur, STOP and request user decision with options.
8) No truncated errors: always write full traceback/output to evidence/audits.
```

*court_sweep must never declare PASS/FAIL without attaching its full raw outputs + exit codes + environment snapshot evidence