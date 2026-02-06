### The 7 Classes of Receipts (Reality 1 -> 7)

Think of receipts as checkpoints in meaning-space, not just logs.

### State & Authority Receipts 

What they answer:

?Who was allowed to do this, and under what rules??

Collect receipts when:

State changes (OBSERVE ? RECORD)

STGRAIL rules are relaxed or expanded

New permissions are introduced (e.g. --allow-observe)

### Artifacts

STATE_HISTORY.md

STATE_HISTORY_LEGACY_SID_ADDENDUM.json

Optional: RECEIPT_STATE_POLICY_CHANGE.json



Anchor Lifecycle Receipts (Critical)

What they answer:

?Where did this memory come from, and why does it exist??

Collect receipts when:

A new anchor is added

An anchor is archived, deprecated, or superseded

An invariant (like WAI) changes

Artifacts

RECEIPT_ANCHOR_ADDED.json

RECEIPT_ANCHOR_UPGRADED.json

RECEIPT_ANCHOR_DEPRECATED.json

 This prevents retroactive canon rewriting.

Ingestion & Chunking Receipts (Reality 3?4 backbone)

What they answer:

?How did raw meaning become indexed meaning??

Collect receipts when:

Chunking occurs (PDF, text, lexicon)

Chunk rules change (page-based -> paragraph-based, etc.)

Collisions are detected or prevented

Artifacts

RECEIPT_CHUNKS_<ANCHOR>.json

Collision reports

Page counts / word counts / deltas

 These are your legal-grade provenance proofs.

Evidence & Index Receipts (Reality 4 glue)

What they answer:

?Is the system lying to itself??

Collect receipts when:

Evidence index is rebuilt

Supreme bundles are declared

A-Z completeness is certified

Artifacts

RECEIPT_EVIDENCE_INDEX_REBUILD.json

RECEIPT_LEXICON_AZ_COVERAGE_LEDGER.json

RECEIPT_SUPREME_BUNDLE.json

These prevent silent erosion.

### Change Control Receipts

What they answer:

?What actually changed in the machine??

Collect receipts when:

Code is modified

Scripts are added or removed

Logic paths change

Artifacts

CODEBASE_BEFORE.json

CODEBASE_AFTER.json

CODEBASE_DIFF.json

Optional: RECEIPT_IMPLEMENTATION_INTENT.json

This is is how we get Git without getting Git lol get it ? loool 

 Interpretation & Derivation Receipts 

What they answer:

?How did meaning get inferred, summarized, or embedded??

Collect receipts when:

Embeddings are generated

Summaries are created

AI produces interpretations tied to anchors

Artifacts

RECEIPT_EMBEDDING_RUN.json

RECEIPT_SUMMARY_DERIVATION.json

run_citations DB entries

This is where AI hallucination is kept on a leash.

7?Boundary & Epoch Receipts (Rare but powerful)

What they answer:

?When did the rules of the universe change??

Collect receipts when:

Witness Epoch begins

Legacy rules are frozen

Major architectural phase ends (Reality 5 -> 6)

Artifacts

Epoch statements

Addendums

Seals

 These stop future actors from saying
?It was always like this.? (It never was.)

 ### What We Do NOT Collect Receipts For

This is just as important.

We do not receipt:

Read-only inspections

Queries

Exploratory experiments

Failed attempts that leave no artifact

Human thoughts not enacted

Receipts are for actions that change the world, not thoughts about it.

Otherwise you drown in paper.


Receipts are not for remembering ? they are for defending memory.

That?s the difference between:

a notebook
and

a civilization archive