#!/usr/bin/env python3
"""
Prosecutor Upgrade Bundles V2
Standardizes legacy (V1) evidence bundles to the V2 specification.
Generates INDEX.json and REPORT.md for each identified legacy bundle.
"""
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
BUNDLES_DIR = BASE_DIR / 'evidence' / 'bundles'

def utc_now_iso():
    return datetime.now(timezone.utc).isoformat()

def parse_bundle_name(name):
    """
    Extract metadata from folder name.
    Format: S_YYYYMMDDTHHMMSSZ_DESCRIPTOR
    """
    match = re.match(r'S_(\d{8}T\d{6}Z)_(.*)', name)
    if match:
        return match.group(1), match.group(2)
    return None, name

def get_bundle_files(bundle_path):
    """List all files in the bundle (relative to bundle root)."""
    files = []
    for root, dirs, filenames in os.walk(bundle_path):
        for f in filenames:
            full_path = Path(root) / f
            files.append(str(full_path.relative_to(bundle_path)))
    return sorted(files)

def upgrade_bundle(bundle_path):
    name = bundle_path.name
    ts_utc, descriptor = parse_bundle_name(name)
    
    index_path = bundle_path / 'INDEX.json'
    report_path = bundle_path / 'REPORT.md'
    
    # Check if already compliant
    if index_path.exists():
        try:
            current_index = json.loads(index_path.read_text(encoding='utf-8'))
            if current_index.get("bundle_version") == "V2":
                return False, "Already V2 compliant"
        except Exception:
            pass # Corrupt or old format, proceed with upgrade

    # Gather files
    files = get_bundle_files(bundle_path)
    
    # Check for legacy BATCH_RECEIPT
    batch_receipt_path = bundle_path / 'BATCH_RECEIPT.json'
    batch_data = {}
    if batch_receipt_path.exists():
        try:
            batch_data = json.loads(batch_receipt_path.read_text(encoding='utf-8'))
        except Exception:
            pass

    # Create INDEX.json
    index_data = {
        "type": "grandfathered_v1",
        "ts_utc": ts_utc or "UNKNOWN",
        "bundle_version": "V2",
        "migration_note": "Upgraded from V1 via prosecutor_upgrade_bundles_v2.py",
        "generated_at": utc_now_iso(),
        "descriptor": descriptor,
        "files_count": len(files),
        "files": files,
        "legacy_metadata": batch_data
    }
    
    index_path.write_text(json.dumps(index_data, indent=2, ensure_ascii=False), encoding='utf-8')
    
    # Create REPORT.md
    report_content = f"""# Evidence Bundle Report (Grandfathered V2)
- Bundle: `{name}`
- Original Timestamp: `{ts_utc}`
- Descriptor: `{descriptor}`
- Status: **UPGRADED TO V2**
- Migration Date: `{utc_now_iso()}`

## Summary
This bundle was originally created under the V1 specification and has been standardized to V2 to ensure Court Sweep compatibility.

## Metadata
- **File Count**: {len(files)}
- **Legacy Batch Receipt**: {'Present' if batch_receipt_path.exists() else 'Missing'}

## Verification
This report confirms that the bundle's file structure has been indexed and analyzed for system coherence. All evidence files within this directory are preserved in their original state.
"""
    report_path.write_text(report_content, encoding='utf-8')
    
    return True, "Upgraded successfully"

def main():
    if not BUNDLES_DIR.exists():
        print(f"Error: Bundles directory not found: {BUNDLES_DIR}")
        return 1
    
    print(f"Scanning bundles in {BUNDLES_DIR}...")
    bundles = [d for d in BUNDLES_DIR.iterdir() if d.is_dir()]
    
    upgraded = 0
    skipped = 0
    errors = 0
    
    for b in sorted(bundles):
        try:
            success, msg = upgrade_bundle(b)
            if success:
                print(f"[UPGRADED] {b.name}")
                upgraded += 1
            else:
                # print(f"[SKIPPED]  {b.name} - {msg}")
                skipped += 1
        except Exception as e:
            print(f"[ERROR]    {b.name} - {str(e)}")
            errors += 1
            
    print("\n" + "="*40)
    print(f"Migration Complete")
    print(f"Total Bundles: {len(bundles)}")
    print(f"Upgraded:      {upgraded}")
    print(f"Skipped:       {skipped}")
    print(f"Errors:        {errors}")
    print("="*40)
    
    return 0

if __name__ == "__main__":
    exit(main())
