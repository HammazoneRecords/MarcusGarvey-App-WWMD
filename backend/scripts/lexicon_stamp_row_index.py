from __future__ import annotations

import argparse
import json
import os
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from state_guard import require_allowed

BASE_DIR = Path(__file__).resolve().parent.parent

def require_recorded() -> None:
    if os.environ.get("SOLOB_RECORDED_RUN") != "1":
        raise RuntimeError("BLOCKED: must run via scripts/run_recorded.py (recorded only).")

def utc_z_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def read_bytes(p: Path) -> bytes:
    return p.read_bytes()

def write_text_atomic(p: Path, text: str) -> None:
    # simple atomic-ish write: write temp then replace
    tmp = p.with_suffix(p.suffix + ".tmp")
    tmp.write_text(text, encoding="utf-8", newline="\n")
    tmp.replace(p)

def main() -> int:
    require_recorded()
    require_allowed("run_script")

    ap = argparse.ArgumentParser(description="Stamp lexicon entries with deterministic row_index (no reinterpretation).")
    ap.add_argument("--json", required=True, help="Path to lexicon JSON (expects dict with key 'entries').")
    ap.add_argument("--letter", required=True, help="Expected letter (A/B/C...). Used as guard only.")
    ap.add_argument("--sid", required=True, help="import_session_id / batch id for receipts.")
    ap.add_argument("--backup-dir", default="data/orphans/lexicon_backups", help="Backup directory (append-only).")
    ap.add_argument("--receipt-out", default="", help="Optional receipt JSON output path.")
    ap.add_argument("--in-place", action="store_true", help="Write stamped output back to the same file.")
    ap.add_argument("--out", default="", help="Optional output file path if not in-place.")
    ap.add_argument("--allow-existing", action="store_true",
                    help="Allow existing row_index fields ONLY if they match 1..N exactly.")
    ap.add_argument("--fail-on-mismatch-letter", action="store_true",
                    help="Fail if top-level lexicon['letter'] doesn't match --letter.")
    args = ap.parse_args()

    json_path = Path(args.json)
    if not json_path.is_absolute():
        json_path = (BASE_DIR / json_path).resolve()
    if not json_path.exists():
        raise FileNotFoundError(f"Lexicon JSON not found: {json_path}")

    raw_bytes_before = read_bytes(json_path)
    before_sha = sha256_bytes(raw_bytes_before)

    data = json.loads(raw_bytes_before.decode("utf-8"))

    if not isinstance(data, dict):
        raise ValueError("Lexicon JSON must be an object (dict) with keys: letter, entry_count, entries.")

    top_letter = str(data.get("letter", "")).strip()
    expected_letter = str(args.letter).strip()

    if args.fail_on_mismatch_letter and top_letter and (top_letter.upper() != expected_letter.upper()):
        raise ValueError(f"Letter mismatch: file letter='{top_letter}' vs --letter='{expected_letter}'")

    entries = data.get("entries")
    if not isinstance(entries, list):
        raise ValueError("Lexicon JSON must contain key 'entries' as a list.")

    # Optional: ensure entry_count is consistent (we don't *trust* it, we verify it)
    entry_count = data.get("entry_count")
    if entry_count is not None and int(entry_count) != len(entries):
        raise ValueError(f"entry_count mismatch: entry_count={entry_count} but len(entries)={len(entries)}")

    # Guard: existing row_index handling
    existing = [e.get("row_index") for e in entries if isinstance(e, dict) and "row_index" in e]
    if existing and not args.allow_existing:
        raise ValueError("row_index already present in some entries. Re-run with --allow-existing if intended.")

    # Stamp deterministically
    for i, e in enumerate(entries, start=1):
        if not isinstance(e, dict):
            raise ValueError("Each entry in 'entries' must be an object (dict).")

        if "row_index" in e:
            # only valid if it matches the deterministic numbering
            if int(e["row_index"]) != i:
                raise ValueError(f"Existing row_index mismatch at position {i}: got {e['row_index']} expected {i}")
        else:
            e["row_index"] = i

    # Mark stamp metadata at top-level (structural, not reinterpretation)
    data["_stamp"] = {
        "stamp_version": "LEXICON_ROW_INDEX_V1",
        "stamped_utc": utc_z_now(),
        "sid": args.sid,
        "source_file": json_path.relative_to(BASE_DIR).as_posix(),
        "before_sha256": before_sha,
        "entry_count": len(entries),
    }

    stamped_text = json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    after_sha = sha256_bytes(stamped_text.encode("utf-8"))

    # Backup (append-only)
    backup_dir = Path(args.backup_dir)
    if not backup_dir.is_absolute():
        backup_dir = (BASE_DIR / backup_dir).resolve()
    backup_dir.mkdir(parents=True, exist_ok=True)

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    backup_name = f"{json_path.stem}.PRESTAMP_{ts}.json"
    backup_path = backup_dir / backup_name
    backup_path.write_bytes(raw_bytes_before)

    # Write output
    if args.in_place:
        out_path = json_path
    else:
        if not args.out:
            raise ValueError("If not using --in-place, you must provide --out.")
        out_path = Path(args.out)
        if not out_path.is_absolute():
            out_path = (BASE_DIR / out_path).resolve()
        out_path.parent.mkdir(parents=True, exist_ok=True)

    write_text_atomic(out_path, stamped_text)

    # Receipt
    if args.receipt_out:
        rpath = Path(args.receipt_out)
        if not rpath.is_absolute():
            rpath = (BASE_DIR / rpath).resolve()
        rpath.parent.mkdir(parents=True, exist_ok=True)

        receipt = {
            "sid": args.sid,
            "letter": expected_letter,
            "source_file": json_path.relative_to(BASE_DIR).as_posix(),
            "output_file": out_path.relative_to(BASE_DIR).as_posix(),
            "backup_file": backup_path.relative_to(BASE_DIR).as_posix(),
            "before_sha256": before_sha,
            "after_sha256": after_sha,
            "entries": len(entries),
            "stamp_version": "LEXICON_ROW_INDEX_V1",
            "generated_utc": utc_z_now(),
        }
        rpath.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"OK: wrote receipt {rpath.relative_to(BASE_DIR).as_posix()}")

    print("LEXICON STAMP: PASS")
    print(f"OK: file={out_path.relative_to(BASE_DIR).as_posix()}")
    print(f"OK: backup={backup_path.relative_to(BASE_DIR).as_posix()}")
    print(f"OK: entries={len(entries)} before_sha256={before_sha} after_sha256={after_sha}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
