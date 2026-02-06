from __future__ import annotations

import argparse
import hashlib
import json
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict

from state_guard import require_allowed

BASE_DIR = Path(__file__).resolve().parent.parent


def require_recorded_run() -> None:
    if os.environ.get("SOLOB_RECORDED_RUN") != "1":
        raise RuntimeError("BLOCKED: must run via scripts/run_recorded.py")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def utc_z_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_expect(spec: str) -> Dict[str, int]:
    # "anchors=8 chunks=0 runs=0 run_citations=0"
    out: Dict[str, int] = {}
    for part in spec.split():
        if "=" not in part:
            continue
        k, v = part.split("=", 1)
        out[k.strip()] = int(v.strip())
    return out


def main() -> int:
    require_recorded_run()
    require_allowed("run_script")

    ap = argparse.ArgumentParser(description="Seal a checkpoint with expected table counts + db sha.")
    ap.add_argument("--db", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--expect", required=True, help="Space-separated k=v counts (anchors=8 chunks=0 ...)")
    ap.add_argument("--manifest", default=None, help="Optional manifest path to include + hash")
    args = ap.parse_args()

    db_path = Path(args.db)
    if not db_path.is_absolute():
        db_path = (BASE_DIR / db_path).resolve()
    if not db_path.exists():
        raise FileNotFoundError(f"Missing DB: {db_path}")

    out_path = Path(args.out)
    if not out_path.is_absolute():
        out_path = (BASE_DIR / out_path).resolve()

    expect = parse_expect(args.expect)
    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA foreign_keys = ON;")
    try:
        counts = {
            "anchors": conn.execute("SELECT COUNT(*) FROM anchors;").fetchone()[0],
            "chunks": conn.execute("SELECT COUNT(*) FROM chunks;").fetchone()[0],
            "runs": conn.execute("SELECT COUNT(*) FROM runs;").fetchone()[0],
            "run_citations": conn.execute("SELECT COUNT(*) FROM run_citations;").fetchone()[0],
        }
    finally:
        conn.close()

    for k, v in expect.items():
        if k not in counts:
            raise SystemExit(f"AUDIT FAILED: unknown expect key '{k}' (known: {sorted(counts)})")
        if counts[k] != v:
            raise SystemExit(f"AUDIT FAILED: {k}={counts[k]} expected={v}")

    payload = {
        "kind": "CHECKPOINT",
        "checkpoint": "ANCHORS_ONLY",
        "version": "V1",
        "generated_utc": utc_z_now(),
        "db_rel": db_path.relative_to(BASE_DIR).as_posix(),
        "db_sha256": sha256_file(db_path),
        "counts": counts,
    }

    if args.manifest:
        mp = Path(args.manifest)
        if not mp.is_absolute():
            mp = (BASE_DIR / mp).resolve()
        if not mp.exists():
            raise FileNotFoundError(f"Missing manifest: {mp}")
        payload["manifest_rel"] = mp.relative_to(BASE_DIR).as_posix()
        payload["manifest_sha256"] = sha256_file(mp)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"OK: wrote {out_path.relative_to(BASE_DIR).as_posix()}")
    print(f"OK: counts={counts}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())