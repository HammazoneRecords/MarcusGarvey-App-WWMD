#!/usr/bin/env python3
"""
Marcus BOX Anchor Registration

Registers all 8 Marcus Garvey PDFs as anchors in the database.
"""

import hashlib
import json
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

# Setup path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from utils.sid import get_active_sid

# =========================
# PATHS
# =========================
DB_PATH = BASE_DIR / "data" / "memory.db"
MARCUS_BOX = BASE_DIR / "anchors/canon/Marcus BOX"

# =========================
# HELPERS
# =========================

def sha256_file(path: Path) -> str:
    """Calculate file SHA256."""
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def utc_now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def register_anchor(conn, anchor_id, title, desc, pdf_path):
    """Register anchor in database."""
    sha = sha256_file(pdf_path)
    size = pdf_path.stat().st_size
    
    conn.execute(
        """
        INSERT INTO anchors (
            anchor_id, title, description, format,
            canonical_path, sha256, size_bytes, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            anchor_id,
            title,
            desc,
            "PDF",
            str(pdf_path.relative_to(BASE_DIR).as_posix()),
            sha,
            size,
            utc_now()
        )
    )
    conn.commit()
    print(f"  ✓ Registered: {anchor_id}")
    return sha

def main():
    print("=" * 70)
    print("Marcus BOX Anchor Registration")
    print("=" * 70)
    print()
    
    session_id = get_active_sid()
    print(f"Session: {session_id}")
    print()
    
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    
    # Register Marcus BOX anchors
    print("[REGISTERING] Marcus BOX anchors...")
    print()
    
    marcus_pdfs = [
        ("marcus_garvey_teachers_notes", "CC_MarcusGarvey_Teachers_Notes.pdf", "Marcus Garvey Teachers Notes"),
        ("marcus_garvey_selected_writings", "Selected Writings and Speeches of Marcus Garvey (Marcus Garvey) (Z-Library).pdf", "Selected Writings and Speeches"),
        ("marcus_garvey_philosophy_opinions", "eBook Phil and Opinions.pdf", "Philosophy and Opinions of Marcus Garvey"),
        ("marcus_garvey_memorial_collection", "garvey-amymemorialcollectiononmarcusgarvey1776-1971.pdf", "Amy Jacques Garvey Memorial Collection (1776-1971)"),
        ("marcus_garvey_timeline", "marcus g timeline.pdf", "Marcus Garvey Timeline"),
        ("marcus_garvey_unia_papers", "marcus g unia papers 1910-1920 vol 11.pdf", "UNIA Papers Volume 11 (1910-1920)"),
        ("marcus_garvey_article", "marcus-garvey-article.pdf", "Marcus Garvey Biographical Article"),
        ("marcus_garvey_message_to_people", "message-to-the-people_-the-course-of-afric-marcus-garvey.pdf", "Message to the People - Course of African Philosophy"),
    ]
    
    anchor_manifest = []
    for anchor_id, filename, title in marcus_pdfs:
        pdf_path = MARCUS_BOX / filename
        if not pdf_path.exists():
            print(f"  [ERROR] File not found: {filename}")
            continue
            
        sha = register_anchor(conn, anchor_id, title, f"Marcus Garvey - {title}", pdf_path)
        anchor_manifest.append({
            "anchor_id": anchor_id,
            "path": str(pdf_path.relative_to(BASE_DIR).as_posix()),
            "sha256": sha,
            "size_bytes": pdf_path.stat().st_size,
            "title": title
        })
    
    # Save anchor manifest
    manifest_path = MARCUS_BOX / "anchors_manifest.json"
    manifest_path.write_text(json.dumps({
        "manifest_version": "V1",
        "created_utc": utc_now(),
        "anchors": anchor_manifest
    }, indent=2), encoding="utf-8")
    print()
    print(f"  ✓ Manifest saved: {manifest_path.relative_to(BASE_DIR)}")
    
    conn.close()
    
    print()
    print("=" * 70)
    print("Anchor Registration Complete")
    print("=" * 70)
    print(f"Total anchors: {len(anchor_manifest)}")
    print()
    print("NEXT STEP: Run python scripts/chunk_marcus_box_pdfs.py")
    print()
    
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
