"""
core/chain_constitution.py

Constitutional implementation for Merkle chain payload hashing.

DO NOT MODIFY THIS FILE WITHOUT CREATING payload_v2.

This module defines the canonical algorithm for computing payload hashes
in the Solob Wrapper receipt chain system (payload_v1).

Philosophy:
- "A Merkle chain is a scar, not a tattoo" - Chains record participation
- Optional but strict - Chains are optional, but when present, all rules enforced
- Constitution, not configuration - payload_v1 is locked, not customizable
- Version, don't mutate - Changes require payload_v2, never silent edits

Version: payload_v1 (FROZEN)
"""

from __future__ import annotations

import hashlib
import json
from typing import Any

# Constitutional constants (FROZEN - do not modify)
CHAIN_FIELDS_TOPLEVEL = frozenset({
    "chain_id",
    "chain_spec",
    "sequence",
    "payload_hash",
    "payload_hash_mode",
    "sealed",
})

HASH_EXCLUDE_TOPLEVEL = frozenset({
    "receipt_id",      # Volatile (generated)
    "timestamp_utc",   # Volatile (generated)
    *CHAIN_FIELDS_TOPLEVEL,  # Chain fields excluded from payload hash
})


def canonical_json_bytes(obj: Any) -> bytes:
    """
    Convert object to canonical JSON bytes for hashing.
    
    Constitutional lock: This serialization is immutable for payload_v1.
    
    Args:
        obj: Python object to serialize
        
    Returns:
        UTF-8 encoded JSON bytes with sorted keys, no whitespace
        
    DO NOT MODIFY: Changing this breaks historical chain validation.
    """
    return json.dumps(
        obj,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def compute_payload_view(
    receipt: dict[str, Any],
    exclude_keys: frozenset[str] | None = None,
) -> dict[str, Any]:
    """
    Compute the payload view for hashing (top-level exclusions only).
    
    Constitutional lock: For payload_v1, exclude_keys parameter is FORBIDDEN.
    
    Args:
        receipt: Receipt dictionary
        exclude_keys: MUST be None for payload_v1 (raises ValueError otherwise)
        
    Returns:
        Receipt with excluded top-level keys removed
        
    Raises:
        ValueError: If exclude_keys is provided (customization forbidden)
        
    DO NOT MODIFY: Exclusion set is constitutional for payload_v1.
    """
    if exclude_keys is not None:
        raise ValueError(
            "Cannot customize exclusions for payload_v1. "
            "To change exclusion logic, create payload_v2."
        )
    
    # Use constitutional exclusion set
    return {k: v for k, v in receipt.items() if k not in HASH_EXCLUDE_TOPLEVEL}


def compute_payload_hash(receipt: dict[str, Any]) -> str:
    """
    Compute SHA256 hash of canonical payload view (payload_v1).
    
    This is the constitutional hash algorithm for Merkle chain receipts.
    
    Exclusions (top-level only):
        - receipt_id, timestamp_utc (volatile)
        - All chain fields (chain_id, chain_spec, sequence, payload_hash, payload_hash_mode, sealed)
        
    Inclusions:
        - integrity.previous_receipt_sha256 (linkage is semantic)
        - Everything else in receipt
        
    Args:
        receipt: Receipt dictionary
        
    Returns:
        64-character lowercase hex SHA256 hash
        
    DO NOT MODIFY: This is the immutable hash algorithm for payload_v1.
    Historical chains depend on this never changing.
    """
    payload_view = compute_payload_view(receipt)
    canonical_bytes = canonical_json_bytes(payload_view)
    return hashlib.sha256(canonical_bytes).hexdigest()


# Version lock
PAYLOAD_VERSION = "payload_v1"

# Versioning rules (for future reference):
# 
# When payload_v2 is needed:
# 1. Create new functions: compute_payload_view_v2(), compute_payload_hash_v2()
# 2. Keep v1 functions FOREVER (historical validation)
# 3. Update emitter to use v2 for new receipts
# 4. Update validator to route based on payload_hash_mode field
# 5. NEVER modify v1 logic - historical chains are sacred
