# Citation Metadata Strategy (No Schema Change Needed)

## Current Situation

**Schema has NO metadata column:**
```sql
anchor_locator TEXT NOT NULL,  -- Only field for location info
```

**Current script stores:**
```python
locator = f"pdf:page:{page_num:04d}"  # e.g., "pdf:page:0015"
```

---

## Problem

For Prosecutor-grade citations, we need:
1. **Page number** (for "TMS, p. 15")
2. **Character offsets** (for precise spans)
3. **Section/paragraph** (optional structure)

But we can't query by page number easily from a TEXT field.

---

## Solutions (in Order of Preference)

### Option 1: Enhanced anchor_locator (NO schema change)

**Use structured format that's still parseable:**

```python
# Current (basic):
locator = "pdf:page:0015"

# Enhanced (citation-ready):
locator = "pdf:page:0015:chars:0-1234"
# Format: pdf:page:{page}:chars:{start}-{end}
```

**Pros:**
- [OK] No schema migration needed
- [OK] Backward compatible (can still parse old "pdf:page:NNNN")
- [OK] Can extract page number with: `int(locator.split(':')[2])`
- [OK] Can extract char range with: `locator.split(':')[4]`

**Cons:**
- [ERROR] Requires string parsing (not as clean as columns)
- [ERROR] Can't index/query efficiently

### Option 2: Add metadata JSON column (schema migration)

```sql
ALTER TABLE chunks ADD COLUMN metadata_json TEXT;
-- Store: {"page": 15, "char_start": 0, "char_end": 1234}
```

**Pros:**
- [OK] Clean structured data
- [OK] Extensible (can add fields later)
- [OK] Can use JSON functions in SQLite

**Cons:**
- [ERROR] Requires schema migration
- [ERROR] Need to update all existing chunks or leave NULL
- [ERROR] More complex (STGRAIL ceremony for migration)

### Option 3: Separate citations table (future)

```sql
CREATE TABLE chunk_citations (
    chunk_id TEXT PRIMARY KEY,
    page_number INTEGER,
    char_start INTEGER,
    char_end INTEGER,
    FOREIGN KEY (chunk_id) REFERENCES chunks(chunk_id)
);
```

**Pros:**
- [OK] Clean relational design
- [OK] Queryable/indexable
- [OK] Doesn't touch existing chunks table

**Cons:**  
- [ERROR] Requires schema migration
- [ERROR] More joins for queries
- [ERROR] Over-engineered for current need

---

## Recommendation: Option 1 (Enhanced anchor_locator)

**Minimal, no schema change, works today.**

**Implementation:**

```python
def extract_pdf_pages_with_offsets(pdf_path: Path) -> List[tuple[int, str, int, int]]:
    """
    Extract pages with character offset tracking.
    Returns: [(page_num, content, char_start, char_end), ...]
    """
    doc = fitz.open(pdf_path)
    pages_with_offsets = []
    char_offset = 0
    
    for i in range(doc.page_count):
        text = doc.load_page(i).get_text("text") or ""
        text = text.strip()
        
        char_start = char_offset
        char_end = char_offset + len(text)
        
        pages_with_offsets.append((i + 1, text, char_start, char_end))
        
        char_offset = char_end  # Next page starts here
    
    doc.close()
    return pages_with_offsets

# In main():
for page_num, content, char_start, char_end in pages_with_offsets:
    if not content.strip():
        continue
    
    # Enhanced locator with citation metadata
    locator = f"pdf:page:{page_num:04d}:chars:{char_start}-{char_end}"
    
    inserts.append((cid, locator, content))
```

**Citation extraction later:**

```python
def parse_pdf_locator(locator: str) -> dict:
    """Parse enhanced locator into citation components."""
    parts = locator.split(':')
    
    citation = {
        'format': parts[0],  # 'pdf'
        'page': int(parts[2]),  # 15
    }
    
    if len(parts) >= 5 and parts[3] == 'chars':
        char_range = parts[4].split('-')
        citation['char_start'] = int(char_range[0])
        citation['char_end'] = int(char_range[1])
    
    return citation

# Usage:
# locator = "pdf:page:0015:chars:3200-4567"
# citation = parse_pdf_locator(locator)
# print(f"TMS, p. {citation['page']}, chars {citation['char_start']}-{citation['char_end']}")
```

---

## Updated Script

Would you like me to update `chunk_tms_pages_pilot.py` to use **Option 1** (enhanced locator)?

This adds citation metadata TODAY without schema migration ceremony.

**Changes would be:**
1. Track character offsets during extraction
2. Store as `"pdf:page:0015:chars:3200-4567"` in `anchor_locator`
3. Add helper function to `utils/` for parsing citations

**Zero schema changes. Works in current RECORD session.**
