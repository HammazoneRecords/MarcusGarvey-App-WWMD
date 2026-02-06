import sqlite3
import json
from pathlib import Path
from datetime import datetime, timezone

BASE_DIR = Path().resolve()
DB_PATH = BASE_DIR / "data" / "memory.db"
REGISTRY_PATH = BASE_DIR / "docs" / "ANCHOR_REGISTRY_PLAN.json"
SID = "S_20251224T233858Z_LEXICON_AZ_FULL"

def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def main():
    with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
        anchors = json.load(f)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    inserted = 0
    now = utc_now_iso()
    
    for a in anchors:
        aid = a["anchor_id"]
        cursor.execute("SELECT 1 FROM anchors WHERE anchor_id=?", (aid,))
        if cursor.fetchone():
            continue
            
        print(f"Registering missing anchor: {aid}")
        cursor.execute(
            """
            INSERT INTO anchors (
                anchor_id, anchor_type, title, source_path,
                source_format, status, provenance,
                import_session_id, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
            """,
            (
                aid,
                a["anchor_type"],
                a["title"],
                a["source_path"],
                a["source_format"],
                a["status"],
                a["provenance"],
                SID,
                now
            )
        )
        inserted += 1
    
    conn.commit()
    conn.close()
    print(f"DONE: registered {inserted} new anchors.")

if __name__ == "__main__":
    main()
