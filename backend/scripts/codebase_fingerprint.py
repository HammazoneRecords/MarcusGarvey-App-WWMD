from __future__ import annotations

import argparse
import hashlib
import json
import os
import fnmatch
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

from state_guard import require_allowed

BASE_DIR = Path(__file__).resolve().parent.parent


def require_recorded_run() -> None:
    if os.environ.get("SOLOB_RECORDED_RUN") != "1":
        raise RuntimeError("BLOCKED: codebase_fingerprint.py must run via scripts/run_recorded.py (recorded-only).")


def now_local_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def now_utc_iso_z() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def should_exclude(rel_path: str, exclude_patterns: List[str]) -> bool:
    # Check if any part of the path matches an exclude pattern (naive approach for directories)
    # We want to match path parts against patterns. 
    # Also handle typical gitignore-style globbing vaguely.
    # The prompt specified exclude patterns like "anchors", "evidence".
    # Check if the path starts with an excluded directory
    
    parts = rel_path.split("/")
    
    for pattern in exclude_patterns:
        # Check exact matches on path components (e.g. "anchors" matching "anchors/foo.txt")
        if pattern in parts:
            return True
        # Check standard glob matching on the full relative path
        if fnmatch.fnmatch(rel_path, pattern):
            return True
        # Check if the pattern is a directory prefix
        if rel_path.startswith(pattern + "/"):
            return True
            
    return False


def main() -> int:
    require_recorded_run()
    require_allowed("run_script")

    ap = argparse.ArgumentParser(description="Generate a deterministic SHA256 map of the codebase.")
    ap.add_argument("--root", default=".", help="Root directory to scan (default: .).")
    ap.add_argument("--out", required=True, help="Output JSON path.")
    ap.add_argument("--exclude", nargs="*", default=["data", "evidence", "logs", "__pycache__", ".venv", ".git", ".idea", ".vscode"], help="Directories/patterns to exclude.")
    
    args = ap.parse_args()
    
    out_path = Path(args.out)
    if not out_path.is_absolute():
        out_path = (BASE_DIR / out_path).resolve()
        
    root_dir = (BASE_DIR / args.root).resolve()
    if not root_dir.exists():
        raise FileNotFoundError(f"Root dir not found: {root_dir}")
    
    excludes = args.exclude
    files_list: List[Dict[str, Any]] = []
    total_bytes = 0
    
    # Walk the tree from root
    for root, dirs, files in os.walk(root_dir):
        # Prune excluded dirs in-place to prevent recursion
        # We must check relative path of dir against excludes
        # This is tricky because 'root' is absolute.
        
        # 1. Filter dirs
        allowed_dirs = []
        for d in dirs:
            d_abs = Path(root) / d
            try:
                # We always fingerprint relative to BASE_DIR for the report
                d_rel = d_abs.relative_to(BASE_DIR).as_posix()
            except ValueError:
                # If root is outside BASE_DIR, we fingerprint relative to root_dir
                d_rel = d_abs.relative_to(root_dir).as_posix()

            if not should_exclude(d_rel, excludes):
                allowed_dirs.append(d)
        
        # Update dirs[:] to prune walk
        dirs[:] = allowed_dirs
        
        # 2. Process files
        for name in files:
            fpath = Path(root) / name
            try:
                rel = fpath.relative_to(BASE_DIR).as_posix()
            except ValueError:
                rel = fpath.relative_to(root_dir).as_posix()
                
            if not should_exclude(rel, excludes):
                size = fpath.stat().st_size
                sha = sha256_file(fpath)
                files_list.append({
                    "rel_path": rel,
                    "sha256": sha,
                    "bytes": size
                })
                total_bytes += size

    # Sort files for determinism
    files_list.sort(key=lambda x: x["rel_path"].lower())
    
    # Calculate fingerprint of the files list itself
    files_json_bytes = json.dumps(files_list, ensure_ascii=False, sort_keys=True).encode("utf-8")
    fingerprint = sha256_bytes(files_json_bytes)
    
    report = {
        "kind": "CODEBASE_FINGERPRINT",
        "generated_local": now_local_iso(),
        "generated_utc": now_utc_iso_z(),
        "root": args.root,
        "exclusions": sorted(excludes),
        "file_count": len(files_list),
        "total_bytes": total_bytes,
        "fingerprint_sha256": fingerprint,
        "files": files_list
    }
    
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    
    print(f"OK: wrote {out_path.relative_to(BASE_DIR).as_posix()}")
    print(f"OK: files={len(files_list)} bytes={total_bytes} fingerprint={fingerprint}")
    
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
