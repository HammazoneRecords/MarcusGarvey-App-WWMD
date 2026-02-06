# scripts/inspect_anchor_chunks.py
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "memory.db"

def main():
    if not DB_PATH.exists():
        print(f"DB missing: {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    try:
        rows = conn.execute(
            "SELECT anchor_id, COUNT(*) FROM chunks GROUP BY anchor_id ORDER BY anchor_id"
        ).fetchall()

        print("-" * 50)
        print(f"{'ANCHOR_ID':<35} | {'CHUNKS':<10}")
        print("-" * 50)
        total = 0
        for rid, count in rows:
            print(f"{rid:<35} | {count:<10}")
            total += count
        print("-" * 50)
        print(f"{'TOTAL':<35} | {total:<10}")
    finally:
        conn.close()

if __name__ == "__main__":
    main()
