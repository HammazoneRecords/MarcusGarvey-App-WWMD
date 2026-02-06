# WWMD Output Contract

This document defines the JSON structure returned by the WWMD (What Would Marcus Do) engine. Frontend components should validate against this schema.

**Endpoint Simulation**: `backend/scripts/wwmd_ask_hybrid.py "Query" --json`

## JSON Schema

```json
{
  "query": "string (original user query)",
  "mode": "string (e.g. 'garvey_lens')",
  "answer": "string (the main AI response, markdown supported)",
  "action_steps": ["string", "string"], // Optional: Future use
  "principle": "string", // Optional: Future use
  "citations": [
    {
      "source_id": "string (e.g. 'marcus_garvey_selected_writings')",
      "loc": "string (e.g. 'pdf:page:0059:line:19')",
      "excerpt": "string (the actual matched text from source)",
      "score": "integer (quality score, higher is better)",
      "match_type": "string ('exact', 'partial_ngram', 'fuzzy_set')"
    }
  ],
  "meta": {
    "chunks_found": "integer (number of retrieval hits)",
    "citation_search_space": "integer (total lines scanned)",
    "timestamp": "ISO 8601 string (with timezone)",
    "latency_ms": "integer"
  }
}
```

## Session Vault

All queries are automatically logged to the Session Vault for playback/mocking:
`sessions/YYYY-MM-DD/HHMMSS_query_slug.json`

## Configuration

Control behavior via Environment Variables:
- `CITATION_EXPAND_MAX_LINES`: Max lines to scan for citations (default: 500)
- `CITATION_MAX_DISPLAY`: Max top citations to return (default: 8)

## Flag Usage

- `--json`: Output pure JSON to stdout
- `--out [file.json]`: Save JSON to specific file
- `--debug [expand|strict|off]`: Control citation search scope
