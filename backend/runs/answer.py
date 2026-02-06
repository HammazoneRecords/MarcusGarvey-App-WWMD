#!/usr/bin/env python3
"""
Simple Retrieval Script for Marcus Garvey App Corpus
"""

import sqlite3
import sys
import argparse
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "memory.db"

def main():
    parser = argparse.ArgumentParser(description="Marcus Garvey App Retrieval")
    parser.add_argument("--query", required=True, help="Search query")
    parser.add_argument("--limit", type=int, default=5, help="Max results")
    args = parser.parse_args()
    
    if not DB_PATH.exists():
        print(f"Error: Database not found at {DB_PATH}")
        sys.exit(1)
        
    conn = sqlite3.connect(DB_PATH)
    
    # Simple keyword search (LIKE)
    # In a real RAG system, this would be vector search or FTS5
    query_pattern = f"%{args.query}%"
    
    print(f"Searching for: '{args.query}'...")
    print("-" * 60)
    
    cursor = conn.execute(
        """
        SELECT chunk_id, anchor_id, anchor_locator, content, created_at
        FROM chunks 
        WHERE content LIKE ? 
        LIMIT ?
        """, 
        (query_pattern, args.limit)
    )
    
    results = cursor.fetchall()
    
    if not results:
        print("No results found.")
    else:
        for i, row in enumerate(results, 1):
            cid, anchor, loc, content, created = row
            snippet = content[:200].replace("\n", " ") + "..."
            print(f"[{i}] {anchor} | {loc}")
            print(f"    {snippet}")
            print("-" * 60)
            
    conn.close()

if __name__ == "__main__":
    main()