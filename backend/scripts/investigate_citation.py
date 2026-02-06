#!/usr/bin/env python3
"""
Investigate citation accuracy issue in ARK database
"""
import sqlite3
import sys

# Windows console safety
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DB_PATH = "backend/data/memory.db"

conn = sqlite3.connect(DB_PATH)

# Find chunks containing "African Communities"
print("=" * 60)
print("Searching for 'African Communities' in chunks...")
print("=" * 60)

cursor = conn.execute("""
    SELECT chunk_id, anchor_id, anchor_locator, content 
    FROM chunks 
    WHERE content LIKE '%African Communities%'
    LIMIT 5
""")

for row in cursor.fetchall():
    chunk_id, anchor_id, locator, content = row
    print(f"\nChunk ID: {chunk_id}")
    print(f"Anchor: {anchor_id}")
    print(f"Locator: {locator}")
    print(f"Content (first 400 chars):\n{content[:400]}...")
    print("-" * 60)

# Also check what's on page 10 specifically
print("\n" + "=" * 60)
print("All chunks from page 0010 of selected_writings:")
print("=" * 60)

cursor = conn.execute("""
    SELECT chunk_id, substr(content, 1, 300)
    FROM chunks 
    WHERE anchor_id = 'marcus_garvey_selected_writings'
      AND anchor_locator = 'pdf:page:0010'
""")

for row in cursor.fetchall():
    chunk_id, content_preview = row
    print(f"\nChunk {chunk_id}:")
    print(content_preview)
    print("-" * 60)

conn.close()
