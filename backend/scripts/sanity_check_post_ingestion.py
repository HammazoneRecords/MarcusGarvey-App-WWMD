from __future__ import annotations
import os, argparse, sqlite3
from pathlib import Path
from state_guard import require_allowed

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "memory.db"

def require_recorded() -> None:
    if os.environ.get("SOLOB_RECORDED_RUN") != "1":
        raise RuntimeError("BLOCKED: must run via scripts/run_recorded.py.")

def q1(conn: sqlite3.Connection, sql: str, params=()):
    return conn.execute(sql, params).fetchone()[0]

def main() -> int:
    require_recorded()
    require_allowed("run_script")

    ap = argparse.ArgumentParser()
    ap.add_argument("--expect-anchors", type=int, default=8)
    ap.add_argument("--min-chunks", type=int, default=1)
    args = ap.parse_args()

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    try:
        fk = conn.execute("PRAGMA foreign_keys;").fetchone()[0]
        if fk != 1:
            raise SystemExit("AUDIT FAILED: foreign_keys != 1")

        integrity = conn.execute("PRAGMA integrity_check;").fetchone()[0]
        if str(integrity).lower() != "ok":
            raise SystemExit(f"AUDIT FAILED: integrity_check={integrity}")

        anchors = q1(conn, "SELECT COUNT(*) FROM anchors;")
        chunks = q1(conn, "SELECT COUNT(*) FROM chunks;")
        runs = q1(conn, "SELECT COUNT(*) FROM runs;")
        cites = q1(conn, "SELECT COUNT(*) FROM run_citations;")

        print(f"counts: anchors={anchors} chunks={chunks} runs={runs} run_citations={cites}")

        if anchors != args.expect_anchors:
            raise SystemExit(f"AUDIT FAILED: expected anchors={args.expect_anchors}, got {anchors}")
        if chunks < args.min_chunks:
            raise SystemExit(f"AUDIT FAILED: expected chunks>={args.min_chunks}, got {chunks}")
        if runs != 0 or cites != 0:
            raise SystemExit("AUDIT FAILED: runs/run_citations must still be 0 at this stage.")

        # Orphans check
        orphan = q1(conn, """
          SELECT COUNT(*) FROM chunks c
          LEFT JOIN anchors a ON a.anchor_id=c.anchor_id
          WHERE a.anchor_id IS NULL;
        """)
        if orphan != 0:
            raise SystemExit(f"AUDIT FAILED: orphan_chunks={orphan}")

        print("POST-INGEST SANITY: PASS")
        return 0
    finally:
        conn.close()

if __name__ == "__main__":
    raise SystemExit(main())
