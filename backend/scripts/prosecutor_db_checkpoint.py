from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict

BASE_DIR = Path(__file__).resolve().parent.parent

def utc_z() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def q1(conn: sqlite3.Connection, sql: str) -> int:
    return int(conn.execute(sql).fetchone()[0])

def main() -> int:
    ap = argparse.ArgumentParser(description="Emit DB checkpoint receipt (counts + hashes).")
    ap.add_argument("--sid", required=True)
    ap.add_argument("--db", default="data/memory.db")
    ap.add_argument("--out", required=True, help="Evidence bundle dir, e.g. evidence/<SID>")
    args = ap.parse_args()

    db_path = (BASE_DIR / args.db).resolve()
    out_dir = (BASE_DIR / args.out).resolve()

    if not db_path.exists():
        raise SystemExit(f"AUDIT FAILED: db missing: {db_path}")
    out_dir.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(db_path))
    try:
        conn.execute("PRAGMA foreign_keys = ON;")
        receipt: Dict = {
            "bundle_version": "V1",
            "generated_utc": utc_z(),
            "import_session_id": args.sid,
            "db_sha256": sha256_file(db_path),
            "counts": {
                "anchors": q1(conn, "SELECT COUNT(*) FROM anchors;"),
                "chunks": q1(conn, "SELECT COUNT(*) FROM chunks;"),
                "runs": q1(conn, "SELECT COUNT(*) FROM runs;"),
                "run_citations": q1(conn, "SELECT COUNT(*) FROM run_citations;"),
                "provenance_notes": q1(conn, "SELECT COUNT(*) FROM provenance_notes;"),
            },
        }
    finally:
        conn.close()

    out_path = out_dir / "DB_CHECKPOINT.json"
    out_path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(f"OK: wrote {out_path.as_posix()}")
    print(f"OK: counts={receipt['counts']}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
