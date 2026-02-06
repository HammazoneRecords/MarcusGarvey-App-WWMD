# RAGBox - Portable RAG System
**Hybrid RAG with Line-Level Chunking & Citation Injection**

**Version**: 1.0  
**Last Updated**: 2025-12-30  
**Source**: Marcus Garvey App WWMD ARK System

---

## What is RAGBox?

RAGBox is a **production-ready, portable RAG (Retrieval-Augmented Generation) system** that solves the LLM citation hallucination problem through:

1. **Line-level chunking** - Cite exact lines, not just pages
2. **Post-process citation validation** - Verify citations match actual content
3. **Quality scoring** - Rank citations by relevance
4. **Session vault** - Save every query for replay/debugging

---

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Environment

Create `.env` file:
```bash
GEMINI_API_KEY="your_api_key_here"
CITATION_EXPAND_MAX_LINES=500
CITATION_MAX_DISPLAY=8
PYTHONUTF8=1
PYTHONIOENCODING=utf-8
```

### 3. Initialize Database

```bash
python scripts/init_db.py
```

This creates `data/memory.db` with the schema.

### 4. Ingest Your Content

See `examples/ingestion_example.py` for how to ingest PDFs, JSON, or text files.

### 5. Query the System

```bash
# Basic query
python scripts/wwmd_ask_hybrid.py "Your question here"

# JSON output
python scripts/wwmd_ask_hybrid.py "Your question here" --json

# Save to file
python scripts/wwmd_ask_hybrid.py "Your question here" --json --out output.json
```

---

## Directory Structure

```
ragbox/
├── scripts/           # Core RAG scripts
│   ├── wwmd_ask_hybrid.py      # Main RAG engine
│   ├── hybrid_retriever.py     # Retrieval module
│   ├── citation_injector.py    # Citation validation
│   ├── wwmd_ask.py             # Basic RAG (legacy)
│   └── init_db.py              # Database initialization
├── docs/              # Documentation
│   ├── rag_and_audit_implementation_guide.md
│   ├── SCRIPTS_INVENTORY.md
│   ├── WWMD_RAG_PROTOCOL.md
│   ├── WWMD_OUTPUT_CONTRACT.md
│   └── CITATION_ACCURACY_ANALYSIS.md
├── config/            # Configuration files
│   └── .env.example
├── examples/          # Usage examples
│   ├── ingestion_example.py
│   ├── query_example.py
│   └── batch_query_example.py
├── tests/             # Test suite
│   ├── test_retrieval.py
│   ├── test_citation.py
│   └── test_integration.py
├── data/              # Database storage
│   └── memory.db (created by init_db.py)
├── sessions/          # Query session vault (auto-created)
│   └── YYYY-MM-DD/
│       └── HHMMSS_query_slug.json
├── requirements.txt   # Python dependencies
└── README.md          # This file
```

---

## Core Components

### 1. Database Schema

**Three-table design**:
- `anchors` - Source documents
- `chunks` - Parent chunks (pages, sections)
- `line_chunks` - Individual lines within chunks

See `docs/rag_and_audit_implementation_guide.md` for full schema.

### 2. Hybrid Retriever (`hybrid_retriever.py`)

**Functions**:
- `extract_keywords(query)` - Extract keywords with stopword removal
- `retrieve_hybrid(query, max_results=15)` - Retrieve line + parent chunks
- `build_hybrid_context(results)` - Build context for LLM
- `fetch_all_lines_for_parents(parent_ids)` - Expand citation search space

### 3. Citation Injector (`citation_injector.py`)

**Functions**:
- `score_citation(line_text, query_terms)` - Quality scoring
- `find_text_matches(ai_response, line_data)` - 3-strategy matching:
  - Exact substring match
  - Partial n-gram match (sliding window)
  - Fuzzy set match (token overlap >75%)
- `get_citations(ai_response, line_data)` - Main entry point

### 4. Main RAG Engine (`wwmd_ask_hybrid.py`)

**Features**:
- Line-level precision citations
- Post-process citation validation
- Quality scoring
- **Garvey Lens Mode**: Structured analysis (Principle, Analogy, Action Steps) via `ask_marcus_lens`
- Session vault (saves to `sessions/YYYY-MM-DD/`)
- JSON output contract

**Flags**:
- `--json` - Output JSON only
- `--out <file>` - Save JSON to file
- `--debug expand|strict|off` - Citation search scope

---

## JSON Output Contract

```json
{
  "query": "What did Marcus Garvey say about unity?",
  "mode": "knowledge_base",
  "answer": "...",
  "citations": [
    {
      "excerpt": "...",
      "loc": "pdf:page:0021:line:5",
      "source_id": "doc_001",
      "score": 9,
      "match_type": "exact"
    }
  ],
  "meta": {
    "chunks_found": 15,
    "citation_search_space": 450,
    "timestamp": "2025-12-30T19:20:33-05:00",
    "latency_ms": 1234
  }
}
```

---

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `GEMINI_API_KEY` | Required | Gemini API key |
| `CITATION_EXPAND_MAX_LINES` | 500 | Max lines for citation search |
| `CITATION_MAX_DISPLAY` | 8 | Max citations to display |
| `PYTHONUTF8` | 1 | Force UTF-8 encoding |
| `PYTHONIOENCODING` | utf-8 | Python I/O encoding |

### Debug Modes

- `expand` (default) - Search all lines in retrieved parent chunks
- `strict` - Search only initially retrieved lines
- `off` - No citation expansion

---

## Usage Examples

### Basic Query

```bash
python scripts/wwmd_ask_hybrid.py "What is the foundation of success?"
```

### JSON Output

```bash
python scripts/wwmd_ask_hybrid.py "What is the foundation of success?" --json
```

### Save to File

```bash
python scripts/wwmd_ask_hybrid.py "What is the foundation of success?" --json --out result.json
```

### Strict Citation Mode

```bash
python scripts/wwmd_ask_hybrid.py "What is the foundation of success?" --debug strict
```

---

## Testing

```bash
# Run all tests
python -m pytest tests/

# Run specific test
python -m pytest tests/test_retrieval.py

# Run with coverage
python -m pytest tests/ --cov=scripts --cov-report=html
```

---

## Troubleshooting

### No citations found

**Problem**: `citation_search_space` is 0 in meta  
**Solution**: Check retrieval - ensure database has content

**Problem**: `citation_search_space` > 0 but no citations  
**Solution**: Adjust scoring thresholds in `citation_injector.py`

### Wrong citations

**Problem**: Citations don't match query  
**Solution**: Increase `CITATION_EXPAND_MAX_LINES` to search more context

### Slow performance

**Problem**: Queries take >5 seconds  
**Solution**: Add database indexes:
```sql
CREATE INDEX idx_line_chunks_content ON line_chunks(content);
CREATE INDEX idx_chunks_content ON chunks(content);
```

---

## Key Principles

1. **Never trust LLM citations** - Always post-process and validate
2. **Line-level precision** - Cite exact lines, not just pages
3. **Quality scoring** - Rank citations by relevance
4. **Session vault** - Save every query for replay/debugging

---

## Success Metrics

From the Marcus Garvey App ARK V0:
- ✅ **3,446 chunks** ingested with 0 orphans
- ✅ **Citation accuracy**: >90% with post-process validation
- ✅ **Average latency**: <2 seconds per query
- ✅ **Session vault**: 100% query replay capability

---

## Documentation

- **[Implementation Guide](docs/rag_and_audit_implementation_guide.md)** - Complete implementation guide
- **[Scripts Inventory](docs/SCRIPTS_INVENTORY.md)** - All scripts and their purposes
- **[RAG Protocol](docs/WWMD_RAG_PROTOCOL.md)** - Prosecutor's standard for citations
- **[Output Contract](docs/WWMD_OUTPUT_CONTRACT.md)** - JSON schema specification
- **[Citation Analysis](docs/CITATION_ACCURACY_ANALYSIS.md)** - How we solved hallucination

---

## License

This RAG system is extracted from the Marcus Garvey App WWMD ARK System.

---

## Support

For questions or issues, refer to the implementation guide or scripts inventory.

**Estimated Setup Time**: 30 minutes  
**Estimated Integration Time**: 2-3 hours
