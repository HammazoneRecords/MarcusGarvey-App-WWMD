#!/usr/bin/env python3
"""
Create Genesis Receipt for Merkle Chain

This is a ONE-TIME operation per chain. Subsequent receipts will be
automatically linked via prosecutor_emit_evidence_bundle.py.

Usage:
    python scripts/create_genesis_receipt.py --chain-id ARK_MAIN

Philosophy:
    "A Merkle chain is a scar, not a tattoo" ? immutable historical record
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# Import FROZEN constitutional hash function
sys.path.insert(0, str(Path(__file__).parent.parent))
from core.chain_constitution import compute_payload_hash, PAYLOAD_VERSION

BASE_DIR = Path(__file__).resolve().parent.parent
CHAIN_STATE_PATH = BASE_DIR / "docs" / "CHAIN_STATE.json"


def utc_now_z() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def create_genesis_receipt(chain_id: str) -> int:
    """Create genesis receipt (sequence 1) to initialize the chain"""
    
    print(f"[GENESIS] Creating genesis receipt for chain: {chain_id}")
    
    # Check if chain already has genesis
    if CHAIN_STATE_PATH.exists():
        chain_state = json.loads(CHAIN_STATE_PATH.read_text(encoding="utf-8"))
        if chain_id in chain_state.get("chains", {}):
            existing = chain_state["chains"][chain_id]
            if existing.get("last_sequence", 0) > 0:
                print(f"[ERROR] Chain {chain_id} already has genesis (sequence {existing['last_sequence']})")
                print(f"  Last Receipt: {existing.get('last_receipt_id')}")
                return 1
    
    receipt_id = f"RCPT_{chain_id}_SEQ_0001"
    
    # Create genesis receipt
    genesis = {
        "receipt_version": "V2",
        "receipt_id": receipt_id,
        "timestamp_utc": utc_now_z(),
        "generated_utc": utc_now_z(),
        "import_session_id": "GENESIS",
        
        # Chain fields (constitutional)
        "chain_id": chain_id,
        "chain_spec": None,
        "sequence": 1,
        "payload_hash": None,  # Computed below
        "payload_hash_mode": PAYLOAD_VERSION,
        "sealed": None,
        
        # Integrity section
        "integrity": {
            "previous_receipt_sha256": None,  # GENESIS has no previous
            "previous_receipt_id": None,
            "note": "Genesis receipt - first in chain"
        },
        
        # Genesis metadata
        "anchor": {
            "anchor_id": "GENESIS",
            "anchor_type": "system",
            "title": f"Genesis Receipt - {chain_id} Chain Initialization",
            "source_path": "system/genesis",
            "source_format": "genesis",
            "status": "genesis",
            "provenance": "system_generated",
            "created_at": utc_now_z()
        },
        
        "counts": {
            "chunks_for_anchor_in_this_batch": 0
        },
        
        "strict_rules": {
            "genesis": "IMMUTABLE",
            "chain_linkage": "MANDATORY"
        },
        
        "note": f"This is the genesis (first) receipt in the {chain_id} Merkle chain. "
                f"All subsequent receipts must link to this via payload_hash."
    }
    
    # Compute constitutional payload hash using FROZEN function
    print(f"[GENESIS] Computing payload hash using payload_v1 (FROZEN)...")
    payload_hash = compute_payload_hash(genesis)
    genesis["payload_hash"] = payload_hash
    
    # Create genesis bundle directory
    genesis_dir = BASE_DIR / "evidence" / "bundles" / f"GENESIS_{chain_id}"
    genesis_dir.mkdir(parents=True, exist_ok=True)
    
    # Write genesis receipt
    genesis_path = genesis_dir / "GENESIS_RECEIPT.json"
    genesis_path.write_text(
        json.dumps(genesis, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8"
    )
    
    print(f"[GENESIS] [OK] Genesis receipt created: {genesis_path.relative_to(BASE_DIR)}")
    print(f"  Receipt ID: {receipt_id}")
    print(f"  Sequence: 1")
    print(f"  Payload Hash: {payload_hash}")
    
    # Update/create chain state
    if CHAIN_STATE_PATH.exists():
        chain_state = json.loads(CHAIN_STATE_PATH.read_text(encoding="utf-8"))
    else:
        chain_state = {
            "version": "1.0",
            "updated_utc": utc_now_z(),
            "note": "Merkle chain state tracking",
            "chains": {}
        }
    
    chain_state["chains"][chain_id] = {
        "last_sequence": 1,
        "last_receipt_id": receipt_id,
        "last_payload_hash": payload_hash,
        "created_utc": utc_now_z(),
        "status": "active",
        "genesis_receipt_path": str(genesis_path.relative_to(BASE_DIR)),
        "description": f"Canonical {chain_id} chain"
    }
    chain_state["updated_utc"] = utc_now_z()
    
    CHAIN_STATE_PATH.write_text(
        json.dumps(chain_state, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8"
    )
    
    print(f"\n[GENESIS] [OK] Chain state updated: {CHAIN_STATE_PATH.relative_to(BASE_DIR)}")
    print(f"  Chain ID: {chain_id}")
    print(f"  Status: active")
    print(f"  Ready for sequence 2+")
    
    print(f"\n[SUCCESS] Genesis receipt created. Chain {chain_id} is now ACTIVE.")
    print(f"[NEXT] Subsequent receipts will automatically link to this genesis.")
    
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Create genesis receipt for Merkle chain")
    parser.add_argument(
        "--chain-id",
        required=True,
        help="Chain identifier (e.g., ARK_MAIN)"
    )
    args = parser.parse_args()
    
    return create_genesis_receipt(args.chain_id)


if __name__ == "__main__":
    raise SystemExit(main())
