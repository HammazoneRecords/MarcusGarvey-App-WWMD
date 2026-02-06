# TERMINAL_CANON.md

**Purpose**: Canonical terminal usage guide for the Solob Wrapper MW CLI tool.

**Last Updated**: 2025-12-28T00:59:31-05:00

---

## MW CLI Overview

The `mw` (Merkle Wrapper) CLI is the unified command-line interface for audit, lint, and court-sweep operations in the Solob Wrapper project.

**Design Principles:**
- **OBSERVE Mode Safe**: Never mutates source files
- **Evidence-Only Output**: All outputs go to `evidence/audits/` or `evidence/bundles/`
- **Four-Strike Roadblock**: After 4 consecutive failures, requests user input
- **OS-Agnostic**: Detects Windows/Linux/macOS and adapts paths

---

## Installation

The MW CLI is located at `tools/cli/mw.py` and requires:
- Python 3.8+ in `.venv/`
- PowerShell 7+ (for encoding/witness audits)
- Repository root with `ANTIFRAGILITY_CONTEXT.md`

**No installation needed** - run directly from repo root.

---

## Usage

### Basic Syntax

```bash
python tools/cli/mw.py <command> [subcommand]
```

### Available Commands

#### 1. State Management
```bash
python tools/cli/mw.py state
```
**What it does:**
- Prints current system state (OBSERVE/RECORD) and active Session ID (SID).

---

#### 2. Observe Mode (Seal)
```bash
python tools/cli/mw.py observe --note "Seal after work"
```
**What it does:**
- Transitions system to **OBSERVE** (read-only) mode.
- Enforces "YES_I_MEAN_IT" confirmation latch.
- Logs transition to `docs/STATE_HISTORY.md`.

---

#### 3. Record Mode (Open)
```bash
python tools/cli/mw.py record --note "Open RECORD window"
```
**What it does:**
- Transitions system to **RECORD** (write/execute) mode.
- Generates new Session ID (SID) if none exists (Format: `S_<UTC>_ARKV0`).
- Enforces "YES_I_MEAN_IT" confirmation latch.

---

#### 4. Run Recorded Script
```bash
python tools/cli/mw.py run --intent "Explain why" --script scripts/some_script.py -- --arg1 val
```
**What it does:**
- Wraps `scripts/run_recorded.py`.
- **Only allowed in RECORD mode.**
- Sets `SOLOB_RECORDED_RUN=1`.
- Logs execution to `logs/ops_ledger.jsonl`.

---

#### 5. Audit Encoding
```bash
python tools/cli/mw.py audit encoding
```

**What it does:**
- Runs `tools/encoding_report.ps1`
- Detects UTF-16, UTF-8 BOM, NUL bytes, high bytes
- Saves output to `evidence/audits/encoding_audit_latest.txt`

**Success Criteria:**
- Exit code 0
- Zero UTF-16 files
- Zero NUL byte files

---

#### 2. Audit Witness Epoch
```bash
python tools/cli/mw.py audit witness
```

**What it does:**
- Runs `tools/verify_witness_epoch.ps1`
- Checks `STATE_HISTORY.md` for SID compliance after 2025-12-25
- Validates legacy addendum for pre-epoch transitions
- Saves output to `evidence/audits/witness_audit_latest.txt`

**Success Criteria:**
- Exit code 0
- All post-epoch transitions have SID
- Legacy addendum covers pre-epoch transitions

---

#### 3. Lint Bundles
```bash
python tools/cli/mw.py lint bundles
```

**What it does:**
- Runs `tools/verify_witness_epoch.py` (Python, cross-platform)
- Validates witness epoch compliance for all state transitions
- Checks that post-epoch transitions have SID markers
- Saves output to `evidence/audits/bundle_lint_latest.txt`

**Success Criteria:**
- Exit code 0
- "[OK] zero violations" in stdout
- No SID violations detected

---

#### 4. Court Sweep
```bash
python tools/cli/mw.py court-sweep
```

**What it does:**
- Runs `scripts/preflight_balance_check.py`
- Comprehensive GO/NO-GO system health check:
  - Constitution integrity
  - Import stability
  - Database coherence
  - Receipt schema compliance
- Saves output to `evidence/audits/court_sweep_latest.txt`

**Success Criteria:**
- Exit code 0 = GO verdict
- Exit code 1 = NO-GO verdict

---

## Four-Strike Roadblock Protocol

If the MW CLI encounters 4 consecutive roadblocks (failures), it will:

1. **Stop execution** immediately
2. **Display roadblock history** (all 4 failures)
3. **Request user input** with a menu:
   - Paste full error output
   - Confirm repo root path
   - Confirm venv exists
   - Choose: retry / skip / manual-fix

**Roadblock Examples:**
- Script not found
- Venv Python not detected
- Repo root not located
- Script timeout (>5 minutes)
- Execution error

**Philosophy:** *"After 4 strikes, the AI must not guess state. Human input required."*

---

## Output Locations

All MW CLI outputs are written to:

```
evidence/
??? audits/
?   ??? encoding_audit_latest.txt
?   ??? witness_audit_latest.txt
?   ??? bundle_lint_latest.txt
?   ??? court_sweep_latest.txt
??? bundles/
    ??? (future bundle outputs)
```

**OBSERVE Mode Guarantee:**
- No source files modified
- No database mutations
- No state transitions
- Read-only operations only

---

## Troubleshooting

### "Could not locate repository root"
**Solution:** Run `mw.py` from within the repository directory structure. The script searches upward for `ANTIFRAGILITY_CONTEXT.md`.

### "Could not locate venv Python"
**Solution:** Ensure `.venv/` exists at repo root with Python installed:
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Unix
```

### "Script not found"
**Solution:** Verify the script exists at the expected path:
- `tools/encoding_report.ps1`
- `tools/verify_witness_epoch.ps1`
- `scripts/preflight_balance_check.py`

### "Four-strike roadblock limit reached"
**Solution:** Review the roadblock history and provide the requested user input. Do not retry without addressing the root cause.

---

## Integration with ACDOC

The MW CLI respects all ACDOC policies:

- **Canon Ladder**: Trusts execution logs > DB queries > STATE.json > docs
- **Sankofa Forward**: Never restores quarantined files
- **Verification First**: Defines proof artifacts before actions
- **Four-Strike Protocol**: Escalates to human after 4 consecutive failures

**Reference:** `docs/ANTIFRAGILITY_CONTEXT_ACDOC.md`

---

## Examples

### Daily Encoding Check
```bash
python tools/cli/mw.py audit encoding
cat evidence/audits/encoding_audit_latest.txt
```

### Pre-Commit Court Sweep
```bash
python tools/cli/mw.py court-sweep
# Check exit code
echo $?  # Unix
echo $LASTEXITCODE  # PowerShell
```

### Witness Epoch Verification
```bash
python tools/cli/mw.py audit witness
grep "GO" evidence/audits/witness_audit_latest.txt
```

---

**Philosophy**: *"One command, one purpose, one output location. No surprises."*
