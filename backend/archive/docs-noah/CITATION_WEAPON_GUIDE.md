# Citation Weapon - Complete Guide

## Overview

**TMS is now a citable legal archive.**

You can:
- Cite any page with prosecutor-grade precision
- Search for quotes and get automatic citations
- Extract page ranges
- Get exact character offsets for verification

---

## Quick Start

### Cite a Page
```bash
python scripts/cite_tms.py --page 15
```

**Output:**
```
======================================================================
CITATION
======================================================================

TMS, p. 15, chars 19234-20567

Locator: pdf:page:0015:chars:019234-020567
Page: 15
Char range: 19234-20567

======================================================================
EXCERPT
======================================================================

[Full page text displayed]
```

### Find a Quote
```bash
python scripts/cite_tms.py --quote "love"
```

**Output:**
```
======================================================================
FOUND 23 MATCHING CHUNK(S)
======================================================================

[1] TMS, p. 45, chars 58392-59821
    Locator: pdf:page:0045:chars:058392-059821
    Context: ...connection to the African continent, its rich...

[2] TMS, p. 127, chars 165432-166891
    Locator: pdf:page:0127:chars:165432-166891
    Context: ...We love to act like we can just "make up for...

[Shows all matches with context]
```

### Extract Page Range
```bash
python scripts/cite_tms.py --pages 10-15
```

**Output:**
```
======================================================================
EXTRACT: TMS, pp. 10-15
======================================================================

Total characters: 8,234
Total words (approx): 1,456

======================================================================
CONTENT
======================================================================

[Concatenated text from pages 10-15]
```

### Cite with Exact Character Range
```bash
python scripts/cite_tms.py --page 15 --chars 19234-20567
```

---

## Features

### 1. Page Sorting Fixed

**Problem:** Database `chunk_id` order ? page order  
**Solution:** All retrieval functions sort by page number parsed from locator

```python
from utils.chunk_retrieval import get_chunks_sorted_by_page

# ALWAYS returns chunks in page order (1, 2, 3...)
# Never random order (367, 346, 234...)
chunks = get_chunks_sorted_by_page("to_my_son_v1")
```

### 2. Multiple Search Methods

**By page:**
```python
from utils.chunk_retrieval import get_chunks_by_page
chunks = get_chunks_by_page("to_my_son_v1", page_num=15)
```

**By page + char range:**
```python
from utils.chunk_retrieval import get_chunk_by_page_and_chars
chunk = get_chunk_by_page_and_chars("to_my_son_v1", 15, 19234, 20567)
```

**By text search:**
```python
from utils.chunk_retrieval import search_chunks_by_text
chunks = search_chunks_by_text("to_my_son_v1", "love")
# Returns all matching chunks, sorted by page
```

**By page range:**
```python
from utils.chunk_retrieval import extract_page_range
text = extract_page_range("to_my_son_v1", start_page=10, end_page=15)
```

### 3. Citation Formatting

```python
from utils.citations import format_citation

# Prosecutor style (full precision)
format_citation("To My Son ? TMS", locator, style="prosecutor")
# "TMS, p. 15, chars 19234-20567"

# Academic style (page only)
format_citation("To My Son ? TMS", locator, style="academic")
# "TMS, 15"

# Minimal style
format_citation("To My Son ? TMS", locator, style="minimal")
# "TMS p.15"
```

---

## API Reference

### utils/chunk_retrieval.py

**`parse_page_from_locator(locator: str) -> int | None`**
- Extract page number from locator string
- Returns None if not parseable

**`get_chunks_by_page(anchor_id: str, page_num: int) -> List[dict]`**
- Get all chunks for a specific page
- Returns list of chunk dicts (chunk_id, anchor_locator, content)

**`get_chunks_sorted_by_page(anchor_id: str) -> List[dict]`**
- Get ALL chunks for anchor, sorted by page
- Critical for document reconstruction

**`get_chunk_by_page_and_chars(anchor_id, page_num, char_start?, char_end?) -> dict | None`**
- Get specific chunk by page and char range
- If no char range, returns first chunk on page

**`search_chunks_by_text(anchor_id: str, search_text: str) -> List[dict]`**
- Search for chunks containing text (case-insensitive)
- Returns matches sorted by page

**`extract_page_range(anchor_id: str, start_page: int, end_page: int) -> str`**
- Extract concatenated text from page range
- Returns text in page order

### scripts/cite_tms.py

**CLI Arguments:**
- `--page N` - Cite page N
- `--chars START-END` - Add char range to page citation
- `--quote "text"` - Search for quote and cite all matches
- `--pages START-END` - Extract page range

---

## Use Cases

### Legal Brief
```bash
# Cite evidence from TMS
python scripts/cite_tms.py --page 45 --quote "constitutional"

# Get exact citation for court filing
# "TMS, p. 45, chars 58392-59821"
```

### Research Paper
```bash
# Extract entire chapter
python scripts/cite_tms.py --pages 50-75

# Search for all mentions of concept
python scripts/cite_tms.py --quote "freedom"
```

### Fact Checking
```bash
# Verify quote exists and get context
python scripts/cite_tms.py --quote "exact quote from memory"

# Shows all matches with surrounding context
```

### Document Analysis
```python
from utils.chunk_retrieval import get_chunks_sorted_by_page

# Get entire document in order
chunks = get_chunks_sorted_by_page("to_my_son_v1")

# Analyze: word count, themes, structure
full_text = '\n'.join(c['content'] for c in chunks)
```

---

## Why This Matters

### Before
- Text pile (can't cite specific passages)
- No way to verify quotes
- Manual page counting
- No audit trail

### After
- **Legal archive** (prosecutor-grade citations)
- **Verifiable** (exact char offsets)
- **Automated** (CLI tool, API)
- **Traceable** (locator = citation = verification)

---

## Example Session

```bash
# 1. Find a quote
$ python scripts/cite_tms.py --quote "Ubuntu"

FOUND 3 MATCHING CHUNK(S)
[1] TMS, p. 127, chars 165432-166891
    Context: ...Ubuntu is our African philosophy...

# 2. Get full page for context
$ python scripts/cite_tms.py --page 127

CITATION: TMS, p. 127, chars 165432-166891
[Full page text...]

# 3. Extract surrounding pages
$ python scripts/cite_tms.py --pages 125-130

EXTRACT: TMS, pp. 125-130
Total characters: 12,456
[Full chapter text...]
```

---

## Integration with Query Logging (Future)

**Next step:** Add RUN records for provenance:

```python
# When citing, optionally log the query
def cite_with_logging(page: int):
    # Get citation
    chunk = get_chunks_by_page("to_my_son_v1", page)[0]
    
    # Log the query
    run_id = log_run(
        intent="CITE_TMS",
        query_params={"page": page}
    )
    
    # Log the citation
    log_run_citation(
        run_id=run_id,
        chunk_id=chunk['chunk_id'],
        citation_text=format_citation(...)
    )
    
    return chunk
```

**This creates:**
- Audit trail of what was cited when
- Provenance chain (query -> citation -> chunk)
- Reproducible research log

---

## Files Created

1. **`utils/chunk_retrieval.py`** - Retrieval helpers (page sorting)
2. **`scripts/cite_tms.py`** - Citation CLI weapon
3. **`utils/citations.py`** - Citation formatting (already created)

---

## Summary

**TMS is now:**
- [OK] Fully citable (prosecutor-grade)
- [OK] Searchable (by page, text, range)
- [OK] Verifiable (exact char offsets)
- [OK] Automated (CLI + API)
- [OK] Ordered (page sorting fixed)

**From text pile to legal archive in 3 files.**

**"Your library is now a citation weapon."** ???
