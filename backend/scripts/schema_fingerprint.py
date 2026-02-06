from __future__ import annotations

import argparse
import hashlib
import json
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

from state_guard import require_allowed

BASE_DIR = Path(__file__).resolve().parent.parent


def require_recorded_run() -> None:
    if os.environ.get("SOLOB_RECORDED_RUN") != "1":
        raise RuntimeError("BLOCKED: must run via scripts/run_recorded.py")


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def utc_z_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def main() -> int:
    require_recorded_run()
    require_allowed("run_script")

    ap = argparse.ArgumentParser(description="Fingerprint schema.sql and sqlite_master.")
    ap.add_argument("--schema", required=True)
    ap.add_argument("--db", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    schema_path = Path(args.schema)
    if not schema_path.is_absolute():
        schema_path = (BASE_DIR / schema_path).resolve()
    if not schema_path.exists():
        raise FileNotFoundError(f"Missing schema: {schema_path}")

    db_path = Path(args.db)
    if not db_path.is_absolute():
        db_path = (BASE_DIR / db_path).resolve()
    if not db_path.exists():
        raise FileNotFoundError(f"Missing DB: {db_path}")

    out_path = Path(args.out)
    if not out_path.is_absolute():
        out_path = (BASE_DIR / out_path).resolve()

    schema_sha = sha256_file(schema_path)

    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA foreign_keys = ON;")
    try:
        fk = conn.execute("PRAGMA foreign_keys;").fetchone()[0]
        integ = conn.execute("PRAGMA integrity_check;").fetchone()[0]

        rows = conn.execute(
            """
            SELECT type, name, tbl_name, sql
            FROM sqlite_master
            WHERE type IN ('table','index','trigger','view')
            ORDER BY type ASC, name ASC;
            """
        ).fetchall()

        items: List[Dict[str, str]] = []
        dump_lines: List[str] = []
        for t, name, tbl, sql in rows:
            sqls = (sql or "").strip()
            items.append({"type": t, "name": name, "table": tbl, "sql": sqls})
            dump_lines.append(f"{t}|{name}|{tbl}|{sqls}")

        master_dump = "\n".join(dump_lines).encode("utf-8", errors="replace")
        master_sha = sha256_bytes(master_dump)

        payload = {
            "kind": "SCHEMA_FINGERPRINT",
            "version": "V1",
            "generated_utc": utc_z_now(),
            "schema_rel": schema_path.relative_to(BASE_DIR).as_posix(),
            "db_rel": db_path.relative_to(BASE_DIR).as_posix(),
            "schema_sha256": schema_sha,
            "sqlite_master_sha256": master_sha,
            "foreign_keys": int(fk),
            "integrity_check": str(integ),
            "sqlite_master_items": items,
        }

    finally:
        conn.close()

    if payload["integrity_check"] != "ok":
        raise SystemExit(f"AUDIT FAILED: PRAGMA integrity_check != ok (got {payload['integrity_check']})")
    if payload["foreign_keys"] != 1:
        raise SystemExit("AUDIT FAILED: PRAGMA foreign_keys != 1")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"OK: wrote {out_path.relative_to(BASE_DIR).as_posix()}")
    print(f"OK: schema_sha256={schema_sha}")
    print(f"OK: sqlite_master_sha256={payload['sqlite_master_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
