# Solob Wrapper ? Christmas Guide (V1)

## What Changed
- **PS Hygiene**: `tools/prove.ps1` and `tools/court_sweep.ps1` are now strictly ASCII-compliant and include `Set-StrictMode` and `Test-ScriptParse`.
- **SID Canon**: Centralized SID resolution in `utils/sid.py`. All scripts now follow priority: `RUN_RECORDED_SID` > `STATE.json:active_session_id`.
- **Bundle Standardization**: Created `docs/EVIDENCE_BUNDLE_SPEC.md` and updated `scripts/prosecutor_consolidate_lexicon_bundle.py` to follow it.
- **BoS Pilot Ingest**: Upgraded `scripts/chunk_bos_pages_pilot.py` with manifest SHA-256 validation, improved collision error messages, and standardized receipt paths.
- **Audit Trails**: Updated `docs/STATE_HISTORY.md` with a "Witness Epoch" and a "SID Witness Policy". Added `tools/verify_witness_epoch.ps1`.

## One-Command Rituals
| Command | Purpose |
| :--- | :--- |
| `.\tools\court_sweep.ps1` | Full health check (State, DB, Index, Anchors). |
| `.\tools\verify_witness_epoch.ps1` | Audit state history for SID compliance. |
| `.\tools\solob.ps1 state` | Check current STGRAIL state and witness SID. |
| `python scripts/inspect_anchor_chunks.py` | Verify DB chunk counts per anchor. |

## Troubleshooting Map
- **Collision Detecting**: If `chunk_bos_pages_pilot.py` fails with "Collision detected," it means the PDF page hashes (V2) already exist. Check `inspect_anchor_chunks.py`.
- **Missing fitz**: BoS ingest requires `PyMuPDF`. Install via `pip install pymupdf`.
- **Missing SID**: Ensure you enter `RECORD` mode via `solob.ps1 record` before running ingestion scripts.
- **Manifest Mismatch**: If `chunk_bos_pages_pilot.py` fails on SHA-256, the file on disk has changed. Verify against `anchors_manifest_*.json`.

## Reality 1-4 Gate Checklist
1. **Anchors**: `anchors/` directory is populated and manifest matches disk.
2. **Map**: `docs/ANCHORS_MAP.md` is updated and synced with DB/Manifest.
3. **Chunk**: Chunks are deterministic (V1 for Lexicon, V2 for BoS) and collision-free.
4. **Prosecutor**: Evidence bundles follow the `EVIDENCE_BUNDLE_SPEC.md` layout.

## Final Verification Commands
```powershell
# 1. Test script parsing
.\tools\prove.ps1 -TestScriptParse
.\tools\court_sweep.ps1 -TestScriptParse

# 2. Run full court sweep
.\tools\court_sweep.ps1 -RepoRoot . -RunProve -RequireAZ

# 3. Verify history integrity
.\tools\verify_witness_epoch.ps1

# 4. Inspect DB counts
python scripts/inspect_anchor_chunks.py
```
