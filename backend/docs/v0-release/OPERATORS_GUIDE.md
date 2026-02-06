# Solobic Wrapper Ark V0 ? Operators Guide

**Version**: 0.1.0  
**Target Audience**: System operators and maintainers

---

## Philosophy & Principles

### Core Tenets
1. **Witness-first**: Every operation tracked with session IDs (SIDs)
2. **Fail fast and loud**: No silent failures
3. **Evidence-based**: Receipts prove every change
4. **Read-only by default**: OBSERVE is the safe state
5. **State discipline**: Explicit transitions required

### STGRAIL (State Transition Gaurdrail) Framework
- **S**tate discipline
- **T**imestamps
- **G**overnanc
- **R**eceipts
- **A**uditability  
- **I**ntegrity
- **L**edger

---

## Daily Operations

### 1. Check System Health

**Morning Routine** (5 minutes):

```bash
# 1. Check current state
python tools/cli/mw.py state

# 2. Run court sweep
python tools/court_sweep.py

# 3. Review latest bundle
cat evidence/bundles/<LATEST_COURT_SWEEP>/REPORT.md
```

**Expected**: All checks PASS, state is OBSERVE.

---

### 2. State Management

**Rule**: Always return to OBSERVE after completing work.

#### Transition to RECORD (for write operations)

```bash
python scripts/log_state_transition.py \
  --from OBSERVE \
  --to RECORD \
  --reason "Starting lexicon ingestion batch"
```

Confirm the SID is logged in `docs/STATE_HISTORY.md`.

#### Transition back to OBSERVE (safe state)

```bash
python scripts/log_state_transition.py \
  --from RECORD \
  --to OBSERVE \
  --reason "Ingestion complete. Verified with court sweep."
```

**Verification**:
```bash
cat docs/STATE_HISTORY.md | tail -2
```

---

### 3. Running a Ritual

**Example**: Ingest new lexicon block

```bash
# 1. Ensure RECORD state
python tools/cli/mw.py state  # Should show RECORD

# 2. Validate config first (dry-run)
python tools/cli/mw.py ritual validate --config config/rituals/lexicon_new.json

# 3. Execute ritual
python tools/cli/mw.py ritual run --config config/rituals/lexicon_new.json

# 4. Verify receipt generated
ls evidence/bundles/S_<LATEST_SID>/RECEIPTS/

# 5. Run court sweep
python tools/court_sweep.py

# 6. Return to OBSERVE
python scripts/log_state_transition.py --from RECORD --to OBSERVE --reason "Ritual complete"
```

---

### 4. Evidence Review

**Daily Evidence Check**:

```bash
# Count recent bundles (last 7 days)
Get-ChildItem evidence/bundles/ | Where-Object { $_.LastWriteTime -gt (Get-Date).AddDays(-7) }

# View latest receipt
cat evidence/bundles/S_<LATEST>/RECEIPTS/RECEIPT_*.json

# Check for orphans
sqlite3 data/memory.db "SELECT COUNT(*) FROM chunks WHERE import_session_id IS NULL;"
# Expected: 0
```

---

## Advanced Operations

### Creating a New Ritual

**Steps**:

1. **Create config file** (`config/rituals/my_ritual.json`):
```json
{
  "ritual_name": "Custom Ingestion",
  "module_type": "json",
  "source_path": "data/source.json",
  "anchor_id": "MY_ANCHOR",
  "config": {}
}
```

2. **Validate schema**:
```bash
python tools/cli/mw.py ritual validate --config config/rituals/my_ritual.json
```

3. **Test with dry-run** (no database mutations)

4. **Execute in RECORD state**

5. **Verify with court sweep**

---

### Custom Module Development

See `modules/base_module.py` for the abstract interface.

**Required methods**:
- `validate_config(config)` ? Validate ritual config
- `execute(dry_run=False)` ? Run ingestion
- `generate_receipt()` ? Create V2 receipt

**Example**: `modules/json_ingestion.py`

---

### Interpreting Court Sweep Results

**Reading the verdict**:
- **PASS**: All checks green, system healthy
- **PASS (WARN)**: Some warnings, investigate details
- **NO-GO**: Critical failures, system needs attention

**Common failure patterns**:

| Check | Failure | Fix |
|-------|---------|-----|
| db_counts | Database corrupt | Restore from backup |
| receipt_validation | Invalid schema | Re-generate receipts |
| orphan_chunks | Missing SIDs | Re-run with SID tracking |
| bundle_layout | V1 bundles | Run bundle migration script |

---

## Maintenance Procedures

### Weekly Maintenance

**Checklist**:

1. [OK] Run court sweep
2. [OK] Review state history for anomalies
3. [OK] Check disk space (`evidence/` directory)
4. [OK] Verify no orphan chunks
5. [OK] Audit receipt validity (should be 100%)
6. [OK] Review CHANGELOG for significant changes

### Monthly Maintenance

**Additional Tasks**:

1. [OK] Run encoding audit
2. [OK] Verify script state registry (SHA256 checks)
3. [OK] Review evidence bundle storage (archive old bundles?)
4. [OK] Database vacuum (optional, if performance degrades):
   ```bash
   sqlite3 data/memory.db "VACUUM;"
   ```

---

## Emergency Procedures

### Recovery from FAIL Court Sweep

**Procedure**:

1. **Read the failure report**:
   ```bash
   cat evidence/bundles/<LATEST_COURT_SWEEP>/REPORT.md
   ```

2. **Identify failed check** (look for `[FAIL]`)

3. **Review check details** in report JSON

4. **Apply fix** (see troubleshooting table above)

5. **Re-run court sweep** to verify fix

6. **Document in HURDLES.md** for future reference

---

### Database Backup & Restore

**Backup** (weekly recommended):
```bash
# Create timestamped backup
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
Copy-Item data/memory.db "backups/memory_db_$timestamp.db"
```

**Restore**:
```bash
# Restore from backup
Copy-Item backups/memory_db_<TIMESTAMP>.db data/memory.db
```

**Verify**:
```bash
python tools/court_sweep.py
```

---

### Evidence-Based Recovery

If database is lost but evidence bundles exist:

1. **Collect all receipts**:
   ```bash
   Get-ChildItem -Recurse evidence/bundles/*/RECEIPTS/*.json
   ```

2. **Replay ingestion operations** using receipt metadata

3. **Verify with court sweep**

---

## Best Practices

### DO [OK]

- Always transition back to OBSERVE after work
- Run court sweep after significant changes
- Use ritual engine for repeatable ingestion
- Generate V2 receipts for all operations
- Document state transitions with clear reasons
- Use dry-run mode to test rituals
- Review evidence bundles regularly

### DON'T [ERROR]

- Never skip court sweep after major changes
- Never manually edit `data/memory.db`
- Never delete receipts or evidence bundles
- Never ignore WARN or FAIL verdicts
- Never run ingestion in OBSERVE state
- Never modify FROZEN scripts
- Never ignore orphan chunks

---

## Troubleshooting

### "Court sweep shows orphan chunks"

**Cause**: Chunks ingested without `import_session_id`

**Fix**:
1. Identify orphan chunks:
   ```sql
   SELECT chunk_id, anchor_id FROM chunks WHERE import_session_id IS NULL;
   ```

2. Determine correct SID from evidence bundles

3. Update chunks (in REPAIR state):
   ```sql
   UPDATE chunks SET import_session_id = 'S_CORRECT_SID' WHERE import_session_id IS NULL;
   ```

4. Run court sweep to verify

---

### "Receipt validation fails"

**Cause**: Receipt doesn't conform to V2 schema

**Fix**:
1. View specific receipt:
   ```bash
   cat <RECEIPT_PATH>
   ```

2. Compare against `docs/RECEIPT_SCHEMA_V2.md`

3. Regenerate receipt if possible, or quarantine for review

---

### "State transition fails"

**Cause**: STATE.json locked or corrupted

**Fix**:
1. Check file exists and is valid JSON:
   ```bash
   cat docs/STATE.json
   ```

2. Manually fix if corrupted (use backup if available)

3. Retry transition

---

## Command Cheat Sheet

| Task | Command |
|------|---------|
| Check state | `python tools/cli/mw.py state` |
| Transition to RECORD | `python scripts/log_state_transition.py --from OBSERVE --to RECORD --reason "..."` |
| Transition to OBSERVE | `python scripts/log_state_transition.py --from RECORD --to OBSERVE --reason "..."` |
| Run court sweep | `python tools/court_sweep.py` |
| Validate ritual | `python tools/cli/mw.py ritual validate --config <path>` |
| Run ritual | `python tools/cli/mw.py ritual run --config <path>` |
| Verify witness epoch | `python tools/verify_witness_epoch.py` |
| Check for orphans | `sqlite3 data/memory.db "SELECT COUNT(*) FROM chunks WHERE import_session_id IS NULL;"` |
| Validate receipt | `python scripts/validate_receipt_v2.py <path>` |
| Add CHANGELOG entry | `python scripts/log_changelog.py --summary "..." --type MAJOR --files "..." --why "..."` |

---

## Further Reading

- **Architecture**: [V0_ARCHITECTURE.md](V0_ARCHITECTURE.md)
- **Features**: [FEATURES_V0.md](FEATURES_V0.md)
- **Evidence**: [EVIDENCE_V0.md](EVIDENCE_V0.md)
- **Quick Start**: [QUICK_START.md](QUICK_START.md)

---

**Remember**: State discipline is the foundation of system integrity. Always return to OBSERVE.

---

END OF OPERATORS GUIDE
