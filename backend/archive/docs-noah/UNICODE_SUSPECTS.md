# Unicode Suspects - Encoding Issues Inventory

**Generated:** 2025-12-27 13:38 EST
**Last Updated:** 2025-12-27 13:52 EST
**Status:** ENCODING RECOVERY PIVOT COMPLETE - Manual Repairs Pending
**Source:** Encoding scan of internal code directories (scripts/, utils/, core/, tools/)

**CRITICAL UPDATE:**
Automated encoding fix approach abandoned due to self-referential issues.
Encoding automation scripts orphaned to: `data/orphans/2025-12-27_encoding-recovery-pivot/`
See `docs/MANUAL_ENCODING_REPAIR.md` for manual repair workflow.

---

## Summary

**Files Scanned:** 75
**Files Flagged:** 8
**Total Non-ASCII Bytes:** 304

---

## Flagged Files

### 1. `scripts/_clean_unicode.py`
**Non-ASCII Bytes:** 180
**Severity:** [WARN] HIGH (ironic - the cleanup tool itself)

**Issue:**
This file contains the actual Unicode characters it's designed to replace (smart quotes, em-dashes, emojis, box-drawing characters) in its character mapping dictionaries.

**Affected Scripts:**
- Any script that imports or calls `_clean_unicode.py` for Unicode normalization

**Resolution:**
- **EXEMPT** - This is intentional. The file needs to contain Unicode characters in its mapping tables.
- Should be excluded from ASCII-only enforcement.
- Consider adding a comment: `# EXEMPT: Contains Unicode mappings by design`

---

### 2. `scripts/test_constitution_tripwire.py`
**Non-ASCII Bytes:** 54
**Severity:** ? CRITICAL

**Issue:**
Contains emoji characters ([OK], [ERROR]) in print statements used for status reporting.

**Affected Scripts:**
- Any script that runs `test_constitution_tripwire.py` as part of validation
- Potentially affects CI/CD pipelines if emojis can't render

**Example Lines:**
```python
print("[OK] Identity lock: All wrappers are constitutional")
print("[ERROR] TRIPWIRE TRIGGERED")
```

**Resolution:**
- Replace `[OK]` with `[OK]`
- Replace `[ERROR]` with `[FAIL]`
- Already documented in Phase 2 of encoding cleanup plan

---

### 3. `scripts/encoding_report.py`
**Non-ASCII Bytes:** 42
**Severity:** ? MEDIUM-HIGH

**Issue:**
Contains Unicode characters in docstrings or comments, possibly mojibake sequences.

**Affected Scripts:**
- `scripts/test_no_unicode_internal.py` (relies on this for diagnostics)
- Any workflow that uses encoding_report.py for scanning

**Resolution:**
- Review and replace with ASCII equivalents
- May contain em-dashes (?) or smart quotes in documentation

---

### 4. `scripts/SCRIPT-LEVEL INVARIANTS.md`
**Non-ASCII Bytes:** 12
**Severity:** ? LOW

**Issue:**
Markdown documentation file with Unicode characters (likely em-dashes, bullets, or smart quotes).

**Affected Scripts:**
- None directly (documentation only)

**Resolution:**
- Replace Unicode punctuation with ASCII equivalents
- Low priority - doesn't affect script execution

---

### 5. `scripts/artisan_emit_anchors_map_ascii.py`
**Non-ASCII Bytes:** 4
**Severity:** ? MEDIUM

**Issue:**
Small number of non-ASCII bytes. This file was previously repaired from ghost question marks.

**Affected Scripts:**
- Anchor generation workflows
- Any script that uses artisan-generated anchor maps

**Resolution:**
- Verify the 4 bytes aren't mojibake remnants
- May need complete re-check after previous ghost question mark repair

---

### 6. `utils/ingest_flow_check.py`
**Non-ASCII Bytes:** 6
**Severity:** ? LOW-MEDIUM

**Issue:**
Utility script with minimal non-ASCII content.

**Affected Scripts:**
- Ingestion workflows
- Any script that validates ingestion flow

**Resolution:**
- Review and replace with ASCII
- Likely safe to batch-fix with `_clean_unicode.py`

---

### 7. `scripts/normalize_encodings.py`
**Non-ASCII Bytes:** 3
**Severity:** ? LOW

**Issue:**
The normalization script itself has minimal non-ASCII bytes (possibly in comments).

**Affected Scripts:**
- Main encoding normalization workflow

**Resolution:**
- Quick fix - likely just 1-2 characters in docstrings
- Low priority

---

### 8. `scripts/test_no_unicode_internal.py`
**Non-ASCII Bytes:** 3
**Severity:** ? LOW

**Issue:**
ASCII enforcement gate has minimal non-ASCII content.

**Affected Scripts:**
- Validation gate for all internal code

**Resolution:**
- Quick fix - likely docstring or comment characters
- Should be fixed to "eat own dog food"

---

## Impact Analysis

### Critical Path Scripts (Must Fix)

1. **`test_constitution_tripwire.py`** - Blocks validation workflows
2. **`encoding_report.py`** - Can't reliably report if it has issues itself

### Safe to Defer

1. **`_clean_unicode.py`** - Intentionally contains Unicode (exempt)
2. **`SCRIPT-LEVEL INVARIANTS.md`** - Documentation only

### Quick Wins (Low Effort)

1. **`normalize_encodings.py`** - 3 bytes (likely docstring)
2. **`test_no_unicode_internal.py`** - 3 bytes (likely comment)
3. **`ingest_flow_check.py`** - 6 bytes

---

## Recommended Fix Order

### Phase 1: Critical (Do First)
1. Fix `test_constitution_tripwire.py` - Replace [OK]/[ERROR] with [OK]/[FAIL]
2. Fix `encoding_report.py` - Ensure diagnostic tools are clean

### Phase 2: Foundation (Next)
3. Fix `test_no_unicode_internal.py` - 3 bytes
4. Fix `normalize_encodings.py` - 3 bytes

### Phase 3: Validation (Then)
5. Re-check `artisan_emit_anchors_map_ascii.py` - Verify no mojibake remnants
6. Fix `ingest_flow_check.py` - 6 bytes

### Phase 4: Cleanup (Last)
7. Fix `SCRIPT-LEVEL INVARIANTS.md` - Documentation polish
8. **EXEMPT** `_clean_unicode.py` - Add exemption comment

---

## Exemption Policy

**Files that MUST contain Unicode:**

- `scripts/_clean_unicode.py` - Contains character mapping tables
- Any file with `# EXEMPT: Unicode by design` comment

**Exemption Format:**
```python
# EXEMPT: Unicode by design - contains character mappings for normalization
UNICODE_MAP = {
    "?": "-",  # Em-dash
    """: '"',  # Smart quote
    ...
}
```

---

## Verification Command

After fixes, verify with:

```bash
python scripts/test_no_unicode_internal.py
```

Expected result: **0 violations** (except exempted files)

---

**END OF UNICODE SUSPECTS REPORT**
