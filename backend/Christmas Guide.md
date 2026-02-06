# GEMINI FLASH PROMPT ? SOLOB WRAPPER ?CHRISTMAS GUIDE? FIX ORDER (V1)

You are acting as a strictly constrained repo mechanic for the project `solob-wrapper`.
Your job: fix the repository so that the ?front door? workflow is reliable and uniform.

## Non-negotiable rules (read carefully)
1) DO NOT invent new architecture. Only fix what is broken and unify what already exists.
2) DO NOT delete evidence folders or historical logs. Preserve history.
3) All PowerShell scripts MUST parse cleanly (no encoding garbage, no missing braces, no unterminated strings).
4) Every recorded run MUST be executable through `scripts/run_recorded.py` and must use a valid SID witness.
5) Outputs must be deterministic, Windows-safe, and compatible with PowerShell 7+.
6) If you are unsure, prefer conservative STOP behavior (fail early with a clear error).

## Primary objectives (in strict order)
You MUST execute these objectives in order. Do not skip ahead.

### Objective 1 ? Encode hygiene + parsing health (PowerShell)
A) Audit `tools/prove.ps1` and `tools/court_sweep.ps1`:
   - Fix any syntax errors: missing braces, missing quotes, missing catch/finally, etc.
   - Remove/replace any bad unicode rendering sequences (e.g., ?????, ?????, ?????) with plain ASCII equivalents.
   - Ensure the scripts run in PowerShell without parser errors.

B) Add at top of each `.ps1`:
   - `Set-StrictMode -Version Latest`
   - `$ErrorActionPreference = "Stop"`
   - Use ASCII-only strings for banners/sections.

C) Provide a small self-test function in each script:
   - `Test-ScriptParse` that prints ?OK: parse? and exits 0.

### Objective 2 ? ?SID Witness? propagation is canonical everywhere
A) Confirm current SID witness system:
   - `tools/solob.ps1` writes/retains `active_session_id` in `docs/STATE.json`
   - `scripts/run_recorded.py` exports `RUN_RECORDED_SID`
B) Ensure every script that writes evidence uses:
   - `RUN_RECORDED_SID` first
   - then `docs/STATE.json:active_session_id`
   - never uses `recorded_at` in filenames or folder names
C) Add a shared helper in Python:
   - `utils/sid.py` (or similar) providing `get_active_sid()` with the above priority
   - Update `scripts/chunk_bos_pages_pilot.py` to import and use it

### Objective 3 ? Bundle uniformity standard (Court Exhibit layout)
We want bundles to look uniform and ?patent-ready?.
Define the canonical bundle structure inside `docs/EVIDENCE_BUNDLE_SPEC.md` (update if needed):

For any bundle directory `evidence/<BUNDLE_NAME>/`:
- `INDEX.json`  (hash index of all bundle files)
- `RECEIPTS/`   (json receipts)
- `STAMPS/`     (json stamps)
- `LOGS/`       (selected stdout/stderr logs if included)
- `DB/`         (optional db checkpoint receipts or copies if included)

Implement (or fix) a Prosecutor script:
- If `scripts/prosecutor_consolidate_lexicon_bundle.py` exists, ensure it creates:
  - `evidence/<sid>_SUPREME_LEXICON_BUNDLE/{INDEX.json,RECEIPTS,STAMPS,DB(optional),LOGS(optional)}`
- Ensure it supports `--include-db-checkpoint` through `run_recorded.py` by passing args after `--`
- Ensure it prints:
  - ?OK: created ??
  - ?OK: receipts=X stamps=Y?
  - ?OK: index file_count=Z?

### Objective 4 ? Fix/upgrade ARTISAN BoS chunk pilot to be front-door reliable
We have `scripts/chunk_bos_pages_pilot.py` (shown below). Make it reliable.

Required behavior:
1) Must STOP if anchor is missing in DB.
2) Must STOP if PDF sha256 does not match manifest entry sha256.
3) Must write receipt into: `evidence/<sid>/RECEIPTS/RECEIPT_CHUNKS_book_of_solobility_v1_PDF_PAGES_PILOT.json`
4) Must be collision-safe and explain collisions clearly:
   - If chunk_ids already exist, STOP with message:
     ?STOP: chunk_id collision (likely already ingested). existing_count=? sample=??
   - Provide a suggestion in error text: run query to count chunks for that anchor.
5) Must not require `pypdf`. Prefer PyMuPDF (`fitz`).
6) Chunk IDs MUST be namespace-separated from lexicon:
   - Use `CHUNK_ID_NAMESPACE = "SOLOB|V2|CHUNK|PDF_PAGE|BOOK_OF_SOLOBILITY"`
   - Derive `chunk_id = sha256(namespace|anchor_id|manifest_sha|page_num)`
7) Must not create invalid Windows paths. Use SID as folder name exactly.

Also add a small script:
- `scripts/inspect_anchor_chunks.py`:
  - prints counts per anchor_id, and specifically BoS count
  - runs via `run_recorded.py` but does not mutate DB

### Objective 5 ? Court sweep script becomes the single ?one command? health ritual
Fix/implement `tools/court_sweep.ps1` so it can run:

`.\tools\court_sweep.ps1 -RepoRoot . -RunProve -RequireAZ`

Behavior:
1) Prints ?1) STATE GUARD CHECK? (ASCII)
2) Runs database sync audit:
   - `python scripts/audit_lexicon_counts.py`
3) Verifies evidence index:
   - reads `evidence/INDEX.json` and prints:
     - Evidence_Files
     - Bundles_Found
     - Generated_UTC
4) If `-RunProve` calls:
   - `.\tools\prove.ps1 -EvidenceDir .\evidence -Scope lexicon -RequireAZ` (if RequireAZ)
5) Must not crash on property access:
   - When reading `$index.bundles`, handle it as either array or object properties safely.

### Objective 6 ? Update STATE_HISTORY.md formatting and SID coverage (no rewriting history)
We will NOT rewrite old history. But we will:
1) Add a new section near the top:
   - ?SID Witness Policy?
   - explain that older lines may not contain sid= and that is acceptable
2) Add a helper command snippet:
   - find lines without sid= for recent transitions (already used)
3) Ensure future transitions always append `(sid=...)`

## Inputs you must respect
- Repo has folders: tools/, scripts/, docs/, evidence/, data/, anchors/
- Python version: 3.13 on Windows
- This file exists: `data/schema.sql` with chunks table and import_session_id
- This is the current BoS chunk pilot script (do not lose features, only fix/upgrade it):

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

CHUNK_ID_NAMESPACE = "CHUNK_V2|PDF_PAGE"

# =========================
# HELPERS
# =========================

def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def sha256_text(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

def load_state() -> dict:
    return json.loads(STATE_PATH.read_text(encoding="utf-8"))

def get_import_session_id() -> str:
    """
    Canonical SID resolution for Solob Wrapper.

    Priority:
    1. RUN_RECORDED_SID (set by run_recorded.py)
    2. SOLOB_IMPORT_SESSION_ID / IMPORT_SESSION_ID (fallback)
    3. STATE.json recorded_at (last-resort provenance anchor)
    """

    sid = (
        os.environ.get("RUN_RECORDED_SID")
        or os.environ.get("SOLOB_IMPORT_SESSION_ID")
        or os.environ.get("IMPORT_SESSION_ID")
    )

    if sid:
        return sid

    # Try STATE.json active_session_id
    try:
        st = load_state()
        sid = st.get("active_session_id")
        if sid:
            return sid
    except Exception:
        pass

    raise RuntimeError("STOP: import_session_id not resolvable. Run via solob.ps1 record + run_recorded.py")

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
            f"Sample: {collisions[:5]}"
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
        "source_path": str(PDF_REL_PATH),
        "manifest_entry_sha256": MANIFEST_ENTRY_SHA256,
        "import_session_id": sid,
        "generated_utc": utc_now(),
        "pdf": {
            "pages_total": len(pages),
            "pages_inserted": len(inserts),
        },
        "db": {
            "path": str(DB_PATH),
            "chunks_before": before,
            "chunks_after": after,
            "delta": delta,
        },
        "chunk_id_scheme": CHUNK_ID_NAMESPACE,
        "strict_rules": {
            "chunk_collision": "STOP",
            "missing_anchor": "STOP",
            "missing_pdf": "STOP",
        },
    }

    out_dir = EVIDENCE_ROOT / sid
    out_dir.mkdir(parents=True, exist_ok=True)

    receipt_path = out_dir / f"RECEIPT_CHUNKS_{ANCHOR_ID}_PDF_PAGES_PILOT.json"
    receipt_path.write_text(json.dumps(receipt, indent=2), encoding="utf-8")

    print(f"OK: inserted {delta} PDF page chunks for {ANCHOR_ID}")
    print(f"OK: receipt written: {receipt_path}")

    return 0

if __name__ == "__main__":
    raise SystemExit(main())


## Output deliverables (MUST produce all)
 1) Apply code changes in the repo (PowerShell + Python + docs).
 2) Create `docs/christmas_guide.md` with:
   - ?What changed? (bullet list)
   - ?One-command rituals? (exact commands)
   - ?Troubleshooting map? (collision, missing fitz, missing sid, manifest mismatch)
   - ?Reality 1?4 gate checklist? (anchors, map, chunk, prosecutor)
3) Provide final verification commands the user can run in PowerShell:
   - parse tests
   - court sweep
   - bos chunk pilot
   - sanity check
4) When modifying files:
- Show unified diffs (--- / +++) for PowerShell and Python changes
- Do not restate unchanged code



7) DO NOT rename existing files unless explicitly instructed. Prefer in-place fixes.


## Definition of Done (must meet all)
- `.\tools\prove.ps1` runs without parser errors
- `.\tools\court_sweep.ps1` runs without parser errors
- `scripts/chunk_bos_pages_pilot.py` runs via run_recorded and writes receipt to correct location
- All evidence folder creation uses safe SIDs
- Bund
