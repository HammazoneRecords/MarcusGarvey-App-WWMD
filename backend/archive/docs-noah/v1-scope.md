# Solob Wrapper V1 ? Scope + Operator Workflow (Front-Door Safe)

This file defines **V1 scope** for the Solob Wrapper repository and provides the **navigation + workflow** needed to operate, audit, and extend the wrapper safely.

V1 is a **proof-first, offline-first memory wrapper** with STGRAIL state gating, evidence receipts, SQLite storage, deterministic ingestion, and audit harnesses.

> Vision and future product direction are intentionally excluded from this file.
> See `docs/vision.md` for long-horizon intent.

---

## 0) What V1 Guarantees (Non-Negotiables)

V1 is designed to make the following true:

- **STGRAIL discipline is enforced**
  - OBSERVE blocks state-changing operations (unless explicitly allowed as read-only audit with flags).
  - RECORD is required for anything that writes to DB / evidence / state history.
- **Front-door auditable**
  - Every registered anchor maps to a manifest entry and has receipts in `evidence/`.
- **Database coherence**
  - Required tables exist; chunks/anchors relationships are valid.
  - No chunks exist without anchors (structural integrity).
- **Reproducibility over vibes**
  - Embeddings are derivative artifacts; canonical truth is the anchor + chunk + receipt chain.
- **Chain constitution is immutable**
  - payload_v1 hash algorithm is frozen (chain/1.0 spec)
  - Changes require version bump (payload_v2), never silent mutation
  - Single canonical implementation prevents drift

---

## 1) Repo Navigation (Where Things Live)

### Primary ?Human? entry points
- `README.md` ? quick start / operator intro
- `docs/roadmap.md` ? V1 plan and sequencing
- `docs/v1-scope.md` ? this file (scope + workflow + conventions)
- `docs/vision.md` ? long-term vision and philosophy
- `docs/invariants.md` + `docs/invariants.lock.json` ? invariants and locked fingerprints
- `docs/STATE.json` + `docs/STATE_HISTORY.md` ? current state + state transitions log
- `docs/CHANGE_CONTROL.md` ? change discipline for the repo
- `docs/KNOWN_ARTIFACTS.md` ? canonical artifacts inventory
- `docs/ANCHORS_MAP.md` / `docs/ANCHORS_MAP_ASCII.md` ? anchor map for humans

### Governance & Receipt System
- `docs/RECEIPT_LIFECYCLE_RULES.md` ? receipt immutability and lifecycle governance
- `docs/RECEIPT_SCHEMAS.md` ? receipt structure and validation schemas
- `docs/The 7 Classes Of Receipts.md` ? receipt taxonomy and classification
- `docs/TIMEZONE_REFERENCE.md` ? timezone conventions (Kingston UTC-5)
- `docs/threat-model.md` ? corruption resistance and anti-fragility
- `docs/CHAIN_VERSIONING_RULES.md` ? chain constitution versioning discipline
- `docs/IMPORT_STABILITY.md` ? import bootstrap anti-drift strategy
- `docs/RECEIPT_CHAIN_LAYERING.md` ? optional Merkle chain strategy
- `docs/RECEIPT_CHAIN_IMPLEMENTATION.md` ? chain implementation summary

### Canon sources (inputs)
- `anchors/` ? canonical anchor files (PDFs / JSON / MD)
  - `anchors/canon/` ? canonical content by category
  - `anchors/wrapper_anchor_invariants/WAI.md` ? invariants anchor

### Storage (truth containers)
- `data/memory.db` ? SQLite database (canonical storage for anchors/chunks/runs)
- `data/schema.sql` ? schema definition
- `data/checkpoints/` ? DB snapshots/checkpoints (evidence-grade)
- `data/orphans/` ? quarantined artifacts (not canonical)

### Evidence (receipts + bundles)
- `evidence/` ? witness sessions, receipts, stamps, ledgers, bundles, global index
  - Each SID directory is a courtroom folder.
  - `evidence/INDEX.json` is the front-door evidence index.
  - **Receipts are immutable** ? never edited, only superseded or sealed.
  - See [RECEIPT_LIFECYCLE_RULES.md](./RECEIPT_LIFECYCLE_RULES.md) for governance.
  - See [The 7 Classes Of Receipts.md](./The%207%20Classes%20Of%20Receipts.md) for taxonomy.

### Core Python systems
- `core/` ? constitutional implementations (chain hashing, immutable canon)
- `scripts/` ? operator scripts (entry tools, audits, fingerprints, guard rails)
- `ingestion/` ? ingestion pipeline (register anchors, chunking, embeddings)
- `retrieval/` ? searching/ranking across chunks
- `runs/` ? answering and run provenance plumbing
- `utils/` ? shared utilities (hashing, sid, time, validation, receipt chain)
- `api/` ? minimal API layer (V1 uses local SQLite; API is optional surface)

### Operator harnesses (PowerShell)
- `tools/solob.ps1` ? state transitions (observe/record) + discipline gates
- `tools/mw_full_proof.ps1` ? full proof suite (Reality 1?5 harness)
- `tools/court_sweep.ps1` ? structured audit sweep
- `tools/prove.ps1` ? proof helper runner
- `tools/verify_witness_epoch.ps1` ? witness epoch verification

### UI (optional surface)
- `frontend/` ? lightweight front-end for interacting with wrapper state/visuals
## 1.1 Folder -> Meaning (Repo Compass)

This table is the fast map: **where to look**, **what is canonical**, and **what must remain derivative**.
It also includes **planned future folders** so expansion is pre-labeled and doesn?t become drift.

| Path / Folder | Meaning (Purpose) | Canonical? | Typical Contents | Rules / Notes |
|---|---|---:|---|---|
| `anchors/` | **Source-of-truth inputs** (raw canon) | [OK] Yes | PDFs, JSON lexicon, MD notes | Inputs only. Never generated by scripts except by explicit human placement. |
| `anchors/canon/` | Canon materials grouped by domain | [OK] Yes | BoS PDF, TMS PDF, lexicon JSONs | Must remain stable; changes require receipts + state discipline. |
| `anchors/wrapper_anchor_invariants/` | Invariants-as-anchor (WAI) | [OK] Yes | `WAI.md` | Treat as constitutional text. Changes are rare + audited. |
| `data/` | **SQLite truth container + snapshots** | [OK] Yes | `memory.db`, `schema.sql` | DB writes require RECORD unless read-only flags. |
| `data/checkpoints/` | DB checkpoint artifacts | [OK] Yes | DB copies, checkpoint receipts | Checkpoints referenced by evidence receipts; do not ?clean up? casually. |
| `data/orphans/` | Quarantine zone for suspicious/extra artifacts | [ERROR] No | backups, drafts, stray files | Nothing here is trusted until re-anchored + receipted. |
| `evidence/` | **Courtroom evidence tree** (receipts, bundles, indexes) | [OK] Yes | SID folders, receipts, stamps, ledgers | Evidence is append-only in spirit. Don?t edit historical receipts. |
| `evidence/<SID>/` | A single witnessed session folder | [OK] Yes | receipts, audits, bundle index | Every write window should have an SID and leave a trace here. |
| `docs/` | Human-readable governance + maps + protocols | [OK] Yes | invariants, scope, state history, maps | If it changes procedure, it must be versioned + disciplined. |
| `core/` | **Constitutional implementations** (immutable canon) | [OK] Yes | chain_constitution.py | Versioned canon; modifications require version bump (e.g. payload_v2). |
| `scripts/` | Python operator scripts (guards, audits, generators) | [OK] Yes | `sanity_check.py`, `snapshot_anchors.py` | Must parse clean; harness should verify parse gates. |
| `tools/` | PowerShell harness + state control entrypoints | [OK] Yes | `solob.ps1`, `mw_full_proof.ps1` | ?Front door? commands. Keep stable and documented. |
| `ingestion/` | Ingestion pipeline (register -> chunk -> embed) | [OK] Yes | chunkers, importers, embedding scripts | Embeddings are derivative; chunking must be deterministic. |
| `retrieval/` | Search + ranking across chunks | [OK] Yes | rank/search modules | Should be pure functions over DB where possible. |
| `runs/` | Run execution + provenance + citations | [OK] Yes | run models, answer plumbing | Runs are outputs; must reference chunks via citations edges. |
| `api/` | Minimal API surface (optional interface) | [WARN] Surface | FastAPI/Flask app, DB access | Must not bypass STGRAIL. Writes require RECORD + receipts. |
| `frontend/` | Lightweight UI/operator surface | [WARN] Surface | HTML/JS/CSS, state viewer | UI must not become a second truth store. |
| `utils/` | Shared small utilities | [OK] Yes | sid/time/hash/validate helpers | Keep dependency-light; used across scripts. |
| `logs/` | Local run logs (debugging + reproducibility help) | [ERROR] No | stdout/stderr captures | Useful but not canonical evidence. Evidence lives in `evidence/`. |
| `.venv/` | Local Python environment | [ERROR] No | installed packages | Never commit; never treated as part of proof chain. |
| `.vs/` | IDE metadata | [ERROR] No | indices, workspace state | Never treated as canonical. |
| `tests/` *(future)* | Automated tests for invariants + scripts | [OK] Yes | unit tests, integration tests | Future: run in CI; should mirror harness expectations. |
| `ci/` *(future)* | CI configuration + reproducibility checks | [OK] Yes | GitHub Actions / pipelines | Future: enforce parse gates, sanity checks, fingerprints. |
| `migrations/` *(future)* | DB schema migrations | [OK] Yes | numbered migration scripts | Future: upgrade DB without breaking audit chain. |
| `schemas/` *(future)* | JSON schema definitions for receipts/manifests | [OK] Yes | `*.schema.json` | Future: lock formats; prevent ?creative receipts.? |
| `configs/` *(future)* | Central config profiles | [OK] Yes | env templates, defaults | Future: keep config explicit and diffable. No secrets committed. |
| `models/` *(future)* | Local model artifacts (NOT training data) | [WARN] Derivative | gguf pointers, metadata | Future: store references + hashes, not private data. |
| `embeddings/` *(future)* | Embedding caches/exports | [ERROR] Derivative | vector exports, indexes | Embeddings must be reproducible from chunks; never canonical truth. |
| `exports/` *(future)* | Human/export packages | [ERROR] Output | PDFs, zips, reports | Output-only; regenerate from canon+DB. |
| `notebooks/` *(future)* | Experimental analysis | [ERROR] No | Jupyter notebooks | Allowed for exploration, but results must be ?blessed? into scripts/docs if adopted. |
| `plugins/` *(future)* | Optional extension modules | [OK] Yes | tool adapters, extra retrievers | Must respect invariants; no bypassing witness gates. |
| `integrations/` *(future)* | External connectors | [OK] Yes | cloud sync adapters, importers | Must be opt-in; must preserve receipts + provenance. |
| `secrets/` *(future, discouraged)* | Secret storage (prefer OS keychain) | [ERROR] No | placeholder only | Avoid. If needed, use `.gitignore` + local secret manager. |

**Legend**
- **Canonical** = part of the auditable truth chain (inputs, DB, evidence, governance).
- **Surface** = allowed interface layer, but must not become a competing truth store.
- **Derivative/Output** = reproducible artifacts; safe to delete/regenerate.

     **88** 
**Canon must be hashable.**

**Derivatives must be reproducible.**

**Surfaces must be gated.** 
     **88**

---

## 2) V1 Workflow: The ?Reality Ladder?

V1 work is staged so the system is always auditable:

### Reality 1 ? Monk: Anchors-only
Goal: register canonical anchors only, no chunking, no runs.

Key outputs:
- anchor registry entries
- receipts in `evidence/<SID>/anchors_receipts/`
- manifest snapshots

### Reality 2 ? Cartographer: Maps, indexes, fingerprints
Goal: generate maps + indexes that describe the system.

Key outputs:
- anchors map (`docs/ANCHORS_MAP*.md`)
- evidence index (`evidence/INDEX.json`)
- codebase fingerprints/diff reports

### Reality 3 ? Prosecutor: Court sweeps + bundles
Goal: verify all invariants and build evidence bundles.

Key outputs:
- bundle indexes and verification receipts
- DB checkpoint receipts
- court sweep logs

### Reality 4 ? Artisan: UI + ergonomics (safe surfaces)
Goal: operator usability without weakening invariants.

Key outputs:
- non-canonical UI scaffolds (no truth stored outside DB/evidence)

### Reality 5 ? Front-Door Safe (Audit-grade)
Goal: prove the repository is coherent from the ?front door.?

Key properties:
- All anchors mapped to manifest sha256.
- All anchors have receipts and associated chunks (where applicable).
- Sanity checks pass in OBSERVE via read-only allowance flags.

---

## 3) State Discipline (STGRAIL)

### States
- **OBSERVE**: read-only posture (no writes)
- **RECORD**: write-enabled posture (witnessed)

### Rules
- Use `tools/solob.ps1` for state transitions.
- Do not edit `docs/STATE_HISTORY.md` manually (avoid drift + encoding artifacts).

### Typical transition commands
- Enter RECORD (with a note):
  - `.\tools\solob.ps1 record -note "why this write window exists"`
- Return to OBSERVE (seal note):
  - `.\tools\solob.ps1 observe -note "seal note + what was completed"`

---

## 4) Proof + Audit: How We Confirm Reality

### Primary proof harness (recommended)
- `.\tools\mw_full_proof.ps1 -RepoRoot . -RequireAZ -VerifySupremeBundle`

This harness checks:
- state + witness epoch
- parse gates
- court sweep (layers)
- evidence index integrity
- DB sanity checks (read-only allowed in OBSERVE with flags)
- lexicon counts audit (A?Z)
- anchor->chunks inspection
- bundle verification (optional)

### Sanity check (DB coherence)
- `python .\scripts\sanity_check.py --allow-observe`

Expected success signals:
- required tables present
- anchors/chunks counts present
- import_session_id populated
- lexicon chunks populated correctly
- run_citations edges valid

---

## 5) Ingestion Model (V1)

V1 ingestion is deterministic and evidence-backed.

### 5.1 Anchor registration (before chunking)
- Anchors originate from `anchors/`.
- Registration creates:
  - DB anchor row
  - receipt under `evidence/<SID>/anchors_receipts/`
  - manifest entries/snapshots

Scripts commonly involved:
- `scripts/add_anchor.py`
- `scripts/register_anchors_from_registry.py`
- `ingestion/register_anchor.py`

### 5.2 Chunking
Goal: transform canonical sources into stable DB chunks.

Examples:
- Lexicon A?Z JSON -> 1625 chunks
- Book of Solobility PDF -> 1214 chunks

Chunking outputs must include:
- anchor linkage
- import_session_id
- anchor_locator
- (lexicon) lexicon_word when applicable

Key scripts/modules:
- `ingestion/parse_chunks.py`
- `scripts/import_lexicon_chunks_v1_1.py`
- `scripts/chunk_bos_pages_pilot.py` (pattern reference)

### 5.3 Embeddings (Derivative)
Embeddings are computed *after* chunking and are always reproducible.
They must never be treated as canonical truth.

Key module:
- `ingestion/embed_chunks.py`

---

## 6) How to ?View the System? Quickly (Operator Checklist)

When you open the repo and need orientation:

1) **State**
- `docs/STATE.json`
- `docs/STATE_HISTORY.md` (and legacy addendum if needed)

2) **What?s registered**
- `data/memory.db` (counts)
- `docs/KNOWN_ARTIFACTS.md`
- `docs/ANCHOR_REGISTRY_PLAN.json`

3) **What?s proven**
- `.\tools\mw_full_proof.ps1 -RepoRoot . -RequireAZ -VerifySupremeBundle`
- proof logs in `logs/` and evidence receipts in `evidence/`

4) **What?s canonical inputs**
- `anchors/` tree (PDFs / JSON / MD)

5) **What?s the current map**
- `docs/ANCHORS_MAP.md` / `docs/ANCHORS_MAP_ASCII.md`

---

## 7) V1 API + UI Surface (Optional)

V1 prioritizes audit-grade storage + workflows. API/UI are allowed surfaces as long as they:
- do not bypass state guard rules
- do not write to canonical stores without RECORD posture + receipts

Relevant folders:
- `api/` ? minimal API surface
- `frontend/` ? lightweight UI

---

## 8) V1 Scope Boundaries (What is NOT included)

Out of scope for V1 (explicitly):
- distributed sync / multi-device replication
- cloud hosting requirements
- advanced auth / multi-tenant identity
- ?autonomous agents? that write without witness discipline
- long-term product vision (kept in `docs/vision.md`)

---

## 9) Conventions (Naming + Encoding Safety)

- Use ASCII-safe separators in logs and state history:
  - `-` and `->` (avoid em-dashes/arrows that cause PowerShell mojibake)
- Prefer deterministic filenames for receipts and ledgers.
- Keep canonical truth in:
  - `anchors/` (inputs)
  - `data/memory.db` (structured)
  - `evidence/` (proof chain)

### Timezone Handling
- **Canonical timestamps:** Always UTC (ISO8601 with `Z` suffix)
- **Human-readable logs:** Local time with offset (e.g. `-05:00`)
- **Operator timezone:** Kingston, Jamaica (UTC-5, no DST)
- **Conversion:** Only at display boundaries, never in storage
- **See:** [TIMEZONE_REFERENCE.md](./TIMEZONE_REFERENCE.md) for complete documentation

### Receipt System Governance
- **Receipts are immutable:** Never edited, overwritten, or deleted
- **Corrections via new receipts:** Supersession or addendum, never in-place edits
- **Lifecycle states:** ACTIVE -> SUPERSEDED -> SEALED (deletion forbidden)
- **Evidence is append-only:** Historical receipts preserved even when wrong
- **See:** [RECEIPT_LIFECYCLE_RULES.md](./RECEIPT_LIFECYCLE_RULES.md) for complete governance

---

## 10) Practical ?Start Here? Commands

### Read-only audit (safe in OBSERVE)
- `python .\scripts\sanity_check.py --allow-observe`
- `.\tools\mw_full_proof.ps1 -RepoRoot . -RequireAZ -VerifySupremeBundle`

### Prepare for writes (enter RECORD)
- `.\tools\solob.ps1 record -note "write window: <purpose>"`

### Seal after writes (return OBSERVE)
- `.\tools\solob.ps1 observe -note "seal: <what changed + why>"`

---

## 11) V1 Foundation Summary

V1 is not just software.  
V1 is **epistemic discipline**.

### Core Guarantees

1. **STGRAIL discipline** ? No writes without witness
2. **Front-door auditable** ? Every anchor has receipts
3. **Database coherence** ? Chunks always link to anchors
4. **Reproducibility** ? Derivatives never become canon
5. **Receipt immutability** ? History preserved, not rewritten
6. **Timezone consistency** ? UTC-first, local for display only
7. **Chain constitution** ? payload_v1 frozen, single canonical implementation

### What Makes This Suitable

- **Canon vs Derivative** ? Never confused
- **Append-only evidence** ? Mistakes preserved as proof
- **Witness Epoch** ? Every action has a session ID
- **Receipt lifecycle** ? Corrections via new receipts, not edits
- **Hash-first integrity** ? If you can't hash it, you can't prove it
- **Constitutional versioning** ? Canon changes only by version bump

### The Lattice

This system is a **lattice**, not a loop:
- Time flows one direction
- Receipts form a DAG (directed acyclic graph)
- Supersession is explicit, never implied
- Confusion has nowhere to hide

**That's the standard.**

---

END OF V1 SCOPE

