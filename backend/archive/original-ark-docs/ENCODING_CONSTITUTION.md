# ENCODING_CONSTITUTION.md

**Purpose**: Canonical encoding standards for the Solob Wrapper project to prevent corruption and ensure reproducibility.

**Last Updated**: 2025-12-28T00:54:48-05:00

---

## Encoding Standards

### File Encoding
- **All text files**: UTF-8 without BOM
- **Line endings**: LF (Unix-style) preferred, CRLF (Windows) acceptable
- **No exceptions**: Python, PowerShell, Markdown, JSON, SQL, all text formats

### Enforcement Mechanisms

#### VSCode Settings
The `.vscode/settings.json` file enforces:
```json
{
  "files.encoding": "utf8",
  "files.autoGuessEncoding": false,
  "files.eol": "\n"
}
```

#### Python Environment
All Python scripts run with UTF-8 mode enabled via environment variables:
```
PYTHONUTF8=1
PYTHONIOENCODING=utf-8
```

These are automatically set in the VSCode integrated terminal.

---

## Terminal Execution Requirement

**CRITICAL**: All wrapper commands MUST be executed from the VSCode integrated terminal.

**Why**:
- The integrated terminal automatically sets `PYTHONUTF8=1` and `PYTHONIOENCODING=utf-8`
- This prevents encoding corruption during script execution
- External terminals (cmd.exe, standalone PowerShell) may use different encodings

**Verification**:
To verify your terminal has correct encoding:
```powershell
# PowerShell
$env:PYTHONUTF8
$env:PYTHONIOENCODING
```

Both should return `1` and `utf-8` respectively.

---

## Forbidden Patterns

### Never Use
- UTF-16 LE/BE encoding
- UTF-8 with BOM (Byte Order Mark)
- Windows-1252 or other legacy encodings
- Mixed encodings within the same file

### Ghost Character Pattern (Corruption Indicator)
If you see this pattern, the file is corrupted:
```
?i?m?p?o?r?t? ?o?s?
```

This indicates UTF-16/UTF-8 binary-level mismatch. **Do not attempt automated repair**. Use manual file-by-file inspection per `docs/MANUAL_ENCODING_REPAIR.md`.

---

## File Creation Checklist

Before creating any new file:
- [ ] Confirm VSCode is using UTF-8 (check status bar)
- [ ] Verify `.vscode/settings.json` is present
- [ ] Use integrated terminal for any script execution
- [ ] Check file encoding after save: `file <filename>` should show `UTF-8 Unicode text`

---

## Repair Protocol

If encoding corruption is detected:

1. **DO NOT** run automated batch fixes
2. **DO** follow `docs/MANUAL_ENCODING_REPAIR.md`
3. **DO** quarantine corrupted files to `data/orphans/`
4. **DO** recreate functionality cleanly (Sankofa Forward Policy)

---

## References

- `.vscode/settings.json` - VSCode encoding enforcement
- `docs/MANUAL_ENCODING_REPAIR.md` - Manual repair workflow
- `docs/QUARANTINE_TOMBSTONES.md` - Quarantined file ledger
- `tools/encoding_report.ps1` - Non-destructive encoding audit

---

**Philosophy**: *"Prevention > Cure. Manual > Automated when dealing with corruption."*
