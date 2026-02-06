from __future__ import annotations

import argparse
import json
import os
import re
import sqlite3
from pathlib import Path
from typing import Dict, List, Set

from state_guard import require_allowed

BASE_DIR = Path(__file__).resolve().parent.parent


def require_recorded_run() -> None:
    if os.environ.get("SOLOB_RECORDED_RUN") != "1":
        raise RuntimeError("BLOCKED: must run via scripts/run_recorded.py")


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def parse_check_in_list(schema_sql: str, column: str) -> Set[str]:
    # Looks for CHECK( column IN ('a','b',...) )
    # Tolerant regex; returns empty set if not found.
    pattern = re.compile(rf"CHECK\s*\(\s*{re.escape(column)}\s+IN\s*\((.*?)\)\s*\)", re.IGNORECASE | re.DOTALL)
    m = pattern.search(schema_sql)
    if not m:
        return set()
    inside = m.group(1)
    vals = re.findall(r"'([^']+)'", inside)
    return set(vals)


def main() -> int:
    require_recorded_run()
    require_allowed("run_script")

    ap = argparse.ArgumentParser(description="Validate registry against disk + DB (anchors-only).")
    ap.add_argument("--registry", required=True)
    ap.add_argument("--db", default="data/memory.db")
    ap.add_argument("--schema", default="data/schema.sql")
    ap.add_argument("--expect-anchors", type=int, default=None)
    ap.add_argument("--require-empty-chunks", action="store_true", default=True)
    ap.add_argument("--require-empty-runs", action="store_true", default=True)
    args = ap.parse_args()

    reg_path = Path(args.registry)
    if not reg_path.is_absolute():
        reg_path = (BASE_DIR / reg_path).resolve()
    if not reg_path.exists():
        raise FileNotFoundError(f"Registry not found: {reg_path}")

    db_path = Path(args.db)
    if not db_path.is_absolute():
        db_path = (BASE_DIR / db_path).resolve()
    if not db_path.exists():
        raise FileNotFoundError(f"DB not found: {db_path}")

    schema_path = Path(args.schema)
    if not schema_path.is_absolute():
        schema_path = (BASE_DIR / schema_path).resolve()
    schema_sql = schema_path.read_text(encoding="utf-8", errors="replace") if schema_path.exists() else ""

    allowed_anchor_type = parse_check_in_list(schema_sql, "anchor_type")
    allowed_status = parse_check_in_list(schema_sql, "status")
    allowed_source_format = parse_check_in_list(schema_sql, "source_format")

    reg = load_json(reg_path)
    if not isinstance(reg, list):
        raise SystemExit("AUDIT FAILED: registry must be a JSON array.")

    seen_ids: Set[str] = set()
    missing_files: List[str] = []
    dupes: List[str] = []
    bad_fields: List[str] = []
    bad_enums: List[str] = []

    required = ["anchor_id", "anchor_type", "title", "source_path", "source_format", "status", "provenance"]

    for i, entry in enumerate(reg):
        if not isinstance(entry, dict):
            raise SystemExit(f"AUDIT FAILED: registry entry[{i}] is not an object.")
        for k in required:
            if k not in entry or str(entry.get(k, "")).strip() == "":
                bad_fields.append(f"entry[{i}] missing/blank '{k}'")

        aid = str(entry.get("anchor_id", "")).strip()
        if aid in seen_ids:
            dupes.append(aid)
        seen_ids.add(aid)

        sp = str(entry.get("source_path", "")).strip()
        fp = (BASE_DIR / sp).resolve() if not Path(sp).is_absolute() else Path(sp)
        if not fp.exists():
            missing_files.append(sp)

        at = str(entry.get("anchor_type", "")).strip()
        st = str(entry.get("status", "")).strip()
        sf = str(entry.get("source_format", "")).strip()

        if allowed_anchor_type and at not in allowed_anchor_type:
            bad_enums.append(f"entry[{i}] anchor_type='{at}' not in {sorted(allowed_anchor_type)}")
        if allowed_status and st not in allowed_status:
            bad_enums.append(f"entry[{i}] status='{st}' not in {sorted(allowed_status)}")
        if allowed_source_format and sf not in allowed_source_format:
            bad_enums.append(f"entry[{i}] source_format='{sf}' not in {sorted(allowed_source_format)}")

    if dupes or bad_fields or missing_files or bad_enums:
        lines = ["AUDIT FAILED: registry validation errors:"]
        for x in dupes:
            lines.append(f"- duplicate_anchor_id: {x}")
        for x in bad_fields:
            lines.append(f"- bad_field: {x}")
        for x in missing_files:
            lines.append(f"- missing_file: {x}")
        for x in bad_enums:
            lines.append(f"- enum_violation: {x}")
        raise SystemExit("\n".join(lines))

    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA foreign_keys = ON;")
    try:
        fk = conn.execute("PRAGMA foreign_keys;").fetchone()[0]
        if fk != 1:
            raise SystemExit("AUDIT FAILED: PRAGMA foreign_keys != 1")

        db_anchors = conn.execute("SELECT COUNT(*) FROM anchors;").fetchone()[0]
        db_chunks = conn.execute("SELECT COUNT(*) FROM chunks;").fetchone()[0]
        db_runs = conn.execute("SELECT COUNT(*) FROM runs;").fetchone()[0]

        if args.expect_anchors is not None and db_anchors != args.expect_anchors:
            raise SystemExit(f"AUDIT FAILED: db_anchors={db_anchors} expected={args.expect_anchors}")

        if db_anchors != len(reg):
            raise SystemExit(f"AUDIT FAILED: registry_entries={len(reg)} db_anchors={db_anchors} mismatch")

        if args.require_empty_chunks and db_chunks != 0:
            raise SystemExit(f"AUDIT FAILED: chunks must be empty, found chunks={db_chunks}")

        if args.require_empty_runs and db_runs != 0:
            raise SystemExit(f"AUDIT FAILED: runs must be empty, found runs={db_runs}")

        db_ids = {r[0] for r in conn.execute("SELECT anchor_id FROM anchors;").fetchall()}
        reg_ids = set(seen_ids)

        missing_in_db = sorted(reg_ids - db_ids)
        if missing_in_db:
            raise SystemExit(f"AUDIT FAILED: registry anchor_ids missing in DB: {missing_in_db}")

    finally:
        conn.close()

    print("REGISTRY VALIDATOR: PASS")
    print(f"OK: registry_entries={len(reg)} db_anchors={db_anchors} chunks={db_chunks} runs={db_runs}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
