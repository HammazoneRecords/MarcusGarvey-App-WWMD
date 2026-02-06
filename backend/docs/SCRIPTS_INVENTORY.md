# Scripts & Tools Inventory
**Marcus Garvey App WWMD - ARK System**

**Last Updated**: 2025-12-30  
**Total Scripts**: 78 (scripts/) + 18 (tools/) = 96 total  
**Registry Coverage**: 68/96 (71%)

---

## Table of Contents

1. [Core System Scripts](#core-system-scripts)
2. [RAG System Scripts](#rag-system-scripts)
3. [Ingestion Scripts](#ingestion-scripts)
4. [Audit & Verification Scripts](#audit--verification-scripts)
5. [Evidence & Receipt Scripts](#evidence--receipt-scripts)
6. [State Management Scripts](#state-management-scripts)
7. [Utility Scripts](#utility-scripts)
8. [Tools (Audit & Governance)](#tools-audit--governance)
9. [Modules (Ritual Engine)](#modules-ritual-engine)
10. [Deprecated/Legacy Scripts](#deprecatedlegacy-scripts)

---

## Core System Scripts

### `scripts/init_db.py`
**Purpose**: Initialize SQLite database with schema  
**State**: OBSERVE  
**Usage**: `python scripts/init_db.py`  
**Creates**: `data/memory.db` with `anchors`, `chunks`, `line_chunks` tables

### `scripts/check_db_stats.py`
**Purpose**: Quick database statistics check  
**State**: Not in registry  
**Usage**: `python scripts/check_db_stats.py`  
**Output**: Anchor count, chunk count, line chunk count

### `scripts/reset_database_clean_baseline.py`
**Purpose**: Reset database to clean baseline (DESTRUCTIVE)  
**State**: Not in registry  
**Usage**: `python scripts/reset_database_clean_baseline.py`  
**Warning**: Deletes all data, creates genesis receipt

---

## RAG System Scripts

### `scripts/wwmd_ask.py`
**Purpose**: Basic RAG query (keyword-based retrieval)  
**State**: Not in registry  
**Usage**: `python scripts/wwmd_ask.py "What did Marcus Garvey say about unity?"`  
**Features**: Simple keyword matching, LLM generation with citations

### `scripts/wwmd_ask_hybrid.py` ⭐
**Purpose**: Hybrid RAG with line-level chunking + citation injection  
**State**: Not in registry  
**Usage**: `python scripts/wwmd_ask_hybrid.py "query" --json`  
**Features**:
- Line-level precision citations
- Post-process citation validation
- Quality scoring
- Session vault (saves to `sessions/YYYY-MM-DD/`)
- JSON output contract

**Flags**:
- `--json`: Output JSON only
- `--out <file>`: Save JSON to file
- `--debug expand|strict|off`: Citation search scope

### `scripts/wwmd_ask_exact.py`
**Purpose**: Exact match RAG (experimental)  
**State**: Not in registry  
**Usage**: `python scripts/wwmd_ask_exact.py "query"`

### `scripts/hybrid_retriever.py`
**Purpose**: Hybrid retrieval module (line chunks + parent chunks)  
**State**: Not in registry  
**Type**: Module (imported by `wwmd_ask_hybrid.py`)  
**Functions**:
- `extract_keywords(query)` - Keyword extraction with stopwords
- `retrieve_hybrid(query, max_results=15)` - Retrieve line + parent chunks
- `build_hybrid_context(results)` - Build context for LLM
- `fetch_all_lines_for_parents(parent_ids)` - Expand citation search space

### `scripts/citation_injector.py`
**Purpose**: Post-process citation discovery and validation  
**State**: Not in registry  
**Type**: Module (imported by `wwmd_ask_hybrid.py`)  
**Functions**:
- `score_citation(line_text, query_terms)` - Quality scoring
- `find_text_matches(ai_response, line_data)` - 3-strategy matching (exact, n-gram, fuzzy)
- `get_citations(ai_response, line_data)` - Main entry point

### `scripts/investigate_citation.py`
**Purpose**: Debug citation accuracy issues  
**State**: Not in registry  
**Usage**: `python scripts/investigate_citation.py`

---

## Ingestion Scripts

### `scripts/register_anchors_from_registry.py` ⭐
**Purpose**: Register anchors from canonical registry  
**State**: STABLE  
**SHA256**: `276b0fe014f4e9277a5fe5f5e51b5b9f27581a59a15a997aeac18aac91fc6df5`  
**Usage**: `python scripts/register_anchors_from_registry.py`  
**Reads**: `docs/ANCHOR_REGISTRY_PLAN.json`

### `scripts/import_lexicon_chunks_v1_1.py` ⭐
**Purpose**: Ingest lexicon JSON with row index derivation  
**State**: STABLE  
**SHA256**: `f826d540cd3d5f8b863ec700d2c29ac671453a3c656bf62ca4a0e754394dcc44`  
**Usage**: `python scripts/import_lexicon_chunks_v1_1.py`

### `scripts/chunk_bos_pages_pilot.py` ⭐
**Purpose**: PDF page chunking (Book of Solobility)  
**State**: STABLE  
**SHA256**: `220901015a5e105ac967946048b56f1e05b2b66d6ab7660f5460bf1eee6249f8`  
**Usage**: `python scripts/chunk_bos_pages_pilot.py`

### `scripts/ingest_marcus_unified.py` ⭐
**Purpose**: Unified Marcus Garvey corpus ingestion  
**State**: Not in registry  
**Usage**: `python scripts/ingest_marcus_unified.py`  
**Features**: Ingests all Marcus Garvey PDFs with line-level chunking

### `scripts/ingest_marcus_corpus_step1_anchors.py`
**Purpose**: Step 1 of Marcus Garvey ingestion (anchors only)  
**State**: Not in registry  
**Usage**: `python scripts/ingest_marcus_corpus_step1_anchors.py`

### `scripts/ritual_engine.py` ⭐
**Purpose**: Config-driven ritual engine framework  
**State**: STABLE  
**SHA256**: `35092c2ce26beeb16310729c6cb0eb8fee622361aa9aee13b2600bd01616144b`  
**Usage**: `python scripts/ritual_engine.py --config config/rituals/example.json`  
**Features**: Dry-run support, auto-receipt generation, portable across projects

---

## Audit & Verification Scripts

### `scripts/audit_ingestion_trail.py`
**Purpose**: Forensic reconstruction of ingestion history  
**State**: OBSERVE  
**Usage**: `python scripts/audit_ingestion_trail.py`

### `scripts/audit_lexicon_counts.py`
**Purpose**: Verify lexicon chunk counts  
**State**: OBSERVE  
**Usage**: `python scripts/audit_lexicon_counts.py`

### `scripts/pre_ingestion_audit.py`
**Purpose**: Pre-ingestion system check  
**State**: OBSERVE  
**Usage**: `python scripts/pre_ingestion_audit.py`

### `scripts/pre_ingestion_audit_ext.py`
**Purpose**: Extended pre-ingestion audit  
**State**: OBSERVE  
**Usage**: `python scripts/pre_ingestion_audit_ext.py`

### `scripts/post_ingestion_audit_ext.py`
**Purpose**: Extended post-ingestion audit  
**State**: OBSERVE  
**Usage**: `python scripts/post_ingestion_audit_ext.py`

### `scripts/preflight_balance_check.py`
**Purpose**: Preflight system integrity check  
**State**: OBSERVE  
**Usage**: `python scripts/preflight_balance_check.py`

### `scripts/sanity_check.py`
**Purpose**: Basic system sanity check  
**State**: OBSERVE  
**Usage**: `python scripts/sanity_check.py`

### `scripts/sanity_check_post_ingestion.py`
**Purpose**: Post-ingestion sanity verification  
**State**: OBSERVE  
**Usage**: `python scripts/sanity_check_post_ingestion.py`

---

## Evidence & Receipt Scripts

### `scripts/prosecutor_emit_evidence_bundle.py` ⭐
**Purpose**: Generate V2 evidence bundles  
**State**: STABLE  
**SHA256**: `d54e944f47e83a8cc78dc710fe6f711958d811829e68fa376925631d6e468fb3`  
**Usage**: `python scripts/prosecutor_emit_evidence_bundle.py`  
**Creates**: `evidence/bundles/S_<TIMESTAMP>_<DESCRIPTOR>/`

### `scripts/prosecutor_verify_evidence_bundle.py` ⭐
**Purpose**: Verify evidence bundle integrity  
**State**: STABLE  
**SHA256**: `abfc2c7b69ddee1c0d06c9d4c217fdfa16f9931e3d3e89201d03c9104c21481d`  
**Usage**: `python scripts/prosecutor_verify_evidence_bundle.py <bundle_path>`

### `scripts/prosecutor_upgrade_bundles_v2.py` ⭐
**Purpose**: Migrate V1 bundles to V2 spec  
**State**: STABLE  
**SHA256**: `e42dfaf4ef2148f7a32b616f7bd33a520cd56b5c692b60d7cdb82bcc7863c564`  
**Usage**: `python scripts/prosecutor_upgrade_bundles_v2.py`

### `scripts/prosecutor_consolidate_lexicon_bundle.py` ⭐
**Purpose**: Consolidate lexicon evidence  
**State**: STABLE  
**SHA256**: `2c084a1090779240edcbc1e75b8333b9afa79a4c6f63efa5320c677d3689237e`  
**Usage**: `python scripts/prosecutor_consolidate_lexicon_bundle.py`

### `scripts/prosecutor_db_checkpoint.py`
**Purpose**: Database checkpoint utility  
**State**: OBSERVE  
**Usage**: `python scripts/prosecutor_db_checkpoint.py`

### `scripts/validate_receipt.py` ⭐
**Purpose**: V1 receipt validator (legacy)  
**State**: STABLE  
**SHA256**: `f515ecc65a6f06c2829d95689b2fa0aced7b82d03e7db1e894adda3b8d5b2bcb`  
**Usage**: `python scripts/validate_receipt.py <receipt_path>`

### `scripts/validate_receipt_v2.py` ⭐
**Purpose**: V2 receipt schema validator  
**State**: STABLE  
**SHA256**: `709e9e6ad8b70391e597c40e43392aa0793d3273b2c1973fa7c26968fc549158`  
**Usage**: `python scripts/validate_receipt_v2.py <receipt_path>`

### `scripts/upgrade_receipts_to_v2.py`
**Purpose**: Migrate V1 receipts to V2  
**State**: OBSERVE  
**Usage**: `python scripts/upgrade_receipts_to_v2.py`

### `scripts/create_genesis_receipt.py` ⭐
**Purpose**: Create genesis receipt for Merkle chain  
**State**: STABLE  
**SHA256**: `440b860900ad3e1e272459a184966d92622d1709be8a38f72aaa697ce3f4180e`  
**Usage**: `python scripts/create_genesis_receipt.py`

### `scripts/emit_weekly_evidence_bundle.py`
**Purpose**: Weekly evidence aggregation  
**State**: OBSERVE  
**Usage**: `python scripts/emit_weekly_evidence_bundle.py`

### `scripts/evidence_index.py`
**Purpose**: Generate evidence index  
**State**: OBSERVE  
**Usage**: `python scripts/evidence_index.py`

### `scripts/init_evidence_vault.py`
**Purpose**: Initialize evidence vault with genesis hashes  
**State**: OBSERVE  
**Usage**: `python scripts/init_evidence_vault.py`

---

## State Management Scripts

### `scripts/log_state_transition.py` ⭐
**Purpose**: Canonical state transition logger (enforces format)  
**State**: STABLE  
**SHA256**: `4be9b18b7871ddd3b97ec06adbe60dc8634e77fd141b274daf09c4b84f2d215f`  
**Usage**: `python scripts/log_state_transition.py --from OBSERVE --to RECORD --reason "Starting ingestion" --sid S_20251230T000000Z_DESC`  
**Updates**: `docs/STATE_HISTORY.md`

### `scripts/log_changelog.py` ⭐
**Purpose**: Canonical changelog entry helper  
**State**: STABLE  
**SHA256**: `ad9c68caec68887a9ba7d5f67ecade900db290a8662ff85fe856911a4782f0a2`  
**Usage**: `python scripts/log_changelog.py --summary "Summary" --type MAJOR --files "path/to/file" --why "Reason"`  
**Updates**: `CHANGELOG.MD`

### `scripts/add_changelog_entry.py`
**Purpose**: Add changelog entry (alternative)  
**State**: Not in registry  
**Usage**: `python scripts/add_changelog_entry.py`

### `scripts/state_transition.py`
**Purpose**: State transition utility (legacy, use `log_state_transition.py`)  
**State**: OBSERVE  
**Usage**: Deprecated

### `scripts/state_history_note.py`
**Purpose**: State history annotation utility  
**State**: OBSERVE  
**Usage**: `python scripts/state_history_note.py`

### `scripts/state_guard.py`
**Purpose**: State discipline guard  
**State**: OBSERVE  
**Usage**: `python scripts/state_guard.py`

---

## Utility Scripts

### `scripts/create_xl_capsule.py`
**Purpose**: Generate XL context capsule for AI  
**State**: OBSERVE  
**Usage**: `python scripts/create_xl_capsule.py`  
**Creates**: `ContextCapsuleBOX/XL_CAPSULE_<TIMESTAMP>.md`

### `scripts/create_mini_capsule.py`
**Purpose**: Generate mini context capsule  
**State**: OBSERVE  
**Usage**: `python scripts/create_mini_capsule.py`

### `scripts/create_filled_capsule.py`
**Purpose**: Generate filled context capsule  
**State**: Not in registry  
**Usage**: `python scripts/create_filled_capsule.py`

### `scripts/generate_coherence_report.py`
**Purpose**: Generate coherence report  
**State**: OBSERVE  
**Usage**: `python scripts/generate_coherence_report.py`

### `scripts/codebase_diff_report.py`
**Purpose**: Codebase differential reporting  
**State**: OBSERVE  
**Usage**: `python scripts/codebase_diff_report.py`

### `scripts/codebase_fingerprint.py`
**Purpose**: Codebase fingerprinting utility  
**State**: OBSERVE  
**Usage**: `python scripts/codebase_fingerprint.py`

### `scripts/schema_fingerprint.py`
**Purpose**: Schema fingerprinting utility  
**State**: OBSERVE  
**Usage**: `python scripts/schema_fingerprint.py`

### `scripts/invariants_fingerprint.py`
**Purpose**: Invariants fingerprinting utility  
**State**: OBSERVE  
**Usage**: `python scripts/invariants_fingerprint.py`

### `scripts/cartographer_emit_anchors_map.py`
**Purpose**: Generate anchor registry map  
**State**: OBSERVE  
**Usage**: `python scripts/cartographer_emit_anchors_map.py`

### `scripts/naming_guard.py`
**Purpose**: Naming convention enforcement  
**State**: OBSERVE  
**Usage**: `python scripts/naming_guard.py`

### `scripts/registry_validator.py`
**Purpose**: Registry validation utility  
**State**: OBSERVE  
**Usage**: `python scripts/registry_validator.py`

### `scripts/hash_utils.py`
**Purpose**: SHA256 hashing utilities  
**State**: OBSERVE  
**Type**: Module  
**Functions**: `sha256_file(path)`, `sha256_string(text)`

### `scripts/update_registry_sha256.py`
**Purpose**: Update SHA256 hashes for STABLE scripts in registry  
**State**: OBSERVE  
**Usage**: `python scripts/update_registry_sha256.py`

### `scripts/gen_legacy_addendum.py`
**Purpose**: Generate legacy state history addendum  
**State**: OBSERVE  
**Usage**: `python scripts/gen_legacy_addendum.py`

### `scripts/gen_coverage_ledger.py`
**Purpose**: Generate coverage ledger  
**State**: OBSERVE  
**Usage**: `python scripts/gen_coverage_ledger.py`

### `scripts/ops_log.py`
**Purpose**: Operations logging utility  
**State**: OBSERVE  
**Usage**: `python scripts/ops_log.py`

### `scripts/print_recorded_env.py`
**Purpose**: Print recorded environment variables  
**State**: OBSERVE  
**Usage**: `python scripts/print_recorded_env.py`

### `scripts/run_recorded.py`
**Purpose**: Recorded command execution wrapper  
**State**: OBSERVE  
**Usage**: `python scripts/run_recorded.py <command>`

### `scripts/session_lock.py`
**Purpose**: Session locking mechanism  
**State**: OBSERVE  
**Usage**: `python scripts/session_lock.py`

### `scripts/seal_checkpoint.py`
**Purpose**: Checkpoint sealing utility  
**State**: OBSERVE  
**Usage**: `python scripts/seal_checkpoint.py`

### `scripts/save_test_result.py`
**Purpose**: Save test results to evidence  
**State**: Not in registry  
**Usage**: `python scripts/save_test_result.py`

### `scripts/serve_vault.py`
**Purpose**: Serve evidence vault via HTTP  
**State**: Not in registry  
**Usage**: `python scripts/serve_vault.py`

### `scripts/quote_extractor.py`
**Purpose**: Extract quotes from corpus  
**State**: Not in registry  
**Usage**: `python scripts/quote_extractor.py`

### `scripts/quote_verifier.py`
**Purpose**: Verify quote citations  
**State**: Not in registry  
**Usage**: `python scripts/quote_verifier.py`

---

## Anchor Management Scripts

### `scripts/add_anchor.py`
**Purpose**: Manual anchor addition utility  
**State**: OBSERVE  
**Usage**: `python scripts/add_anchor.py`

### `scripts/register_missing_anchors.py`
**Purpose**: Register missing anchors  
**State**: OBSERVE  
**Usage**: `python scripts/register_missing_anchors.py`

### `scripts/inspect_anchor_chunks.py`
**Purpose**: Inspect chunks for specific anchor  
**State**: OBSERVE  
**Usage**: `python scripts/inspect_anchor_chunks.py <anchor_id>`

### `scripts/snapshot_anchors.py`
**Purpose**: Snapshot anchor registry  
**State**: OBSERVE  
**Usage**: `python scripts/snapshot_anchors.py`

---

## Lexicon-Specific Scripts

### `scripts/hard_check_lexicon.py`
**Purpose**: Lexicon integrity hard check  
**State**: OBSERVE  
**Usage**: `python scripts/hard_check_lexicon.py`

### `scripts/lexicon_stamp_row_index.py`
**Purpose**: Stamp row indices on lexicon chunks  
**State**: OBSERVE  
**Usage**: `python scripts/lexicon_stamp_row_index.py`

---

## API & Testing Scripts

### `scripts/test_api_key.py`
**Purpose**: Test Gemini API key validity  
**State**: Not in registry  
**Usage**: `python scripts/test_api_key.py`

### `scripts/test_generate.py`
**Purpose**: Test Gemini generation  
**State**: Not in registry  
**Usage**: `python scripts/test_generate.py`

### `scripts/debug_gemini.py`
**Purpose**: Debug Gemini API issues  
**State**: Not in registry  
**Usage**: `python scripts/debug_gemini.py`

### `scripts/list_models.py`
**Purpose**: List available Gemini models  
**State**: Not in registry  
**Usage**: `python scripts/list_models.py`

---

## Cleanup Scripts

### `scripts/cleanup_for_marcus_garvey_app.py`
**Purpose**: Clean up ARK for Marcus Garvey app fork  
**State**: Not in registry  
**Usage**: `python scripts/cleanup_for_marcus_garvey_app.py`  
**Warning**: DESTRUCTIVE - removes frontend, lexicon data, old evidence

---

## Tools (Audit & Governance)

### `tools/court_sweep.py` ⭐
**Purpose**: 10-check comprehensive system audit  
**State**: STABLE  
**SHA256**: `1ede71b370bcc0e56017a68c852e730a1a8eeca0cbb9241cd9d6fd54680d2d8e`  
**Usage**: `python tools/court_sweep.py`  
**Checks**:
1. db_counts
2. state_history_witness
3. evidence_index
4. bundle_uniformity
5. encoding_reports_present
6. receipt_validation
7. orphan_chunks
8. bundle_layout
9. state_history_format
10. script_state_lookout

**Output**: `evidence/bundles/S_<TIMESTAMP>_COURT_SWEEP/`

### `tools/full_court_press.py` ⭐
**Purpose**: 3-layer audit (Evidence Vault + Merkle Chain + Court Sweep)  
**State**: STABLE  
**SHA256**: `d337f721bd0b1476e54cbcd38fa494dfaaab0c16e2c44f1d49d886f0cae265a5`  
**Usage**: `python tools/full_court_press.py`  
**Layers**:
1. Evidence Vault verification
2. Merkle Chain integrity
3. Court Sweep (10 checks)

### `scripts/run_full_court_press.py` ⭐
**Purpose**: Python wrapper for Full Court Press (UTF-8 handling)  
**State**: STABLE  
**SHA256**: `deb4c1ce2be00d87a909dbc793d56217dfd13e740aca7318c111480eabd3f525`  
**Usage**: `python scripts/run_full_court_press.py`

### `tools/script_state_lookout.py` ⭐
**Purpose**: Proactive script drift monitoring  
**State**: STABLE  
**SHA256**: `a675a162f37fe223bccb939ebdb14e978cb7d725485507263d722f49881db835`  
**Usage**: `python tools/script_state_lookout.py --json`  
**Features**: Detects unauthorized script modifications, FROZEN/STABLE drift

### `tools/script_state_check.py` ⭐
**Purpose**: Script governance verification  
**State**: STABLE  
**SHA256**: `0dbd9dcadce58d560b45456e799096a3dbb8514572d99d840c99d58644c72b54`  
**Usage**: `python tools/script_state_check.py`

### `tools/verify_witness_epoch.py` ⭐
**Purpose**: Witness epoch compliance verification  
**State**: STABLE  
**SHA256**: `f17a9f309aa5e1960c374540c19ebfd1ef32aa1b75d72333f31db85e5a12c891`  
**Usage**: `python tools/verify_witness_epoch.py`

### `tools/validate_state_history_format.py` ⭐
**Purpose**: State history format validator  
**State**: STABLE  
**SHA256**: `405996cb2670c866fb7a44fba58dbb163357f3f5e7bf47a4e72088101be0b14e`  
**Usage**: `python tools/validate_state_history_format.py --state-history docs/STATE_HISTORY.md`

### `tools/format_state_history.py`
**Purpose**: State history formatting utility  
**State**: OBSERVE  
**Usage**: `python tools/format_state_history.py`

### `tools/audit_encoding_repo.py`
**Purpose**: Encoding hygiene audit  
**State**: OBSERVE  
**Usage**: `python tools/audit_encoding_repo.py`

### `tools/compile_audit.py`
**Purpose**: Python syntax compilation check  
**State**: OBSERVE  
**Usage**: `python tools/compile_audit.py`

### `tools/verify_chain_integrity.py` ⭐
**Purpose**: Merkle chain integrity verification  
**State**: STABLE  
**SHA256**: `c06af738cf2e4cc27eb02df69b4215140c6f32a9588f9aa2dc277eff308eebc4`  
**Usage**: `python tools/verify_chain_integrity.py`

### `tools/verify_evidence_vault.py` ⭐
**Purpose**: Evidence vault tamper detection  
**State**: STABLE  
**SHA256**: `86c33132aabc548188014bf289e6df0cf1e7d27857f60e3bc931258eb99f4379`  
**Usage**: `python tools/verify_evidence_vault.py`

---

## PowerShell Tools

### `tools/court_sweep.ps1`
**Purpose**: PowerShell wrapper for court_sweep.py  
**Usage**: `.\tools\court_sweep.ps1`

### `tools/mw_full_proof.ps1`
**Purpose**: Full proof audit (PowerShell)  
**Usage**: `.\tools\mw_full_proof.ps1`

### `tools/prove.ps1`
**Purpose**: Quick proof utility  
**Usage**: `.\tools\prove.ps1`

### `tools/script_state_scan.ps1`
**Purpose**: Script state scanning (PowerShell)  
**Usage**: `.\tools\script_state_scan.ps1`

### `tools/verify_witness_epoch.ps1`
**Purpose**: Witness epoch verification (PowerShell)  
**Usage**: `.\tools\verify_witness_epoch.ps1`

### `tools/solob.ps1`
**Purpose**: Solob wrapper utility  
**Usage**: `.\tools\solob.ps1`

---

## Modules (Ritual Engine)

### `modules/base_module.py` ⭐
**Purpose**: Ritual engine base module abstraction  
**State**: STABLE  
**SHA256**: `c8be833af2192cca1ea4cbc8512db98ed11e351af63694444ccd05fe7bab504f`  
**Type**: Base class for all ingestion modules

### `modules/json_ingestion.py` ⭐
**Purpose**: JSON ingestion module for ritual engine  
**State**: STABLE  
**SHA256**: `6e7bc94b87b24f0bf110ac7f3c4c1230ff3b4fda2479f19b02fafb80bb1c0211`  
**Usage**: Via `ritual_engine.py` with JSON config

### `modules/lexicon_ingestion.py` ⭐
**Purpose**: Lexicon ingestion module for ritual engine  
**State**: STABLE  
**SHA256**: `44e4268fbfc59e0b0bd0ee020903b231335daf01c186a673b89daa9937cceab1`  
**Usage**: Via `ritual_engine.py` with lexicon config

### `modules/pdf_ingestion.py` ⭐
**Purpose**: PDF ingestion module for ritual engine  
**State**: STABLE  
**SHA256**: `74edd46f1068434301f3e62ee562b47bc221678e5a4d3a059f8b36a987699801`  
**Usage**: Via `ritual_engine.py` with PDF config

### `modules/registry_ingestion.py` ⭐
**Purpose**: Registry ingestion module for ritual engine  
**State**: STABLE  
**SHA256**: `9b120e5c920664b8b8af3cc05ab40fd9ba38c53a72b7f553efe0727ca0f7ecb0`  
**Usage**: Via `ritual_engine.py` with registry config

### `modules/__init__.py`
**Purpose**: Python package initialization  
**State**: OBSERVE

---

## Core Module

### `core/chain_constitution.py` ⭐
**Purpose**: Merkle chain constitution (CRITICAL)  
**State**: FROZEN  
**SHA256**: `d348a20b25fd99825169b5e17c603af62a6e4e8072741833badcc95dd3e481cc`  
**Warning**: NEVER EDIT - Cryptographically locked

---

## Deprecated/Legacy Scripts

### `scripts/state_transition.py`
**Replaced by**: `scripts/log_state_transition.py`  
**Status**: Deprecated

---

## Script States Explained

| State | Meaning | Can Edit? | SHA256 Required? |
|-------|---------|-----------|------------------|
| **FROZEN** | Cryptographically locked, never edit | ❌ No | ✅ Yes |
| **STABLE** | Production-ready, edit with approval | ⚠️ With consent | ✅ Yes |
| **HOLSTERED** | Active development, evolving | ✅ Yes | ❌ No |
| **OBSERVE** | Track but don't execute | ✅ Yes | ❌ No |
| **REPAIR** | Under active fix | ✅ Yes | ❌ No |

---

## Quick Reference

### Most Important Scripts

1. **`wwmd_ask_hybrid.py`** - Hybrid RAG with citation injection
2. **`court_sweep.py`** - 10-check system audit
3. **`full_court_press.py`** - 3-layer comprehensive audit
4. **`register_anchors_from_registry.py`** - Anchor registration
5. **`ingest_marcus_unified.py`** - Unified corpus ingestion
6. **`log_state_transition.py`** - State transition logger
7. **`log_changelog.py`** - Changelog entry helper
8. **`validate_receipt_v2.py`** - Receipt validator
9. **`ritual_engine.py`** - Config-driven ingestion
10. **`script_state_lookout.py`** - Script drift monitoring

### Common Workflows

**Ingest New Corpus**:
```bash
# 1. Register anchors
python scripts/register_anchors_from_registry.py

# 2. Ingest content
python scripts/ingest_marcus_unified.py

# 3. Verify
python tools/court_sweep.py
```

**Query RAG System**:
```bash
python scripts/wwmd_ask_hybrid.py "What did Marcus Garvey say about unity?" --json
```

**Run Full Audit**:
```bash
python tools/full_court_press.py
```

**Log State Change**:
```bash
python scripts/log_state_transition.py --from OBSERVE --to RECORD --reason "Starting work" --sid S_20251230T000000Z_DESC
```

---

## Notes

- ⭐ = Production-critical script
- Scripts with SHA256 hashes are tracked in `docs/SCRIPT_STATE_REGISTRY.json`
- All scripts assume UTF-8 encoding (`PYTHONUTF8=1`)
- Run from repository root: `python scripts/<script>.py`

---

**Last Updated**: 2025-12-30T20:07:43-05:00  
**Registry Version**: 1.1  
**Total Scripts Documented**: 96
