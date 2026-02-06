# Encoding Constitution (Repo Standard)

**Status:** Constitutional (Immutable)  
**Version:** 1.0  
**Effective:** 2025-12-27

---

## Core Standards

### All Code + Docs: UTF-8 without BOM

**Extensions:**
- `.py` `.js` `.ts` `.json` `.md` `.sql` `.html` `.css` `.yml` `.yaml` `.txt`

**Rule:** UTF-8 encoding, **no BOM** (Byte Order Mark)

### PowerShell Scripts: UTF-8 with BOM

**Extensions:**
- `.ps1`

**Rule:** UTF-8 encoding **with BOM** (for Windows PowerShell 5.1 compatibility)

**Reason:** PS 5.1 misreads UTF-8 without BOM as ANSI/cp1252

### Line Endings: LF (`\n`) Everywhere

**Rule:** Unix-style line endings (`\n`), never CRLF (`\r\n`)

**Exception:** None. Even on Windows, use LF.

---

## Immutable Zones (Never Normalize)

These directories/files must **never** be touched during encoding normalization:

- `evidence/**` - Receipts, bundles, chain proofs (sealed evidence)
- `data/checkpoints/**` - Database checkpoints (forensic integrity)
- `data/*.db` - SQLite databases (binary, untouchable)
- `**/*.pdf` - PDF files (binary, canonical sources)
- `.venv/**` - Virtual environment (external dependencies)
- `.vs/**` - IDE metadata (not canonical)
- Any binary files: `.dll`, `.exe`, `.pyd`, `.so`, `.lib`, `.png`, `.jpg`, `.webp`, `.zip`, etc.

**Philosophy:** Code can evolve. Evidence must not.

**Rule:** If evidence is corrupt, you don't "edit history"?you supersede it with a new receipt.

---

## Why This Keeps Happening

### Usual Culprits

1. **Windows PowerShell 5.1 Defaults**
   - `Out-File` without `-Encoding` -> UTF-16LE
   - `>` redirection -> UTF-16LE
   - `Set-Content` without `-Encoding` -> ANSI/UTF-16

2. **AI-Generated Scripts**
   - Often use `>` or `Out-File` without explicit encoding

3. **Copy/Paste from Chat**
   - Introduces invisible characters (zero-width spaces, smart quotes, em-dashes)

4. **Editor Misconfigurations**
   - VS Code auto-detecting encoding incorrectly
   - Different encoding per-file

### Hard Truth About `?` Characters

If a file already contains literal `?` where real characters used to be, that's **data loss**, not encoding mismatch.

**Cause:** Some tool decoded wrong and re-saved, replacing unknown bytes.

**Cannot fix:** Automation can't reconstruct original without backups or untouched source.

**Prevention:** Normalize **before** editing. Encoding repair is like sterilizing surgical tools?do it once, early, never freestyle.

---

## Prevention Rules

### Rule 1: Any Script That Writes Files Must Explicitly Set Encoding

**Bad:**
```powershell
$data | Out-File output.json  # [ERROR] Encoding undefined
```

**Good:**
```powershell
$data | Out-File output.json -Encoding utf8  # [OK] Explicit
```

**Better (for non-.ps1 files):**
```powershell
# Use helper function for UTF-8 no BOM
Write-TextUtf8NoBom -Path "output.json" -Text $data
```

### Rule 2: Use Helper Functions

**PowerShell:** Source `tools/encoding_defaults.ps1` at top of scripts

**Python:** Use explicit `encoding="utf-8"` in all `open()` and `Path.write_text()` calls

### Rule 3: Never Freestyle Text Transformations

**Pipeline mutations** (PowerShell piping + width wrapping) = silent mutation engine

**Prefer:** Python scripts for text transformation (single encoding reality)

---

## VS Code Settings (Stop the Bleed)

Create `.vscode/settings.json`:

```json
{
  "files.encoding": "utf8",
  "files.autoGuessEncoding": false,
  "files.eol": "\n",
  "files.insertFinalNewline": true,
  "files.trimTrailingWhitespace": true,
  "[powershell]": {
    "files.encoding": "utf8bom"
  }
}
```

**Result:**
- All files default to UTF-8 no BOM
- LF line endings
- PowerShell files get UTF-8 with BOM
- Trailing whitespace auto-trimmed

---

## PowerShell Encoding Helpers

**File:** `tools/encoding_defaults.ps1`

Dot-source this in any script that writes files:

```powershell
# At top of script
. "$PSScriptRoot/encoding_defaults.ps1"
```

**Provides:**
- `Write-TextUtf8NoBom` - For JSON/MD/txt/etc.
- `Write-Ps1Utf8Bom` - For `.ps1` files
- Default parameter values for `Out-File`, `Set-Content`, `Add-Content`

---

## Normalization Workflow (Git Without Git)

### Phase 0 ? Freeze (Receipt Mindset)

**Before any normalization:**

1. Run snapshot tools:
   ```bash
   python scripts/codebase_fingerprint.py
   python scripts/schema_fingerprint.py
   python scripts/invariants_fingerprint.py
   ```

2. Make local checkpoint (zip of mutable zones only)

### Phase 1 ? Diagnose (No Changes Yet)

Run encoding scan and produce report:

```powershell
# PowerShell version
powershell -ExecutionPolicy Bypass -File tools/normalize_repo_text.ps1 -Root . -WhatIf
```

```bash
# Python version
python scripts/normalize_encodings.py . --dry-run
```

**Review report** before proceeding.

### Phase 2 ? Normalize (Surgical Changes)

**Normalize only mutable zones:**

```powershell
# PowerShell
powershell -ExecutionPolicy Bypass -File tools/normalize_repo_text.ps1 -Root .
```

```bash
# Python
python scripts/normalize_encodings.py .
```

**Backups written to:** `data/orphans/encoding_backups/<timestamp>/`

### Phase 3 ? Prove (Balance Check Must Pass)

Verify system integrity:

```bash
python scripts/sanity_check.py
python scripts/preflight_balance_check.py
```

**If balance fails** after normalization, the failure is now **real logic**, not "file corruption ghosts".

---

## Normalization Tools

### PowerShell: `tools/normalize_repo_text.ps1`

**Features:**
- Skips immutable zones
- Detects BOM + UTF-16 via null bytes
- Converts to UTF-8 no BOM (UTF-8 BOM for `.ps1`)
- Normalizes line endings to LF
- Creates backups in `data/orphans/encoding_backups/`

**Usage:**
```powershell
# Dry run
powershell -ExecutionPolicy Bypass -File tools/normalize_repo_text.ps1 -Root . -WhatIf

# Real run
powershell -ExecutionPolicy Bypass -File tools/normalize_repo_text.ps1 -Root .
```

### Python: `scripts/normalize_encodings.py`

**Features:**
- Same logic as PowerShell version
- Works cross-platform
- Integrates with existing scripts ecosystem

**Usage:**
```bash
# Dry run
python scripts/normalize_encodings.py . --dry-run

# Real run
python scripts/normalize_encodings.py .
```

---

## Philosophy Summary

| Principle | Rule |
|-----------|------|
| **Code Reality** | UTF-8 no BOM + LF |
| **PowerShell Reality** | UTF-8 with BOM (PS 5.1 compat) |
| **Evidence Reality** | Immutable. Never normalize. |
| **Correction Reality** | Supersede, never edit. |
| **Prevention Reality** | Explicit encoding, always. |

---

## Internal = Court Transcripts (ASCII)
## External = Stage Performance (Unicode)

**Internal code** (scripts/, utils/, core/, tools/): ASCII-only  
**External content** (docs/, README, web UI): Unicode allowed  

Court can't accept "my terminal couldn't render it" as evidence.

---

**This encoding constitution is immutable.**  
**Changes require constitutional amendment (version bump).**

**END OF ENCODING CONSTITUTION V1.0**
