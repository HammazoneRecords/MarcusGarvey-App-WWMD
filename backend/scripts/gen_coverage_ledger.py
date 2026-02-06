# scripts/gen_coverage_ledger.py
import sqlite3, json, string, sys
from datetime import datetime, timezone
from pathlib import Path

def main(sid):
    conn = sqlite3.connect("data/memory.db")
    cur = conn.cursor()
    letters = {}
    total = 0
    for L in string.ascii_uppercase:
        aid = f"lexicon_{L}"
        cur.execute("SELECT COUNT(*) FROM chunks WHERE anchor_id=?", (aid,))
        db_count = cur.fetchone()[0]
        letters[L] = {"anchor_id": aid, "db_count": db_count, "status": "OK" if db_count>0 else "ZERO"}
        total += db_count
    
    out = {
      "receipt_version": "V1",
      "intent": "PROSECUTOR_LEXICON_AZ_COVERAGE_LEDGER",
      "generated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
      "import_session_id": sid,
      "lexicon_total_chunks": total,
      "letters": letters
    }
    print(json.dumps(out, indent=2))
    conn.close()

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "S_NO_SID")
