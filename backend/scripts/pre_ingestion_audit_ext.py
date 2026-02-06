from __future__ import annotations

import argparse
import hashlib
import json
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

from state_guard import require_allowed

BASE_DIR = Path(__file__).resolve().parent.parent
ANCHORS_DIR = BASE_DIR / "anchors"


def require_recorded_run() -> None:
    if os.environ.get("SOLOB_RECORDED_RUN") != "1":
        raise RuntimeError("BLOCKED: must be executed via scripts/run_recorded.py")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def utc_z_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def now_local_offset_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def load_manifest(path: Path) -> Dict[str, Any]:
    d = json.loads(path.read_text(encoding="utf-8"))
    files = d.get("files")
    if not isinstance(files, list):
        raise ValueError("Manifest invalid: expected key 'files' as list.")
    norm: List[Tuple[str, str]] = []
    for item in files:
        if not (isinstance(item, (list, tuple)) and len(item) == 2):
            raise ValueError("Manifest invalid: each files entry must be [rel_path, sha256].")
        rel = str(item[0]).replace("\\", "/").strip()
        sha = str(item[1]).strip()
        norm.append((rel, sha))
    d["files_norm"] = sorted(norm, key=lambda x: x[0].lower())
    return d


def compute_anchors_fingerprint(ignore_hidden: bool = True) -> List[Tuple[str, str]]:
    if not ANCHORS_DIR.exists():
        raise FileNotFoundError(f"Missing anchors dir: {ANCHORS_DIR}")
    out: List[Tuple[str, str]] = []
    for p in sorted(ANCHORS_DIR.rglob("*"), key=lambda x: x.as_posix().lower()):
        if p.is_dir():
            continue
        rel_parts = p.relative_to(ANCHORS_DIR).parts
        if ignore_hidden and any(part.startswith(".") for part in rel_parts):
            continue
        rel = p.relative_to(ANCHORS_DIR).as_posix()
        out.append((rel, sha256_file(p)))
    return out


def parse_schema_hints(schema_sql: str) -> Dict[str, List[str]]:
    tables: List[str] = []
    indexes: List[str] = []
    for line in schema_sql.splitlines():
        s = line.strip()
        if not s:
            continue
        up = s.upper()
        if up.startswith("CREATE TABLE"):
            # best-effort hint only (not a full SQL parser)
            toks = s.replace("(", " ").split()
            # try to pick the token after TABLE / IF / NOT / EXISTS
            # CREATE TABLE [IF NOT EXISTS] name
            candidates = [t for t in toks if t.upper() not in {"CREATE", "TABLE", "IF", "NOT", "EXISTS"}]
            if candidates:
                tables.append(candidates[0].strip('"`[]'))
        if up.startswith("CREATE INDEX") or up.startswith("CREATE UNIQUE INDEX"):
            toks = s.replace("(", " ").split()
            candidates = [t for t in toks if t.upper() not in {"CREATE", "UNIQUE", "INDEX"}]
            if candidates:
                indexes.append(candidates[0].strip('"`[]'))
    return {
        "schema_tables_hint": sorted(set(tables), key=str.lower),
        "schema_indexes_hint": sorted(set(indexes), key=str.lower),
    }


def read_sqlite_master(conn: sqlite3.Connection) -> Dict[str, List[str]]:
    rows = conn.execute(
        """
        SELECT type, name
        FROM sqlite_master
        WHERE type IN ('table','index')
        ORDER BY type ASC, name ASC;
        """
    ).fetchall()
    tables = sorted([r[1] for r in rows if r[0] == "table"], key=lambda x: x.lower())
    indexes = sorted([r[1] for r in rows if r[0] == "index"], key=lambda x: x.lower())
    return {"tables": tables, "indexes": indexes}


def ledger_tail(path: Path, n: int) -> List[Dict[str, Any]]:
    if not path.exists():
        raise FileNotFoundError(f"Missing ledger: {path}")
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    tail = lines[-n:] if n > 0 else lines
    out: List[Dict[str, Any]] = []
    for i, ln in enumerate(tail):
        ln = ln.strip()
        if not ln:
            continue
        try:
            out.append(json.loads(ln))
        except Exception as e:
            raise SystemExit(f"AUDIT FAILED: ops_ledger JSON parse error in tail line[{i}]: {e}")
    return out


def main() -> int:
    require_recorded_run()
    require_allowed("run_script")

    ap = argparse.ArgumentParser(description="STRICT pre-ingestion audit (anchors-only).")
    ap.add_argument("--db", default="data/memory.db")
    ap.add_argument("--schema", default="data/schema.sql")
    ap.add_argument("--registry", default="docs/ANCHOR_REGISTRY_PLAN.json")
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--ledger", default="logs/ops_ledger.jsonl")
    ap.add_argument("--ledger-tail", type=int, default=25)
    ap.add_argument("--require-anchors", type=int, default=None)
    ap.add_argument("--allow-wal", action="store_true", default=False)
    ap.add_argument("--out", default=None, help="Optional JSON report output path")
    args = ap.parse_args()

    db_path = (BASE_DIR / args.db).resolve() if not Path(args.db).is_absolute() else Path(args.db)
    schema_path = (BASE_DIR / args.schema).resolve() if not Path(args.schema).is_absolute() else Path(args.schema)
    registry_path = (BASE_DIR / args.registry).resolve() if not Path(args.registry).is_absolute() else Path(args.registry)
    manifest_path = (BASE_DIR / args.manifest).resolve() if not Path(args.manifest).is_absolute() else Path(args.manifest)
    ledger_path = (BASE_DIR / args.ledger).resolve() if not Path(args.ledger).is_absolute() else Path(args.ledger)

    for p, name in [
        (db_path, "DB"),
        (schema_path, "schema.sql"),
        (registry_path, "registry"),
        (manifest_path, "manifest"),
        (ledger_path, "ops ledger"),
    ]:
        if not p.exists():
            raise FileNotFoundError(f"{name} not found: {p}")

    # WAL/SHM gate
    wal = Path(str(db_path) + "-wal")
    shm = Path(str(db_path) + "-shm")
    wal_present = wal.exists()
    shm_present = shm.exists()
    if not args.allow_wal and (wal_present or shm_present):
        raise SystemExit(
            "AUDIT FAILED: WAL/SHM artifacts present.\n"
            f"- wal_exists={wal_present} ({wal})\n"
            f"- shm_exists={shm_present} ({shm})\n"
            "If you intentionally allow WAL/SHM, rerun with --allow-wal."
        )

    # Schema
    schema_sha = sha256_file(schema_path)
    schema_sql = schema_path.read_text(encoding="utf-8", errors="replace")
    schema_hints = parse_schema_hints(schema_sql)

    # Manifest fidelity
    manifest = load_manifest(manifest_path)
    manifest_sha = sha256_file(manifest_path)
    fs_files = compute_anchors_fingerprint()
    man_files = manifest["files_norm"]

    if len(fs_files) != len(man_files):
        raise SystemExit(
            f"AUDIT FAILED: Manifest/filecount mismatch. manifest={len(man_files)} filesystem={len(fs_files)}"
        )

    fs_map = {rel: sha for rel, sha in fs_files}
    for rel, sha in man_files:
        if rel not in fs_map:
            raise SystemExit(f"AUDIT FAILED: manifest rel_path missing on disk: {rel}")
        if fs_map[rel] != sha:
            raise SystemExit(f"AUDIT FAILED: sha256 mismatch for {rel}\nexpected={sha}\nactual={fs_map[rel]}")

    # DB checks (read-only)
    conn = sqlite3.connect(f"file:{db_path.as_posix()}?mode=ro", uri=True)
    try:
        conn.execute("PRAGMA foreign_keys = ON;")
        fk = conn.execute("PRAGMA foreign_keys;").fetchone()[0]
        integ = conn.execute("PRAGMA integrity_check;").fetchone()[0]

        counts = {
            "anchors": conn.execute("SELECT COUNT(*) FROM anchors;").fetchone()[0],
            "chunks": conn.execute("SELECT COUNT(*) FROM chunks;").fetchone()[0],
            "runs": conn.execute("SELECT COUNT(*) FROM runs;").fetchone()[0],
            "run_citations": conn.execute("SELECT COUNT(*) FROM run_citations;").fetchone()[0],
        }

        # STRICT pre-ingest: no chunks, no runs, no citations
        if counts["chunks"] != 0:
            raise SystemExit(f"AUDIT FAILED: require-empty violated: chunks={counts['chunks']}")
        if counts["runs"] != 0:
            raise SystemExit(f"AUDIT FAILED: require-empty violated: runs={counts['runs']}")
        if counts["run_citations"] != 0:
            raise SystemExit(f"AUDIT FAILED: require-empty violated: run_citations={counts['run_citations']}")

        if args.require_anchors is not None and counts["anchors"] != args.require_anchors:
            raise SystemExit(f"AUDIT FAILED: anchors={counts['anchors']} expected={args.require_anchors}")

        master = read_sqlite_master(conn)
    finally:
        conn.close()

    if fk != 1:
        raise SystemExit("AUDIT FAILED: PRAGMA foreign_keys != 1")
    if integ != "ok":
        raise SystemExit(f"AUDIT FAILED: PRAGMA integrity_check != ok (got {integ})")

    # Registry sanity
    reg = json.loads(registry_path.read_text(encoding="utf-8"))
    if not isinstance(reg, list):
        raise SystemExit("AUDIT FAILED: registry must be a JSON array.")
    if len(reg) != counts["anchors"]:
        raise SystemExit(f"AUDIT FAILED: registry_entries={len(reg)} != db_anchors={counts['anchors']}")

    # Ledger coherence (tail parse)
    ledger_events = ledger_tail(ledger_path, args.ledger_tail)
    for ev in ledger_events:
        if not isinstance(ev, dict):
            raise SystemExit("AUDIT FAILED: bad ledger event type")

    report: Dict[str, Any] = {
        "kind": "PRE_INGESTION_AUDIT_EXT",
        "version": "V1_STRICT",
        "generated_local": now_local_offset_iso(),
        "generated_utc": utc_z_now(),
        "db_rel": db_path.relative_to(BASE_DIR).as_posix(),
        "db_counts": counts,
        "foreign_keys": int(fk),
        "integrity_check": str(integ),
        "schema_rel": schema_path.relative_to(BASE_DIR).as_posix(),
        "schema_sha256": schema_sha,
        "schema_hints": schema_hints,
        "sqlite_master": master,
        "registry_rel": registry_path.relative_to(BASE_DIR).as_posix(),
        "registry_entries": len(reg),
        "manifest_rel": manifest_path.relative_to(BASE_DIR).as_posix(),
        "manifest_sha256": manifest_sha,
        "manifest_files": len(man_files),
        "anchors_files": len(fs_files),
        "ledger_rel": ledger_path.relative_to(BASE_DIR).as_posix(),
        "ledger_tail_checked": len(ledger_events),
        "wal_exists": wal_present,
        "shm_exists": shm_present,
        "allow_wal": bool(args.allow_wal),
    }

    if args.out:
        out_path = Path(args.out)
        if not out_path.is_absolute():
            out_path = (BASE_DIR / out_path).resolve()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"OK: wrote {out_path.relative_to(BASE_DIR).as_posix()}")

    print("PRE-INGESTION AUDIT EXT: PASS (STRICT)")
    print(f"OK: counts={counts} fk={fk} integrity={integ}")
    print(f"OK: manifest={report['manifest_rel']} files={report['manifest_files']} sha256={report['manifest_sha256']}")
    print(f"OK: schema_sha256={schema_sha}")
    print(f"OK: ledger_tail_checked={report['ledger_tail_checked']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
