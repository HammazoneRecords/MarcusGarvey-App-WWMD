# THREAT-MODEL.md  
## How the Solob Wrapper Resists Corruption

---

## 0. Why a Threat Model Exists

Most systems fail not because they are wrong ?  
but because they are **quietly compromised**.

Corruption rarely arrives as an attack.
It arrives as:
- Convenience
- Shortcuts
- ?Just this once?
- Silent edits
- Forgotten context
- Missing witnesses

This document defines how the Solob Wrapper **detects, resists, and documents corruption** ? even when corruption is accidental, internal, or well-intentioned.

---

## 1. Definition of Corruption (Explicit)

In this system, corruption means **any change that breaks traceability**.

This includes:
- Writes without a witness
- State transitions without proof
- Data without anchors
- Chunks without lineage
- History rewritten instead of reconciled
- Outputs that cannot explain themselves

Corruption is not moral failure.  
It is **epistemic failure**.

---

## 2. Threat Classes

### 2.1 Accidental Corruption (Most Common)

Examples:
- Running a script in the wrong state
- Editing DB content manually
- Re-ingesting data with different logic
- Partial runs after failure
- Overwriting receipts

**Mitigations:**
- STGRAIL state enforcement
- Append-only evidence discipline
- Deterministic chunk IDs
- Preflight checks + hard STOP rules
- Front-door-only ingestion philosophy

---

### 2.2 Tool Drift (Silent Killer)

Examples:
- IDE auto-formatting logs
- Unicode -> ASCII corruption (mojibake)
- Script behavior changing over time
- Dependency updates altering output

**Mitigations:**
- ASCII-safe logging rules
- Deterministic output formats
- Parse gates (prove.ps1, mw_full_proof.ps1)
- Evidence-based validation, not stdout trust
- Scripts treated as evidence-producing actors

---

### 2.3 Intentional Tampering (Internal or External)

Examples:
- Editing STATE_HISTORY.md directly
- Deleting evidence folders
- Injecting chunks without anchors
- Rewriting receipts
- Faking counts or audits

**Mitigations:**
- Cross-layer verification (DB ? evidence ? manifests)
- Court sweep (Layer A?C proof pyramid)
- Witness Epoch enforcement
- Addendum-based reconciliation (never silent deletion)
- Future-readiness for cryptographic sealing

---

### 2.4 Narrative Corruption (The Subtle One)

Examples:
- ?This idea always meant X?
- Retroactive interpretation
- Mixing canon with commentary
- AI hallucinations treated as truth

**Mitigations:**
- Canon vs Derivative separation
- Truth types (empirical vs interpretive)
- Mutation modes (append-only)
- Receipts that capture *when* meaning emerged
- Future models trained to cite lineage, not vibes

---

## 3. Systemic Anti-Corruption Patterns

### 3.1 State as Law (STGRAIL)

No write occurs unless:
- State == RECORD
- Transition is witnessed
- Session ID is present
- Evidence is emitted

This blocks:
- Accidental writes
- Background script drift
- ?I forgot what mode I was in? disasters

---

### 3.2 Witness Epoch

All meaningful actions are:
- Timestamped
- Session-bound
- Replayable
- Auditable

Legacy gaps are **documented**, not erased.

This ensures:
- Historical honesty
- No fake continuity
- Trust across time

---

### 3.3 Evidence First, DB Second

The DB is *not* the source of truth.
It is a **projection**.

Truth lives in:
- Receipts
- Indexes
- Anchors
- State history

If the DB is corrupted, it can be rebuilt.
If evidence is corrupted, corruption is visible.

---

## 4. AI-Specific Corruption Risks

### 4.1 Hallucination Amplification

AI systems tend to:
- Sound confident
- Compress nuance
- Lose provenance

**Countermeasure:**
This system trains models on:
- Witnessed transitions
- Explicit anchors
- Provenance chains

Future models should learn:
> ?If I can?t cite it, I don?t say it.?

---

### 4.2 Model Drift Over Time

Models trained later may reinterpret earlier data.

**Countermeasure:**
- Anchors are immutable
- Chunks carry creation context
- Interpretations are stored as derivatives, never canon

---

## 5. What This System Cannot Prevent (By Design)

This system does **not** prevent:
- Bad ideas
- Wrong hypotheses
- Cultural bias
- Human error

What it prevents is:
- **Lying about how those ideas came to be**

Truth is allowed to be wrong.
It is not allowed to be **unaccountable**.

---

## 6. Final Assertion

This system resists corruption not by force ?
but by **making corruption visible, costly, and undeniable**.

Nothing here claims perfection.

It claims:
- Memory
- Witness
- Proof
- Discipline
- Lineage

That is enough.
