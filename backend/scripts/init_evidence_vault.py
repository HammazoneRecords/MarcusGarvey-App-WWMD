#!/usr/bin/env python3
"""
Initialize Evidence Vault with Genesis Bundle

Calculates full SHA256 hashes for genesis bundle and creates vault.
"""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
VAULT_PATH = BASE_DIR / "docs" / "EVIDENCE_VAULT.json"
GENESIS_DIR = BASE_DIR / "evidence" / "bundles" / "GENESIS_ARK_MAIN"


def sha256_file(filepath: Path) -> str:
    """Calculate SHA256 of a file"""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    # Calculate hashes
    files = {
        "GENESIS_RECEIPT.json": f"sha256:{sha256_file(GENESIS_DIR / 'GENESIS_RECEIPT.json')}",
        "INDEX.json": f"sha256:{sha256_file(GENESIS_DIR / 'INDEX.json')}",
        "REPORT.md": f"sha256:{sha256_file(GENESIS_DIR / 'REPORT.md')}"
    }
    
    vault = {
        "version": "1.0",
        "created_utc": "2025-12-29T08:00:00Z",
        "updated_utc": "2025-12-29T08:00:00Z",
        "note": "Evidence Vault - Primary tamper detection layer",
        "entries": [
            {
                "entry_id": 1,
                "timestamp": "2025-12-29T07:34:41Z",
                "bundle_id": "GENESIS_ARK_MAIN",
                "bundle_type": "genesis",
                "receipt_id": "RCPT_ARK_MAIN_SEQ_0001",
                "sequence": 1,
                "files": files,
                "locked": True,
                "recorded_run": "create_genesis_receipt.py",
                "operator": "system"
            }
        ],
        "vault_integrity": {
            "total_entries": 1,
            "total_files_tracked": 3
        }
    }
    
    VAULT_PATH.write_text(json.dumps(vault, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"[OK] Vault initialized: {VAULT_PATH.relative_to(BASE_DIR)}")
    print(f"  Files tracked: {len(files)}")
    for fname, fhash in files.items():
        print(f"    {fname}: {fhash[:22]}...")
    

if __name__ == "__main__":
    main()
