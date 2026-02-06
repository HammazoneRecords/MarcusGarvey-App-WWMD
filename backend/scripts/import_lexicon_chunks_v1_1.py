# scripts/import_lexicon_chunks_v1_1.py
from __future__ import annotations

import argparse, json, os, sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from state_guard import require_allowed

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "memory.db"

ROW_INDEX_KEYS_DEFAULT = ["row_index", "rowIndex", "row", "Row", "index", "idx", "id"]

def require_recorded() -> None:
    if os.environ.get("SOLOB_RECORDED_RUN") != "1":
        raise RuntimeError("BLOCKED: must run via scripts/run_recorded.py (recorded only).")

def now_utc_iso_z() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")

def norm_rel(p: str) -> str:
    s = (p or "").strip().replace("\\", "/")
    if s.startswith("./"):
        s = s[2:]
    return s

def find_row_index(entry: Dict[str, Any], keys: List[str]) -> Optional[int]:
    for k in keys:
        if k in entry and entry[k] is not None:
            v = entry[k]
            # allow "12" / 12
            try:
                iv = int(v)
                return iv
            except Exception:
                return None
    return None

def main() -> int:
    require_recorded()
    require_allowed("run_script")

    ap = argparse.ArgumentParser(
        description="Import lexicon JSON entries into chunks (deterministic, no reinterpretation)."
    )
    ap.add_argument("--anchor-id", required=True)
    ap.add_argument("--json", required=True)
    ap.add_argument("--letter", required=True)
    ap.add_argument("--import-session-id", required=True)
    ap.add_argument("--limit", type=int, default=0, help="0 = no limit (import all).")
    ap.add_argument("--receipt-out", required=True, help="REQUIRED: V2 receipt output path (prosecutor-grade).")
    ap.add_argument("--derive-row-index", action="store_true",
                    help="If entries lack row_index, derive 1-based index by order (explicit opt-in).")
    ap.add_argument("--row-index-keys", default=",".join(ROW_INDEX_KEYS_DEFAULT),
                    help="Comma-separated keys to try for row index (default includes row_index,row,index,id,...)")
    args = ap.parse_args()

    json_path = Path(args.json)
    if not json_path.is_absolute():
        json_path = (BASE_DIR / json_path).resolve()
    if not json_path.exists():
        raise FileNotFoundError(f"Lexicon JSON not found: {json_path}")

    raw = json.loads(json_path.read_text(encoding="utf-8"))

    # Accept both formats:
    # (1) legacy: top-level list
    # (2) current: dict with "entries"
    if isinstance(raw, list):
        entries = raw
        top_letter = None
        top_entry_count = None
        format_mode = "top_level_list"
    elif isinstance(raw, dict) and isinstance(raw.get("entries"), list):
        entries = raw["entries"]
        top_letter = raw.get("letter")
        top_entry_count = raw.get("entry_count")
        format_mode = "top_level_dict_entries"
    else:
        raise ValueError("Lexicon JSON must be a list, or an object with key 'entries' as a list.")

    # Hard checks (defensible)
    if top_letter is not None and str(top_letter).strip().upper() != str(args.letter).strip().upper():
        raise ValueError(f"Letter mismatch: file letter={top_letter!r} but --letter={args.letter!r}")

    if top_entry_count is not None:
        try:
            expected = int(top_entry_count)
        except Exception:
            raise ValueError(f"entry_count must be int-like, got {top_entry_count!r}")
        if expected != len(entries):
            raise ValueError(f"entry_count mismatch: entry_count={expected} but len(entries)={len(entries)}")

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    try:
        # Require anchor exists (STOP on missing)
        ok = conn.execute("SELECT 1 FROM anchors WHERE anchor_id=? LIMIT 1;", (args.anchor_id,)).fetchone()
        if not ok:
            raise RuntimeError(f"STOP: missing_anchor={args.anchor_id}")

        # Track database state (V2 requirement)
        chunks_before = conn.execute("SELECT COUNT(*) FROM chunks").fetchone()[0]

        started_utc = now_utc_iso_z()
        inserted = 0

        keys = [k.strip() for k in args.row_index_keys.split(",") if k.strip()]
        derived_used = False

        for i, entry in enumerate(entries):
            if not isinstance(entry, dict):
                raise ValueError("Each lexicon entry must be an object.")

            row_index = find_row_index(entry, keys)

            if row_index is None:
                if not args.derive_row_index:
                    raise ValueError(
                        "Entry missing required field: row_index (or equivalent). "
                        "Fix converter to stamp row_index OR re-run with --derive-row-index."
                    )
                derived_used = True
                row_index = i + 1  # deterministic 1-based

            word = entry.get("word") or entry.get("Word") or entry.get("term") or ""

            chunk_id = f"{args.anchor_id}:{args.letter}:{row_index}"
            locator = f"lexicon:{args.letter}:row:{row_index}"

            content = json.dumps(entry, ensure_ascii=False, sort_keys=True)

            try:
                conn.execute(
                    """
                    INSERT INTO chunks (
                      chunk_id, anchor_id, anchor_locator,
                      lexicon_word, content,
                      truth_type, mutation_mode, confidence,
                      import_session_id, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                    """,
                    (
                        chunk_id,
                        args.anchor_id,
                        locator,
                        str(word),
                        content,
                        "definition",
                        "append-only",
                        None,
                        args.import_session_id,
                        now_utc_iso_z(),
                    ),
                )
            except sqlite3.IntegrityError as e:
                raise RuntimeError(f"Chunk collision (blocked): chunk_id={chunk_id}") from e

            inserted += 1
            if args.limit and inserted >= args.limit:
                break

        conn.commit()
        ended_utc = now_utc_iso_z()

        # Database state verification (V2 requirement)
        chunks_after = conn.execute("SELECT COUNT(*) FROM chunks").fetchone()[0]
        delta = chunks_after - chunks_before

        if delta != inserted:
            raise RuntimeError(
                f"STOP: database delta mismatch (expected={inserted}, actual={delta})"
            )

        # Receipt generation (MANDATORY for V2)
        outp = Path(args.receipt_out)
        if not outp.is_absolute():
            outp = (BASE_DIR / outp).resolve()
        outp.parent.mkdir(parents=True, exist_ok=True)

        # V2 Receipt Schema
        receipt = {
            "receipt_version": "V2",
            "intent": f"LEXICON_IMPORT_{args.letter.upper()}",
            "generated_utc": now_utc_iso_z(),
            "import_session_id": args.import_session_id,
            "anchor_id": args.anchor_id,
            "source_path": norm_rel(str(json_path.relative_to(BASE_DIR).as_posix())),
            "db": {
                "path": "data/memory.db",
                "chunks_before": chunks_before,
                "chunks_after": chunks_after,
                "delta": delta,
            },
            "strict_rules": {
                "chunk_collision": "STOP",
                "missing_anchor": "STOP",
                "schema_mismatch": "STOP",
            },
            "timestamps": {
                "start_utc": started_utc,
                "end_utc": ended_utc,
            },
            "lexicon": {
                "letter": args.letter,
                "entries_total": len(entries),
                "entries_inserted": inserted,
                "format_mode": format_mode,
                "row_index_keys": keys,
                "row_index_derived": derived_used,
            },
        }
        outp.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"OK: wrote V2 receipt {outp.relative_to(BASE_DIR).as_posix()}")

        print(f"OK: imported_lexicon_chunks={inserted} anchor_id={args.anchor_id} sid={args.import_session_id}")
        return 0
    finally:
        conn.close()

if __name__ == "__main__":
    raise SystemExit(main())
