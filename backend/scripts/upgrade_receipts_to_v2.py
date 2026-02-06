#!/usr/bin/env python3
"""
Upgrade Legacy Receipts to V2 Schema

Scans evidence/ for old receipts and upgrades them to V2 format.
Creates V2-compliant receipts in RECEIPTS/ subdirectories.
"""
import json
import sqlite3
from pathlib import Path
from datetime import datetime

# Repo root
REPO_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = REPO_ROOT / "data" / "memory.db"


def get_current_chunk_count():
    """Get current chunk count from database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM chunks")
    count = cursor.fetchone()[0]
    conn.close()
    return count


def upgrade_legacy_receipt(old_receipt_path: Path) -> dict:
    """
    Upgrade a legacy receipt to V2 format.
    
    Returns the V2-compliant receipt dict.
    """
    # Load old receipt
    old_receipt = json.loads(old_receipt_path.read_text(encoding='utf-8'))
    
    # Extract session ID from path or receipt
    session_id = old_receipt.get('import_session_id', 'UNKNOWN_SESSION')
    
    # Extract anchor_id
    anchor_id = old_receipt.get('anchor_id', 'unknown_anchor')
    
    # Determine intent from old receipt or filename
    if 'letter' in old_receipt:
        intent = f"LEGACY_LEXICON_IMPORT_{old_receipt['letter']}"
    else:
        intent = f"LEGACY_IMPORT_{anchor_id.upper()}"
    
    # Get timestamps
    generated_utc = old_receipt.get('ended_utc', old_receipt.get('started_utc', datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")))
    
    # Get source path
    source_path = old_receipt.get('source_json', old_receipt.get('source_path', f'anchors/canon/{anchor_id}'))
    
    # Build V2 receipt
    v2_receipt = {
        "receipt_version": "V2",
        "intent": intent,
        "generated_utc": generated_utc,
        "import_session_id": session_id,
        "anchor_id": anchor_id,
        "source_path": source_path,
        "manifest_entry_sha256": old_receipt.get('manifest_entry_sha256', 'legacy_no_hash_available'),
        
        "db": {
            "path": "data/memory.db",
            "chunks_before": 0,  # Unknown for legacy
            "chunks_after": old_receipt.get('inserted', 0),
            "delta": old_receipt.get('inserted', 0)
        },
        
        "strict_rules": {
            "chunk_collision": "STOP",
            "missing_anchor": "STOP"
        }
    }
    
    # Add type-specific fields if present
    if 'letter' in old_receipt:
        v2_receipt['lexicon'] = {
            "letter": old_receipt['letter'],
            "entries_total": old_receipt.get('inserted', 0),
            "entries_inserted": old_receipt.get('inserted', 0)
        }
        v2_receipt['format_mode'] = old_receipt.get('format_mode', 'top_level_dict_entries')
    
    # Add timestamps section if we have start/end
    if 'started_utc' in old_receipt and 'ended_utc' in old_receipt:
        v2_receipt['timestamps'] = {
            "start_utc": old_receipt['started_utc'],
            "end_utc": old_receipt['ended_utc']
        }
    
    # Preserve legacy fields as metadata
    v2_receipt['_legacy_fields'] = {
        k: v for k, v in old_receipt.items() 
        if k not in v2_receipt and k not in ['letter', 'inserted', 'started_utc', 'ended_utc']
    }
    
    return v2_receipt


def main():
    print("=== Legacy Receipt Upgrade to V2 ===\n")
    
    # Find all receipt JSON files
    evidence_dir = REPO_ROOT / "evidence"
    receipt_files = []
    
    for session_dir in evidence_dir.glob("S_*"):
        if not session_dir.is_dir():
            continue
        
        # Check for receipts in root of session dir
        for receipt in session_dir.glob("RECEIPT_*.json"):
            receipt_files.append(receipt)
        
        # Check for receipts in RECEIPTS subdirectory
        receipts_dir = session_dir / "RECEIPTS"
        if receipts_dir.exists():
            for receipt in receipts_dir.glob("RECEIPT_*.json"):
                receipt_files.append(receipt)
    
    print(f"Found {len(receipt_files)} receipt files\n")
    
    upgraded_count = 0
    skipped_count = 0
    
    for receipt_path in receipt_files:
        try:
            # Load and check if already V2
            receipt = json.loads(receipt_path.read_text(encoding='utf-8'))
            
            if receipt.get('receipt_version') == 'V2':
                print(f"[SKIP]  SKIP: {receipt_path.relative_to(REPO_ROOT)} (already V2)")
                skipped_count += 1
                continue
            
            # Upgrade to V2
            v2_receipt = upgrade_legacy_receipt(receipt_path)
            
            # Write V2 receipt (overwrite in place)
            receipt_path.write_text(json.dumps(v2_receipt, indent=2), encoding='utf-8')
            
            print(f"[OK] UPGRADED: {receipt_path.relative_to(REPO_ROOT)}")
            upgraded_count += 1
            
        except Exception as e:
            print(f"[ERROR] ERROR: {receipt_path.relative_to(REPO_ROOT)}: {e}")
    
    print(f"\n=== Summary ===")
    print(f"[OK] Upgraded: {upgraded_count}")
    print(f"[SKIP]  Skipped (already V2): {skipped_count}")
    print(f"[STATS] Total processed: {len(receipt_files)}")
    
    # Get current chunk count
    chunk_count = get_current_chunk_count()
    print(f"\n[DB]  Current database: {chunk_count} chunks")
    
    return 0 if upgraded_count > 0 else 1


if __name__ == "__main__":
    exit(main())
