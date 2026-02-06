#!/usr/bin/env python3
"""
Audit Ingestion Trail - Forensic Reconstruction Script

Reality 4 (The Prosecutor): Reconstruct the complete chain of custody for all chunks.

Purpose:
- Verify every chunk can be traced back to a receipt
- Identify orphan chunks (no receipt trail)
- Reconstruct ingestion timeline
- Validate session ID coherence

Usage:
    python scripts/audit_ingestion_trail.py

Exit Codes:
    0 = All chunks accounted for
    1 = Orphans detected
    2 = Critical error
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "memory.db"
EVIDENCE_ROOT = BASE_DIR / "evidence"


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_text(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def load_all_receipts(evidence_root: Path) -> List[Dict[str, Any]]:
    """Load all V2 receipts from evidence directory"""
    receipts = []
    for receipt_path in evidence_root.glob("**/RECEIPTS/RECEIPT_*.json"):
        try:
            data = json.loads(receipt_path.read_text(encoding="utf-8"))
            data["_receipt_path"] = str(receipt_path.relative_to(BASE_DIR))
            receipts.append(data)
        except Exception as e:
            print(f"WARN: Failed to load receipt {receipt_path}: {e}", file=sys.stderr)
    return receipts


def get_all_chunks(db_path: Path) -> List[Dict[str, Any]]:
    """Query all chunks from database"""
    if not db_path.exists():
        raise FileNotFoundError(f"Database not found: {db_path}")

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        cur = conn.execute(
            """
            SELECT 
                chunk_id,
                anchor_id,
                anchor_locator,
                lexicon_word,
                import_session_id,
                created_at
            FROM chunks
            ORDER BY created_at ASC
            """
        )
        chunks = [dict(row) for row in cur.fetchall()]
        return chunks
    finally:
        conn.close()


def audit_trail(chunks: List[Dict], receipts: List[Dict]) -> Dict[str, Any]:
    """Reconstruct audit trail and identify orphans"""

    # Build receipt index by session ID
    receipt_by_sid = {}
    for r in receipts:
        sid = r.get("import_session_id")
        if sid:
            if sid not in receipt_by_sid:
                receipt_by_sid[sid] = []
            receipt_by_sid[sid].append(r)

    # Analyze chunks
    total_chunks = len(chunks)
    receipted_chunks = 0
    orphan_chunks = []
    session_summary = {}

    for chunk in chunks:
        sid = chunk.get("import_session_id")
        
        if not sid:
            orphan_chunks.append({
                "chunk_id": chunk["chunk_id"],
                "anchor_id": chunk["anchor_id"],
                "reason": "NULL import_session_id"
            })
            continue

        # Track session
        if sid not in session_summary:
            session_summary[sid] = {
                "chunks": 0,
                "has_receipt": sid in receipt_by_sid,
                "receipt_count": len(receipt_by_sid.get(sid, []))
            }
        session_summary[sid]["chunks"] += 1

        # Check if session has receipt
        if sid in receipt_by_sid:
            receipted_chunks += 1
        else:
            orphan_chunks.append({
                "chunk_id": chunk["chunk_id"],
                "anchor_id": chunk["anchor_id"],
                "import_session_id": sid,
                "reason": "no_receipt_for_session"
            })

    # Calculate statistics
    orphan_count = len(orphan_chunks)
    orphan_rate = (orphan_count / total_chunks * 100) if total_chunks > 0 else 0

    return {
        "total_chunks": total_chunks,
        "receipted_chunks": receipted_chunks,
        "orphan_chunks": orphan_count,
        "orphan_rate": f"{orphan_rate:.2f}%",
        "total_receipts": len(receipts),
        "unique_sessions": len(session_summary),
        "sessions_with_receipts": sum(1 for s in session_summary.values() if s["has_receipt"]),
        "session_summary": session_summary,
        "orphan_samples": orphan_chunks[:20],  # Show first 20 orphans
    }


def main() -> int:
    print("=" * 60)
    print("AUDIT INGESTION TRAIL - Forensic Reconstruction")
    print("=" * 60)
    print()

    # Load data
    print(f"Loading chunks from {DB_PATH}...")
    chunks = get_all_chunks(DB_PATH)
    print(f"[OK] Loaded {len(chunks)} chunks")

    print(f"Loading receipts from {EVIDENCE_ROOT}...")
    receipts = load_all_receipts(EVIDENCE_ROOT)
    print(f"[OK] Loaded {len(receipts)} receipts")
    print()

    # Audit
    print("Reconstructing audit trail...")
    result = audit_trail(chunks, receipts)

    # Report
    print()
    print("=" * 60)
    print("AUDIT RESULTS")
    print("=" * 60)
    print(f"Total Chunks:          {result['total_chunks']}")
    print(f"Receipted Chunks:      {result['receipted_chunks']}")
    print(f"Orphan Chunks:         {result['orphan_chunks']} ({result['orphan_rate']})")
    print(f"Total Receipts:        {result['total_receipts']}")
    print(f"Unique Sessions:       {result['unique_sessions']}")
    print(f"Sessions w/ Receipts:  {result['sessions_with_receipts']}")
    print()

    if result["orphan_chunks"] > 0:
        print("[WARN]  ORPHANS DETECTED")
        print()
        print("Sample orphan chunks:")
        for orphan in result["orphan_samples"]:
            print(f"  - {orphan['chunk_id'][:40]}... ({orphan['reason']})")
        print()
        print(f"See full report in evidence/audits/INGESTION_TRAIL_AUDIT_*.json")
        verdict = "FAIL"
        exit_code = 1
    else:
        print("[OK] PASS: All chunks accounted for")
        verdict = "PASS"
        exit_code = 0

    # Write detailed report
    audit_dir = BASE_DIR / "evidence" / "audits"
    audit_dir.mkdir(parents=True, exist_ok=True)

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    report_path = audit_dir / f"INGESTION_TRAIL_AUDIT_{ts}.json"

    report = {
        "audit_type": "ingestion_trail",
        "generated_utc": utc_now(),
        "verdict": verdict,
        **result
    }

    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"[OK] Report written: {report_path.relative_to(BASE_DIR)}")

    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
