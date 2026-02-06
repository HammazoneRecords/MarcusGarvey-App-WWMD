#!/usr/bin/env python3
"""
Database Reset to Clean Baseline

Clears all chunks and anchors, creates new session for Marcus Garvey baseline.
NO BACKUP - this is a fork of the original ARK.
"""

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "memory.db"
STATE_PATH = BASE_DIR / "docs" / "STATE.json"
EVIDENCE_ROOT = BASE_DIR / "evidence"

def utc_now():
    """Generate UTC timestamp."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def create_new_session():
    """Create new session ID for Marcus Garvey baseline."""
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"S_{timestamp}_MARCUS_GARVEY_BASELINE"

def main():
    print("=" * 60)
    print("Database Reset - Clean Baseline")
    print("=" * 60)
    print()
    
    # 1. Document current state
    conn = sqlite3.connect(DB_PATH)
    chunks_before = conn.execute("SELECT COUNT(*) FROM chunks").fetchone()[0]
    anchors_before = conn.execute("SELECT COUNT(*) FROM anchors").fetchone()[0]
    
    print(f"Pre-Reset State:")
    print(f"  Chunks: {chunks_before}")
    print(f"  Anchors: {anchors_before}")
    print()
    
    # 2. Delete all chunks
    print("[RESET] Deleting all chunks...")
    conn.execute("DELETE FROM chunks")
    conn.commit()
    print("  ✓ Chunks table cleared")
    
    # 3. Delete all anchors
    print("[RESET] Deleting all anchors...")
    conn.execute("DELETE FROM anchors")
    conn.commit()
    print("  ✓ Anchors table cleared")
    
    # 4. Verify deletion
    chunks_after = conn.execute("SELECT COUNT(*) FROM chunks").fetchone()[0]
    anchors_after = conn.execute("SELECT COUNT(*) FROM anchors").fetchone()[0]
    conn.close()
    
    print()
    print(f"Post-Reset State:")
    print(f"  Chunks: {chunks_after}")
    print(f"  Anchors: {anchors_after}")
    print()
    
    if chunks_after != 0 or anchors_after != 0:
        print("[ERROR] Database reset failed!")
        return 1
    
    # 5. Create new session
    new_session_id = create_new_session()
    print(f"[CREATE] New session: {new_session_id}")
    
    # 6. Update STATE.json
    state_data = {
        "active_session_id": new_session_id,
        "created_utc": utc_now(),
        "purpose": "Marcus Garvey App Clean Baseline",
        "mode": "EXECUTE"
    }
    
    STATE_PATH.write_text(json.dumps(state_data, indent=2), encoding='utf-8')
    print(f"  ✓ Updated {STATE_PATH.relative_to(BASE_DIR)}")
    
    # 7. Generate genesis receipt
    genesis_receipt = {
        "receipt_version": "V2",
        "intent": "GENESIS_BASELINE_RESET",
        "generated_utc": utc_now(),
        "import_session_id": new_session_id,
        "action": "database_reset",
        "db": {
            "path": "data/memory.db",
            "chunks_before": chunks_before,
            "chunks_after": chunks_after,
            "anchors_before": anchors_before,
            "anchors_after": anchors_after
        },
        "purpose": "Clean baseline for Marcus Garvey App corpus ingestion"
    }
    
    receipt_dir = EVIDENCE_ROOT / new_session_id / "RECEIPTS"
    receipt_dir.mkdir(parents=True, exist_ok=True)
    
    receipt_path = receipt_dir / "RECEIPT_GENESIS_BASELINE_RESET.json"
    receipt_path.write_text(json.dumps(genesis_receipt, indent=2), encoding='utf-8')
    print(f"  ✓ Genesis receipt: {receipt_path.relative_to(BASE_DIR)}")
    
    print()
    print("=" * 60)
    print("Database Reset Complete")
    print("=" * 60)
    print()
    print(f"Ready for ingestion with session: {new_session_id}")
    print()
    
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
