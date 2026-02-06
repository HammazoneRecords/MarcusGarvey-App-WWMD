# scripts/chunk_bos_pages_pilot.py
"""
ARTISAN: BoS1v1 PDF page chunk pilot (mechanical, no embeddings, no interpretation)

? One chunk per PDF page
? Deterministic V2 chunk IDs (collision-proof)
? Strict STOP on any violation
? Writes receipt into evidence/<SID>/

Reality: 3 ? Artisan
"""

from __future__ import annotations

import hashlib
import json
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import List

# =========================
# CONFIG (CANONICAL)
# =========================

ANCHOR_ID = "book_of_solobility_v1"
PDF_REL_PATH = Path("anchors/canon/book_of_solobility/BoS1v1.pdf")

# MUST match anchors_manifest entry sha256
MANIFEST_ENTRY_SHA256 = "ec86c62764501d41676a2237e8ff5c4a21bad3d9525bafa550b12349c9c216bd"

TRUTH_TYPE = "empirical"
MUTATION_MODE = "append-only"

DB_PATH = Path("data/memory.db")
STATE_PATH = Path("docs/STATE.json")
EVIDENCE_ROOT = Path("evidence")

CHUNK_ID_NAMESPACE = "SOLOB|V2|CHUNK|PDF_PAGE|BOOK_OF_SOLOBILITY"

# =========================
# HELPERS
# =========================

def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def sha256_text(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

def load_state() -> dict:
    return json.loads(STATE_PATH.read_text(encoding="utf-8"))

# Add repo root to path for utils import
import sys
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from utils.sid import get_active_sid

def get_import_session_id() -> str:
    return get_active_sid()

def require_file(path: Path) -> None:
    if not path.exists():
        raise RuntimeError(f"STOP: missing required file: {path}")

def require_anchor(conn: sqlite3.Connection) -> None:
    cur = conn.execute(
        "SELECT anchor_id FROM anchors WHERE anchor_id = ?",
        (ANCHOR_ID,),
    )
    if not cur.fetchone():
        raise RuntimeError(f"STOP: anchor_id not found in DB: {ANCHOR_ID}")

def chunk_id_for(page_num: int) -> str:
    """
    V2 namespace ? GUARANTEED non-collision with lexicon chunks
    """
    base = f"{CHUNK_ID_NAMESPACE}|{ANCHOR_ID}|{MANIFEST_ENTRY_SHA256}|{page_num}"
    return sha256_text(base)

# =========================
# PDF EXTRACTION
# =========================

def extract_pdf_pages(pdf_path: Path) -> List[str]:
    try:
        import fitz  # PyMuPDF
    except Exception as e:
        raise RuntimeError("STOP: PyMuPDF (fitz) not available") from e

    doc = fitz.open(pdf_path)
    pages: List[str] = []

    for i in range(doc.page_count):
        text = doc.load_page(i).get_text("text") or ""
        pages.append(text.strip())

    doc.close()
    return pages

# =========================
# MAIN INGEST
# =========================

def main() -> int:
    require_file(DB_PATH)
    require_file(STATE_PATH)
    require_file(PDF_REL_PATH)

    # 1) Verify SHA256 matches manifest expectation
    actual_sha = sha256_file(PDF_REL_PATH)
    if actual_sha != MANIFEST_ENTRY_SHA256:
        raise RuntimeError(
            f"STOP: PDF SHA256 mismatch.\n"
            f"Expected: {MANIFEST_ENTRY_SHA256}\n"
            f"Actual:   {actual_sha}"
        )

    sid = get_import_session_id()
    pages = extract_pdf_pages(PDF_REL_PATH)

    if not pages:
        raise RuntimeError("STOP: PDF yielded zero pages")

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    require_anchor(conn)

    before = conn.execute("SELECT COUNT(*) FROM chunks").fetchone()[0]

    # Preflight: build all chunk IDs & detect collisions BEFORE insert
    inserts = []
    for page_num, content in enumerate(pages, start=1):
        if not content.strip():
            continue

        cid = chunk_id_for(page_num)
        locator = f"pdf:page:{page_num:04d}"

        inserts.append((cid, locator, content))

    if not inserts:
        raise RuntimeError("STOP: no non-empty pages to insert")

    # Collision scan
    ids = [cid for cid, _, _ in inserts]
    qmarks = ",".join("?" for _ in ids)
    cur = conn.execute(
        f"SELECT chunk_id FROM chunks WHERE chunk_id IN ({qmarks})",
        ids,
    )
    collisions = [r[0] for r in cur.fetchall()]
    if collisions:
        raise RuntimeError(
            f"STOP: chunk_id collision detected ({len(collisions)}). "
            f"Likely already ingested.\n"
            f"Sample: {collisions[:5]}\n"
            "Suggestion: run scripts/inspect_anchor_chunks.py to verify counts."
        )

    # Insert transaction
    created_at = utc_now()
    with conn:
        for cid, locator, content in inserts:
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
                VALUES (?, ?, ?, NULL, ?, ?, ?, NULL, ?, ?)
                """,
                (
                    cid,
                    ANCHOR_ID,
                    locator,
                    content,
                    TRUTH_TYPE,
                    MUTATION_MODE,
                    sid,
                    created_at,
                ),
            )

    after = conn.execute("SELECT COUNT(*) FROM chunks").fetchone()[0]
    delta = after - before

    # =========================
    # RECEIPT
    # =========================

    receipt = {
        "receipt_version": "V1",
        "intent": "ARTISAN_PDF_PAGE_CHUNK_PILOT",
        "anchor_id": ANCHOR_ID,
        "source_path": str(PDF_REL_PATH.as_posix()),
        "manifest_entry_sha256": MANIFEST_ENTRY_SHA256,
        "import_session_id": sid,
        "generated_utc": utc_now(),
        "pdf": {
            "pages_total": len(pages),
            "pages_inserted": len(inserts),
        },
        "db": {
            "path": str(DB_PATH.as_posix()),
            "chunks_before": before,
            "chunks_after": after,
            "delta": delta,
        },
        "chunk_id_scheme": CHUNK_ID_NAMESPACE,
        "strict_rules": {
            "chunk_collision": "STOP",
            "missing_anchor": "STOP",
            "missing_pdf": "STOP",
            "manifest_sha_mismatch": "STOP",
        },
    }

    receipt_dir = EVIDENCE_ROOT / sid / "RECEIPTS"
    receipt_dir.mkdir(parents=True, exist_ok=True)

    receipt_path = receipt_dir / f"RECEIPT_CHUNKS_{ANCHOR_ID}_PDF_PAGES_PILOT.json"
    receipt_path.write_text(json.dumps(receipt, indent=2), encoding="utf-8")

    print(f"OK: inserted {delta} PDF page chunks for {ANCHOR_ID}")
    print(f"OK: receipt written: {receipt_path}")

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
