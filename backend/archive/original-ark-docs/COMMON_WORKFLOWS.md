# Common Workflows ? Solobic Wrapper Ark

**Version**: 1.0  
**Target**: System Operators

---

## Workflow 1: Daily Health Check (Morning Routine)

**Duration**: 5 minutes  
**Frequency**: Daily  
**State**: OBSERVE (read-only)

### Steps

1. **Check current state**
   ```bash
   python tools/cli/mw.py state
   ```
   **Expected**: `Current state: OBSERVE`

2. **Run court sweep**
   ```bash
   python tools/court_sweep.py
   ```
   **Expected**: `[VERDICT] PASS`

3. **Review latest report**
   ```bash
   # Find latest bundle
   ls evidence/bundles/ | grep COURT_SWEEP | sort | tail -1
   
   # View report
   cat evidence/bundles/S_<LATEST>_COURT_SWEEP/REPORT.md
   ```
   **Expected**: All 8 checks show `[PASS]`

4. **Check for orphans**
   ```bash
   sqlite3 data/memory.db "SELECT COUNT(*) FROM chunks WHERE import_session_id IS NULL;"
   ```
   **Expected**: `0`

**If any check fails**: See Workflow 8 (Investigating Failures)

---

## Workflow 2: Ingesting New Content (End-to-End)

**Duration**: 15-30 minutes  
**Frequency**: As needed  
**State**: RECORD -> OBSERVE

### Prerequisites
- Content source file ready (JSON, PDF, etc.)
- Anchor registered in database
- Ritual config created (or use existing template)

### Steps

1. **Transition to RECORD state**
   ```bash
   python scripts/log_state_transition.py \
     --from OBSERVE \
     --to RECORD \
     --reason "Ingesting new lexicon block Q"
   ```

2. **Verify state transition**
   ```bash
   python tools/cli/mw.py state
   # Should show: Current state: RECORD
   # Note the SID for later
   ```

3. **Validate ritual config (dry-run)**
   ```bash
   python tools/cli/mw.py ritual validate --config config/rituals/lexicon_q.json
   ```
   **Expected**: `[OK] Ritual config is valid`

4. **Execute ritual**
   ```bash
   python tools/cli/mw.py ritual run --config config/rituals/lexicon_q.json
   ```
   **Monitor output for errors**

5. **Verify receipt generated**
   ```bash
   # Find latest bundle with current SID
   ls evidence/bundles/S_<CURRENT_SID>*/RECEIPTS/
   
   # View receipt
   cat evidence/bundles/S_<CURRENT_SID>*/RECEIPTS/RECEIPT_*.json
   ```

6. **Run court sweep**
   ```bash
   python tools/court_sweep.py
   ```
   **Expected**: `[VERDICT] PASS`

7. **Return to OBSERVE**
   ```bash
   python scripts/log_state_transition.py \
     --from RECORD \
     --to OBSERVE \
     --reason "Lexicon Q ingestion complete. Court sweep PASS."
   ```

**Final verification**: Check `docs/STATE_HISTORY.md` for both transitions

---

## Workflow 3: Creating a Custom Ritual

**Duration**: 10-20 minutes  
**State**: OBSERVE (config creation is read-only)

### Steps

1. **Choose a template**
   ```bash
   ls config/rituals/*_template.json
   ```

2. **Copy and customize**
   ```bash
   cp config/rituals/lexicon_a_template.json config/rituals/custom_source.json
   ```

3. **Edit config** (example for JSON ingestion):
   ```json
   {
     "ritual_name": "Custom Data Ingestion",
     "module_type": "json",
     "source_path": "data/custom/source.json",
     "anchor_id": "CUSTOM_ANCHOR",
     "config": {
       "chunk_id_template": "CUSTOM|{index}",
       "derive_row_index": true
     }
   }
   ```

4. **Validate config**
   ```bash
   python tools/cli/mw.py ritual validate --config config/rituals/custom_source.json
   ```

5. **Test with dry-run** (no database changes)
   ```bash
   python scripts/ritual_engine.py --config config/rituals/custom_source.json --dry-run
   ```

6. **Review dry-run output** for expected chunks

7. **Execute for real** (see Workflow 2)

---

## Workflow 4: Investigating Court Sweep Failures

**Duration**: 10-30 minutes  
**State**: OBSERVE

### Steps

1. **Read the failure report**
   ```bash
   cat evidence/bundles/<LATEST_COURT_SWEEP>/REPORT.md
   ```

2. **Identify failed check** (look for `[FAIL]` or `[WARN]`)

3. **Review check details**
   ```bash
   cat evidence/bundles/<LATEST_COURT_SWEEP>/INDEX.json | grep -A 10 "<failed_check>"
   ```

4. **Common failures and fixes**:

   **db_counts FAIL**:
   - Check database file exists: `ls -lh data/memory.db`
   - Verify not corrupted: `sqlite3 data/memory.db "PRAGMA integrity_check;"`
   - Compare expected vs actual counts

   **receipt_validation FAIL**:
   - Find invalid receipt: Check `INDEX.json` -> `invalid` array
   - Validate manually: `python scripts/validate_receipt_v2.py <path>`
   - Review receipt against schema: `docs/RECEIPT_SCHEMA_V2.md`

   **orphan_chunks FAIL**:
   - Query orphans: `sqlite3 data/memory.db "SELECT chunk_id FROM chunks WHERE import_session_id IS NULL;"`
   - Trace origin using chunk_id pattern
   - Determine correct SID from evidence bundles

   **bundle_layout FAIL**:
   - Check for V1 bundles: `ls evidence/bundles/*/BATCH_RECEIPT.json`
   - Run migration: `python scripts/prosecutor_upgrade_bundles_v2.py`

5. **Apply fix** based on issue

6. **Re-run court sweep**
   ```bash
   python tools/court_sweep.py
   ```

7. **Document in HURDLES.md** if novel issue

---

## Workflow 5: Receipt Forensics (Tracing Chunk Origin)

**Duration**: 5-10 minutes  
**State**: OBSERVE

### Use Case
Find out when/how a specific chunk was ingested.

### Steps

1. **Find chunk in database**
   ```bash
   sqlite3 data/memory.db "SELECT * FROM chunks WHERE chunk_id = 'SOLOB|V2|CHUNK|LEXICON|A|001';"
   ```
   **Note the `import_session_id`**

2. **Find evidence bundle with that SID**
   ```bash
   ls evidence/bundles/ | grep <SID>
   ```

3. **Review bundle receipts**
   ```bash
   ls evidence/bundles/S_<SID>*/RECEIPTS/
   ```

4. **Read relevant receipt**
   ```bash
   cat evidence/bundles/S_<SID>*/RECEIPTS/RECEIPT_CHUNKS_*.json
   ```

5. **Verify integrity**
   ```bash
   python scripts/validate_receipt_v2.py evidence/bundles/S_<SID>*/RECEIPTS/RECEIPT_*.json
   ```

**Result**: Full chain of custody for the chunk

---

## Workflow 6: Backup and Restore

**Duration**: 5 minutes (backup), 10 minutes (restore)  
**State**: OBSERVE

### Backup

```bash
# Create timestamped backup
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
New-Item -ItemType Directory -Path "backups" -Force
Copy-Item data/memory.db "backups/memory_db_$timestamp.db"
Copy-Item docs/STATE.json "backups/STATE_$timestamp.json"
Copy-Item docs/STATE_HISTORY.md "backups/STATE_HISTORY_$timestamp.md"

# Verify backup
ls backups/*$timestamp*
```

### Restore

```bash
# CAUTION: This overwrites current database!
# Choose backup to restore
ls backups/ | sort

# Restore database
Copy-Item backups/memory_db_<TIMESTAMP>.db data/memory.db -Force

# Restore state files
Copy-Item backups/STATE_<TIMESTAMP>.json docs/STATE.json -Force
Copy-Item backups/STATE_HISTORY_<TIMESTAMP>.md docs/STATE_HISTORY.md -Force

# Verify restoration
python tools/court_sweep.py
```

---

## Workflow 7: Weekly Maintenance

**Duration**: 15 minutes  
**Frequency**: Weekly  
**State**: OBSERVE

### Checklist

- [ ] Run court sweep
- [ ] Review state history for anomalies
- [ ] Check disk space in `evidence/` directory
- [ ] Verify no orphan chunks
- [ ] Audit receipt validity (should be 100%)
- [ ] Review recent CHANGELOG entries
- [ ] Backup database

### Commands

```bash
# Court sweep
python tools/court_sweep.py

# Orphan check
sqlite3 data/memory.db "SELECT COUNT(*) FROM chunks WHERE import_session_id IS NULL;"

# Disk space (Windows)
Get-ChildItem evidence\ -Recurse | Measure-Object -Property Length -Sum

# Receipt validation
python scripts/validate_receipt_v2.py evidence/bundles/*/RECEIPTS/*.json

# Backup
# (See Workflow 6)
```

---

## Workflow 8: Emergency Database Recovery

**Duration**: 30-60 minutes  
**State**: REPAIR

### When to Use
- Database corrupted
- Critical data loss
- Integrity check fails

### Steps

1. **Assess damage**
   ```bash
   sqlite3 data/memory.db "PRAGMA integrity_check;"
   ```

2. **If repairable**:
   ```bash
   # Try to repair
   sqlite3 data/memory.db ".recover" > recovered.sql
   sqlite3 recovered.db < recovered.sql
   
   # Verify
   python tools/court_sweep.py --db recovered.db
   
   # If PASS, replace
   mv data/memory.db data/memory.db.corrupt
   mv recovered.db data/memory.db
   ```

3. **If not repairable, restore from backup**:
   ```bash
   # List backups
   ls backups/ | sort
   
  # Restore (see Workflow 6)
   ```

4. **If no backup, reconstruct from receipts**:
   ```bash
   # This is advanced - requires replaying all ingestion operations
   # from receipts. See OPERATORS_GUIDE.md "Evidence-Based Recovery"
   ```

5. **Final verification**
   ```bash
   python tools/court_sweep.py
   ```

---

## Workflow 9: Monthly Audit

**Duration**: 30 minutes  
**Frequency**: Monthly  
**State**: OBSERVE

### Steps

1. **Run encoding audit**
   ```bash
   python tools/encoding_audit.py
   ```
   **Expected**: 0 suspicious files

2. **Verify script state registry**
   ```bash
   python tools/script_state_check.py
   ```
   **Expected**: No drift detected

3. **Review court sweep trend** (check last 4 sweeps)
   ```bash
   ls evidence/bundles/*COURT_SWEEP* | sort | tail -4
   # Manually review each REPORT.md
   ```

4. **Check evidence bundle storage**
   ```bash
   # Count bundles
   ls evidence/bundles/ | wc -l
   
   # Consider archiving old bundles if >100
   ```

5. **Database optimization** (optional)
   ```bash
   sqlite3 data/memory.db "VACUUM;"
   sqlite3 data/memory.db "ANALYZE;"
   ```

6. **Update documentation** if needed

---

## Workflow 10: Handoff to New Operator

**Duration**: 1 week  
**State**: OBSERVE initially

### Week Overview

**Day 1**: Orientation
- New operator reads all V0 release documentation
- Install and verify system (court sweep PASS)
- Shadow current operator for daily health check

**Day 2-3**: Supervised Operations
- New operator performs daily health check alone
- Reviews evidence bundles
- Practices state transitions (dry-run)

**Day 4-5**: Guided Operations
- New operator executes test ritual (supervised)
- Handles simulated court sweep failure
- Reviews receipts and forensics

**Day 6**: Independent Trial
- New operator runs full end-to-end workflow independently
- Current operator observes but doesn't intervene

**Day 7**: Certification
- New operator demonstrates competency:
  - Daily health check
  - Ritual execution
  - Troubleshooting
  - Emergency procedures
- Handoff complete

### Handoff Checklist

- [ ] All documentation reviewed
- [ ] Court sweep execution demonstrated
- [ ] Ritual execution successful
- [ ] Troubleshooting demonstrated
- [ ] Emergency procedures understood
- [ ] Backup/restore practiced
- [ ] Independent operation validated

---

## Quick Reference Card

| Task | Command |
|------|---------|
| Check state | `python tools/cli/mw.py state` |
| Court sweep | `python tools/court_sweep.py` |
| To RECORD | `python scripts/log_state_transition.py --from OBSERVE --to RECORD --reason "..."` |
| To OBSERVE | `python scripts/log_state_transition.py --from RECORD --to OBSERVE --reason "..."` |
| Validate ritual | `python tools/cli/mw.py ritual validate --config <path>` |
| Run ritual | `python tools/cli/mw.py ritual run --config <path>` |
| Check orphans | `sqlite3 data/memory.db "SELECT COUNT(*) FROM chunks WHERE import_session_id IS NULL;"` |
| Backup DB | `Copy-Item data/memory.db backups/memory_db_$(Get-Date -Format yyyyMMdd_HHmmss).db` |

---

**Solobic Wrapper Ark** ? Production-ready workflows for confident operation

---

END OF COMMON WORKFLOWS
