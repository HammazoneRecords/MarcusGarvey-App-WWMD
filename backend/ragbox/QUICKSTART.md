# RAGBox Quick Start Guide
**Get Running in 5 Minutes**

---

## Step 1: Environment Setup (1 minute)

```bash
# Copy environment template
cp config/.env.example .env

# Edit .env and add your Gemini API key
# GEMINI_API_KEY="your_key_here"
```

---

## Step 2: Initialize Database (30 seconds)

```bash
python scripts/init_db.py
```

**Expected output**:
```
✓ Database initialized at data/memory.db
✓ Created tables: anchors, chunks, line_chunks
```

---

## Step 3: Ingest Sample Content (1 minute)

```bash
python examples/ingestion_example.py
```

**Expected output**:
```
✓ Created anchor: example_001
✓ Ingested 3 chunks, 8 lines
  Session ID: S_20251230T220530Z_INGESTION
```

---

## Step 4: Run Your First Query (30 seconds)

```bash
python scripts/wwmd_ask_hybrid.py "What does the example say?" --json
```

**Expected output**:
```json
{
  "query": "What does the example say?",
  "mode": "knowledge_base",
  "answer": "...",
  "citations": [
    {
      "excerpt": "...",
      "loc": "text:chunk:0001:line:1",
      "source_id": "example_001",
      "score": 9,
      "match_type": "exact"
    }
  ],
  "meta": {
    "chunks_found": 3,
    "citation_search_space": 8,
    "timestamp": "2025-12-30T22:05:30-05:00",
    "latency_ms": 1234
  }
}
```

---

## Step 5: Verify Session Vault (30 seconds)

```bash
# Check that query was saved
ls sessions/
```

**Expected**:
```
sessions/
└── 2025-12-30/
    └── 220530_What_does_the_example_say.json
```

---

## ✅ Success!

You now have a working RAG system with:
- ✅ Line-level chunking
- ✅ Citation validation
- ✅ Quality scoring
- ✅ Session vault

---

## Next Steps

### Ingest Your Own Content

1. Create an anchor:
```python
from examples.ingestion_example import create_anchor
create_anchor("my_doc_001", "My Document", author="Me", year=2025)
```

2. Ingest content:
```python
from examples.ingestion_example import ingest_text_document
content = open("my_document.txt").read()
ingest_text_document("my_doc_001", content)
```

### Query Your Content

```bash
python scripts/wwmd_ask_hybrid.py "Your question here" --json
```

### Run Tests

```bash
python tests/test_retrieval.py
python tests/test_citation.py
```

---

## Troubleshooting

### "No module named 'sqlite3'"
SQLite3 is built into Python. If you see this error, your Python installation may be incomplete.

### "No citations found"
- Check that content was ingested: `sqlite3 data/memory.db "SELECT COUNT(*) FROM line_chunks;"`
- Try a broader query
- Increase `CITATION_EXPAND_MAX_LINES` in `.env`

### "API key error"
- Verify `.env` file exists
- Check `GEMINI_API_KEY` is set correctly
- Test with: `python scripts/test_api_key.py` (if you copied it from main system)

---

## Configuration

### Adjust Citation Behavior

Edit `.env`:
```bash
# Expand search to more lines
CITATION_EXPAND_MAX_LINES=1000

# Show more citations
CITATION_MAX_DISPLAY=15
```

### Debug Modes

```bash
# Expand mode (default) - search all lines in parent chunks
python scripts/wwmd_ask_hybrid.py "query" --debug expand

# Strict mode - only search initially retrieved lines
python scripts/wwmd_ask_hybrid.py "query" --debug strict

# Off mode - no citation expansion
python scripts/wwmd_ask_hybrid.py "query" --debug off
```

---

## Performance Tips

### Add Database Indexes

```sql
sqlite3 data/memory.db
CREATE INDEX idx_line_chunks_content ON line_chunks(content);
CREATE INDEX idx_chunks_content ON chunks(content);
.exit
```

### Optimize Chunk Size

For faster retrieval, keep chunks to 500-1000 characters.

### Batch Processing

Use `examples/batch_query_example.py` for multiple queries.

---

## Ready to Deploy?

See `docs/rag_and_audit_implementation_guide.md` for:
- Production deployment
- Frontend integration
- API endpoints
- Scaling strategies

---

**Total Setup Time**: ~5 minutes  
**Next Query Time**: ~2 seconds
