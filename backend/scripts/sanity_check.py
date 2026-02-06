# scripts/sanity_check.py
from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path

from state_guard import get_state, require_allowed

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "memory.db"


def sanity_check(allow_observe: bool = False) -> None:
    state = get_state()
    print(f"Current STGRAIL state: {state}")

    # Strict by default: require RECORD (existing behavior)
    # But allow a read-only audit mode in OBSERVE if explicitly requested.
    if state != "RECORD":
        if allow_observe and state == "OBSERVE":
            print("NOTE: Running READ-ONLY sanity audit in OBSERVE (allowed by flag).")
        else:
            # preserve STGRAIL discipline
            require_allowed("run_script")

    if not DB_PATH.exists():
        raise FileNotFoundError("memory.db does not exist. Run init_db.py first (via recorder).")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        conn.execute("PRAGMA foreign_keys = ON;")
        print("Running sanity checks...\n")

        required_tables = {
            "anchors",
            "chunks",
            "provenance_notes",
            "runs",
            "run_citations",
        }

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        existing_tables = {row[0] for row in cursor.fetchall()}

        missing_tables = required_tables - existing_tables
        if missing_tables:
            raise RuntimeError(f"Missing tables: {sorted(missing_tables)}")
        print("All required tables present.")

        cursor.execute("SELECT COUNT(*) FROM anchors;")
        anchor_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM chunks;")
        chunk_count = cursor.fetchone()[0]

        if chunk_count > 0 and anchor_count == 0:
            raise RuntimeError("Chunks exist but no anchors registered.")
        print(f"Anchors: {anchor_count}, Chunks: {chunk_count}")

        cursor.execute("SELECT COUNT(*) FROM anchors WHERE import_session_id IS NULL;")
        bad_anchors = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM chunks WHERE import_session_id IS NULL;")
        bad_chunks = cursor.fetchone()[0]

        if bad_anchors > 0 or bad_chunks > 0:
            raise RuntimeError(
                f"Missing import_session_id (anchors: {bad_anchors}, chunks: {bad_chunks})"
            )
        print("import_session_id present on all anchors and chunks.")

        cursor.execute(
            """
            SELECT COUNT(*) FROM chunks
            WHERE anchor_locator LIKE 'lexicon:%'
              AND lexicon_word IS NULL;
            """
        )
        bad_lexicon = cursor.fetchone()[0]
        if bad_lexicon > 0:
            raise RuntimeError(f"{bad_lexicon} lexicon chunks missing lexicon_word.")
        print("Lexicon chunks correctly populated (where applicable).")

        cursor.execute(
            """
            SELECT COUNT(*) FROM run_citations rc
            LEFT JOIN runs r ON r.run_id = rc.run_id
            LEFT JOIN chunks c ON c.chunk_id = rc.chunk_id
            WHERE r.run_id IS NULL OR c.chunk_id IS NULL;
            """
        )
        broken_edges = cursor.fetchone()[0]
        if broken_edges > 0:
            raise RuntimeError(f"run_citations has {broken_edges} broken edges.")
        print("run_citations edges are valid.")

        print("\nSANITY CHECK PASSED - DATABASE IS COHERENT.")
    finally:
        conn.close()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--allow-observe",
        action="store_true",
        help="Allow running sanity_check in OBSERVE in READ-ONLY mode.",
    )
    args = ap.parse_args()
    sanity_check(allow_observe=args.allow_observe)


if __name__ == "__main__":
    main()
