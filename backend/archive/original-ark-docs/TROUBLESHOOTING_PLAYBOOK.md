# Troubleshooting Playbook ? Solobic Wrapper Ark

**Quick Reference**: Problem -> Diagnosis -> Solution

---

## Court Sweep Failures

### Problem: db_counts FAIL

**Symptoms**:
- Court sweep reports database count mismatch
- Expected vs actual counts don't match

**Diagnosis**:
```bash
sqlite3 data/memory.db "SELECT COUNT(*) FROM anchors;"
sqlite3 data/memory.db "SELECT COUNT(*) FROM chunks;"
sqlite3 data/memory.db "PRAGMA integrity_check;"
```

**Solutions**:
1. If integrity check fails -> Database corrupted, restore from backup
2. If counts unexpected -> Review recent ingestion receipts
3. If orphan chunks -> Run orphan detection (see below)

---

### Problem: receipt_validation FAIL

**Symptoms**:
- Court sweep shows invalid receipts
- Receipt doesn't conform to V2 schema

**Diagnosis**:
```bash
# Find invalid receipt path in court sweep INDEX.json
cat evidence/bundles/<LATEST_COURT_SWEEP>/INDEX.json | grep "invalid"

# Validate manually
python scripts/validate_receipt_v2.py <receipt_path>
```

**Solutions**:
1. Compare receipt against `docs/RECEIPT_SCHEMA_V2.md`
2. Check for required fields: `receipt_id`, `session_id`, `strict_rules`, `db_state`
3. If legacy format -> Regenerate using current scripts
4. If corrupted -> Quarantine and investigate origin

---

### Problem: orphan_chunks FAIL

**Symptoms**:
- Court sweep shows chunks without `import_session_id`
- Chain of custody broken

**Diagnosis**:
```bash
sqlite3 data/memory.db "SELECT chunk_id, anchor_id FROM chunks WHERE import_session_id IS NULL;"
```

**Solutions**:
1. **Identify orphan source**:
   - Check chunk_id pattern to determine origin
   - Review timestamp of chunk creation

2. **Find correct SID**:
   - Search evidence bundles for matching anchor/timestamp
   - Review receipts for ingestion batch

3. **Fix (in REPAIR state)**:
   ```sql
   UPDATE chunks 
   SET import_session_id = 'S_CORRECT_SID' 
   WHERE import_session_id IS NULL AND anchor_id = 'SPECIFIC_ANCHOR';
   ```

4. **Verify fix**:
   ```bash
   python tools/court_sweep.py
   ```

---

### Problem: bundle_layout FAIL

**Symptoms**:
- V1 legacy bundles detected
- Missing INDEX.json or REPORT.md

**Diagnosis**:
```bash
# Find V1 bundles
ls evidence/bundles/*/BATCH_RECEIPT.json

# Check missing files
find evidence/bundles/ -type d -name "S_*" ! -exec test -f {}/INDEX.json  \; -print
```

**Solutions**:
1. Run bundle migration:
   ```bash
   python scripts/prosecutor_upgrade_bundles_v2.py
   ```

2. Manually upgrade if needed:
   - Create INDEX.json with `bundle_version: "V2"`
   - Create REPORT.md summary
   - Move BATCH_RECEIPT.json to RECEIPTS/

3. Verify:
   ```bash
   python tools/court_sweep.py
   ```

---

## Ingestion Errors

### Problem: Chunk Collision

**Error Message**: `"chunk_collision": "STOP"`

**Cause**: Attempting to insert chunk with existing chunk_id

**Solutions**:
1. **Check if duplicate ingestion**:
   ```bash
   sqlite3 data/memory.db "SELECT * FROM chunks WHERE chunk_id = '<COLLIDING_ID>';"
   ```

2. **If legitimate duplicate** -> Update chunk_id pattern in ritual config

3. **If error** -> Remove duplicate from source file

4. **Never override**: System prevents chunk collision by design

---

### Problem: Missing Anchor

**Error Message**: `"missing_anchor": "STOP"`

**Cause**: Ritual references anchor_id not in database

**Solutions**:
1. **Verify anchor exists**:
   ```bash
   sqlite3 data/memory.db "SELECT * FROM anchors WHERE anchor_id = '<ANCHOR_ID>';"
   ```

2. **If missing** -> Register anchor first:
   ```bash
   # Add to anchor registry, then:
   python scripts/register_anchors_from_registry.py
   ```

3. **Retry ritual** after anchor registration

---

### Problem: Manifest SHA Mismatch

**Error Message**: `"manifest_sha_mismatch": "STOP"`

**Cause**: Source file modified after manifest generation

**Solutions**:
1. **Verify source integrity**:
   ```bash
   sha256sum <source_file>
   # Compare against manifest
   ```

2. **If source changed** -> Regenerate manifest

3. **If corruption** -> Restore source from backup

4. **Never proceed with mismatched SHA**: Data integrity paramount

---

## State Management Issues

### Problem: Transition Fails

**Error Message**: State transition rejected

**Solutions**:
1. **Check current state**:
   ```bash
   cat docs/STATE.json
   ```

2. **Verify transition path**:
   - OBSERVE -> RECORD (valid)
   - RECORD -> OBSERVE (valid)
   - OBSERVE -> EXECUTE (valid)
   - EXECUTE -> OBSERVE (valid)
   - Invalid transitions will fail

3. **If STATE.json corrupted**:
   - Restore from backup
   - Manually fix JSON (ensure valid format)

---

### Problem: SID Mismatch

**Symptoms**:
- Receipt shows different SID than state history
- Transition logged with wrong SID

**Solutions**:
1. **Review state history**:
   ```bash
   cat docs/STATE_HISTORY.md | tail -10
   ```

2. **Check active SID**:
   ```bash
   python tools/cli/mw.py state
   ```

3. **If mismatch** -> Investigate:
   - Manual edits to STATE.json?
   - Transition not properly logged?
   - Multiple operators editing simultaneously?

4. **Fix**: Document discrepancy in HURDLES.md for audit trail

---

### Problem: Witness Violations

**Error**: `verify_witness_epoch.py` reports violations

**Solutions**:
1. **Identify violations**:
   ```bash
   python tools/verify_witness_epoch.py
   ```

2. **Review state history** for post-epoch transitions missing SID

3. **Add missing SID**:
   - Determine correct SID from context
   - Edit STATE_HISTORY.md (append-only, mark as correction)

4. **Verify fix**:
   ```bash
   python tools/verify_witness_epoch.py
   # Expected: Exit code 0
   ```

---

## System Errors

### Problem: UnicodeEncodeError

**Error**:
```
UnicodeEncodeError: 'charmap' codec can't encode character
```

**Solutions**:
1. **Set UTF-8 encoding**:
   ```powershell
   # PowerShell
   $env:PYTHONUTF8="1"
   $env:PYTHONIOENCODING="utf-8"
   ```

2. **Use VSCode integrated terminal** (UTF-8 pre-configured)

3. **Permanent fix**:
   - Set environment variables system-wide
   - Update `.vscode/settings.json`

---

### Problem: Database Locked

**Error**: `sqlite3.OperationalError: database is locked`

**Solutions**:
1. **Check for concurrent access**:
   - Only one script should write at a time
   - Close DB Browser or other tools

2. **Wait and retry** (lock usually temporary)

3. **If persistent**:
   ```bash
   # Check for stale lock
   ls data/*.db-shm
   ls data/*.db-wal
   
   # Remove if stale (ONLY if no processes running)
   rm data/memory.db-shm
   rm data/memory.db-wal
   ```

---

### Problem: Permission Denied

**Error**: `PermissionError: [Errno 13]`

**Solutions**:
1. **Windows**: Run terminal as Administrator

2. **Linux/Mac**: Check file permissions:
   ```bash
   ls -l <file>
   chmod +x <script>  # If executable needed
   ```

3. **VSCode**: Ensure workspace trusted

---

## Performance Issues

### Problem: Slow Queries

**Symptoms**:
- Database queries take >5 seconds
- Court sweep slow

**Solutions**:
1. **Check database size**:
   ```bash
   ls -lh data/memory.db
   ```

2. **Analyze query performance**:
   ```sql
   EXPLAIN QUERY PLAN SELECT * FROM chunks WHERE anchor_id = 'LEXICON_A';
   ```

3. **Optimize** (if >10MB):
   ```bash
   sqlite3 data/memory.db "VACUUM;"
   sqlite3 data/memory.db "ANALYZE;"
   ```

---

### Problem: Large Evidence Bundles

**Symptoms**:
- evidence/bundles/ directory >5GB
- Disk space warnings

**Solutions**:
1. **Archive old bundles**:
   ```bash
   # Create archive directory
   mkdir -p archive/evidence-packs/2025-Q4
   
   # Move old bundles (older than 90 days)
   # (Manual selection recommended)
   ```

2. **Compress archives**:
   ```bash
   tar -czf archive/evidence-packs/2025-Q4.tar.gz archive/evidence-packs/2025-Q4/
   ```

3. **Keep recent** (last 30 days) in active directory

---

### Problem: Disk Space Low

**Symptoms**:
- Warnings about disk space
- Write operations failing

**Solutions**:
1. **Check usage**:
   ```bash
   # Windows
   Get-PSDrive C | Select-Object Used,Free
   
   # Linux/Mac
   df -h
   ```

2. **Identify large files**:
   ```bash
   du -sh evidence/bundles/* | sort -hr | head -20
   ```

3. **Clean up**:
   - Archive old evidence bundles
   - Remove temporary files
   - Vacuum database

---

## Quick Diagnostic Commands

```bash
# System health overview
python tools/court_sweep.py

# Database integrity
sqlite3 data/memory.db "PRAGMA integrity_check;"

# Orphan check
sqlite3 data/memory.db "SELECT COUNT(*) FROM chunks WHERE import_session_id IS NULL;"

# Receipt validation
python scripts/validate_receipt_v2.py evidence/bundles/*/RECEIPTS/*.json

# Witness epoch compliance
python tools/verify_witness_epoch.py

# State verification
python tools/cli/mw.py state
cat docs/STATE_HISTORY.md | tail -5

# Disk usage
du -sh evidence/bundles/
```

---

**Remember**: When in doubt, run court sweep. It's the single source of truth for system health.

---

END OF TROUBLESHOOTING PLAYBOOK
