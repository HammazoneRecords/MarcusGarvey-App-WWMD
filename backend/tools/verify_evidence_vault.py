#!/usr/bin/env python3
"""
Verify Evidence Vault Integrity

Primary tamper detection layer. Verifies actual evidence files match vault hashes.

Usage:
    python tools/verify_evidence_vault.py

Exit Codes:
    0 = Vault intact (all files match hashes)
    1 = Vault compromised (tampering detected)
"""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
VAULT_PATH = BASE_DIR / "docs" / "EVIDENCE_VAULT.json"
BUNDLES_DIR = BASE_DIR / "evidence" / "bundles"


def utc_now_z() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def calculate_sha256(filepath: Path) -> str:
    """Calculate SHA256 hash of a file"""
    sha256_hash = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except Exception as e:
        return f"ERROR: {str(e)}"


def verify_vault_integrity() -> tuple[bool, str, list[dict]]:
    """
    Verify all evidence files match vault hashes.
    
    Returns:
        (is_valid, message, alerts)
    """
    
    if not VAULT_PATH.exists():
        return False, "CRITICAL: Evidence vault not found", []
    
    try:
        vault = json.loads(VAULT_PATH.read_text(encoding="utf-8"))
    except Exception as e:
        return False, f"CRITICAL: Cannot read vault: {e}", []
    
    entries = vault.get("entries", [])
    if not entries:
        return True, "Vault empty (no entries)", []
    
    print(f"[VAULT] Verifying {len(entries)} vault entries...")
    
    alerts = []
    verified_count = 0
    
    for entry in entries:
        entry_id = entry.get("entry_id")
        bundle_id = entry.get("bundle_id")
        files = entry.get("files", {})
        
        print(f"[VAULT] Entry {entry_id}: {bundle_id}")
        
        bundle_dir = BUNDLES_DIR / bundle_id
        if not bundle_dir.exists():
            alerts.append({
                "severity": "CRITICAL",
                "entry_id": entry_id,
                "bundle_id": bundle_id,
                "issue": "Bundle directory missing",
                "remediation": f"Bundle {bundle_id} directory not found - evidence deleted or moved"
            })
            continue
        
        # Verify each file in entry
        entry_ok = True
        for filename, expected_hash in files.items():
            filepath = bundle_dir / filename
            
            if not filepath.exists():
                alerts.append({
                    "severity": "CRITICAL",
                    "entry_id": entry_id,
                    "bundle_id": bundle_id,
                    "file": filename,
                    "issue": "File missing",
                    "remediation": f"Evidence file {filename} deleted or moved"
                })
                entry_ok = False
                continue
            
            # Calculate actual hash
            actual_hash = calculate_sha256(filepath)
            
            if actual_hash.startswith("ERROR"):
                alerts.append({
                    "severity": "CRITICAL",
                    "entry_id": entry_id,
                    "bundle_id": bundle_id,
                    "file": filename,
                    "issue": f"Cannot read file: {actual_hash}",
                    "remediation": "Check file permissions"
                })
                entry_ok = False
                continue
            
            # Compare hashes (vault stores "sha256:hash", actual is just hash)
            expected_hash_clean = expected_hash.replace("sha256:", "")
            
            if actual_hash != expected_hash_clean:
                alerts.append({
                    "severity": "CRITICAL",
                    "entry_id": entry_id,
                    "bundle_id": bundle_id,
                    "file": filename,
                    "issue": "File tampered",
                    "expected_hash": expected_hash_clean[:16] + "...",
                    "actual_hash": actual_hash[:16] + "...",
                    "remediation": f"CRITICAL: Evidence file {filename} has been modified - investigate immediately"
                })
                entry_ok = False
            else:
                print(f"  [OK] {filename}: {actual_hash[:16]}...")
        
        if entry_ok:
            verified_count += 1
    
    # Overall verdict
    if alerts:
        critical_count = len([a for a in alerts if a.get("severity") == "CRITICAL"])
        return False, f"Vault compromised: {critical_count} CRITICAL alert(s)", alerts
    else:
        return True, f"Vault intact: {verified_count}/{len(entries)} entries verified", alerts


def main() -> int:
    is_valid, message, alerts = verify_vault_integrity()
    
    if not is_valid:
        print(f"\n[FAILURE] {message}")
        if alerts:
            print("\n=== ALERTS ===")
            for alert in alerts:
                print(f"\n[{alert['severity']}] Entry {alert.get('entry_id')}: {alert.get('bundle_id')}")
                print(f"  File: {alert.get('file', 'N/A')}")
                print(f"  Issue: {alert.get('issue')}")
                if "expected_hash" in alert:
                    print(f"  Expected: {alert['expected_hash']}")
                    print(f"  Actual:   {alert['actual_hash']}")
                print(f"  Remediation: {alert.get('remediation')}")
        return 1
    else:
        print(f"\n[SUCCESS] {message}")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
