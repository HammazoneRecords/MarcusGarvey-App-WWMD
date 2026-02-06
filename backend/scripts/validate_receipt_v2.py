#!/usr/bin/env python3
"""
Receipt Schema V2 Validator

Validates ingestion receipts against RECEIPT_SCHEMA_V2.md specification.

Usage:
    python scripts/validate_receipt_v2.py path/to/receipt.json

Exit Codes:
    0 = Valid
    1 = Invalid (see stderr for details)
"""

import json
import sys
from pathlib import Path
from typing import List, Tuple
from datetime import datetime

# Add repo root to path
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


class ReceiptValidationError(Exception):
    """Raised when receipt validation fails"""
    pass


def validate_required_fields(receipt: dict) -> List[str]:
    """Check for presence of all required root fields"""
    errors = []
    
    required_root = [
        'receipt_version',
        'intent',
        'generated_utc',
        'import_session_id',
        'anchor_id',
        'source_path',
        'manifest_entry_sha256',
        'db',
        'strict_rules'
    ]
    
    for field in required_root:
        if field not in receipt:
            errors.append(f"Missing required field: {field}")
    
    # Check db subfields
    if 'db' in receipt:
        db = receipt['db']
        required_db = ['path', 'chunks_before', 'chunks_after', 'delta']
        for field in required_db:
            if field not in db:
                errors.append(f"Missing required field: db.{field}")
    
    return errors


def validate_types(receipt: dict) -> List[str]:
    """Validate field types"""
    errors = []
    
    # String fields
    string_fields = [
        'receipt_version',
        'intent',
        'generated_utc',
        'import_session_id',
        'anchor_id',
        'source_path',
        'manifest_entry_sha256'
    ]
    
    for field in string_fields:
        if field in receipt and not isinstance(receipt[field], str):
            errors.append(f"Field '{field}' must be string, got {type(receipt[field]).__name__}")
    
    # DB integer fields
    if 'db' in receipt:
        db = receipt['db']
        int_fields = ['chunks_before', 'chunks_after', 'delta']
        for field in int_fields:
            if field in db and not isinstance(db[field], int):
                errors.append(f"Field 'db.{field}' must be integer, got {type(db[field]).__name__}")
            if field in db and db[field] < 0:
                errors.append(f"Field 'db.{field}' must be >= 0, got {db[field]}")
    
    return errors


def validate_db_delta(receipt: dict) -> List[str]:
    """Validate database delta calculation"""
    errors = []
    
    if 'db' not in receipt:
        return errors
    
    db = receipt['db']
    required = ['chunks_before', 'chunks_after', 'delta']
    
    if all(f in db for f in required):
        before = db['chunks_before']
        after = db['chunks_after']
        delta = db['delta']
        expected_delta = after - before
        
        if delta != expected_delta:
            errors.append(
                f"Database delta mismatch: "
                f"delta={delta}, but chunks_after({after}) - chunks_before({before}) = {expected_delta}"
            )
    
    return errors


def validate_strict_rules(receipt: dict) -> List[str]:
    """Validate strict_rules object"""
    errors = []
    
    if 'strict_rules' not in receipt:
        return errors
    
    strict_rules = receipt['strict_rules']
    
    if not isinstance(strict_rules, dict):
        errors.append("Field 'strict_rules' must be an object")
        return errors
    
    if len(strict_rules) == 0:
        errors.append("Field 'strict_rules' must contain at least one rule")
    
    for rule_name, rule_value in strict_rules.items():
        if rule_value != "STOP":
            errors.append(
                f"Strict rule '{rule_name}' must be 'STOP', got '{rule_value}'. "
                "Prosecutor-grade receipts require all failures to STOP."
            )
    
    return errors


def validate_session_id_format(receipt: dict) -> List[str]:
    """Validate import_session_id format"""
    errors = []
    
    if 'import_session_id' not in receipt:
        return errors
    
    sid = receipt['import_session_id']
    
    # Basic pattern check: S_<timestamp>_<descriptor>
    if not sid.startswith('S_'):
        errors.append(f"Session ID must start with 'S_', got '{sid}'")
        return errors
    
    parts = sid.split('_')
    if len(parts) < 3:
        errors.append(
            f"Session ID must have format 'S_<UTC>_<DESCRIPTOR>', got '{sid}'"
        )
    
    # Check UTC timestamp part (position 1)
    if len(parts) >= 2:
        timestamp_part = parts[1]
        # Should be like 20251225T075155Z
        if not timestamp_part.endswith('Z'):
            errors.append(f"Session ID timestamp must end with 'Z' (UTC), got '{timestamp_part}'")
        if 'T' not in timestamp_part:
            errors.append(f"Session ID timestamp must contain 'T' separator, got '{timestamp_part}'")
    
    return errors


def validate_timestamps(receipt: dict) -> List[str]:
    """Validate timestamp format (if present)"""
    errors = []
    
    timestamp_fields = ['generated_utc']
    if 'timestamps' in receipt:
        timestamp_fields.extend(['timestamps.start_utc', 'timestamps.end_utc'])
    
    for field_path in timestamp_fields:
        if '.' in field_path:
            parent, field = field_path.split('.')
            value = receipt.get(parent, {}).get(field)
        else:
            value = receipt.get(field_path)
        
        if value is None:
            continue
        
        # Try parsing as ISO8601
        try:
            # Should end with Z for UTC
            if not value.endswith('Z'):
                errors.append(f"Timestamp '{field_path}' must end with 'Z' (UTC), got '{value}'")
            
            # Try parsing (basic validation)
            datetime.fromisoformat(value.replace('Z', '+00:00'))
        except ValueError as e:
            errors.append(f"Timestamp '{field_path}' is not valid ISO8601: {value} ({e})")
    
    return errors


def validate_ritual_metadata(receipt: dict) -> List[str]:
    """Validate ritual_metadata object (V2+ for Reality 5)"""
    errors = []
    
    if 'ritual_metadata' not in receipt:
        return errors  # Optional field
    
    metadata = receipt['ritual_metadata']
    
    if not isinstance(metadata, dict):
        errors.append("Field 'ritual_metadata' must be an object")
        return errors
    
    # Required fields within ritual_metadata
    required_fields = ['ritual_name', 'config_hash', 'config_path', 'module_name']
    
    for field in required_fields:
        if field not in metadata:
            errors.append(f"Missing required field: ritual_metadata.{field}")
        elif not isinstance(metadata[field], str):
            errors.append(f"Field 'ritual_metadata.{field}' must be string")
    
    # Validate config_hash format (should start with sha256:)
    if 'config_hash' in metadata:
        config_hash = metadata['config_hash']
        if not config_hash.startswith('sha256:'):
            errors.append(
                f"Field 'ritual_metadata.config_hash' should start with 'sha256:', got '{config_hash}'"
            )
        else:
            hash_part = config_hash[7:]  # Remove 'sha256:' prefix
            if len(hash_part) != 64 or not all(c in '0123456789abcdef' for c in hash_part):
                errors.append(
                    f"Field 'ritual_metadata.config_hash' should be 'sha256:<64-hex-chars>', got '{config_hash}'"
                )
    
    return errors


def validate_receipt_v2(receipt_path: Path) -> Tuple[bool, List[str]]:
    """
    Validate a receipt against RECEIPT_SCHEMA_V2
    
    Returns: (is_valid, list_of_errors)
    """
    errors = []
    
    # Load receipt
    try:
        receipt = json.loads(receipt_path.read_text(encoding='utf-8'))
    except json.JSONDecodeError as e:
        return False, [f"Invalid JSON: {e}"]
    except Exception as e:
        return False, [f"Cannot read file: {e}"]
    
    # Run all validations
    errors.extend(validate_required_fields(receipt))
    errors.extend(validate_types(receipt))
    errors.extend(validate_db_delta(receipt))
    errors.extend(validate_strict_rules(receipt))
    errors.extend(validate_session_id_format(receipt))
    errors.extend(validate_timestamps(receipt))
    errors.extend(validate_ritual_metadata(receipt))  # V2+ support
    
    # Check receipt_version
    if 'receipt_version' in receipt:
        version = receipt['receipt_version']
        if version not in ['V1', 'V2']:
            errors.append(f"Unsupported receipt_version: '{version}' (expected 'V1' or 'V2')")
        elif version == 'V1':
            # Warn about V1
            print(f"[WARN] Receipt uses version V1 (informal schema)", file=sys.stderr)
    
    return len(errors) == 0, errors


def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <receipt.json>", file=sys.stderr)
        return 1
    
    receipt_path = Path(sys.argv[1])
    
    if not receipt_path.exists():
        print(f"ERROR: File not found: {receipt_path}", file=sys.stderr)
        return 1
    
    print(f"Validating receipt: {receipt_path}")
    
    is_valid, errors = validate_receipt_v2(receipt_path)
    
    if is_valid:
        print("[VALID] Receipt conforms to RECEIPT_SCHEMA_V2")
        return 0
    else:
        print("\n[INVALID] Receipt has schema violations:\n", file=sys.stderr)
        for i, error in enumerate(errors, 1):
            print(f"  {i}. {error}", file=sys.stderr)
        errors_count = len(errors)
        print(f"Total errors: {errors_count}", file=sys.stderr)
        print("\nSee docs/RECEIPT_SCHEMA_V2.md for specification.", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
