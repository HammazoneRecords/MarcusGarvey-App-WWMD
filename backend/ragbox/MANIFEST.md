# RAGBox Manifest
**Complete Package Inventory**

**Created**: 2025-12-30T22:05:30-05:00  
**Updated**: 2025-12-31  
**Version**: 1.2 (Production Ready)  
**Source**: Marcus Garvey App WWMD ARK System

---

## Package Contents

### Core Scripts (9 files)

| File | Purpose | Lines | State |
|------|---------|-------|-------|
| `scripts/wwmd_ask_hybrid.py` | Main RAG engine with citation injection | ~185 | Production |
| `scripts/hybrid_retriever.py` | Hybrid retrieval (line + parent chunks) | ~159 | Production |
| `scripts/citation_injector.py` | Post-process citation validation | ~123 | Production |
| `scripts/wwmd_ask.py` | Basic RAG (legacy, for reference) | ~224 | Reference |
| `scripts/init_db.py` | Database initialization | ~50 | Production |
| `scripts/chunk_bos_pages_pilot.py` | **NEW** PDF Page Chunking | ~200 | Production |
| `scripts/import_lexicon_chunks_v1_1.py`| **NEW** Lexicon Ingestion | ~200 | Production |
| `scripts/ingest_marcus_unified.py` | **NEW** Unified Ingestion Pipeline | ~250 | Production |
| `scripts/register_anchors_from_registry.py` | **NEW** Anchor Registration | ~150 | Production |

### Audit Suite (New)

| File | Purpose | Location |
|------|---------|----------|
| `tools/court_sweep.py` | **Critical** System Health Check | `tools/` |
| `scripts/validate_receipt_v2.py` | Receipt Schema Validator | `scripts/` |
| `tools/validate_state_history_format.py` | History Format Validator | `tools/` |
| `tools/script_state_lookout.py` | Script Integrity Monitor | `tools/` |

### Critical Helpers

| File | Purpose |
|------|---------|
| `utils/sid.py` | Session ID generation (prevents crashes) |
| `scripts/hash_utils.py` | SHA256 utilities |

### Documentation (9 files)

| File | Purpose |
|------|---------|
| `docs/rag_and_audit_implementation_guide.md` | Complete implementation guide |
| `docs/SCRIPTS_INVENTORY.md` | All scripts reference |
| `docs/CHUNKING_GUIDE.md` | Chunking procedures guide |
| `docs/INTEGRATION_GUIDE.md` | **NEW** Guide for Operating AI |
| `docs/WWMD_RAG_PROTOCOL.md` | Prosecutor's standard for citations |
| `docs/WWMD_OUTPUT_CONTRACT.md` | JSON schema |
| `docs/CITATION_ACCURACY_ANALYSIS.md` | Hallucination analysis |
| `docs/STATE.json` | **NEW** System State Tracker |
| `docs/STATE_HISTORY.md` | **NEW** State History Log |
| `README.md` | Quick start guide |

### Configuration

| File | Purpose |
|------|---------|
| `config/.env.example` | Environment template |
| `requirements.txt` | Python dependencies (Includes PyMuPDF) |

### Directories

| Directory | Purpose |
|-----------|---------|
| `anchors/` | **NEW** Place PDFs here |
| `evidence/` | **NEW** Audit reports go here |
| `tools/` | **NEW** Audit tools |
| `utils/` | **NEW** Helper scripts |
| `data/` | Database storage |
| `sessions/` | Query vault |

---

## Status

✅ **Self-Contained**: No external dependencies (except Python packages).
✅ **Verifiable**: Includes full Audit Suite.
✅ **Instructional**: Includes Integration Guide for AI.

**Ready for Transfer.**
