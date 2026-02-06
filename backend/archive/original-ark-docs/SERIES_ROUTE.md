# SERIES_ROUTE (V1)
Monk -> Cartographer -> Prosecutor -> Artisan -> Product Builder

## Purpose
This repo is a *proof-first* wrapper around memory ingestion.
We do not ?trust the system.? We *force it to testify*.

**Core rule:** If it cannot be audited, it is not allowed.

---

## States (STGRAIL)
- **OBSERVE**: read-only posture. No recorded runs permitted.
- **RECORD**: recorded runs permitted via `scripts/run_recorded.py`.
- **EXECUTE**: reserved (future).

**Law:** State-changing scripts must be run only through the front door:
`python scripts/run_recorded.py --intent "..." script.py -- ...`

---

## Bridge Rituals
Real implementation requires more than just states; it requires strict handoffs.
1. **DRIFT re-snapshot**: If reality drifted from the last snapshot, manifest the drift before fixing it.
2. **INGEST PILOT**: A controlled, small ingestion (e.g. Lexicon A) to prove the pipe.
3. **SESSION LOCK**: The baseline ritual for any implementation batch. Captures DB, anchors, and code state.

---

## Reality 1 ? MONK (Anchors Only)
**Goal:** Create an empty-but-real spine.
**Allowed:** register anchors, manifests, invariants, schema init, proofs.
**Forbidden:** chunks, embeddings, interpretation.

**Entry criteria**
- DB exists (or will be initialized)
- State can be set to RECORD intentionally

**Allowed actions**
- `init_db.py`, `snapshot_anchors.py`, `register_anchors_from_registry.py`
- `sanity_check.py`, `pre_ingestion_audit_ext.py`

**Exit criteria**
- anchors registered
- counts prove anchors-only baseline (anchors>0, chunks=0, runs=0)
- OBSERVE seal written

**Typical artifacts**
- `data/snapshots/anchors_manifest_*.json`
- `docs/STATE.json`, `docs/STATE_HISTORY.md`
- `docs/invariants.md` + `docs/invariants.lock.json`

---

## Reality 2 ? CARTOGRAPHER (Maps)
**Goal:** Emit navigation maps. No new truth.
**Allowed:** read DB + registry + manifest and output maps.
**Forbidden:** altering anchors or meaning.

**Exit criteria**
- `docs/ANCHORS_MAP.md` emitted
- map matches DB+registry+manifest counts

**Typical artifacts**
- `docs/ANCHORS_MAP.md`
- `docs/ANCHORS_MAP_ASCII.md`

---

## Reality 3 ? PROSECUTOR (Evidence Bundle)
**Goal:** Produce courtroom-grade chain-of-custody.
**Allowed:** bundle receipts, checkpoints, verification scripts, codebase fingerprints.
**Forbidden:** interpretation, rewriting content.

**Exit criteria**
- evidence bundle exists
- verifier passes (hashes + ledger match)
- DB checkpoint written
- **Code Change Receipts** generated (BEFORE vs AFTER fingerprints + DIFF report)

**Typical artifacts**
- `evidence/<SID>/...`
  - `SESSION_LOCK.json`
  - `CODEBASE_BEFORE.json`
  - `CODEBASE_AFTER.json`
  - `CODEBASE_DIFF.json`
  - `audit_*.json`

---

## Reality 4 ? ARTISAN (Refinement Without Drift)
**Goal:** Improve ergonomics without altering meaning.
**Allowed:** ASCII-safe outputs, naming policies, allowlists, stricter guards.
**Forbidden:** silent auto-repair, covert rewrites.

**Exit criteria**
- guardrails strengthened
- audits still pass
- evidence index rebuilds cleanly

**Typical artifacts**
- `docs/NAMING_ALLOWLIST.json`
- `evidence/INDEX.json`

---

## Reality 5 ? PRODUCT BUILDER (Interfaces + Workflows)
**Goal:** Build tools on top of a proven spine.
**Allowed:** UI, browsing, citations, export, controlled agent tooling.
**Forbidden:** any ?side door? execution; everything routes through recorded runs.

---

## Special Note: Ingestion Begins After Prosecutor Floor
Once chunks exist, **pre-ingestion audits no longer apply**.
Use **post-ingestion audits** that expect chunks and verify:
- no duplicate chunk_ids
- no duplicate locators
- no orphan chunks
- stable manifest + receipts + ledger chain

---

## Closing Principle
**The system is not a brain.**
It is a courtroom clerk.
It files evidence; it does not invent meaning.
