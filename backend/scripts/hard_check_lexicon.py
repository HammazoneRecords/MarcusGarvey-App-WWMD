# scripts/hard_check_lexicon.py
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "memory.db"

def main():
    if not DB_PATH.exists():
        print(f"FAIL: DB not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    missing = []
    zero_count = []

    print("-" * 40)
    print(f"{'Letter':<10} | {'DB Count':<10}")
    print("-" * 40)

    for char in letters:
        anchor_id = f"lexicon_{char}"
        cursor.execute("SELECT COUNT(*) FROM chunks WHERE anchor_id=?", (anchor_id,))
        count = cursor.fetchone()[0]
        
        print(f"{char:<10} | {count:<10}")
        
        if count == 0:
            zero_count.append(char)

    conn.close()
    print("-" * 40)

    if zero_count:
        print(f"FAIL: Zero counts found for: {', '.join(zero_count)}")
        exit(1)
    else:
        print("PASS: Chunks exist for every letter (A-Z).")
        exit(0)

if __name__ == "__main__":
    main()
