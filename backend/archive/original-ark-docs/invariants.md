# SOLOB WRAPPER ? INVARIANTS (CANONICAL)
Version: V1.0  
Scope: Repo-wide invariants (governance + safety + traceability)

These invariants define what must remain true even as code evolves.
If an invariant must change, the change must be recorded in STATE_HISTORY and documented as a versioned revision.

---

## 0. PRIME DIRECTIVE
**Presence over performance. Evidence over vibes.**

This system is a *memory spine*, not a convenience tool.
Convenience is allowed only when it does not weaken auditability.

---

## 1. STGRAIL STATE MACHINE IS LAW
**Invariant:**
- The current state lives in `docs/STATE.json`.
- Allowed states: `OBSERVE`, `RECORD`, `(future) EXECUTE`.

**Rules:**
- `OBSERVE` = read-only posture; no recorded runs permitted.
- `RECORD` = recorded runs permitted via the front door.
- `EXECUTE` = reserved; must not be used casually.

**Enforcement:**
- `scripts/state_guard.py` blocks disallowed actions.
- Any state change must go through `scripts/state_transition.py` (or its approved wrapper tool).

---

## 2. ONLY ONE FRONT DOOR FOR STATE-CHANGING ACTIONS
**Invariant:**
Any script that writes to disk, changes DB state, or emits canonical artifacts MUST be executed via:

`python scripts/run_recorded.py --intent "..." <script> -- <args...>`

**Guaranteed outputs of a recorded run:**
- stdout + stderr captured to `logs/`
- immutable ledger event appended to `logs/ops_ledger.jsonl`
- consistent environment encoding protections (when applicable)

**Forbidden:**
- ?Direct python script.py? for any state-changing script
- Hidden execution via imports or package init side effects

---

## 3. INTENT MUST BE HUMAN-READABLE AND NON-EMPTY
**Invariant:**
Every recorded run must include a meaningful intent string.

**Rule:**
- Empty intent is prohibited.
- Intent must explain *why* the action happened, not just what was run.

Rationale: intent is part of provenance.

---

## 4. APPEND-ONLY GOVERNANCE (NO HISTORY REWRITES)
**Invariant:**
- `logs/ops_ledger.jsonl` is append-only.
- `docs/STATE_HISTORY.md` is append-only.
- Failures remain visible; success does not erase them.

Rationale: antifragility requires preserving the ?scar tissue.?

---

## 5. ANCHORS ARE CANON (CONTENT IS NEVER MODIFIED BY PIPELINE)
**Invariant:**
Anchors under `anchors/canon/` are treated as source-of-truth.
Scripts may:
- snapshot anchors (hash manifest)
- register anchor references into DB
- chunk (extract) without rewriting the original anchor files

Scripts MUST NOT:
- rewrite anchor content
- ?clean up? author text
- normalize meaning
- paraphrase or interpret during ingestion

Structure may change. Meaning must not.

---

## 6. MANIFEST FIDELITY IS REQUIRED
**Invariant:**
Any canonical anchor must be traceable to a manifest entry:
- rel_path (normalized)
- sha256

Rationale: the manifest is the cryptographic witness that ?this file existed in this exact state.?

---

## 7. IMPORT SESSION IDS ARE BATCH IDENTITIES
**Invariant:**
Any registration/ingestion batch must be labeled with exactly one `import_session_id` (SID),
and that SID must propagate through:
- anchor registration
- chunk imports
- evidence bundles / receipts
- checkpoints

Rationale: one batch = one story = one trace.

---

## 8. FAILURE MUST STOP THE LINE
**Invariant:**
If a critical invariant is violated, the script must exit non-zero and halt.

Examples (hard stop):
- missing anchor file
- chunk_id collision
- schema mismatch
- manifest mismatch
- registry mismatch

Forbidden:
- silent fallback
- auto-repair without recorded intent and explicit script name

---

## 9. NAMING INVARIANTS + GRANDFATHERING
**Invariant:**
The repo enforces naming rules for determinism and portability (Windows + tooling + future packaging).

**Rule:**
- New canon artifacts SHOULD use: lowercase, digits, underscores, hyphens.
- Avoid spaces and special punctuation in canonical paths where possible.

**Grandfathering:**
Legacy paths that violate naming rules may be allowlisted in:
- `docs/NAMING_ALLOWLIST.json`

Allowlisting must be:
- explicit
- minimal
- documented (why it exists, and whether it will be migrated later)

Rationale: you don?t weaken the law; you record the exception.

---

## 10. CANONICAL ARTIFACTS MUST BE REPRODUCIBLE
**Invariant:**
Canonical emitted artifacts (maps, manifests, evidence bundles) must be deterministic:
- stable ordering
- stable formatting rules
- stable normalization rules

When ?ASCII-safe? versions exist, they must be explicitly labeled.

---

## 11. SEALING RITUAL (RETURN TO OBSERVE)
**Invariant:**
After completing a defined operation window (Monk/Cartographer/Prosecutor/Artisan),
the system SHOULD return to `OBSERVE` with a non-empty note.

Rationale: prevents accidental shuffles; reinforces conscious operation.

---

## Closing Principle
**This repo is a courtroom + a temple.**
If you can?t explain what happened, when it happened, and why it happened?
it didn?t happen.
