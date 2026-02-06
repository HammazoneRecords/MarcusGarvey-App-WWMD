#!/usr/bin/env python3
"""
Unified Ingestion Script for Marcus Garvey App

Orchestrates the entire ingestion lifecycle in one pass:
1. Schema Fix (Upgrade anchors table to V2)
2. Anchor Registration (8 Marcus BOX PDFs)
3. Content Chunking (Page-by-page extraction)
4. Receipt Generation (V2 Prosecutor-grade)
5. Proof Chain Generation (Merkle Tree + Evidence Bundle)

Target: Marcus Garvey Corpus (8 PDFs)
"""

import hashlib
import json
import sqlite3
import sys
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any

# =========================
# CONFIG & PATHS
# =========================

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from utils.sid import get_active_sid

DB_PATH = BASE_DIR / "data" / "memory.db"
EVIDENCE_ROOT = BASE_DIR / "evidence"
MARCUS_BOX = BASE_DIR / "anchors/canon/Marcus BOX"
STATE_PATH = BASE_DIR / "docs" / "STATE.json"

CHUNK_NAMESPACE_PREFIX = "SOLOB|V2|CHUNK|PDF_PAGE|MARCUS_CORPUS"

# PDF Definitions
MARCUS_PDFS = [
    ("marcus_garvey_teachers_notes", "CC_MarcusGarvey_Teachers_Notes.pdf", "Marcus Garvey Teachers Notes"),
    ("marcus_garvey_selected_writings", "Selected Writings and Speeches of Marcus Garvey (Marcus Garvey) (Z-Library).pdf", "Selected Writings and Speeches"),
    ("marcus_garvey_philosophy_opinions", "eBook Phil and Opinions.pdf", "Philosophy and Opinions of Marcus Garvey"),
    ("marcus_garvey_memorial_collection", "garvey-amymemorialcollectiononmarcusgarvey1776-1971.pdf", "Amy Jacques Garvey Memorial Collection"),
    ("marcus_garvey_timeline", "marcus g timeline.pdf", "Marcus Garvey Timeline"),
    ("marcus_garvey_unia_papers", "marcus g unia papers 1910-1920 vol 11.pdf", "UNIA Papers Vol 11"),
    ("marcus_garvey_article", "marcus-garvey-article.pdf", "Biographical Article"),
    ("marcus_garvey_message_to_people", "message-to-the-people_-the-course-of-afric-marcus-garvey.pdf", "Message to the People")
]

# =========================
# HELPERS
# =========================

def utc_now() -> str:
    """Current UTC timestamp ISO format."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def sha256_file(path: Path) -> str:
    """Calculate file SHA256 efficiently."""
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(4096 * 4096), b""):
            h.update(chunk)
    return h.hexdigest()

def sha256_text(text: str) -> str:
    """Calculate SHA256 of text string."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def get_session_id() -> str:
    """Retrieve active session ID."""
    return get_active_sid()

# =========================
# 1. SCHEMA FIX
# =========================

def upgrade_schema(conn: sqlite3.Connection):
    """Upgrade database schema to V2."""
    print("[SCHEMA] Checking schema...")
    
    # Check if we need to upgrade anchors table
    cursor = conn.execute("PRAGMA table_info(anchors)")
    columns = {row[1] for row in cursor.fetchall()}
    
    required_columns = {"sha256", "description", "size_bytes", "canonical_path"}
    
    if not required_columns.issubset(columns):
        print("[SCHEMA] Upgrading anchors table to V2...")
        
        # Drop and recreate (since data was reset, this is safe)
        conn.execute("DROP TABLE IF EXISTS anchors")
        
        conn.execute("""
            CREATE TABLE anchors (
                anchor_id TEXT PRIMARY KEY,
                title TEXT,
                description TEXT,
                format TEXT,
                canonical_path TEXT,
                sha256 TEXT,
                size_bytes INTEGER,
                created_at TEXT
            )
        """)
        conn.commit()
        print("  ✓ Schema upgraded")
    else:
        print("  ✓ Schema already V2")

# =========================
# 2. INGESTION LOGIC
# =========================

def extract_pages(pdf_path: Path) -> List[str]:
    """Extract text from PDF pages using PyMuPDF."""
    try:
        import fitz
    except ImportError:
        print("ERROR: PyMuPDF (fitz) not installed.")
        sys.exit(1)
        
    doc = fitz.open(pdf_path)
    pages = []
    for i in range(doc.page_count):
        text = doc.load_page(i).get_text("text") or ""
        pages.append(text.strip())
    return pages

def chunk_id_for(anchor_id: str, file_sha: str, page_num: int) -> str:
    """Generate deterministic chunk ID."""
    raw = f"{CHUNK_NAMESPACE_PREFIX}|{anchor_id}|{file_sha}|{page_num}"
    return sha256_text(raw)

def ingest_pdf(conn: sqlite3.Connection, anchor_def: tuple, session_id: str) -> Dict[str, Any]:
    """Ingest a single PDF: Register anchor -> Chunk -> Receipt."""
    
    anchor_id, filename, title = anchor_def
    pdf_path = MARCUS_BOX / filename
    
    if not pdf_path.exists():
        print(f"  [SKIP] File not found: {filename}")
        return None

    print(f"  > Processing: {title}...")
    
    # 1. Calc Metadata
    file_sha = sha256_file(pdf_path)
    file_size = pdf_path.stat().st_size
    
    # 2. Register Anchor
    conn.execute(
        """
        INSERT OR REPLACE INTO anchors 
        (anchor_id, title, description, format, canonical_path, sha256, size_bytes, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            anchor_id, 
            title, 
            f"Marcus Garvey Corpus: {title}", 
            "PDF",
            str(pdf_path.relative_to(BASE_DIR).as_posix()), 
            file_sha, 
            file_size, 
            utc_now()
        )
    )
    
    # 3. Chunk Pages
    pages = extract_pages(pdf_path)
    chunks_inserted = 0
    
    for i, content in enumerate(pages):
        if not content: continue # Skip empty pages
        
        page_num = i + 1
        cid = chunk_id_for(anchor_id, file_sha, page_num)
        locator = f"pdf:page:{page_num:04d}"
        
        try:
            conn.execute(
                """
                INSERT INTO chunks 
                (chunk_id, anchor_id, anchor_locator, content, truth_type, mutation_mode, import_session_id, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    cid,
                    anchor_id,
                    locator,
                    content,
                    "empirical",
                    "append-only",
                    session_id,
                    utc_now()
                )
            )
            chunks_inserted += 1
        except sqlite3.IntegrityError:
            print(f"    [WARN] Duplicate chunk {cid} skipped")
            
    conn.commit()
    print(f"    ✓ Inserted {chunks_inserted} chunks")

    # 4. Generate Receipt Data
    receipt = {
        "receipt_version": "V2",
        "intent": "MARCUS_APP_INGESTION",
        "anchor_id": anchor_id,
        "source_path": str(pdf_path.relative_to(BASE_DIR).as_posix()),
        "manifest_entry_sha256": file_sha,
        "import_session_id": session_id,
        "generated_utc": utc_now(),
        "pdf": {
            "pages_total": len(pages),
            "pages_inserted": chunks_inserted
        },
        "db_delta": chunks_inserted
    }
    return receipt

# =========================
# 3. PROOF CHAIN
# =========================

def generate_proof_chain(session_id: str, receipts: List[Dict]):
    """Generate Merkle Tree and Evidence Bundle."""
    print("\n[CHAIN] Generating Proof Chain...")
    
    receipt_dir = EVIDENCE_ROOT / session_id / "RECEIPTS"
    receipt_dir.mkdir(parents=True, exist_ok=True)
    
    # Write receipts to disk
    hashes = []
    
    for r in receipts:
        anchor_id = r['anchor_id']
        filename = f"RECEIPT_{anchor_id}.json"
        path = receipt_dir / filename
        
        json_bytes = json.dumps(r, indent=2).encode('utf-8')
        path.write_bytes(json_bytes)
        hashes.append(hashlib.sha256(json_bytes).hexdigest())
    
    # Simple Merkle Root (Hash of concatenated receipt hashes)
    hashes.sort()
    merkle_root = hashlib.sha256("".join(hashes).encode('utf-8')).hexdigest()
    
    # Create Index Bundle
    bundle = {
        "bundle_version": "V2",
        "session_id": session_id,
        "created_utc": utc_now(),
        "merkle_root": merkle_root,
        "receipt_count": len(receipts),
        "receipt_hashes": hashes,
        "purpose": "Marcus Garvey App Corpus Baseline"
    }
    
    bundle_path = EVIDENCE_ROOT / session_id / "INDEX.json"
    bundle_path.write_text(json.dumps(bundle, indent=2), encoding="utf-8")
    
    # Generate Report
    report = f"""# Evidence Bundle Report
    
**Session**: {session_id}
**Created**: {utc_now()}
**Merkle Root**: `{merkle_root}`

## Ingested Anchors
"""
    for r in receipts:
        report += f"- **{r['anchor_id']}**: {r['db_delta']} chunks ({r['source_path']})\n"
        
    report_path = EVIDENCE_ROOT / session_id / "REPORT.md"
    report_path.write_text(report, encoding="utf-8")
    
    print(f"  ✓ Evidence Bundle created at {bundle_path}")

# =========================
# MAIN
# =========================

def main():
    print("="*60)
    print(" UNIFIED MARCUS GARVEY INGESTION")
    print("="*60)
    
    session_id = get_session_id()
    print(f"Active Session: {session_id}\n")
    
    conn = sqlite3.connect(DB_PATH)
    
    # 1. Fix Schema
    upgrade_schema(conn)
    
    # 2. Ingest Corpus
    all_receipts = []
    print("\n[INGEST] Processing Corpus...")
    
    for anchor_def in MARCUS_PDFS:
        receipt = ingest_pdf(conn, anchor_def, session_id)
        if receipt:
            all_receipts.append(receipt)
            
    conn.close()
    
    # 3. Create Proof Chain
    if all_receipts:
        generate_proof_chain(session_id, all_receipts)
    else:
        print("\n[WARN] No receipts generated. Nothing to chain.")
        
    print("\n" + "="*60)
    print(" UNIFIED RUN COMPLETE")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
