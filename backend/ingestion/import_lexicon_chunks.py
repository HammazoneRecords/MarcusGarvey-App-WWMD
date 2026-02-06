import sqlite3
from datetime import datetime
from pathlib import Path
import PyPDF2

# -----------------------------
# CONFIG
# -----------------------------

IMPORT_SESSION_ID = "pdf_solobility_2025-12-20"

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "memory.db"

# -----------------------------
# CORE FUNCTION
# -----------------------------

def import_pdf(anchor_id: str, pdf_path: Path):
    reader = PyPDF2.PdfReader(str(pdf_path))
    conn = sqlite3.connect(DB_PATH)

    try:
        for i, page in enumerate(reader.pages, start=1):
            text = page.extract_text()

            if not text or not text.strip():
                continue

            chunk_id = f"{anchor_id}:page:{i}"

            conn.execute(
                """
                INSERT INTO chunks (
                    chunk_id,
                    anchor_id,
                    anchor_locator,
                    lexicon_word,
                    content,
                    truth_type,
                    mutation_mode,
                    confidence,
                    import_session_id,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    chunk_id,
                    anchor_id,
                    f"page:{i}",
                    None,                     # lexicon_word (NOT APPLICABLE)
                    text.strip(),
                    "interpretive",
                    "re-index-only",
                    None,
                    IMPORT_SESSION_ID,
                    datetime.utcnow().isoformat(),
                ),
            )

        conn.commit()
        print(f"[OK] Imported PDF chunks for {anchor_id}")

    finally:
        conn.close()

# -----------------------------
# SCRIPT ENTRY POINT
# -----------------------------

if __name__ == "__main__":
    import_pdf(
        anchor_id="solobility_book_v1",
        pdf_path=Path("anchors/canon/book_of_solobility/book_of_solobility_v1.pdf"),
    )
