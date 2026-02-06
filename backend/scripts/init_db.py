# scripts/init_db.py
from __future__ import annotations

import os
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

DB_PATH = DATA_DIR / "memory.db"
SCHEMA_PATH = DATA_DIR / "schema.sql"


def require_recorded_run() -> None:
    if os.environ.get("SOLOB_RECORDED_RUN") != "1":
        raise RuntimeError(
            "BLOCKED: init_db.py must be executed via scripts/run_recorded.py "
            "(NO UNRECORDED SHUFFLES)."
        )


def init_db() -> None:
    require_recorded_run()

    print("Intent:", os.environ.get("SOLOB_HUMAN_INTENT", "(none)"))

    if not SCHEMA_PATH.exists():
        raise FileNotFoundError(f"schema.sql not found at {SCHEMA_PATH}")

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute("PRAGMA foreign_keys = ON;")
        schema_sql = SCHEMA_PATH.read_text(encoding="utf-8")
        conn.executescript(schema_sql)
        conn.commit()
        print("Database initialized successfully.")
        print(f"DB: {DB_PATH}")
        print(f"Schema: {SCHEMA_PATH}")
    finally:
        conn.close()


if __name__ == "__main__":
    init_db()
