#!/usr/bin/env python3
"""
Verify Merkle Chain Integrity

Verifies that all receipts in a chain are properly linked and untampered.
Uses FROZEN chain_constitution.py to recompute hashes.

Usage:
    python tools/verify_chain_integrity.py --chain-id ARK_MAIN

Exit Codes:
    0 = Chain intact
    1 = Chain broken or tampered
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Import FROZEN constitutional hash function
sys.path.insert(0, str(Path(__file__).parent.parent))
from core.chain_constitution import compute_payload_hash

BASE_DIR = Path(__file__).resolve().parent.parent
CHAIN_STATE_PATH = BASE_DIR / "docs" / "CHAIN_STATE.json"


def load_chain_receipts(chain_id: str) -> list[dict]:
    """Load all receipts for a chain, sorted by sequence"""
    
    receipts = []
    
    # Find all bundles with receipts
    bundles_dir = BASE_DIR / "evidence" / "bundles"
    if not bundles_dir.exists():
        return receipts
    
    for bundle_dir in bundles_dir.iterdir():
        if not bundle_dir.is_dir():
            continue
        
        receipts_dir = bundle_dir / "RECEIPTS"
        if receipts_dir.exists():
            for receipt_file in receipts_dir.glob("*.json"):
                try:
                    receipt = json.loads(receipt_file.read_text(encoding="utf-8"))
                    if receipt.get("chain_id") == chain_id:
                        receipts.append(receipt)
                except Exception:
                    continue
        
        # Check for genesis receipt
        genesis_file = bundle_dir / "GENESIS_RECEIPT.json"
        if genesis_file.exists():
            try:
                receipt = json.loads(genesis_file.read_text(encoding="utf-8"))
                if receipt.get("chain_id") == chain_id:
                    receipts.append(receipt)
            except Exception:
                continue
    
    # Sort by sequence
    receipts.sort(key=lambda r: r.get("sequence", 0))
    
    return receipts


def verify_chain_integrity(chain_id: str) -> tuple[bool, str]:
    """
    Verify entire chain is intact and unbroken.
    
    Returns:
        (is_valid, message)
    """
    
    # Load chain state
    if not CHAIN_STATE_PATH.exists():
        return False, f"Chain state file not found: {CHAIN_STATE_PATH}"
    
    chain_state_doc = json.loads(CHAIN_STATE_PATH.read_text(encoding="utf-8"))
    chain_state = chain_state_doc.get("chains", {}).get(chain_id)
    
    if not chain_state:
        return False, f"Chain {chain_id} not found in chain state"
    
    # Load all receipts
    receipts = load_chain_receipts(chain_id)
    
    if not receipts:
        return False, f"No receipts found for chain {chain_id}"
    
    print(f"[VERIFY] Found {len(receipts)} receipt(s) in chain {chain_id}")
    
    # Verify each receipt
    for i, receipt in enumerate(receipts):
        receipt_id = receipt.get("receipt_id", "UNKNOWN")
        sequence = receipt.get("sequence", 0)
        
        # Verify sequence continuity
        expected_seq = i + 1
        if sequence != expected_seq:
            return False, f"Sequence gap at {receipt_id}: expected {expected_seq}, got {sequence}"
        
        print(f"[VERIFY] Checking sequence {sequence}: {receipt_id}")
        
        # Recompute payload hash using FROZEN constitutional function
        stored_hash = receipt.get("payload_hash")
        if not stored_hash:
            return False, f"Missing payload_hash in {receipt_id}"
        
        computed_hash = compute_payload_hash(receipt)
        
        if stored_hash != computed_hash:
            return False, f"Payload hash tampered in {receipt_id}: stored={stored_hash[:16]}...  vs computed={computed_hash[:16]}..."
        
        print(f"  [OK] Payload hash intact: {computed_hash[:16]}...")
        
        # Verify linkage (except genesis)
        if i > 0:
            prev_receipt = receipts[i - 1]
            prev_hash = prev_receipt.get("payload_hash")
            
            integrity = receipt.get("integrity", {})
            linked_hash = integrity.get("previous_receipt_sha256")
            
            if linked_hash != prev_hash:
                return False, f"Chain broken between {prev_receipt.get('receipt_id')} and {receipt_id}: " \
                             f"expected link to {prev_hash[:16]}..., got {linked_hash[:16] if linked_hash else 'NULL'}..."
            
            print(f"  [OK] Linked to previous: {prev_receipt.get('receipt_id')}")
        else:
            # Genesis must have null previous
            integrity = receipt.get("integrity", {})
            if integrity.get("previous_receipt_sha256") is not None:
                return False, f"Genesis receipt {receipt_id} has non-null previous_receipt_sha256"
            print(f"  [OK] Genesis (no previous)")
    
    # Verify chain state matches last receipt
    last_receipt = receipts[-1]
    if chain_state.get("last_sequence") != last_receipt.get("sequence"):
        return False, f"Chain state last_sequence mismatch: state={chain_state.get('last_sequence')}, actual={last_receipt.get('sequence')}"
    
    if chain_state.get("last_payload_hash") != last_receipt.get("payload_hash"):
        return False, f"Chain state last_payload_hash mismatch"
    
    print(f"\n[VERIFY] [OK] Chain state synchronized with last receipt")
    
    return True, f"Chain {chain_id} is intact ({len(receipts)} receipt(s) verified)"


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify Merkle chain integrity")
    parser.add_argument(
        "--chain-id",
        default="ARK_MAIN",
        help="Chain identifier to verify (default: ARK_MAIN)"
    )
    args = parser.parse_args()
    
    is_valid, message = verify_chain_integrity(args.chain_id)
    
    if is_valid:
        print(f"\n[SUCCESS] {message}")
        return 0
    else:
        print(f"\n[FAILURE] {message}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
