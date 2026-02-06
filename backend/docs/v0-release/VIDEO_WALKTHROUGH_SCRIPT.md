# Video Walkthrough Script ? Solobic Wrapper Ark V0

**Target Duration**: 15-20 minutes  
**Format**: Screen recording with voiceover  
**Audience**: New operators and technical reviewers

---

## Part 1: Introduction (2 minutes)

### Shot 1: Title Slide
**Visual**: Logo/title card
```
Solobic Wrapper Ark
Version 0.1.0
Witness-first. Audit-grade. Antifragile.
```

**Voiceover**:
> "Welcome to Solobic Wrapper Ark Version Zero?a prosecutor-grade knowledge management system designed for epistemic discipline and legal defensibility. In this 15-minute walkthrough, we'll tour the system, demonstrate core operations, and show you how to maintain 100% audit compliance."

---

### Shot 2: Achievement Overview
**Visual**: Show `docs/v0-release/EVIDENCE_V0.md` with court sweep results

**Voiceover**:
> "Solobic Wrapper Ark V0 has achieved 100% completion across all six Realities?from anchors-first discipline to prosecutor-grade receipts to config-driven ritual execution. Our latest court sweep shows all eight checks passing: database integrity, witness epoch compliance, receipt validation, and zero orphan chunks."

**On Screen**: Highlight metrics
- 31 anchors
- 3,446 chunks
- 27/27 receipts valid
- 0 violations

---

## Part 2: System Tour (5 minutes)

### Shot 3: Directory Structure
**Visual**: Terminal showing `tree` or `ls -la`

**Commands**:
```bash
cd "c:\Users\Owner\Desktop\PROJECTS IN MOTION\ARK V0\solob wrapper ARK v0\solob-wrapper after abc real4plus"

# Show key directories
ls -l
```

**Voiceover**:
> "The system is organized into seven main directories. Data contains our SQLite database with anchors and chunks. Docs holds all documentation including state tracking. Evidence bundles store our prosecutor-grade audit trail. Modules contain the ritual engine's reusable ingestion patterns. Scripts handle ingestion operations. Tools provide governance and audit capabilities. And config houses our ritual configurations."

**On Screen**: Highlight each directory as mentioned

---

### Shot 4: Database Inspection
**Visual**: DB Browser for SQLite showing `data/memory.db`

**Actions**:
1. Open database
2. Show `anchors` table (31 rows)
3. Show `chunks` table (3,446 rows)
4. Demonstrate relationship (chunk -> anchor foreign key)

**Voiceover**:
> "Our database uses a simple but powerful schema. The anchors table contains thirty-one canonical content sources. The chunks table holds thirty-four forty-six atomic content units, each referencing a parent anchor. Every chunk includes an import session ID for complete chain of custody."

**SQL Demo**:
```sql
SELECT COUNT(*) FROM anchors;  -- 31
SELECT COUNT(*) FROM chunks;    -- 3446
SELECT anchor_id, COUNT(*) FROM chunks GROUP BY anchor_id LIMIT 5;
```

---

### Shot 5: Evidence Bundles
**Visual**: File explorer showing `evidence/bundles/`

**Actions**:
1. List all bundles: `ls evidence/bundles/`
2. Open latest COURT_SWEEP bundle
3. Open INDEX.json (show bundle_version: V2)
4. Open REPORT.md (show PASS verdict)

**Voiceover**:
> "Evidence bundles are the heart of our audit trail. Each bundle includes an INDEX file with metadata, a REPORT summarizing results, and a RECEIPTS directory with operational proofs. This latest court sweep bundle shows our V2 compliant structure and clean PASS verdict across all checks."

---

### Shot 6: State Files
**Visual**: VSCode showing `docs/STATE.json` and `docs/STATE_HISTORY.md`

**Show**:
```json
// STATE.json
{
  "current_state": "OBSERVE",
  "active_session_id": "S_20251225T075155Z_STATE_RECORD",
  "last_updated": "2025-12-29T05:38:15Z"
}
```

**Voiceover**:
> "State discipline is enforced through two files. STATE.json tracks our current mode?OBSERVE for read-only, RECORD for tracked writes. STATE_HISTORY.md provides an append-only ledger of every state transition with timestamps and session IDs. This witness-first approach ensures complete auditability."

---

## Part 3: Daily Operations (5 minutes)

### Shot 7: Daily Health Check
**Visual**: Terminal running commands

**Script**:
```bash
# Step 1: Check state
python tools/cli/mw.py state

# Output shown:
# Current state: OBSERVE
# Active SID: S_20251225T075155Z_STATE_RECORD

# Step 2: Run court sweep
python tools/court_sweep.py

# Output shown:
# [OK] Court sweep bundle: ...
# [VERDICT] PASS
# [REASON]  All checks passed

# Step 3: Check for orphans
sqlite3 data/memory.db "SELECT COUNT(*) FROM chunks WHERE import_session_id IS NULL;"

# Output: 0
```

**Voiceover**:
> "The daily health check takes just five minutes. First, verify system state. Second, run court sweep for comprehensive audit. Third, confirm zero orphan chunks. Green across the board means we're production-ready."

---

### Shot 8: State Transitions
**Visual**: Terminal showing transition commands

**Script**:
```bash
# Transition to RECORD
python scripts/log_state_transition.py \
  --from OBSERVE \
  --to RECORD \
  --reason "Demonstrating state transition for walkthrough"

# Check state
python tools/cli/mw.py state
# Shows: Current state: RECORD

# View state history
tail -5 docs/STATE_HISTORY.md

# Return to OBSERVE
python scripts/log_state_transition.py \
  --from RECORD \
  --to OBSERVE \
  --reason "Demonstration complete"
```

**Voiceover**:
> "State transitions are logged with helper scripts that automatically fetch the active session ID, generate synchronized timestamps, and enforce the canonical format. Every transition is witnessed and auditable."

---

### Shot 9: Ritual Engine Demo
**Visual**: Show ritual config, validate, execute

**Script**:
```bash
# Show config
cat config/rituals/lexicon_a_template.json

# Validate
python tools/cli/mw.py ritual validate --config config/rituals/lexicon_a_template.json

# Dry-run (no mutations)
python scripts/ritual_engine.py --config config/rituals/lexicon_a_template.json --dry-run
```

**Voiceover**:
> "The ritual engine transforms one-off scripts into reusable, config-driven patterns. Each ritual specifies a module type, source path, and target anchor. The engine validates configs, supports dry-runs for testing, and automatically generates V2 receipts."

---

## Part 4: Troubleshooting Demo (3 minutes)

### Shot 10: Reading Court Sweep Failures
**Visual**: Show simulated failure report

**Script**:
```bash
# Simulate reading a failure
cat evidence/bundles/SIMULATED_FAILURE/REPORT.md

# Shows:
# [FAIL] orphan_chunks
# - details: 5 chunks found without import_session_id
```

**Voiceover**:
> "When court sweep fails, the report points directly to the issue. Here, orphan chunks were detected?chunks missing their session ID. The troubleshooting playbook provides step-by-step diagnosis and fixes for every check."

---

### Shot 11: Orphan Investigation
**Visual**: Terminal showing diagnostic commands

**Script**:
```bash
# Find orphans
sqlite3 data/memory.db "SELECT chunk_id, anchor_id FROM chunks WHERE import_session_id IS NULL;"

# Trace origin (example)
# Check evidence bundles for matching anchor/timestamp

# Fix (in REPAIR state)
# UPDATE chunks SET import_session_id = 'S_CORRECT_SID' WHERE ...
```

**Voiceover**:
> "Investigation follows a systematic process: query the database to identify orphans, trace their origin using chunk ID patterns, find the correct session ID from evidence bundles, and apply the fix in REPAIR state. Then verify with another court sweep."

---

## Part 5: Advanced Topics (3 minutes)

### Shot 12: Custom Ritual Creation
**Visual**: VSCode editing a new ritual config

**Show**: Creating `custom_ritual.json`
```json
{
  "ritual_name": "Custom Data Ingestion",
  "module_type": "json",
  "source_path": "data/custom/example.json",
  "anchor_id": "CUSTOM_ANCHOR",
  "config": {
    "chunk_id_template": "CUSTOM|{index}"
  }
}
```

**Voiceover**:
> "Creating custom rituals is straightforward. Choose a module type?JSON, PDF, Lexicon, or Registry. Specify your source path and target anchor. Customize the chunk ID template. Then validate and test with dry-run before live execution."

---

### Shot 13: Receipt Validation
**Visual**: Terminal running receipt validator

**Script**:
```bash
# Validate receipt
python scripts/validate_receipt_v2.py \
  evidence/bundles/S_20251225T075155Z_STATE_RECORD/RECEIPTS/RECEIPT_CHUNKS_book_of_solobility_v1_PDF_PAGES_PILOT.json

# Output: [OK] Receipt is valid (V2 schema)
```

**Voiceover**:
> "Receipt validation ensures every ingestion operation has a prosecutor-grade audit trail. The validator checks for required fields, proper timestamps, strict rule enforcement, and SHA256 integrity hashes. One hundred percent of our receipts pass validation."

---

### Shot 14: Evidence Chain of Custody
**Visual**: Flow diagram or terminal showing trace

**Script**:
```bash
# Find chunk
sqlite3 data/memory.db "SELECT * FROM chunks WHERE chunk_id = 'SOLOB|V2|CHUNK|PDF|BOS|page:0001';"

# Note import_session_id

# Find bundle
ls evidence/bundles/ | grep <SID>

# View receipt
cat evidence/bundles/S_<SID>*/RECEIPTS/RECEIPT_*.json
```

**Voiceover**:
> "Every chunk has a complete chain of custody. From the database, we extract the session ID. From the session ID, we find the evidence bundle. From the bundle, we retrieve the receipt. The receipt shows exactly when, how, and by what operation the chunk was created?with cryptographic proof."

---

## Part 6: Conclusion (2 minutes)

### Shot 15: Six Realities Recap
**Visual**: Diagram or list of 6 Realities

**On Screen**:
1. **The Monk** ? Anchors first [OK]
2. **The Cartographer** ? Structure + naming [OK]
3. **The Artisan** ? Mechanical chunking [OK]
4. **The Prosecutor** ? Legally defensible [OK]
5. **The Product Builder** ? Reusable engine [OK]
6. **The Guardian** ? Governance [OK]

**Voiceover**:
> "Sol obic Wrapper Ark V0 achieves one hundred percent completion across all six Realities. From anchors-first discipline, to clean naming conventions, to mechanical chunking only, to prosecutor-grade receipts, to reusable ritual patterns, to comprehensive governance?every reality enforces epistemic discipline."

---

### Shot 16: Next Steps & Resources
**Visual**: Show documentation index

**On Screen**:
- Quick Start Guide
- Operators Guide
- Common Workflows
- Troubleshooting Playbook
- Operator Onboarding (7 days)

**Voiceover**:
> "For new operators, start with the Quick Start guide for hands-on practice. Review the Operators Guide for daily workflows. Use the Troubleshooting Playbook as your reference. And follow our seven-day onboarding program for certification. Within one week, you'll be independently maintaining this production-ready system."

---

### Shot 17: Final Slide
**Visual**: Court sweep PASS screen

**Voiceover**:
> "Solobic Wrapper Ark: witness-first, audit-grade, antifragile. Version zero point one?production ready. Thank you for watching."

**On Screen**:
```
Court Sweep: S_20251229T061442Z_COURT_SWEEP
Verdict: PASS
All Realities: 100% COMPLETE

Documentation: docs/v0-release/
```

---

## Recording Notes

### Technical Setup
- **Screen Resolution**: 1920x1080
- **Recording Tool**: OBS Studio or similar
- **Audio**: Clear microphone, remove background noise
- **Terminal**: Dark theme, large font (16pt+)
- **Cursor**: Highlight cursor for visibility

### Pacing
- Speak slowly and clearly
- Pause 2-3 seconds after each terminal command
- Allow output to be readable before continuing
- Total runtime: 15-20 minutes (can trim in post)

### Post-Production
- Add chapter markers at each Part
- Include timestamps in video description
- Add captions/subtitles
- Export in multiple formats (MP4, WebM)

---

## Distribution

**Primary Locations**:
1. `docs/v0-release/` ? Link to video file or URL
2. README.md ? Embed video or link
3. YouTube/Vimeo (if public) ? Share link

**Accompanying Materials**:
- This script (for reference)
- COMMON_WORKFLOWS.md (follow-along guide)
- QUICK_START.md (hands-on exercises)

---

END OF VIDEO WALKTHROUGH SCRIPT
