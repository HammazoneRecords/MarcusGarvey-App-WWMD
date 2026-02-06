#!/usr/bin/env python3
"""
Example: Content Ingestion
Demonstrates how to ingest content into the RAG system.
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime, timezone

# Database path
DB_PATH = Path(__file__).parent.parent / "data" / "memory.db"

def create_anchor(anchor_id, title, author=None, year=None, source_type="text"):
    """Create an anchor (source document) in the database."""
    conn = sqlite3.connect(DB_PATH)
    
    try:
        conn.execute("""
            INSERT INTO anchors (anchor_id, title, author, year, source_type)
            VALUES (?, ?, ?, ?, ?)
        """, (anchor_id, title, author, year, source_type))
        conn.commit()
        print(f"✓ Created anchor: {anchor_id}")
    except sqlite3.IntegrityError:
        print(f"⚠ Anchor already exists: {anchor_id}")
    finally:
        conn.close()

def ingest_text_document(anchor_id, content, chunk_size=500):
    """
    Ingest a text document with line-level chunking.
    
    Args:
        anchor_id: ID of the anchor (must exist)
        content: Full text content
        chunk_size: Number of characters per chunk
    """
    conn = sqlite3.connect(DB_PATH)
    
    # Generate session ID
    session_id = f"S_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}_INGESTION"
    
    # Split into chunks
    chunks_created = 0
    lines_created = 0
    
    # Simple chunking by paragraphs
    paragraphs = content.split('\n\n')
    
    for i, paragraph in enumerate(paragraphs, 1):
        if not paragraph.strip():
            continue
            
        # Create parent chunk
        chunk_id = f"{anchor_id}:chunk:{i:04d}"
        chunk_locator = f"text:chunk:{i:04d}"
        
        conn.execute("""
            INSERT INTO chunks (chunk_id, anchor_id, anchor_locator, content, import_session_id)
            VALUES (?, ?, ?, ?, ?)
        """, (chunk_id, anchor_id, chunk_locator, paragraph, session_id))
        chunks_created += 1
        
        # Create line chunks
        lines = paragraph.split('\n')
        for line_num, line_text in enumerate(lines, 1):
            if not line_text.strip():
                continue
                
            line_chunk_id = f"{chunk_id}:line:{line_num}"
            line_locator = f"text:chunk:{i:04d}:line:{line_num}"
            
            conn.execute("""
                INSERT INTO line_chunks 
                (line_chunk_id, parent_chunk_id, line_number, content, anchor_locator, anchor_id, import_session_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (line_chunk_id, chunk_id, line_num, line_text, line_locator, anchor_id, session_id))
            lines_created += 1
    
    conn.commit()
    conn.close()
    
    print(f"✓ Ingested {chunks_created} chunks, {lines_created} lines")
    print(f"  Session ID: {session_id}")

def example_ingestion():
    """Example: Ingest a sample document."""
    
    # Sample content
    anchor_id = "example_001"
    title = "Example Document"
    content = """This is the first paragraph of the example document.
It contains multiple lines.
Each line will be indexed separately for precise citations.

This is the second paragraph.
It demonstrates how the system handles multi-paragraph documents.

The RAG system will be able to cite specific lines from this content.
This enables precise, verifiable citations."""
    
    # Step 1: Create anchor
    create_anchor(anchor_id, title, author="Example Author", year=2025, source_type="text")
    
    # Step 2: Ingest content
    ingest_text_document(anchor_id, content)
    
    print("\n✓ Ingestion complete!")
    print(f"  You can now query: python scripts/wwmd_ask_hybrid.py \"What does the example say?\"")

if __name__ == "__main__":
    example_ingestion()
