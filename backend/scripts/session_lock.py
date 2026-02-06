from __future__ import annotations

import argparse
import hashlib
import json
import os
import sqlite3
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

from state_guard import require_allowed

BASE_DIR = Path(__file__).resolve().parent.parent
ANCHORS_DIR = BASE_DIR / "anchors"
SNAP_DIR = BASE_DIR / "data" / "snapshots"
STATE_PATH = BASE_DIR / "docs" / "STATE.json"


def require_recorded_run() -> None:
    if os.environ.get("SOLOB_RECORDED_RUN") != "1":
        raise RuntimeError("BLOCKED: session_lock.py must run via scripts/run_recorded.py (recorded-only).")


def utc_z(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def now_local_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def now_utc_iso_z() -> str:
    return utc_z(datetime.now(timezone.utc))


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def pick_latest_manifest() -> Path:
    files = sorted(SNAP_DIR.glob("anchors_manifest_*.json"))
    if not files:
        raise FileNotFoundError(f"No anchors manifests found in: {SNAP_DIR}")
    return files[-1]


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


def read_state_json() -> Dict[str, Any]:
    if not STATE_PATH.exists():
        return {"state": "UNKNOWN"}
    return json.loads(STATE_PATH.read_text(encoding="utf-8"))


def tail_lines(path: Path, n: int) -> List[str]:
    if not path.exists():
        raise FileNotFoundError(f"Missing file: {path}")
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    if n <= 0:
        return lines
    return lines[-n:]


def ledger_tail_parse(path: Path, n: int) -> Dict[str, Any]:
    lines = tail_lines(path, n)
    raw = ("\n".join(lines) + "\n").encode("utf-8", errors="replace")
    sha = sha256_bytes(raw)
    parsed: List[Dict[str, Any]] = []
    for i, ln in enumerate(lines):
        if not ln.strip():
            continue
        try:
            obj = json.loads(ln)
        except Exception as e:
            raise SystemExit(f"SESSION LOCK FAILED: ops_ledger JSON parse error in tail line[{i}]: {e}")
        if not isinstance(obj, dict):
            raise SystemExit("SESSION LOCK FAILED: ledger tail contains non-object JSON.")
        parsed.append(obj)
    return {"tail_count": len(parsed), "tail_sha256": sha}


def git_info() -> Dict[str, Any]:
    # Best-effort: do not fail if git isn't available.
    # Suppress stderr so "fatal: not a git repository" doesn't leak.
    out: Dict[str, Any] = {"git_head": None, "git_dirty": None}
    try:
        # Check HEAD
        proc_head = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=str(BASE_DIR),
            capture_output=True,
            text=True
        )
        if proc_head.returncode == 0:
            out["git_head"] = proc_head.stdout.strip()

            # Check Status
            proc_status = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=str(BASE_DIR),
                capture_output=True,
                text=True
            )
            if proc_status.returncode == 0:
                out["git_dirty"] = bool(proc_status.stdout.strip())
    except Exception:
        # Git completely missing or executable not found
        pass
    return out


def sqlite_master_fingerprint(conn: sqlite3.Connection) -> Dict[str, Any]:
    rows = conn.execute(
        """
        SELECT type, name, sql
        FROM sqlite_master
        WHERE type IN ('table','index','trigger','view')
        ORDER BY type ASC, name ASC;
        """
    ).fetchall()

    # Canonical dump
    dump_lines: List[str] = []
    for t, name, sql in rows:
        dump_lines.append(f"{t}:{name}")
        dump_lines.append((sql or "").strip())
        dump_lines.append("")  # separator

    dump = "\n".join(dump_lines).strip() + "\n"
    return {
        "sqlite_master_sha256": sha256_bytes(dump.encode("utf-8", errors="replace")),
        "sqlite_master_items": [{"type": r[0], "name": r[1]} for r in rows],
    }


def main() -> int:
    require_recorded_run()
    require_allowed("run_script")

    ap = argparse.ArgumentParser(description="SESSION LOCK: capture baseline snapshot for controlled implementation.")
    ap.add_argument("--sid", required=True, help="Session id used for evidence folder naming.")
    ap.add_argument("--db", default="data/memory.db")
    ap.add_argument("--schema", default="data/schema.sql")
    ap.add_argument("--registry", default="docs/ANCHOR_REGISTRY_PLAN.json")
    ap.add_argument("--manifest", default="", help="anchors_manifest_*.json path (default latest).")
    ap.add_argument("--ledger", default="logs/ops_ledger.jsonl")
    ap.add_argument("--ledger-tail", type=int, default=80)
    ap.add_argument("--fail-on-wal", action="store_true", default=True)
    ap.add_argument("--allow-wal", action="store_true", default=False)
    ap.add_argument("--out", required=True, help="Output JSON path (recommend evidence/<SID>/SESSION_LOCK.json).")
    args = ap.parse_args()

    sid = args.sid.strip()
    if not sid:
        raise SystemExit("SESSION LOCK FAILED: --sid cannot be blank.")

    db_path = (BASE_DIR / args.db).resolve() if not Path(args.db).is_absolute() else Path(args.db)
    schema_path = (BASE_DIR / args.schema).resolve() if not Path(args.schema).is_absolute() else Path(args.schema)
    registry_path = (BASE_DIR / args.registry).resolve() if not Path(args.registry).is_absolute() else Path(args.registry)
    ledger_path = (BASE_DIR / args.ledger).resolve() if not Path(args.ledger).is_absolute() else Path(args.ledger)

    manifest_path = Path(args.manifest) if args.manifest else pick_latest_manifest()
    if not manifest_path.is_absolute():
        manifest_path = (BASE_DIR / manifest_path).resolve()

    if not db_path.exists():
        raise FileNotFoundError(f"DB not found: {db_path}")
    if not schema_path.exists():
        raise FileNotFoundError(f"schema.sql not found: {schema_path}")
    if not registry_path.exists():
        raise FileNotFoundError(f"registry not found: {registry_path}")
    if not manifest_path.exists():
        raise FileNotFoundError(f"manifest not found: {manifest_path}")
    if not ledger_path.exists():
        raise FileNotFoundError(f"ops ledger not found: {ledger_path}")

    wal = db_path.with_suffix(db_path.suffix + "-wal")
    shm = db_path.with_suffix(db_path.suffix + "-shm")
    wal_present = wal.exists()
    shm_present = shm.exists()
    if not args.allow_wal and args.fail_on_wal and (wal_present or shm_present):
        raise SystemExit(
            "SESSION LOCK FAILED: WAL/SHM artifacts present.\n"
            f"- wal_exists={wal_present} ({wal})\n"
            f"- shm_exists={shm_present} ({shm})\n"
            "If intentional, rerun with --allow-wal."
        )

    # Manifest vs filesystem anchors (hard truth)
    manifest = load_manifest(manifest_path)
    fs_files = compute_anchors_fingerprint()
    man_files = manifest["files_norm"]

    if len(fs_files) != len(man_files):
        raise SystemExit(
            f"SESSION LOCK FAILED: Manifest/filecount mismatch. manifest={len(man_files)} filesystem={len(fs_files)}"
        )

    fs_map = {rel: sha for rel, sha in fs_files}
    for rel, sha in man_files:
        if rel not in fs_map:
            raise SystemExit(f"SESSION LOCK FAILED: manifest rel_path missing on disk: {rel}")
        if fs_map[rel] != sha:
            raise SystemExit(f"SESSION LOCK FAILED: sha256 mismatch for {rel}\nexpected={sha}\nactual={fs_map[rel]}")

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

        dup_chunk_id_groups = conn.execute(
            "SELECT COUNT(*) FROM (SELECT chunk_id FROM chunks GROUP BY chunk_id HAVING COUNT(*)>1);"
        ).fetchone()[0]
        dup_locator_groups = conn.execute(
            "SELECT COUNT(*) FROM (SELECT anchor_id, anchor_locator FROM chunks GROUP BY anchor_id, anchor_locator HAVING COUNT(*)>1);"
        ).fetchone()[0]
        orphan_chunks = conn.execute(
            "SELECT COUNT(*) FROM chunks WHERE anchor_id NOT IN (SELECT anchor_id FROM anchors);"
        ).fetchone()[0]

        sm = sqlite_master_fingerprint(conn)
    finally:
        conn.close()

    if fk != 1:
        raise SystemExit("SESSION LOCK FAILED: PRAGMA foreign_keys != 1")
    if integ != "ok":
        raise SystemExit(f"SESSION LOCK FAILED: PRAGMA integrity_check != ok (got {integ})")

    # Registry shape sanity (minimal)
    reg = json.loads(registry_path.read_text(encoding="utf-8"))
    if not isinstance(reg, list):
        raise SystemExit("SESSION LOCK FAILED: registry must be a JSON array.")

    # Ledger tail digest (also proves ?what the last N recorded acts were?)
    led = ledger_tail_parse(ledger_path, args.ledger_tail)

    out_path = Path(args.out)
    if not out_path.is_absolute():
        out_path = (BASE_DIR / out_path).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    report: Dict[str, Any] = {
        "kind": "SESSION_LOCK",
        "version": "V1",
        "sid": sid,
        "generated_local": now_local_iso(),
        "generated_utc": now_utc_iso_z(),
        "state": read_state_json(),
        "paths": {
            "db": db_path.relative_to(BASE_DIR).as_posix(),
            "schema": schema_path.relative_to(BASE_DIR).as_posix(),
            "registry": registry_path.relative_to(BASE_DIR).as_posix(),
            "manifest": manifest_path.relative_to(BASE_DIR).as_posix(),
            "ledger": ledger_path.relative_to(BASE_DIR).as_posix(),
        },
        "hashes": {
            "db_sha256": sha256_file(db_path),
            "schema_sha256": sha256_file(schema_path),
            "registry_sha256": sha256_file(registry_path),
            "manifest_sha256": sha256_file(manifest_path),
            "anchors_fingerprint_sha256": sha256_bytes(
                json.dumps(fs_files, ensure_ascii=False, sort_keys=True).encode("utf-8", errors="replace")
            ),
            **{"sqlite_master_sha256": sm["sqlite_master_sha256"]},
        },
        "db": {
            "counts": counts,
            "foreign_keys": int(fk),
            "integrity_check": str(integ),
            "dup_chunk_id_groups": int(dup_chunk_id_groups),
            "dup_locator_groups": int(dup_locator_groups),
            "orphan_chunks": int(orphan_chunks),
        },
        "sqlite_master_items": sm["sqlite_master_items"],
        "manifest": {
            "files": len(man_files),
        },
        "anchors": {
            "files": len(fs_files),
        },
        "ledger_tail": led,
        "wal_shm": {
            "wal_exists": wal_present,
            "shm_exists": shm_present,
            "allow_wal": bool(args.allow_wal),
        },
        **git_info(),
    }

    out_path.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(f"OK: wrote {out_path.relative_to(BASE_DIR).as_posix()}")
    print("SESSION LOCK: PASS")
    print(f"OK: db_counts={counts} fk={fk} integrity={integ}")
    print(f"OK: manifest={report['paths']['manifest']} files={len(man_files)} sha256={report['hashes']['manifest_sha256']}")
    print(f"OK: anchors_fingerprint_sha256={report['hashes']['anchors_fingerprint_sha256']}")
    print(f"OK: ledger_tail_count={report['ledger_tail']['tail_count']} ledger_tail_sha256={report['ledger_tail']['tail_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
