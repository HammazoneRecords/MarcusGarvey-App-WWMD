# CHANGELOG.md

All notable changes to the Solob Wrapper project documented chronologically.

This project follows audit-grade discipline: every major change leaves receipts, every state transition is witnessed, and history is append-only.

---

## [Witness Epoch] - 2025-12-25 Onward

**WITNESS_EPOCH_START: 2025-12-25T07:51:59Z**

From this point forward, every state transition carries a canonical Session ID (`sid=...`). Earlier entries may lack this field as the witness system was introduced mid-project.

### 2025-12-27

#### Encoding Recovery Pivot - Manual File-by-File Approach
**CRITICAL**: Repository-wide encoding corruption detected ? automated fix approach abandoned

- **Critical Finding**:
  - Ghost question mark corruption pattern detected across entire repository
  - Pattern: Every character has `?` inserted (`?i?m?p?o?r?t?`)
  - Root cause: UTF-16/UTF-8 binary-level encoding mismatch
  - All Python scripts (56+ files in scripts/, core/, utils/) affected
  - System rendered completely unrunnable

- **Response Actions**:
  - **Orphaned**: 4 encoding automation scripts -> `data/orphans/2025-12-27_encoding-recovery-pivot/removed_scripts/`
    - `scripts/_fix_encoding.py`
    - `scripts/_fix_ghost_question_marks.py`
    - `tools/encoding_defaults.ps1`
    - `tools/encoding_report.ps1`
  - **Deleted**: 6 encoding fix scripts (self-referential encoding issues)
    - `scripts/_clean_unicode.py`, `scripts/encoding_report.py`, `scripts/normalize_encodings.py`
    - `scripts/_quick_encoding_scan.py`, `scripts/test_no_unicode_internal.py`
    - `tools/normalize_repo_text.ps1`
  - **Quarantined**: 3 critically corrupted files -> `data/orphans/2025-12-27_encoding-recovery-pivot/quarantined_files/`
    - `scripts/artisan_emit_anchors_map_ascii.py`
    - `utils/ingest_flow_check.py`
    - `scripts/SCRIPT-LEVEL INVARIANTS.md`

- **Successfully Fixed**:
  - `scripts/test_constitution_tripwire.py` (emojis -> ASCII: [OK] -> [OK], [ERROR] -> [FAIL])

- **Prevention Established**:
  - **Added**: `docs/ENCODING_CONSTITUTION.md` - Canonical encoding standards
  - **Added**: `.vscode/settings.json` - UTF-8 enforcement for all files
  - **Added**: `docs/MANUAL_ENCODING_REPAIR.md` - Manual repair workflow guide
  - **Added**: `docs/ENCODING_RECOVERY_FINAL_STATUS.md` - Full incident report

- **Lessons Learned**:
  - Automated batch fixes are dangerous when encoding is already corrupted
  - Manual file-by-file inspection mandatory before any repair
  - Version control critical (Git not present - major risk)
  - Prevention > Cure

- **Philosophy**: *"Manual repairs are safer than automation when dealing with corruption."*
- **Session**: `S_20251225T075155Z_STATE_RECORD`
- **Date**: 2025-12-27T13:43:00-05:00 through 2025-12-27T13:57:00-05:00

#### Changelog Addendum - Major Undocumented Scripts
**NOTE**: The following scripts were implemented earlier but discovered during static audit and added to changelog on 2025-12-27T17:06:40-05:00

##### Lexicon Ingestion Pipeline (V1.1)
- **Added**: `scripts/import_lexicon_chunks_v1_1.py` (15KB) - V1.1 lexicon chunk ingestion
- **Purpose**: Primary lexicon ingestion script for A-Z lexicon entries
- **Features**:
  - Reads structured lexicon JSON files
  - Creates chunks with proper `anchor_locator` format
  - Assigns `truth_type = 'definition'` for lexicon entries
  - Records `lexicon_word` for each chunk
  - Generates import session receipts
- **Implementation Date**: 2025-12-24 (Lexicon A/B/C Pilot period)

##### Anchor Registration from Registry
- **Added**: `scripts/register_anchors_from_registry.py` (11KB) - Registry-based anchor registration
- **Purpose**: Batch register anchors from `docs/ANCHOR_REGISTRY_PLAN.json`
- **Features**:
  - Reads anchor registry specification
  - Validates source files exist before registration
  - Creates anchors with proper provenance metadata
  - Prevents duplicate anchor registration
- **Implementation Date**: 2025-12-21 (Monk Window period)

##### Cartographer Map Generator
- **Added**: `scripts/cartographer_emit_anchors_map.py` (21KB) - Full anchors map generator
- **Purpose**: Generates comprehensive anchor map documentation with Unicode support
- **Output**: `docs/ANCHORS_MAP.md` - Human-readable anchor navigation
- **Features**:
  - Lists all registered anchors with metadata
  - Shows chunk counts per anchor
  - Displays ingestion status and session IDs
  - Unicode-aware formatting
- **Implementation Date**: 2025-12-22 (Cartographer phase)

##### Registry Validator
- **Added**: `scripts/registry_validator.py` (12KB) - Anchor registry validation
- **Purpose**: Validates `ANCHOR_REGISTRY_PLAN.json` structure and coherence
- **Checks**:
  - Required fields present for each anchor entry
  - Source paths resolve to existing files
  - No duplicate anchor IDs
  - Proper anchor_type and status values
- **Implementation Date**: 2025-12-21 (Monk Window period)

##### Pre-Ingestion Audit Tools
- **Added**: `scripts/pre_ingestion_audit.py` (11KB) - Base pre-ingestion audit
- **Added**: `scripts/pre_ingestion_audit_ext.py` (23KB) - Extended pre-ingestion audit
- **Purpose**: Validate system readiness before any ingestion operation
- **Checks**:
  - Database exists and schema matches
  - Anchor manifest current
  - No drift detected since last snapshot
  - State is RECORD or EXECUTE
- **Implementation Date**: 2025-12-22 through 2025-12-23

##### Post-Ingestion Audit Tools
- **Added**: `scripts/post_ingestion_audit_ext.py` (20KB) - Extended post-ingestion audit
- **Purpose**: Validate system coherence after ingestion operations
- **Checks**:
  - All registered anchors have expected chunks
  - Chunk counts match source file expectations
  - No orphan chunks without anchors
  - Receipt chain integrity
- **Implementation Date**: 2025-12-23

##### Lexicon Row Index Stamping
- **Added**: `scripts/lexicon_stamp_row_index.py` (14KB) - Row index stamping for lexicon
- **Purpose**: Stamps row indices into lexicon JSON files for precise locators
- **Features**:
  - Adds `row_index` field to each lexicon entry
  - Maintains deterministic ordering
  - Required before lexicon ingestion for accurate locators
- **Implementation Date**: 2025-12-22 (Lexicon stamping period)

##### Naming Guard System
- **Added**: `scripts/naming_guard.py` (9KB) - Named entity protection
- **Purpose**: Validates text against naming allowlist before emission
- **Uses**: `docs/NAMING_ALLOWLIST.json` for approved entity names
- **Prevents**: Accidental inclusion of sensitive names in generated content
- **Implementation Date**: 2025-12-22

#### Changelog Addendum - Major Utils Modules
**NOTE**: The following utils were implemented earlier but added to changelog on 2025-12-27T17:06:40-05:00

##### Receipt Chain Utilities
- **Added**: `utils/receipt_chain.py` (24KB) - Receipt chain management
- **Purpose**: Full Merkle chain operations delegating to constitution
- **Features**:
  - Genesis receipt creation
  - Chain continuation with proper linkage
  - Payload hash computation (delegates to `chain_constitution.py`)
  - Chain validation and verification
  - Previous receipt resolution
- **Implementation Date**: 2025-12-26 (Merkle Chain System)

##### Chunk Retrieval Utilities
- **Added**: `utils/chunk_retrieval.py` (12KB) - Chunk retrieval and search
- **Purpose**: Query and retrieve chunks from database with various filters
- **Features**:
  - Retrieve by anchor_id
  - Search by content substring
  - Filter by truth_type
  - Page-based retrieval for PDF chunks
- **Implementation Date**: 2025-12-26 (TMS Ingestion period)

#### Changelog Addendum - Major Scripts Detail Expansion
**NOTE**: The following scripts were mentioned but warrant expanded documentation, added 2025-12-27T17:06:40-05:00

##### Receipt Emission System (Full Documentation)
- **Script**: `scripts/emit_receipt.py` (30KB) - Largest script in repository
- **Purpose**: Universal receipt emission with chain support
- **Receipt Types Supported**:
  - `ANCHOR_REGISTERED` - Anchor registration witness
  - `CHUNKS_INGESTED` - Chunk ingestion witness
  - `SNAPSHOT_CREATED` - Anchor manifest snapshot
  - `SEAL_CREATED` - Epoch boundary seal (chain-enabled)
  - `BUNDLE_CREATED` - Evidence bundle creation (chain-enabled)
  - `BUNDLE_VERIFIED` - Bundle verification witness (chain-enabled)
  - `INDEX_UPDATED` - Evidence index update (chain-enabled)
  - `DB_CHECKPOINT` - Database checkpoint
  - `INGESTION_STARTED` / `INGESTION_COMPLETED` - Ingestion lifecycle
- **Chain Flags**: `--chain`, `--chain-id`, `--previous-receipt`
- **Implementation Date**: Foundation Era through 2025-12-26

##### Receipt Validation System (Full Documentation)
- **Script**: `scripts/validate_receipt.py` (43KB) - Largest file in scripts/
- **Purpose**: Sovereign receipt validation with constitutional hash verification
- **Features**:
  - Schema validation (all required fields present)
  - Payload hash verification (local computation, no external deps)
  - Chain linkage validation (genesis purity, sequence ordering)
  - ImportError bypass eliminated (hardened 2025-12-26)
  - Backward compatible with non-chain receipts
- **Implementation Date**: Foundation Era, hardened 2025-12-26

##### Session Lock System (Full Documentation)
- **Script**: `scripts/session_lock.py` (27KB) - Session management
- **Purpose**: Prevent concurrent access and manage session lifecycle
- **Features**:
  - Lock acquisition and release
  - Git integration for state tracking
  - Session ID generation and validation
  - Stale lock detection and cleanup
  - Multi-process safety
- **Implementation Date**: 2025-12-23

#### Changelog Addendum - Undocumented Documentation Files
**NOTE**: The following docs existed but were not in changelog, added 2025-12-27T17:06:40-05:00

##### Anchors Maps
- **Added**: `docs/ANCHORS_MAP.md` (10KB) - Unicode anchor map
- **Added**: `docs/ANCHORS_MAP_ASCII.md` (10KB) - ASCII-safe anchor map
- **Purpose**: Human-readable navigation of all registered anchors

##### Anchor Registry Plan
- **Added**: `docs/ANCHOR_REGISTRY_PLAN.json` (12KB) - Canonical anchor registry
- **Purpose**: Defines all anchors to be registered with metadata

##### Receipt Documentation
- **Added**: `docs/RECEIPT_EXAMPLES.md` (17KB) - Receipt examples and patterns
- **Added**: `docs/RECEIPT_LIFECYCLE_RULES.md` (9KB) - Receipt lifecycle governance
- **Purpose**: Reference documentation for receipt system

##### Route Documentation
- **Added**: `docs/ROUTE_LEGEND.md` (5KB) - Route legend reference
- **Added**: `docs/SERIES_ROUTE.md` (4KB) - Series routing documentation
- **Purpose**: Navigation and routing documentation

##### Evidence Bundle Specification
- **Added**: `docs/EVIDENCE_BUNDLE_SPEC.md` (1KB) - Bundle format specification
- **Purpose**: Defines structure of evidence bundles

##### Citation Metadata Strategy
- **Added**: `docs/CITATION_METADATA_STRATEGY.md` (4KB) - Citation strategy document
- **Purpose**: Strategy for citation locator design (distinct from UPGRADE doc)

##### Ingestion Completion Markers
- **Added**: `docs/ingest_*_done.json` files - Ingestion completion markers
  - `ingest_eitheror_done.json`
  - `ingest_ramblings_done.json`
  - `ingest_tms_done.json`
  - `ingest_wai_done.json`
- **Purpose**: Track completed ingestion operations

##### Artifact Specifications
- **Added**: `docs/artifacts_*.json` files - Artifact specifications
  - `artifacts_eitheror.json`
  - `artifacts_ramblings.json`
  - `artifacts_tms.json`
  - `artifacts_wai.json`
- **Purpose**: Define expected artifacts for each anchor

#### Changelog Addendum - Foundational Scripts
**NOTE**: The following tools were implemented earlier but added to changelog on 2025-12-27T17:01:20-05:00

##### Lexicon Bundle Consolidation
- **Added**: `scripts/prosecutor_consolidate_lexicon_bundle.py` - Supreme Lexicon Bundle creator
- **Purpose**: Consolidates A-Z lexicon evidence into a single unified bundle
- **Features**:
  - Collects exactly one receipt per letter: `RECEIPT_LEXICON_<L>*.json`
  - Collects exactly one stamp per letter: `LEXICON_STAMP_<L>*.json`
  - Prefers sources from A-Z SID (`LEXICON_AZ`) when multiple exist
  - Emits: `RECEIPTS/`, `STAMPS/`, `BUNDLE.json`, `INDEX.json`
- **Status**: Currently affected by encoding corruption (quarantine candidate)
- **Implementation Date**: 2025-12-25T02:03:41-05:00 (Supreme Lexicon Bundle session)

##### State Transition Controller
- **Added**: `scripts/state_transition.py` - STGRAIL state transition controller
- **Purpose**: Changes `docs/STATE.json` and appends to `docs/STATE_HISTORY.md`
- **Features**:
  - Requires `--to` (OBSERVE | RECORD | EXECUTE)
  - Requires `--note` (cannot be blank - prevents AI-abusable transitions)
  - Requires `--confirm YES_I_MEAN_IT` (safety latch)
  - Supports `--at` for explicit timestamp override
  - Appends transitions with local + UTC timestamps
- **Status**: Currently affected by encoding corruption (quarantine candidate)
- **Implementation Date**: 2025-12-20 (STGRAIL System Activation)

#### Changelog Addendum - Previously Undocumented Tools
**NOTE**: The following tools were implemented on 2025-12-26 but added to changelog on 2025-12-27T15:01:38-05:00

##### Preflight Balance Check System
- **Added**: `scripts/preflight_balance_check.py` - GO/NO-GO decision system
- **Purpose**: Comprehensive system balance verification before progression
- **Checks**:
  - Constitution integrity (exports, identity lock, drift tests)
  - Import stability (bootstrap pattern adoption)
  - Database coherence (anchors, chunks, orphans)
  - Receipt schema compliance (indexed SIDs only)
- **Output**: ASCII-only, exit code 0 (GO) or 1 (NO-GO)
- **Policy**: Only validates receipts under SIDs listed in `evidence/INDEX.json`
- **Documentation**: `docs/PREFLIGHT_BALANCE_CHECK_GUIDE.md`
- **Implementation Date**: 2025-12-26

##### Receipt Audit Script
- **Added**: `scripts/audit_receipts.py` - Receipt enumeration and validation
- **Purpose**: Scan all receipts and classify validation failures
- **Categories**:
  - `legacy_pre_v1` - Old schema versions
  - `partial_chain_fields` - Incomplete chain metadata
  - `missing_base_field` - Required fields missing
  - `json_parse_error` - Cannot parse JSON
  - `other` - Uncategorized
- **Output**: ASCII-only, exit code 0 if all valid, 1 if any fail
- **Implementation Date**: 2025-12-26

##### Quarantine Script (Expanded)
- **Added**: `scripts/quarantine_invalid_receipts.py` - Receipt quarantine automation
- **Purpose**: Move non-compliant receipts to `evidence/_quarantine/<category>/`
- **Features**:
  - Dry-run mode (`--dry-run`)
  - RECORD state enforcement
  - Category-based directory structure
  - Original path preservation in filenames
- **Philosophy**: *"You do not rewrite testimony. You change jurisdiction."*
- **Quarantine Structure**:
  ```
  evidence/_quarantine/
  ??? legacy_pre_v1/
  ??? partial_chain_fields/
  ??? missing_base_field/
  ??? json_parse_error/
  ??? other/
  ```
- **Implementation Date**: 2025-12-26

##### Citation CLI Tool
- **Added**: `scripts/cite_tms.py` - Prosecutor-grade citation CLI
- **Added**: `utils/chunk_retrieval.py` - Chunk retrieval utilities
- **Purpose**: Command-line citations from To My Son anchor
- **Features**:
  - Cite by page number (`--page`)
  - Cite by character range (`--chars`)
  - Search by quote (`--quote`)
  - Extract page ranges (`--pages`)
- **Documentation**: `docs/CITATION_WEAPON_GUIDE.md`
- **Implementation Date**: 2025-12-26

##### Encoding Report Tool
- **Added**: `tools/encoding_report.ps1` - Non-destructive encoding audit
- **Purpose**: Detect encoding issues before repair
- **Detects**:
  - UTF-16 LE/BE BOMs
  - UTF-8 BOMs
  - NUL bytes (ghost character pattern)
  - High bytes (non-ASCII)
- **Output**: `encoding_report.txt` with file-by-file analysis
- **Philosophy**: *"Report before repair - mass surgery with lights off is dangerous"*
- **Implementation Date**: 2025-12-26

#### Changelog Addendum - Previously Undocumented Infrastructure
**NOTE**: The following were implemented earlier but added to changelog on 2025-12-27T15:07:02-05:00

##### State Shortcut CMD Files
- **Added**: `STATE_TO_OBSERVE.cmd` - Quick transition to OBSERVE state
- **Added**: `STATE_TO_RECORD.cmd` - Quick transition to RECORD state
- **Added**: `STATE_NOTE.cmd` - Quick state note addition
- **Purpose**: One-click state transitions for operator convenience
- **Implementation Date**: Pre-Witness Epoch

##### PowerShell Tools
- **Added**: `tools/anchor_ingest_verdict.ps1` - Anchor ingestion verdict checker
  - Validates ingestion success/failure for anchors
  - Reports chunk counts and coherence status
- **Added**: `tools/verify_witness_epoch.ps1` - Witness epoch verification
  - Checks STATE_HISTORY.md for SID compliance after epoch start
  - Respects legacy addendum for pre-epoch transitions
- **Implementation Date**: 2025-12-25

##### Helper Scripts (Internal Use)
- **Added**: `scripts/_check_schema.py` - Schema validation helper
- **Added**: `scripts/_inspect_anchor.py` - Anchor inspection utility
- **Added**: `scripts/_quick_status.py` - Quick system status checker
- **Added**: `scripts/_repair_docstrings.py` - Docstring repair utility
- **Added**: `scripts/add_anchor.py` - Anchor addition stub
- **Added**: `scripts/ops_log.py` - Operations logging utilities
- **Note**: Prefixed with `_` to indicate internal/helper status
- **Implementation Date**: Various (Foundation Era)

##### Potentially Significant - Core Infrastructure
- **Added**: `scripts/audit_anchor_coherence.py` - Anchor coherence audit
  - Validates anchor-to-chunk-to-receipt integrity
  - Cross-references DB, manifest, and evidence
- **Added**: `scripts/register_missing_anchors.py` - Missing anchor registration
  - Detects and registers unregistered canonical anchors
- **Added**: `scripts/seal_checkpoint.py` - Checkpoint sealing
  - Creates sealed checkpoint receipts for state boundaries
- **Added**: `scripts/session_lock.py` - Session locking mechanism
  - Manages concurrent access prevention
  - Git integration for state tracking
  - 27KB substantial implementation
- **Added**: `scripts/state_history_note.py` - State history note addition
  - Appends notes to STATE_HISTORY.md programmatically
- **Added**: `core/config_constitution.py` - Configuration constitution
  - Constitutional configuration management
  - Immutable config patterns (parallel to chain_constitution.py)
- **Implementation Date**: 2025-12-23 through 2025-12-25

##### Utils Module Stubs
- **Added**: `utils/sid.py` - Session ID utilities (canonical SID resolution)
- **Added**: `utils/hash.py` - Hash utilities placeholder
- **Added**: `utils/time.py` - Time utilities placeholder
- **Added**: `utils/validate.py` - Validation utilities placeholder
- **Implementation Date**: Foundation Era

#### Changelog Addendum - Lexicon Recovery Tools
**NOTE**: The following tools were implemented on 2025-12-25 but added to changelog on 2025-12-27T15:15:32-05:00

##### Lexicon Audit and Validation
- **Added**: `scripts/audit_lexicon_counts.py` - JSON vs DB count comparison
  - Compares entry counts in lexicon JSON files against database chunks
  - Output: Per-letter MATCH/MISMATCH status with totals
  - Created during A-Z lexicon recovery session
- **Added**: `scripts/hard_check_lexicon.py` - Hard validation of lexicon structure
  - Validates lexicon entry schema compliance
- **Implementation Date**: 2025-12-25

##### PDF Chunking Pilots
- **Added**: `scripts/chunk_bos_pages_pilot.py` - Book of Solobility PDF chunking pilot
  - Extracts and chunks pages from BOS PDF for ingestion
- **Added**: `scripts/chunk_tms_pages_pilot.py` - To My Son PDF chunking pilot
  - Extracts and chunks pages from TMS PDF for ingestion
  - Related to TMS ingestion milestone on 2025-12-26
- **Implementation Date**: 2025-12-25 through 2025-12-26

##### Generation and Fingerprint Tools
- **Added**: `scripts/gen_coverage_ledger.py` - Coverage ledger generation
  - Generates coverage report for anchor-to-chunk mapping
- **Added**: `scripts/gen_legacy_addendum.py` - Legacy SID addendum generation
  - Creates `STATE_HISTORY_LEGACY_SID_ADDENDUM.json`
- **Added**: `scripts/invariants_fingerprint.py` - Invariants fingerprint generator
  - Creates cryptographic fingerprint of invariants document
- **Added**: `scripts/schema_fingerprint.py` - Schema fingerprint generator
  - Creates cryptographic fingerprint of database schema
- **Implementation Date**: 2025-12-22 through 2025-12-25

##### Inspection and Debug Tools
- **Added**: `scripts/inspect_anchor_chunks.py` - Anchor chunk inspector
  - Displays chunks associated with a specific anchor
- **Added**: `scripts/print_recorded_env.py` - Environment variable printer
  - Displays SOLOB_* environment variables for debugging
- **Added**: `scripts/sanity_check_post_ingestion.py` - Post-ingestion sanity check
  - Validates database coherence after ingestion operations
- **Implementation Date**: Various (Foundation Era through Witness Epoch)

#### Changelog Addendum - Previously Undocumented Documentation
**NOTE**: The following docs were created earlier but added to changelog on 2025-12-27T15:15:32-05:00

##### Reports
- **Added**: `docs/CHANGELOG_VERIFICATION_REPORT.md` - Changelog verification report
- **Added**: `docs/DB_CLEANUP_REPORT.md` - Database cleanup report
- **Added**: `docs/RECEIPT_SYSTEM_IMPROVEMENT_REPORT.md` - Receipt system improvements
- **Added**: `docs/ENCODING_RECOVERY_COMPLETION.md` - Encoding recovery completion status
- **Added**: `docs/UNICODE_SUSPECTS.md` - Unicode encoding suspects list
- **Implementation Date**: 2025-12-26 through 2025-12-27

##### Guides and References
- **Added**: `docs/TMS_INGESTION_GUIDE.md` - To My Son ingestion guide
- **Added**: `docs/KNOWN_ARTIFACTS.md` - Known artifacts reference
- **Added**: `Christmas Guide.md` - Seasonal operational guide (root level)
- **Implementation Date**: 2025-12-25 through 2025-12-26

#### Changelog Addendum - Previously Undocumented Tools
**NOTE**: The following tool was implemented earlier but added to changelog on 2025-12-27T15:15:32-05:00

- **Added**: `tools/prove.ps1` - Proof harness script
  - Simplified proof execution wrapper
  - Related to `mw_full_proof.ps1` workflow
- **Implementation Date**: 2025-12-25

### 2025-12-26

#### TMS (To My Son) Ingestion - Complete Library Upgrade
**MILESTONE**: Transformed from text pile to prosecutor-ready library with citation-grade locators

- **Ingestion Results**:
  - **Added**: 384 chunks from To My Son v1 PDF (all non-empty pages)
  - **Coverage**: Pages 1-399, 15 empty pages skipped (as expected)
  - **Total chunks**: 3,383 (was 2,999)
  - **Result**: 31/31 canon anchors now have chunks [OK]

- **Prosecutor-Grade Locators**:
  - Format: `pdf:page:0367:chars:466492-467136`
  - Character-precise boundaries for courtroom citations
  - Min locator: `pdf:page:0001:chars:000000-001277`
  - Max locator: `pdf:page:0399:chars:492535-492549`
  - Total document: ~492KB of text tracked

- **Citation System**:
  - **Added**: Citation utilities (`utils/citations.py`)
    - `parse_pdf_locator()` - Extract page and char boundaries
    - `format_citation()` - Human-readable citations
    - `extract_span()` - Pull exact text segments
  - Example output: `"TMS, p. 367, chars 466492-467136"`

- **Constitutional Bootstrap**:
  - **Fixed**: Import pattern constitutionalized across all scripts
  - **Pattern**: `from _bootstrap_imports import ensure_repo_root`
  - **Eliminated**: Ad-hoc `sys.path.insert(0, ...)` drift
  - **Updated**: `docs/IMPORT_STABILITY.md` with canonical pattern

- **Evidence Trail**:
  - [OK] `R_..._INGESTION_STARTED` - Court witness (begin)
  - [OK] `RECEIPT_CHUNKS_to_my_son_v1_PDF_PAGES_PILOT.json` - Chunking evidence
  - [OK] `R_..._INGESTION_COMPLETED` - Court witness (384 chunks)

- **Documentation**:
  - **Added**: `docs/TMS_INGESTION_FINAL_REPORT.md` - Forensic verification
  - **Added**: `docs/TMS_INGESTION_WORKFLOW.md` - Workflow documentation
  - **Added**: `docs/CITATION_METADATA_UPGRADE.md` - Citation strategy
  - **Added**: `scripts/_forensic_tms.py` - Page coverage verification

- **Philosophy**: *"The tiny decision that separates a library from a pile of text"*
- **Session**: `S_20251225T075155Z_STATE_RECORD`
- **Date**: 2025-12-26T19:22:12-05:00

#### Validator Hardening - Critical Security Fix
**SECURITY**: Closed ImportError bypass loophole, validator now court-grade sovereign

- **Critical Fix**: ImportError Loophole Eliminated
  - **Fixed**: Validator had `except ImportError: pass` that silently skipped hash verification
  - **Attack vector**: Broken imports allowed fake `payload_hash` to pass validation
  - **Result**: Validator is now self-contained, no external dependencies

- **Sovereign Validator Implementation**:
  - **Added**: Local hash computation (`compute_payload_hash_local()`)
  - **Added**: Self-contained canonical JSON serialization
  - **Removed**: External dependency on `receipt_chain.py`
  - **Result**: Validator forges its own gavel, doesn't borrow

- **Strengthened Linkage Validation**:
  - **Before**: Only checked key existence for `previous_receipt_sha256`
  - **After**: Validates value is non-empty string
  - **Rejects**: Empty strings, `null`, missing hashes

- **Test Results**: 6/6 tests passing
  - [OK] Normal receipts (no chain)
  - [OK] Chain-enabled receipts
  - [OK] Chain linkage verification
  - [OK] Backward compatibility
  - [OK] Incomplete chain rejection
  - [OK] Fake genesis rejection

- **Documentation**:
  - **Added**: `docs/VALIDATOR_HARDENING_SUMMARY.md`
  - **Updated**: Validator docstring: "SOVEREIGN: Does not depend on external modules"

- **Philosophy**:
  - *"The validator is now a judge with their own gavel"*
  - *"A scar must hurt when touched"*
  - *"No loopholes, no excuses"*

- **Session**: Part of Merkle chain implementation
- **Date**: 2025-12-26T04:52:43-05:00

#### Invalid Receipt Quarantine System
- **Added**: Quarantine system for invalid receipts - preserves history while changing jurisdiction
- **Changed**: 42 receipts preserved in `_quarantine` directory
- **Session**: `S_20251225T075155Z_STATE_RECORD`
- **Date**: 2025-12-26T20:45:53-05:00

#### Ghost File Cleanup with Quarantine Protocol
- **Removed**: Empty `solob.db` ghost file
- **Protocol**: File quarantined to `data/orphans/` (not deleted)
- **Principle**: *"Never delete. Always quarantine with evidence."*
- **Documentation**:
  - **Added**: `docs/GHOST_FILE_QUARANTINE.md` - Quarantine protocol and prevention
  - Evidence receipt created before file moved
  - Renamed with timestamp: `solob_GHOST_<timestamp>.db`
- **Result**: Audit trail preserved, file recoverable if needed
- **Session**: `S_20251225T075155Z_STATE_RECORD`
- **Date**: 2025-12-26T18:04:41-05:00

#### Timezone Reference Documentation
- **Added**: Kingston UTC-5 timezone reference documentation (`TIMEZONE_REFERENCE.md`)
- **Changed**: Updated `RECEIPT_SCHEMAS.md` and `v1-scope.md` with Kingston timezone standards
- **Session**: `S_20251225T075155Z_STATE_RECORD`
- **Date**: 2025-12-26T01:46:26-05:00

#### **MERKLE CHAIN SYSTEM** - Constitutional Implementation
**MILESTONE**: Complete Merkle chain cryptographic linkage with anti-drift constitutional protections

- **Core Implementation**:
  - **Added**: Constitutional chain canon (`core/chain_constitution.py`)
    - Immutable `payload_v1` hash algorithm (frozen, versioned)
    - Single canonical source of truth (eliminates implementation drift)
    - Strict genesis purity enforcement (sequence 0 cannot have `previous_receipt_hash`)
    - All-or-nothing chain fields: `chain_id`, `sequence`, `payload_hash`, `sealed`, `payload_hash_mode`

- **Receipt System Integration**:
  - **Added**: Chain utilities (`utils/receipt_chain.py`) - delegates to constitution
  - **Modified**: `scripts/emit_receipt.py` - Added `--chain`, `--chain-id`, `--previous-receipt` flags
  - **Modified**: `scripts/validate_receipt.py` - Constitutional hash verification, fixed ImportError bypass
  - **Backward Compatible**: Normal receipts work without chain fields

- **Chain Specification** (`chain/1.0`):
  - Genesis receipt: `sequence=0`, no `previous_receipt_hash` (enforced)
  - Linked receipt: `sequence>0`, requires valid `previous_receipt_sha256` (64-char hex)
  - Payload hash excludes: `receipt_id`, `timestamp_utc`, all chain fields
  - Payload hash includes: `previous_receipt_sha256` (linkage is semantic)
  - Philosophy: *"This payload as-linked in this chain position"*

- **Anti-Drift Protection**:
  - **Added**: Import bootstrap (`scripts/_bootstrap_imports.py`) - works from any CWD
  - Frozensets for `CHAIN_FIELDS_TOPLEVEL` and `HASH_EXCLUDE_TOPLEVEL` (immutable)
  - Version bump enforcement: cannot modify `payload_v1` without creating `payload_v2`
  - Parameter validation: `exclude_keys` raises `ValueError` if misused

- **Testing & Validation**:
  - **Added**: `scripts/test_receipt_chain_optional.py` (6/6 tests passing)
  - **Added**: `scripts/test_hash_consistency.py` (3/3 tests passing)
  - [OK] Normal receipts (no chain)
  - [OK] Chain-enabled receipts
  - [OK] Chain linkage verification
  - [OK] Backward compatibility
  - [OK] Incomplete chain rejection
  - [OK] Fake genesis rejection

- **Documentation**:
  - **Added**: `docs/CHAIN_CONSTITUTION_SUMMARY.md` - Constitutional implementation summary
  - **Added**: `docs/CHAIN_VERSIONING_RULES.md` - Version discipline and migration path
  - **Added**: `docs/IMPORT_STABILITY.md` - Bootstrap strategy and anti-drift patterns
  - **Added**: `docs/RECEIPT_CHAIN_LAYERING.md` - Optional Merkle chain philosophy
  - **Added**: `docs/RECEIPT_CHAIN_IMPLEMENTATION.md` - Command reference and usage guide
  - **Added**: `schemas/receipt.chain.json` - JSON schema for chain fields
  - **Updated**: `docs/v1-scope.md` - Added chain constitution to guarantees

- **Philosophy**:
  - *"A Merkle chain is a scar, not a tattoo"* - Chains record participation, not decoration
  - *"Constitution, not configuration"* - `payload_v1` is locked law, not customizable
  - *"Optional but strict"* - Chains optional, but when present, all rules enforced
  - *"Version, don't mutate"* - Changes require `payload_v2`, never silent edits

- **Enabled Types**: 4 chain-capable receipt types
  - `SEAL_CREATED` - Epoch boundaries
  - `BUNDLE_CREATED` - Evidence bundles
  - `BUNDLE_VERIFIED` - Bundle verification
  - `INDEX_UPDATED` - Index updates

- **Session**: `S_20251225T075155Z_STATE_RECORD`
- **Date**: 2025-12-26T04:52:43-05:00
- **Status**: [OK] **COMPLETE** - 9/9 tests passing, backward compatible, production ready

#### WAI v1.1 Upgrade
- **Changed**: Upgraded wrapper anchor invariants from v1.0 to v1.1
- **Added**: INVARIANT 14 added
- **Added**: v1.0 archived, new manifest generated
- **Session**: `S_20251225T075155Z_STATE_RECORD`
- **Date**: 2025-12-26T00:24:32-05:00

### 2025-12-25

#### Reality 5 Seal - Front-Door Coherence Achieved
- **Milestone**: Front-door coherence achieved + A-Z ledger verified
- **Evidence**: All lexicon A-Z ingested (1625 chunks), evidence index complete, witness epoch active
- **Session**: `S_20251225T075155Z_STATE_RECORD`
- **Date**: 2025-12-25T16:01:30-05:00

#### Legacy SID Addendum
- **Added**: `STATE_HISTORY_LEGACY_SID_ADDENDUM.json` documenting pre-witness-epoch transitions
- **Session**: `S_20251225T075155Z_STATE_RECORD`
- **Date**: 2025-12-25T16:06:29-05:00

#### Court Sweep After Bundle Fix
- **Added**: Court sweep after bundles_count fix (clean front door)
- **Session**: `S_20251225T075155Z_STATE_RECORD`
- **Date**: 2025-12-25T11:34:02-05:00

#### SID Witness System Testing
- **Added**: SID witness test and epoch verification
- **Session**: `S_20251225T075155Z_STATE_RECORD`
- **Date**: 2025-12-25T02:51:59-05:00

#### Supreme Lexicon Bundle
- **Added**: Prosecutor consolidated A-Z receipts + stamps into Supreme Lexicon Bundle
- **Session**: Various
- **Date**: 2025-12-25T02:03:41-05:00

#### Lexicon A-Z Full Ingestion Complete
- **Added**: All 26 lexicon blocks (A-Z) successfully ingested
- **Added**: 3-layer proof pyramid complete (Layer A: DB, Layer B: Receipts, Layer C: Bundle)
- **Recovered**: From anchor registration blockage
- **Verified**: 1625 total chunks across all lexicon entries
- **Date**: 2025-12-25T01:28:31-05:00

#### Lexicon A-S Recovery
- **Fixed**: Anchor registration blockage (missing SID flag)
- **Recovered**: Blocks A-E ingestion after critical failure
- **Session**: `S_20251224T233858Z_LEXICON_AZ_FULL`
- **Date**: 2025-12-25T00:46:29-05:00

### 2025-12-24

#### Full A-Z Ingest Attempt and Recovery
- **Started**: SESSION: FULL A-Z INGEST
- **Failed**: Critical failure - anchors not registered due to missing SID flag
- **Recovery**: Fixed anchor registration script
- **Session**: `S_20251224T233858Z_LEXICON_AZ_FULL`
- **Date**: 2025-12-24T23:38:58-05:00

#### Database Reset and Fresh Start
- **Added**: Prosecutor checkpoint of POC exhibit DB
- **Changed**: Moved POC DB aside, initialized fresh DB
- **Session**: `S_20251224T225627Z_FULL_RESET`
- **Date**: 2025-12-24T22:56:55-05:00

#### Lexicon A/B/C Pilot Complete
- **Added**: Full lexicon ingestion for blocks A, B, C
- **Session**: `S_20251224T222203Z_LEXICON_FULL`
- **Date**: 2025-12-24T22:22:25-05:00

### 2025-12-23

#### Evidence Index Hardening
- **Changed**: `evidence_index` now requires explicit args (no defaults)
- **Session**: `S_20251223T150316Z_EVIDENCE_INDEX_HARDEN_TEST`
- **Date**: 2025-12-23T15:03:33-05:00

#### Change Control System
- **Added**: Codebase fingerprint baseline
- **Added**: Codebase diff report tool
- **Added**: Change control documentation (`CHANGE_CONTROL.md`)
- **Session**: `S_20251223T133735Z_CODE_AUDIT`
- **Date**: 2025-12-23T13:38:02-05:00

#### Session Lock with Git Integration
- **Added**: Git integration to session lock
- **Added**: State guard enhancement for missing Git repos
- **Session**: `S_20251223T133647Z_GITPATCH_SMOKE`
- **Date**: 2025-12-23T13:36:58-05:00

#### Post-Ingestion Audit Gate
- **Added**: Fresh manifest linking after resnapshot
- **Changed**: Switched from pre-ingest to post-ingest audit
- **Session**: `S_20251223T111520Z_RESNAP_POST`
- **Date**: 2025-12-23T11:15:34-05:00

### 2025-12-22

#### Lexicon Row Index Stamping
- **Added**: Row index stamping for lexicon entries
- **Changed**: Resnapshot required after lexicon stamp changed anchor content
- **Session**: `S_20251222T235915Z_RESNAP`
- **Date**: 2025-12-22T23:59:41-05:00

#### Lexicon Pilot Ingestion
- **Added**: System check + lexicon A pilot ingestion
- **Session**: `S_20251222T224740Z_INGEST_PILOT`
- **Date**: 2025-12-22T22:47:48-05:00

#### Drift Event - Canon File Edit
- **Event**: Edited `canon/eitheror.md` after `anchors_manifest_20251220T173244Z`
- **Added**: New manifest `anchors_manifest_20251223T024745Z`
- **Fixed**: SHA256 mismatch for `canon/eitheror.md`
- **Session**: `S_20251222T214737Z_DRIFT`
- **Date**: 2025-12-22T21:47:45-05:00

#### Pre-Ingestion Audits Extended
- **Added**: Extended audit with evidence index (Step 4 + Step 6)
- **Session**: `S_20251221T201619Z_MONK`
- **Date**: 2025-12-22T21:08:51-05:00

#### Invariants Lock
- **Added**: Invariants lock + registry validate + schema fingerprint
- **Session**: `S_20251221T201619Z_MONK`
- **Date**: 2025-12-22T18:31:05-05:00

#### Naming Guard with Allowlist
- **Added**: Named entity guard with allowlist (`NAMING_ALLOWLIST.json`)
- **Session**: Various
- **Date**: 2025-12-22T08:41:36-05:00

#### Cartographer + Artisan Maps
- **Added**: Cartographer map (Unicode support)
- **Added**: Artisan ASCII-safe map
- **Session**: `S_20251221T201619Z_MONK`
- **Date**: 2025-12-22T08:44:53-05:00

#### Prosecutor Phase 2
- **Added**: Evidence bundle verification
- **Added**: DB checkpoint receipts
- **Session**: `S_20251221T201619Z_MONK`
- **Date**: 2025-12-22T00:37:53-05:00

### 2025-12-21

#### Monk Anchor Registration Sealed
- **Added**: 8 canonical anchors registered (no chunks)
- **Session**: `S_20251221T201619Z_MONK`
- **Status**: anchors=8, chunks=0
- **Date**: 2025-12-22T01:41:18+00:00

#### Monk Window Opened
- **Started**: Monk window for registering canon anchors only
- **Session**: `S_20251221T201619Z_MONK`
- **Date**: 2025-12-22T01:26:02+00:00

### 2025-12-20

#### First Recorded Shuffle Completed
- **Milestone**: Transition from static design to audited reality
- **Added**: `data/memory.db` (initial)
- **Added**: `data/snapshots/anchors_manifest_20251220T173244Z.json`
- **Added**: `logs/ops_ledger.jsonl` (intent-linked receipts)
- **Verified**: All commands exited with code 0, sanity check passed
- **Date**: 2025-12-20T12:42:00-05:00

#### STGRAIL System Activated
- **Added**: State discipline enforcement (OBSERVE/RECORD)
- **Added**: Zero-shuffle protocol
- **Added**: `run_recorded.py` requires `--intent` and sets `SOLOB_RECORDED_RUN=1`
- **Added**: `init_db.py` refuses unrecorded execution
- **Verified**: schema.sql V1.1 (tables before indexes, CHECK constraints present)
- **Verified**: hash_utils.py populated + importable
- **Quarantined**: memory.db placeholder to `data/orphans/`
- **Date**: 2025-12-20T05:10:00-05:00

---

## [Foundation Era] - Pre-Witness Epoch

The following changes occurred before the Witness Epoch (pre-2025-12-25T07:51:59Z). Session IDs may be absent or inconsistent.

### Core System Architecture

#### Constitutional Layer
- **Added**: Chain constitution (`core/chain_constitution.py`)
  - Immutable payload_v1 hash algorithm
  - Chain versioning discipline
  - Single canonical implementation to prevent drift

#### Receipt System
- **Added**: Receipt lifecycle governance
  - 7 classes of receipts taxonomy
  - Immutability rules
  - Supersession protocol
  - Append-only evidence discipline

#### Database Schema
- **Added**: SQLite schema V1.1 (`data/schema.sql`)
  - Tables before indexes pattern
  - CHECK constraints for integrity
  - Anchor/chunk relational model
  - Run citations edges

#### State Management
- **Added**: STGRAIL state discipline
  - OBSERVE mode (read-only)
  - RECORD mode (write-enabled with witness)
  - State history tracking
  - Witness epoch markers

### Documentation Foundation

- **Added**: Vision document (`docs/vision.md`)
- **Added**: V1 Scope (`docs/v1-scope.md`)
- **Added**: Threat model (`docs/threat-model.md`)
- **Added**: Invariants documentation (`docs/invariants.md`)
- **Added**: Receipt schemas (`docs/RECEIPT_SCHEMAS.md`)
- **Added**: Chain versioning rules (`docs/CHAIN_VERSIONING_RULES.md`)

### Tools and Scripts

- **Added**: `tools/solob.ps1` - State transition controller
- **Added**: `tools/mw_full_proof.ps1` - Full proof harness (Reality 1-5)
- **Added**: `tools/court_sweep.ps1` - Structured audit sweep
- **Added**: `scripts/sanity_check.py` - DB coherence verification
- **Added**: `scripts/snapshot_anchors.py` - Cryptographic manifest generator

---

## Versioning Philosophy

This project uses **reality-based versioning** rather than semantic versioning:

- **Reality 1 (Monk)**: Anchors-only, no chunking
- **Reality 2 (Cartographer)**: Maps, indexes, fingerprints
- **Reality 3 (Prosecutor)**: Court sweeps + bundles
- **Reality 4 (Artisan)**: UI + ergonomics
- **Reality 5 (Front-Door Safe)**: Audit-grade coherence

Each "reality" represents a provable milestone where specific invariants hold true.

---

## Principles

- **Witness Over Convenience**: Nothing enters without anchor, session, and receipt
- **Canon vs Derivative**: Never confused - canon is hashable, derivatives are reproducible
- **Append-Only Evidence**: Mistakes preserved as proof, corrections via new receipts
- **Constitutional Versioning**: Payload algorithm changes require version bump, never silent mutation
- **Front-Door Auditable**: Every registered anchor maps to manifest and has receipts

---

**This changelog is maintained as an append-only document following the same principles as the system it describes.**

**The corruption was noise.**

**The changelog is signal.**

**The Ark move is selection.**

**The orphans folder is humility.**

# ** And STATE_HISTORY is sovereignty.** #

## MOOD ANCHOR
- Felt: annoyed -> strangely proud (ledger still clean + Lineage Preserved)
