# Ritual Engine Guide

**Reality 5 (The Product Builder)**: Config-driven ingestion framework.

---

## Quick Start (5 minutes)

### 1. List Available Rituals
```bash
mw ritual list
```

### 2. Validate a Ritual (Dry-Run)
```bash
mw ritual validate --config config/rituals/bos_pdf_template.json
```

### 3. Execute a Ritual
```bash
mw ritual run --config config/rituals/bos_pdf_template.json
```

---

## Why Rituals?

**Before (Reality 4):**
```bash
python scripts/import_lexicon_chunks_v1_1.py \
  --anchor-id lexicon_a_v1 \
  --json data/lexicon/A.json \
  --letter A \
  --import-session-id $SID \
  --receipt-out evidence/$SID/RECEIPTS/... \
  --derive-row-index
```

**After (Reality 5):**
```bash
mw ritual run --config config/rituals/lexicon_a.json
```

**Benefits:**
- Config changes don't require code changes
- Automatic V2 receipt generation
- Consistent error handling
- Self-documenting configs
- Easy to audit and version control

---

## Config Reference

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `ritual_version` | string | Config version (currently "1.0") |
| `ritual_name` | string | Unique identifier (e.g., "lexicon_import_a") |
| `intent` | string | Human-readable intent (e.g., "LEXICON_IMPORT_A") |
| `anchor_id` | string | Target anchor ID |
| `source` | object | Source file configuration |
| `steps` | array | Ingestion steps to execute |
| `strict_rules` | object | Failure handling rules |

### Source Configuration

```json
{
  "source": {
    "type": "json|pdf|csv",
    "path": "relative/path/to/file",
    "format": "lexicon_entries|anchor_registry",
    "manifest_sha256": "optional sha256 for verification",
    "letter": "A"
  }
}
```

### Steps

```json
{
  "steps": [
    {"type": "validate_source"},
    {"type": "validate_anchor"},
    {"type": "verify_manifest"},
    {
      "type": "ingest_chunks",
      "chunk_id_template": "{anchor_id}:{letter}:{row_index}",
      "locator_template": "lexicon:{letter}:row:{row_index}",
      "truth_type": "definition"
    },
    {"type": "generate_receipt", "receipt_version": "V2"}
  ]
}
```

### Strict Rules

```json
{
  "strict_rules": {
    "chunk_collision": "STOP|WARN|IGNORE",
    "missing_anchor": "STOP|WARN|IGNORE",
    "schema_mismatch": "STOP|WARN|IGNORE",
    "manifest_sha_mismatch": "STOP|WARN|IGNORE"
  }
}
```

### Options

```json
{
  "options": {
    "dry_run": false,
    "limit": 0,
    "derive_row_index": true
  }
}
```

---

## Available Modules

| Module | Source Type | Use Case |
|--------|-------------|----------|
| `json` | JSON files | Generic JSON array ingestion |
| `lexicon` | JSON files | Lexicon entries with row_index |
| `pdf` | PDF files | Page-by-page extraction |
| `registry` | JSON files | Anchor registration |

### Module Selection
The engine auto-selects based on `source.type` and `source.format`:
- `format: "lexicon_entries"` -> `lexicon` module
- `type: "pdf"` -> `pdf` module
- `format: "anchor_registry"` -> `registry` module
- Default -> `json` module

---

## Template Variables

Use in `chunk_id_template` and `locator_template`:

| Variable | Description |
|----------|-------------|
| `{anchor_id}` | Anchor ID from config |
| `{index}` | 0-based entry index |
| `{row_index}` | 1-based row index |
| `{letter}` | Letter from config |
| `{<field>}` | Any field from entry |

---

## CLI Commands

```bash
# List all ritual configs
mw ritual list

# Validate without executing
mw ritual validate --config <path>

# Execute ritual
mw ritual run --config <path>

# Execute with dry-run (alias for validate)
mw ritual run --config <path> --dry-run
```

---

## Flow Integration

Rituals integrate with STGRAIL:

1. **State Check**: Must be in RECORD state
2. **Front Door**: Routes through `run_recorded.py`
3. **Evidence**: Receipts saved to `evidence/<SID>/RECEIPTS/`
4. **Ledger**: Execution logged to `logs/ops_ledger.jsonl`

---

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | User error (bad config, missing file) |
| 2 | Strict rule violation (data integrity) |

---

## Example Configs

See `config/rituals/` for templates:
- `lexicon_a_template.json` - Lexicon ingestion
- `bos_pdf_template.json` - PDF ingestion
- `registry_template.json` - Anchor registration

---

## Related Docs
- `docs/SERIES_ROUTE.md` - Reality progression
- `docs/ROUTE_LEGEND.md` - Script reference
- `docs/RECEIPT_SCHEMA_V2.md` - Receipt format
