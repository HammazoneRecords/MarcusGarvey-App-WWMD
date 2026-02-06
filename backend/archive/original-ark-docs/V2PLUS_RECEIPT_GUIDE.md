# V2+ Receipt Example for Ritual Engine

## Standard V2+ Receipt Template

Use this template when emitting receipts from ritual engine modules:

```python
import json
import hashlib
from datetime import datetime
from pathlib import Path

def emit_v2plus_receipt(
    ritual_name: str,
    config_path: str,
    module_name: str,
    anchor_id: str,
    source_path: str,
    manifest_sha256: str,
    db_chunks_before: int,
    db_chunks_after: int,
    session_id: str,
    strict_rules: dict,
    **type_specific_fields
):
    """
    Emit a V2+ receipt with ritual metadata.
    
    Args:
        ritual_name: Ritual identifier (e.g., "lexicon_import")
        config_path: Path to ritual config file
        module_name: Module that executed the ritual
        anchor_id: Anchor being processed
        source_path: Source file path
        manifest_sha256: SHA256 from manifest
        db_chunks_before: Chunk count before ingestion
        db_chunks_after: Chunk count after ingestion
        session_id: Import session ID
        strict_rules: Dict of strict rules (all must be "STOP")
        **type_specific_fields: Additional fields (lexicon, pdf, etc.)
    """
    # Compute config hash
    config_content = Path(config_path).read_bytes()
    config_hash = f"sha256:{hashlib.sha256(config_content).hexdigest()}"
    
    receipt = {
        "receipt_version": "V2",
        "intent": f"RITUAL_{ritual_name.upper()}_{anchor_id.upper()}",
        "generated_utc": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "import_session_id": session_id,
        
        # Ritual metadata (V2+ extension)
        "ritual_metadata": {
            "ritual_name": ritual_name,
            "config_hash": config_hash,
            "config_path": config_path,
            "module_name": module_name,
            "module_version": "1.0"  # Optional
        },
        
        # Standard V2 fields
        "anchor_id": anchor_id,
        "source_path": source_path,
        "manifest_entry_sha256": manifest_sha256,
        
        "db": {
            "path": "data/memory.db",
            "chunks_before": db_chunks_before,
            "chunks_after": db_chunks_after,
            "delta": db_chunks_after - db_chunks_before
        },
        
        "strict_rules": strict_rules
    }
    
    # Add type-specific fields
    receipt.update(type_specific_fields)
    
    return receipt


# Example usage in a ritual module:

def run_lexicon_import(config, session_id):
    """Example ritual module function"""
    
    # ... perform import ...
    
    # Emit V2+ receipt
    receipt = emit_v2plus_receipt(
        ritual_name="lexicon_import",
        config_path=config['_config_path'],
        module_name="lexicon_ingestion",
        anchor_id=config['anchor_id'],
        source_path=config['source']['path'],
        manifest_sha256=config['source']['expected_sha256'],
        db_chunks_before=chunks_before,
        db_chunks_after=chunks_after,
        session_id=session_id,
        strict_rules={
            "chunk_collision": "STOP",
            "missing_anchor": "STOP",
            "schema_mismatch": "STOP"
        },
        # Type-specific fields
        lexicon={
            "letter": config['letter'],
            "entries_total": 102,
            "entries_inserted": 102
        }
    )
    
    # Write receipt
    receipt_path = Path(f"evidence/{session_id}/RECEIPTS/RECEIPT_LEXICON_{config['letter']}.json")
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    receipt_path.write_text(json.dumps(receipt, indent=2), encoding='utf-8')
    
    return receipt
```

## Key Points

1. **Always include `ritual_metadata`** when generating receipts from ritual engine
2. **Compute config_hash** from actual config file content (SHA256)
3. **Format**: `sha256:<64-hex-lowercase>`
4. **Validation**: Court validators accept receipts with or without `ritual_metadata`
5. **Backward Compatible**: V2 receipts without ritual_metadata still valid

## Validation

```bash
# Validate a V2+ receipt
python scripts/validate_receipt_v2.py evidence/S_<SID>/RECEIPTS/RECEIPT_<NAME>.json
```

Expected output:
```
Validating receipt: evidence/S_<SID>/RECEIPTS/RECEIPT_<NAME>.json
[OK] VALID - Receipt conforms to RECEIPT_SCHEMA_V2
```

## See Also

- `docs/RECEIPT_SCHEMA_V2.md` - Full V2+ specification
- `docs/RECEIPT_SCHEMA_COMPARISON.md` - V1 vs V2 comparison
- `scripts/validate_receipt_v2.py` - Receipt validator
