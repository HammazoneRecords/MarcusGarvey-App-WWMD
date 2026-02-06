# Manual Encoding Repair Guide

**Status:** Active
**Date:** 2025-12-27

---

## Files Requiring Manual Repair

### [OK] COMPLETED
1. **scripts/test_constitution_tripwire.py**
   - Fixed: Replaced emojis ([OK] -> [OK], [ERROR] -> [FAIL])
   - Status: ASCII-only [OK]

### ? QUARANTINED (Do Not Repair - Reconstruct Instead)
1. **scripts/artisan_emit_anchors_map_ascii.py**
   - Location: `data/orphans/2025-12-27_encoding-recovery-pivot/quarantined_files/`
   - Issue: Ghost question marks (`?f?r?o?m?`) - critically corrupted
   - Action: Reconstruct from scratch or restore from backup

### ? PENDING MANUAL REPAIR
1. **utils/ingest_flow_check.py**
   - Non-ASCII bytes: 6
   - Likely issue: Unicode arrows in type hints (`->`)

2. **scripts/SCRIPT-LEVEL INVARIANTS.md**
   - Non-ASCII bytes: 12
   - Likely issue: Unicode punctuation (em-dashes, smart quotes)

---

## Manual Repair Workflow (VS Code)

### Step 1: Open File in VS Code
```
File -> Open -> [select corrupted file]
```

### Step 2: Check Current Encoding
Look at bottom-right corner of VS Code window for current encoding.

### Step 3: Reopen with Correct Encoding (if needed)
```
1. Click encoding indicator (bottom-right)
2. Select "Reopen with Encoding"
3. Try: UTF-8, UTF-16 LE, Windows-1252 (in that order)
4. Find encoding that shows readable text
```

### Step 4: Fix Character Corruption
Manually replace corrupted characters:

**Common Replacements:**
- `?` (em-dash) -> `-` (ASCII hyphen)
- `?` (en-dash) -> `-` (ASCII hyphen)
- `"` `"` (smart quotes) -> `"` (straight quotes)
- `'` `'` (smart quotes) -> `'` (straight apostrophe)
- `->` (Unicode arrow) -> `->` (ASCII arrow)
- `?` (replacement char) -> delete or replace with ASCII
- `???` (ghost chars) -> if extensive, quarantine file instead

**For Python type hints specifically:**
- Find: `def foo() -> str:`
- Replace: `def foo() -> str:`

### Step 5: Save with Correct Encoding
```
1. File -> Save with Encoding
2. Select: UTF-8 (DO NOT select UTF-8 with BOM)
3. Save
```

### Step 6: Verify File Parses
**For Python files:**
```powershell
python -m py_compile [filename].py
```

**For Markdown files:**
```
# Just open and visually verify
```

### Step 7: Test Functionality
If file contains critical code, run affected scripts to ensure they work.

---

## Prevention (Already in Place)

[OK] **VS Code Settings** (`.vscode/settings.json`):
- All files default to UTF-8 without BOM
- PowerShell files use UTF-8 with BOM
- LF line endings enforced

[OK] **Documentation** (`docs/ENCODING_CONSTITUTION.md`):
- Standards documented
- Prevention rules established

---

## When to Quarantine vs. Repair

**Repair if:**
- Only a few characters affected (< 20 chars)
- Corruption pattern is simple and repetitive
- You can confidently identify what characters should be

**Quarantine if:**
- Extensive corruption (e.g., every line has `?` characters)
- Unknown what original text should be
- File is too critical to risk guessing wrong

**Quarantine location:**
```
data/orphans/2025-12-27_encoding-recovery-pivot/quarantined_files/
```

---

## After All Repairs Complete

Run validation:
```powershell
python scripts/sanity_check.py
```

Expected: System should compile/run without encoding-related errors.

---

**Manual repairs are safer than automation when dealing with encoding corruption.**

**END OF MANUAL REPAIR GUIDE**
