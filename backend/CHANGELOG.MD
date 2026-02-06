# CHANGELOG.md (Append-only)

## 2025-12-29T20:08:22-05:00 | SID: S_20251230T004902Z_MARCUS_GARVEY_BASELINE | TYPE: MAJOR
SUMMARY: Unified Ingestion & Verification Complete

FILES:
- scripts/ingest_marcus_unified.py, runs/answer.py, evidence/bundles

WHY:
- Executed unified ingestion of 8 Marcus BOX PDFs (~700 chunks) and verified RAG retrieval functionality.

EVIDENCE (only if MAJOR):
- (Pending evidence documentation)


# CHANGELOG - Marcus Garvey App ARK

**Purpose**: Track all changes to the Marcus Garvey App ARK instance.

**Note**: This is a clean baseline fork. Original ARK documentation archived in `archive/original-ark-docs/`.

---

## 2025-12-29T19:55:00-05:00 | SID: S_<BASELINE_SESSION> | TYPE: MAJOR
SUMMARY: Marcus Garvey App ARK - Clean Baseline Initialization

FILES:
- Database reset (0 chunks, 0 anchors)
- Codebase cleanup (removed frontend, lexicon data, old evidence)
- Archive created for original ARK documentation

WHY:
- Fork of original ARK specifically for Marcus Garvey App
- Clean slate for Marcus Garvey corpus ingestion only
- Python backend only (no frontend)
- All scripts preserved for ingestion, diagnostics, audit, verification

EVIDENCE (only if MAJOR):
- Genesis receipt: evidence/S_<BASELINE_SESSION>/RECEIPTS/RECEIPT_GENESIS_BASELINE_RESET.json
- Database state: 0 chunks, 0 anchors (clean baseline)
- Archive: archive/original-ark-docs/ (original documentation preserved)

ROADBLOCKS (if any):
- None

---

## Format Guidelines

Each entry should follow this structure:

```
## YYYY-MM-DDTHH:MM:SS-05:00 | SID: S_YYYYMMDDTHHMMSSZ_DESCRIPTOR | TYPE: MAJOR|MINOR|DOC
SUMMARY: <one sentence summary>

FILES:
- <file path>
- <file path>

WHY:
- <reason/explanation>

EVIDENCE (only if MAJOR):
- <evidence location>
- <verification details>

ROADBLOCKS (if any):
- <blocker description>
```

Use the helper script:
```bash
python scripts/log_changelog.py --summary "Your summary" --type MAJOR --files "path/to/file" --why "Your reason"
```
