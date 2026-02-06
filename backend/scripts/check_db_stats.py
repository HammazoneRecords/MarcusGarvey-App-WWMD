import sqlite3
import os

try:
    conn = sqlite3.connect('data/memory.db')
    chunks = conn.execute("SELECT COUNT(*) FROM chunks").fetchone()[0]
    anchors = conn.execute("SELECT COUNT(*) FROM anchors").fetchone()[0]
    print(f"Chunks: {chunks}")
    print(f"Anchors: {anchors}")
    conn.close()
except Exception as e:
    print(f"Error: {e}")
