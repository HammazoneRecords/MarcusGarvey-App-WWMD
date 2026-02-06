# Solobic Wrapper Ark V0 ? Installation Guide

**Version**: 0.1.0  
**Last Updated**: 2025-12-29

---

## System Requirements

### Minimum Requirements
- **Operating System**: Windows 10+, Linux (Ubuntu 20.04+), macOS 11+
- **Python**: 3.9 or higher
- **RAM**: 2GB minimum, 4GB recommended
- **Disk Space**: 500MB for system + evidence bundles
- **Terminal**: PowerShell (Windows), Bash (Linux/Mac)

### Recommended Setup
- **IDE**: Visual Studio Code with Python extension
- **Terminal**: VSCode integrated terminal (UTF-8 pre-configured)
- **Python**: 3.10+ for best performance
- **SQLite**: 3.35+ (usually bundled with Python)

---

## Installation Steps

### Step 1: System is Already Installed [OK]

**Good news**: If you're reading this from the repository directory, Solobic Wrapper Ark is already installed and configured!

The system is located at:
```
c:\Users\Owner\Desktop\PROJECTS IN MOTION\ARK V0\solob wrapper ARK v0\solob-wrapper after abc real4plus
```

**Skip to**: [Step 6: Verify Installation](#step-6-verify-installation-mandatory)

---

### Step 2: Clone Repository (If Not Already Present)

If you need to set up on a different machine:

```bash
# Clone the repository (adjust path as needed)
git clone <repository-url> solob-wrapper
cd solob-wrapper
```

Or copy the entire directory to your target location.

---

### Step 3: Python Version Check

Verify Python version:

```bash
python --version
# or
python3 --version
```

**Expected**: `Python 3.9.0` or higher

**If Python not installed**:
- Windows: Download from [python.org](https://www.python.org/downloads/)
- Linux: `sudo apt-get install python3.10`
- Mac: `brew install python@3.10`

---

### Step 4: Virtual Environment (Optional but Recommended)

Create and activate a virtual environment:

**Windows PowerShell**:
```powershell
python -m venv .venv
.venv\Scripts\activate
```

**Linux/Mac Bash**:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

You should see `(.venv)` in your prompt.

---

### Step 5: Install Dependencies

**Core Dependencies** (if missing):

The system uses **Python standard library** primarily. Additional dependencies:

```bash
# Install any missing dependencies
pip install --upgrade pip

# If you need specific packages (check requirements.txt if exists)
# pip install -r requirements.txt
```

**Note**: Most scripts use only standard library (`sqlite3`, `json`, `pathlib`, `argparse`, etc.), so external dependencies are minimal.

---

### Step 6: Verify Installation (MANDATORY)

Run the court sweep to verify everything is working:

```bash
python tools/court_sweep.py
```

**Expected Output**:
```
[OK] Court sweep bundle: ...
[VERDICT] PASS
[REASON]  All checks passed
```

**If you see**:
- [OK] `PASS` ? Installation verified!
- [ERROR] `FAIL` or `NO-GO` ? See [Troubleshooting](#troubleshooting)

---

### Step 7: VSCode Configuration (Recommended)

If using VSCode, the repository includes `.vscode/settings.json`:

```json
{
  "files.encoding": "utf8",
  "python.defaultInterpreterPath": "${workspaceFolder}/.venv/Scripts/python.exe",
  "terminal.integrated.env.windows": {
    "PYTHONUTF8": "1",
    "PYTHONIOENCODING": "utf-8"
  }
}
```

**To activate**:
1. Open the repository folder in VSCode: `File > Open Folder`
2. Select the `.venv` Python interpreter when prompted
3. Open integrated terminal: `` Ctrl+` ``
4. Verify UTF-8 encoding is active

---

### Step 8: Environment Variables (Windows)

For consistent UTF-8 encoding across all terminals:

**PowerShell** (session-specific):
```powershell
$env:PYTHONUTF8="1"
$env:PYTHONIOENCODING="utf-8"
```

**PowerShell** (permanent):
```powershell
[System.Environment]::SetEnvironmentVariable('PYTHONUTF8', '1', 'User')
[System.Environment]::SetEnvironmentVariable('PYTHONIOENCODING', 'utf-8', 'User')
```

**Command Prompt**:
```cmd
setx PYTHONUTF8 1
setx PYTHONIOENCODING utf-8
```

**Linux/Mac** (add to `.bashrc` or `.zshrc`):
```bash
export PYTHONUTF8=1
export PYTHONIOENCODING=utf-8
```

---

## Post-Installation Checks

### Check 1: Database Exists

```bash
# Check if database exists
ls data/memory.db

# Query database
python -c "import sqlite3; conn = sqlite3.connect('data/memory.db'); print('Anchors:', conn.execute('SELECT COUNT(*) FROM anchors').fetchone()[0]); print('Chunks:', conn.execute('SELECT COUNT(*) FROM chunks').fetchone()[0])"
```

**Expected**:
```
Anchors: 31
Chunks: 3446
```

---

### Check 2: State Files Exist

```bash
ls docs/STATE.json
ls docs/STATE_HISTORY.md
```

Both files should exist.

---

### Check 3: Evidence Bundles Exist

```bash
ls evidence/bundles/
```

You should see multiple `S_*_COURT_SWEEP` directories.

---

### Check 4: Scripts are Executable

```bash
python tools/cli/mw.py state
python scripts/log_state_transition.py --help
python tools/verify_witness_epoch.py
```

All should execute without import errors.

---

## Optional: SQLite Browser (GUI)

For visual database exploration:

**DB Browser for SQLite** (recommended):
- Windows/Mac/Linux: Download from [sqlitebrowser.org](https://sqlitebrowser.org/)

**Usage**:
1. Open DB Browser
2. File > Open Database
3. Select `data/memory.db`
4. Browse `anchors` and `chunks` tables

---

## File System Layout Verification

Your installation should have this structure:

```
solob-wrapper/
??? config/
?   ??? rituals/               [OK] Ritual configs exist
?   ??? schemas/               [OK] JSON schemas exist
??? core/
?   ??? chain_constitution.py  [OK] Constitutional functions
??? data/
?   ??? memory.db              [OK] Database (500MB+)
??? docs/
?   ??? STATE.json             [OK] Current state
?   ??? STATE_HISTORY.md       [OK] Transition log
?   ??? ... (documentation)
??? evidence/
?   ??? bundles/               [OK] 40+ evidence bundles
?   ??? audits/                [OK] Audit reports
??? modules/                   [OK] Ritual engine modules
??? scripts/                   [OK] Ingestion scripts
??? tools/                     [OK] Audit tools
?   ??? cli/
?       ??? mw.py              [OK] Unified CLI
??? CHANGELOG.MD               [OK] Change history
```

---

## Troubleshooting

### Problem: "ModuleNotFoundError: No module named '...'"

**Solution 1**: Activate virtual environment (if using):
```bash
# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate
```

**Solution 2**: Install missing package:
```bash
pip install <package-name>
```

---

### Problem: "sqlite3.OperationalError: no such table"

**Solution**: Database file is corrupted or incomplete.

**Recovery**:
1. Check if `data/memory.db` exists and is >1MB
2. If corrupt, restore from backup (if available)
3. Contact system administrator for recovery assistance

---

### Problem: "UnicodeEncodeError" in terminal

**Solution**: UTF-8 not configured.

**Windows PowerShell**:
```powershell
$env:PYTHONUTF8="1"
$env:PYTHONIOENCODING="utf-8"
```

**Or**: Use VSCode integrated terminal (UTF-8 pre-configured).

---

### Problem: "Court sweep FAIL"

**Diagnosis**: Check the specific failed check:

```bash
cat evidence/bundles/<LATEST_COURT_SWEEP>/REPORT.md
```

Look for `[FAIL]` markers.

**Common Causes**:
- **db_counts FAIL**: Database corruption
- **receipt_validation FAIL**: Invalid receipt schema
- **orphan_chunks FAIL**: Chunks missing `import_session_id`
- **bundle_layout FAIL**: Legacy V1 bundles (should be 0 in V0)

**Contact**: System administrator if unable to resolve.

---

### Problem: "Permission denied" errors

**Solution**: 

**Windows**: Run terminal as Administrator  
**Linux/Mac**: Check file permissions:
```bash
chmod +x tools/cli/mw.py
chmod +x scripts/*.py
chmod +x tools/*.py
```

---

## Next Steps

After successful installation:

1. **Quick Start**: See [QUICK_START.md](QUICK_START.md) for 5-minute tutorial
2. **Architecture**: Review [V0_ARCHITECTURE.md](V0_ARCHITECTURE.md) to understand the system
3. **Operations**: Read [OPERATORS_GUIDE.md](OPERATORS_GUIDE.md) for daily workflows

---

## Uninstallation (If Needed)

To remove Solobic Wrapper Ark:

1. **Backup Evidence** (if needed):
   ```bash
   # Copy evidence bundles to backup location
   cp -r evidence/ /path/to/backup/
   ```

2. **Deactivate Virtual Environment** (if using):
   ```bash
   deactivate
   ```

3. **Delete Directory**:
   ```bash
   # Windows
   Remove-Item -Recurse -Force "solob-wrapper"
   
   # Linux/Mac
   rm -rf solob-wrapper
   ```

4. **Remove Environment Variables** (if set):
   ```powershell
   # Windows PowerShell
   [System.Environment]::SetEnvironmentVariable('PYTHONUTF8', '', 'User')
   [System.Environment]::SetEnvironmentVariable('PYTHONIOENCODING', '', 'User')
   ```

---

## Support

For installation issues:

1. Check [TROUBLESHOOTING](#troubleshooting) section above
2. Review [QUICK_START.md](QUICK_START.md) for verification steps
3. Run `python tools/court_sweep.py` for diagnostic report

---

**Installation Complete!** [OK]

Proceed to [QUICK_START.md](QUICK_START.md) to begin using Solobic Wrapper Ark V0.

---

END OF INSTALLATION GUIDE
