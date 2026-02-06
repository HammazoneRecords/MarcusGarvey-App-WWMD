# Solobic Wrapper Ark V0 ? Quick Start Guide

**Version**: 0.1.0  
**Estimated Time**: 10 minutes

---

## Prerequisites

Before you begin, ensure you have:

- [OK] **Python 3.9+** installed
- [OK] **Git** (optional, for cloning)
- [OK] **VSCode** (recommended) or any text editor
- [OK] **Windows PowerShell** or **Bash** terminal
- [OK] **~500MB** disk space (for database + evidence bundles)

---

## 5-Minute Quickstart

### Step 1: Verify Installation (2 minutes)

Navigate to the Solobic Wrapper Ark directory:

```bash
cd "c:\Users\Owner\Desktop\PROJECTS IN MOTION\ARK V0\solob wrapper ARK v0\solob-wrapper after abc real4plus"
```

Verify the system is healthy:

```bash
python tools/court_sweep.py
```

**Expected Output**:
```
[OK] Court sweep bundle: ...
[VERDICT] PASS
[REASON]  All checks passed
```

[OK] If you see `PASS`, the system is ready!

---

### Step 2: Check System State (1 minute)

View the current system state:

```bash
python tools/cli/mw.py state
```

**Expected Output**:
```
Current state: OBSERVE
Active SID: S_20251225T075155Z_STATE_RECORD
```

The default state is `OBSERVE` (read-only safe mode).

---

### Step 3: Explore the Database (2 minutes)

Check what's in the system:

```powershell
# On Windows PowerShell:
sqlite3 data/memory.db "SELECT COUNT(*) FROM anchors;"
sqlite3 data/memory.db "SELECT COUNT(*) FROM chunks;"

# On Linux/Mac:
sqlite3 data/memory.db "SELECT COUNT(*) FROM anchors;"
sqlite3 data/memory.db "SELECT COUNT(*) FROM chunks;"
```

**Expected Output**:
```
31    (anchors)
3446  (chunks)
```

---

###Step 4: View a Sample Ritual Config (2 minutes)

Explore the ritual engine configs:

```bash
# List available ritual configs
dir config\rituals\*.json

# View a sample config
cat config/rituals/lexicon_a_template.json
```

**Sample Config**:
```json
{
  "ritual_name": "Lexicon A Ingestion",
  "module_type": "lexicon",
  "source_path": "data/lexicon/lexicon_a.json",
  "anchor_id": "LEXICON_A",
  "config": {
    "derive_row_index": true
  }
}
```

---

### Step 5: Review Evidence Bundles (3 minutes)

Check the latest court sweep bundle:

```bash
# Find the latest COURT_SWEEP bundle
dir evidence\bundles\*COURT_SWEEP* | Sort-Object LastWriteTime -Descending | Select-Object -First 1

# View the report
cat "evidence\bundles\S_20251229T053816Z_COURT_SWEEP\REPORT.md"
```

You should see the **PASS** verdict and all 8 checks green!

---

## Common Workflows

### Workflow 1: Run Court Sweep

Audit the entire system:

```bash
python tools/court_sweep.py
```

This creates an evidence bundle in `evidence/bundles/S_<TIMESTAMP>_COURT_SWEEP/`.

**8 Checks**:
1. db_counts
2. state_history_witness
3. evidence_index
4. bundle_uniformity
5. encoding_reports_present
6. receipt_validation
7. orphan_chunks
8. bundle_layout

---

### Workflow 2: State Transitions

**Transition to RECORD** (for write operations):

```bash
python scripts/log_state_transition.py --from OBSERVE --to RECORD --reason "Starting new ingestion session"
```

**Transition back to OBSERVE** (return to safe state):

```bash
python scripts/log_state_transition.py --from RECORD --to OBSERVE --reason "Completed ingestion session"
```

**Check state history**:

```bash
cat docs/STATE_HISTORY.md
```

---

### Workflow 3: View Receipts

List all receipts:

```bash
dir evidence\bundles\*\RECEIPTS\*.json
```

View a specific receipt:

```bash
cat "evidence\bundles\S_20251225T075155Z_STATE_RECORD\RECEIPTS\RECEIPT_CHUNKS_book_of_solobility_v1_PDF_PAGES_PILOT.json"
```

**Receipt shows**:
- Operation type
- Session ID (SID)
- Before/after database counts
- Strict rules enforced
- SHA256 integrity hashes

---

### Workflow 4: Validate a Receipt

```bash
python scripts/validate_receipt_v2.py "evidence\bundles\S_20251225T075155Z_STATE_RECORD\RECEIPTS\RECEIPT_CHUNKS_book_of_solobility_v1_PDF_PAGES_PILOT.json"
```

**Expected**: Exit code 0 (valid)

---

### Workflow 5: Check Witness Epoch Compliance

```bash
python tools/verify_witness_epoch.py
```

**Expected Output**:
```
PASS: No witness violations found
Epoch: 2025-12-25T07:51:59Z
```

---

## Troubleshooting Quick Reference

### Problem: "Court sweep shows FAIL"

**Solution**: Read the specific check that failed in the REPORT.md:

```bash
cat evidence\bundles\<LATEST_COURT_SWEEP>\REPORT.md
```

Look for `[FAIL]` markers and review the details.

---

### Problem: "Command not found: python"

**Solution**: Try `python3` instead:

```bash
python3 tools/court_sweep.py
```

Or activate your virtual environment (if using one):

```bash
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac
```

---

### Problem: "SQLite not installed"

**Install SQLite**:

**Windows**: Download from [sqlite.org](https://www.sqlite.org/download.html)  
**Linux**: `sudo apt-get install sqlite3`  
**Mac**: `brew install sqlite`

---

### Problem: "Encoding errors in terminal"

**Solution**: Set UTF-8 encoding:

```powershell
# PowerShell
$env:PYTHONUTF8="1"
$env:PYTHONIOENCODING="utf-8"
```

```bash
# Bash
export PYTHONUTF8=1
export PYTHONIOENCODING=utf-8
```

Or use the **VSCode integrated terminal** (UTF-8 enforced).

---

## Next Steps

Now that you're familiar with the basics:

1. **Deep Dive**: Read [V0_ARCHITECTURE.md](V0_ARCHITECTURE.md) to understand the 6 Realities
2. **Operations Manual**: See [OPERATORS_GUIDE.md](OPERATORS_GUIDE.md) for advanced workflows
3. **Features**: Explore [FEATURES_V0.md](FEATURES_V0.md) for complete capabilities
4. **Installation**: For detailed setup, see [INSTALLATION.md](INSTALLATION.md)

---

## Quick Command Reference

| Task | Command |
|------|---------|
| Check state | `python tools/cli/mw.py state` |
| Court sweep | `python tools/court_sweep.py` |
| Transition to RECORD | `python scripts/log_state_transition.py --from OBSERVE --to RECORD --reason "..."` |
| Transition to OBSERVE | `python scripts/log_state_transition.py --from RECORD --to OBSERVE --reason "..."` |
| Verify witness epoch | `python tools/verify_witness_epoch.py` |
| Validate receipt | `python scripts/validate_receipt_v2.py <path>` |
| List ritual configs | `dir config\rituals\*.json` |
| View state history | `cat docs/STATE_HISTORY.md` |

---

## System Status Reference

| State | Meaning | Operations Allowed |
|-------|---------|-------------------|
| **OBSERVE** | Read-only, safe default | Audits, queries, reports |
| **RECORD** | Write mode with SID tracking | Ingestion, modifications |
| **EXECUTE** | One-off operations | Ad-hoc scripts |
| **REPAIR** | Fix-forward mode | Recovery operations |

**Rule**: Always return to `OBSERVE` after completing work.

---

## Help & Support

- **Documentation**: `docs/` directory
- **Evidence**: `evidence/bundles/` directory
- **CHANGELOG**: [CHANGELOG.MD](../CHANGELOG.MD)
- **State History**: [docs/STATE_HISTORY.md](STATE_HISTORY.md)

---

**Congratulations!** You're now ready to use Solobic Wrapper Ark V0.

For advanced operations, proceed to the [OPERATORS_GUIDE.md](OPERATORS_GUIDE.md).

---

END OF QUICK START GUIDE
