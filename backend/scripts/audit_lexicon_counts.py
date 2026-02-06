import sqlite3
import json
from pathlib import Path

BASE_DIR = Path().resolve()
DB_PATH = BASE_DIR / "data" / "memory.db"
LEXICON_ROOT = BASE_DIR / "anchors" / "canon" / "definitions" / "Lexical Canon Anchors"

def main():
    if not DB_PATH.exists():
        print(f"Error: DB not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    out_lines = []
    out_lines.append(f"{'Letter':<10} | {'JSON Count':<12} | {'DB Count':<12} | {'Status'}")
    out_lines.append("-" * 55)

    total_json = 0
    total_db = 0

    for char in letters:
        json_path = LEXICON_ROOT / char / f"{char}.json"
        anchor_id = f"lexicon_{char}"
        
        json_count = 0
        if json_path.exists():
            try:
                with open(json_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    json_count = len(data.get("entries", []))
            except Exception as e:
                out_lines.append(f"Error reading {json_path}: {e}")
        
        cursor.execute("SELECT COUNT(*) FROM chunks WHERE anchor_id=?", (anchor_id,))
        db_count = cursor.fetchone()[0]
        
        status = "MATCH" if json_count == db_count else "MISMATCH"
        if json_count > 0 and db_count == 0:
            status = "MISSING"
        
        out_lines.append(f"{char:<10} | {json_count:<12} | {db_count:<12} | {status}")
        
        total_json += json_count
        total_db += db_count

    conn.close()
    out_lines.append("-" * 55)
    out_lines.append(f"{'TOTAL':<10} | {total_json:<12} | {total_db:<12} | {'OK' if total_json == total_db else 'FAIL'}")

    out_text = "\n".join(out_lines)
    print(out_text)
    with open("audit_results_utf8.txt", "w", encoding="utf-8") as f:
        f.write(out_text)

if __name__ == "__main__":
    main()
