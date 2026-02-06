import sqlite3
from datetime import datetime
from pathlib import Path
import json

# -----------------------------
# PATHS
# -----------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "memory.db"

# -----------------------------
# FIRST AUDITED RUN
# -----------------------------

def log_first_run():
    conn = sqlite3.connect(DB_PATH)

    try:
        run_id = "run_0001"

        input_query = "What is Solob?"

        output_text = (
            "Solob is treated as a condition of alignment rather than a fixed concept, "
            "defined through its usage across canonical anchors."
        )

        cited_chunk_ids = [
            "solobility_book_v1:page:1"
        ]

        conn.execute(
            """
            INSERT INTO runs (
                run_id,
                input_query,
                output_text,
                created_at,
                verdict
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                run_id,
                input_query,
                output_text,
                datetime.utcnow().isoformat(),
                "ok",
            ),
        )

        for chunk_id in cited_chunk_ids:
            conn.execute(
                """
                INSERT INTO run_citations (
                    run_id,
                    chunk_id
                )
                VALUES (?, ?)
                """,
                (
                    run_id,
                    chunk_id,
                ),
            )

        conn.commit()
        print("[OK] First audited run logged successfully.")

    finally:
        conn.close()

# -----------------------------
# SCRIPT ENTRY POINT
# -----------------------------

if __name__ == "__main__":
    log_first_run()
