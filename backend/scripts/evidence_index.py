from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

from state_guard import require_allowed

BASE_DIR = Path(__file__).resolve().parent.parent


def require_recorded_run() -> None:
    if os.environ.get("SOLOB_RECORDED_RUN") != "1":
        raise RuntimeError("BLOCKED: evidence_index.py must run via scripts/run_recorded.py")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def utc_z_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def collect_files(root: Path, strict: bool) -> List[Dict[str, Any]]:
    items: List[Dict[str, Any]] = []
    if not root.exists():
        if strict:
            raise FileNotFoundError(f"Evidence root not found: {root}")
        return items

    for p in sorted(root.rglob("*"), key=lambda x: x.as_posix().lower()):
        if p.is_dir():
            continue
        rel = p.relative_to(BASE_DIR).as_posix() if p.is_absolute() else p.as_posix()
        try:
            items.append(
                {
                    "rel": rel,
                    "bytes": p.stat().st_size,
                    "sha256": sha256_file(p),
                }
            )
        except Exception as e:
            if strict:
                raise
            items.append({"rel": rel, "error": str(e)})
    return items


def group_by_bundle(root: Path, files: List[Dict[str, Any]]) -> Dict[str, Any]:
    # Bundles are typically evidence/<SID>/...
    # We group by first folder under root (sid folder), else "_root"
    bundles: Dict[str, Any] = {}
    root_rel = root.relative_to(BASE_DIR).as_posix()
    for f in files:
        rel = f.get("rel", "")
        if not isinstance(rel, str):
            continue
        # rel like "evidence/SID/file.json"
        parts = rel.split("/")
        bundle = "_root"
        if len(parts) >= 2 and parts[0] == root_rel.split("/")[0]:
            # if root is "evidence", parts[1] is SID
            if parts[0] == root_rel and len(parts) >= 2:
                bundle = parts[1]
        bundles.setdefault(bundle, {"files": []})
        bundles[bundle]["files"].append(f)

    # deterministic ordering inside each bundle
    for b in bundles.values():
        b["files"] = sorted(b["files"], key=lambda x: str(x.get("rel", "")).lower())
    return dict(sorted(bundles.items(), key=lambda kv: kv[0].lower()))


def main() -> int:
    require_recorded_run()
    require_allowed("run_script")

    ap = argparse.ArgumentParser(description="Build evidence/INDEX.json with sha256 for every evidence file.")
    ap.add_argument("--root", required=True, help="Evidence root folder (e.g. evidence)")
    ap.add_argument("--out", required=True, help="Output index JSON path (e.g. evidence/INDEX.json)")
    ap.add_argument("--strict", action="store_true", default=True, help="Fail on missing/unreadable evidence root/files")
    ap.add_argument("--non-strict", action="store_true", default=False, help="Don't fail on missing/unreadable files")
    args = ap.parse_args()

    strict = args.strict and not args.non_strict

    root = Path(args.root)
    if not root.is_absolute():
        root = (BASE_DIR / root).resolve()

    out_path = Path(args.out)
    if not out_path.is_absolute():
        out_path = (BASE_DIR / out_path).resolve()

    files = collect_files(root, strict=strict)
    bundles = group_by_bundle(root, files)

    n_files = len(files)
    n_bundles = len(bundles)

    payload: Dict[str, Any] = {
        "kind": "EVIDENCE_INDEX",
        "version": "V1",
        "generated_utc": utc_z_now(),
        "root_rel": root.relative_to(BASE_DIR).as_posix(),
        "strict": strict,
        "file_count": n_files,
        "bundles": bundles,
    }

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(f"OK: wrote {out_path.relative_to(BASE_DIR).as_posix()}")
    print(f"OK: root={root} out={out_path.as_posix()} files={n_files} bundles={n_bundles}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
