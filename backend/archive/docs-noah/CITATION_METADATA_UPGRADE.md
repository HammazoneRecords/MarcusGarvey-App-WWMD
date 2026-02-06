# Citation Metadata Upgrade - Complete [OK]

## What Changed

**Upgraded `chunk_tms_pages_pilot.py` with citation metadata.**

---

## New Locator Format

**Before:**
```
pdf:page:0015
```

**After (Prosecutor-grade):**
```
pdf:page:0015:chars:003200-004567
```

**Structure:**
- `pdf`: Format identifier
- `page:0015`: 1-indexed page number (padded to 4 digits)
- `chars:003200-004567`: 0-indexed character offsets in concatenated document

---

## Changes Made

### 1. Added `_mk_locator()` Helper
```python
def _mk_locator(page_num: int, start_char: int, end_char: int) -> str:
    """Citation-friendly locator format."""
    return f"pdf:page:{page_num:04d}:chars:{start_char:06d}-{end_char:06d}"
```

### 2. Enhanced `extract_pdf_pages()`
Now returns: `List[tuple[int, str, int, int]]`
- `page_num`: 1-indexed page number
- `content`: Page text
- `start_char`: Starting character offset
- `end_char`: Ending character offset

**Added features:**
- Running character cursor across document
- Double newline separator between pages (`\n\n`)
- Offsets account for separators

### 3. Updated Main Loop
```python
for page_num, content, start_char, end_char in pages:
    # ...
    locator = _mk_locator(page_num, start_char, end_char)
```

### 4. Created Citation Utilities
**File:** `utils/citations.py`

**Functions:**
- `parse_pdf_locator(locator)` - Parse locator into components
- `format_citation(title, locator, style)` - Format for display
- `extract_text_span(locator, full_text)` - Extract precise text span

---

## Usage Examples

### Parse Citation
```python
from utils.citations import parse_pdf_locator

locator = "pdf:page:0015:chars:003200-004567"
citation = parse_pdf_locator(locator)
# {
#     'format': 'pdf',
#     'page': 15,
#     'char_start': 3200,
#     'char_end': 4567
# }
```

### Format Citation
```python
from utils.citations import format_citation

# Prosecutor style (full precision)
format_citation("To My Son ? TMS", locator, style="prosecutor")
# "TMS, p. 15, chars 3200-4567"

# Academic style (page only)
format_citation("To My Son ? TMS", locator, style="academic")
# "TMS, 15"

# Minimal style
format_citation("To My Son ? TMS", locator, style="minimal")
# "TMS p.15"
```

### Extract Text Span
```python
from utils.citations import extract_text_span

span = extract_text_span(locator, full_document_text, context_chars=50)
# "...context before [PRECISE EXCERPT] context after..."
```

---

## Database Impact

**Schema:** [OK] NO CHANGES  
**Migration:** [OK] NOT NEEDED  
**Backward compatible:** [OK] YES (can still parse old "pdf:page:NNNN")

**Storage location:** Existing `chunks.anchor_locator` TEXT column

---

## Citation Quality

### Before (Basic)
```
"See TMS page 15"
```
- [ERROR] No way to verify exact text
- [ERROR] Can't link to specific paragraph
- [ERROR] Ambiguous if page renumbered

### After (Prosecutor-grade)
```
"TMS, p. 15, chars 3200-4567"
```
- [OK] Exact character range specified
- [OK] Can extract precise text programmatically
- [OK] Stable across OCR re-runs (based on emitted corpus)
- [OK] Can validate citation matches chunk content

---

## Why This Matters

**"From a pile of text to a library":**

1. **Queryability:** Can find all chunks on page 15
2. **Precision:** Can extract exact quoted text
3. **Verification:** Can validate citations match source
4. **Traceability:** Character offsets create audit trail
5. **Future-proof:** No schema migration needed later

**Decision point:** Doing this BEFORE ingestion means we never have to re-chunk for metadata.

---

## Ingestion Impact

**Next ingestion creates locators like:**
```
pdf:page:0001:chars:000000-003421
pdf:page:0002:chars:003421-006901
pdf:page:0003:chars:006901-010234
...
```

**Each chunk gets:**
- Page number (for human reference)
- Character offsets (for machine precision)
- Ready for Prosecutor citations

---

## Script Status

[OK] **Updated:** `scripts/chunk_tms_pages_pilot.py`  
[OK] **Created:** `utils/citations.py`  
[OK] **Tested:** Compiles successfully  
[OK] **Ready:** For TMS ingestion  

**No schema changes. No migrations. Just better metadata.**

**"Migrations are where discipline dies. Locators are where citations live."**
