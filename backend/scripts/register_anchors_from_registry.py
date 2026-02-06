# scripts/register_anchors_from_registry.py
from __future__ import annotations

import argparse
import json
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "memory.db"

ALLOWED_ANCHOR_TYPES = {"lexicon", "book", "letter", "other"}
ALLOWED_SOURCE_FORMATS = {"json", "pdf", "txt"}
ALLOWED_STATUS = {"canon", "working"}


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def require_recorded_run() -> None:
    if os.environ.get("SOLOB_RECORDED_RUN") != "1":
        raise RuntimeError(
            "BLOCKED: This script must be executed via scripts/run_recorded.py "
            "(NO UNRECORDED SHUFFLES)."
        )


def load_registry(path: Path) -> List[Dict[str, Any]]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, list):
        raise ValueError("Registry must be a JSON array of anchor objects.")
    out: List[Dict[str, Any]] = []
    for i, a in enumerate(raw):
        if not isinstance(a, dict):
            raise ValueError(f"Registry entry {i} is not an object.")
        out.append(a)
    return out


def validate_anchor(a: Dict[str, Any]) -> None:
    required = ["anchor_id", "anchor_type", "title", "source_path", "source_format", "status", "provenance"]
    missing = [k for k in required if k not in a or a[k] is None or str(a[k]).strip() == ""]
    if missing:
        raise ValueError(f"Anchor missing required fields: {missing}")

    at = str(a["anchor_type"]).strip()
    sf = str(a["source_format"]).strip()
    st = str(a["status"]).strip()

    if at not in ALLOWED_ANCHOR_TYPES:
        raise ValueError(f"Invalid anchor_type='{at}'. Allowed: {sorted(ALLOWED_ANCHOR_TYPES)}")
    if sf not in ALLOWED_SOURCE_FORMATS:
        raise ValueError(f"Invalid source_format='{sf}'. Allowed: {sorted(ALLOWED_SOURCE_FORMATS)}")
    if st not in ALLOWED_STATUS:
        raise ValueError(f"Invalid status='{st}'. Allowed: {sorted(ALLOWED_STATUS)}")


def main() -> None:
    require_recorded_run()

    ap = argparse.ArgumentParser()
    ap.add_argument("--registry", required=True, help="Path to JSON registry (relative to repo root or absolute).")
    ap.add_argument("--import-session-id", required=True, help="One session id for this batch.")
    ap.add_argument("--receipt-out", required=True, help="REQUIRED: V2 receipt output path (prosecutor-grade).")
    ap.add_argument(
        "--require-empty-anchors",
        action="store_true",
        help="Fail if anchors table is not empty (Monk-safe default when enabled).",
    )
    args = ap.parse_args()

    reg_path = Path(args.registry)
    if not reg_path.is_absolute():
        reg_path = (BASE_DIR / reg_path).resolve()

    if not reg_path.exists():
        raise FileNotFoundError(f"Registry not found: {reg_path}")

    if not DB_PATH.exists():
        raise FileNotFoundError(f"memory.db not found: {DB_PATH} (run init_db first via recorder).")

    anchors = load_registry(reg_path)

    # Validate + disk existence first (so we can hard-fail before any DB writes)
    seen_ids = set()
    for a in anchors:
        validate_anchor(a)

        aid = str(a["anchor_id"]).strip()
        if aid in seen_ids:
            raise ValueError(f"Duplicate anchor_id in registry: {aid}")
        seen_ids.add(aid)

        sp = str(a["source_path"]).strip()
        full = Path(sp)
        if not full.is_absolute():
            full = (BASE_DIR / full).resolve()
        if not full.exists():
            raise FileNotFoundError(f"Anchor file missing on disk: {full} (registry source_path={sp})")

    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute("PRAGMA foreign_keys = ON;")

        # Track database state (V2 requirement)
        anchors_before = conn.execute("SELECT COUNT(*) FROM anchors").fetchone()[0]

        if args.require_empty_anchors:
            if anchors_before != 0:
                raise RuntimeError(f"STOP: MONK_BLOCK anchors_table_not_empty (anchors={anchors_before})")

        # Transaction: all or nothing
        conn.execute("BEGIN;")

        inserted = 0
        now = utc_now_iso()

        # Fail on collisions (strict)
        for a in anchors:
            aid = str(a["anchor_id"]).strip()
            exists = conn.execute("SELECT 1 FROM anchors WHERE anchor_id=? LIMIT 1;", (aid,)).fetchone()
            if exists:
                raise RuntimeError(f"Collision: anchor_id already exists in DB: {aid}")

            conn.execute(
                """
                INSERT INTO anchors (
                    anchor_id, anchor_type, title, source_path,
                    source_format, status, provenance,
                    import_session_id, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    aid,
                    str(a["anchor_type"]).strip(),
                    str(a["title"]).strip(),
                    str(a["source_path"]).strip(),
                    str(a["source_format"]).strip(),
                    str(a["status"]).strip(),
                    str(a["provenance"]).strip(),
                    str(args.import_session_id).strip(),
                    now,
                ),
            )
            inserted += 1

        conn.commit()
        anchors_after = conn.execute("SELECT COUNT(*) FROM anchors").fetchone()[0]
        delta = anchors_after - anchors_before

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
            "intent": "ANCHOR_REGISTRATION",
            "generated_utc": now,
            "import_session_id": str(args.import_session_id).strip(),
            "source_path": str(reg_path.relative_to(BASE_DIR).as_posix()),
            "db": {
                "path": "data/memory.db",
                "anchors_before": anchors_before,
                "anchors_after": anchors_after,
                "delta": delta,
            },
            "strict_rules": {
                "anchor_collision": "STOP",
                "missing_source_file": "STOP",
                "duplicate_anchor_id": "STOP",
            },
            "anchors": {
                "total_registered": inserted,
                "require_empty_anchors": args.require_empty_anchors,
            },
        }
        outp.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")

        print(f"OK: registered_anchors={inserted} import_session_id={args.import_session_id}")
        print(f"OK: wrote V2 receipt {outp.relative_to(BASE_DIR).as_posix()}")
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    main()
