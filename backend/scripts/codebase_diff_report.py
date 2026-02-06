from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from state_guard import require_allowed

BASE_DIR = Path(__file__).resolve().parent.parent


def require_recorded_run() -> None:
    if os.environ.get("SOLOB_RECORDED_RUN") != "1":
        raise RuntimeError("BLOCKED: codebase_diff_report.py must run via scripts/run_recorded.py (recorded-only).")


def now_local_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def now_utc_iso_z() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def load_fingerprint(path: Path) -> Dict[str, Any]:
    if not path.is_absolute():
        path = (BASE_DIR / path).resolve()
    if not path.exists():
        raise FileNotFoundError(f"Missing fingerprint file: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    require_recorded_run()
    require_allowed("run_script")

    ap = argparse.ArgumentParser(description="Generate a diff report between two codebase fingerprints.")
    ap.add_argument("--before", required=True, help="Path to BEFORE fingerprint JSON.")
    ap.add_argument("--after", required=True, help="Path to AFTER fingerprint JSON.")
    ap.add_argument("--out", required=True, help="Output JSON path for the diff report.")
    
    args = ap.parse_args()
    
    before_data = load_fingerprint(Path(args.before))
    after_data = load_fingerprint(Path(args.after))
    
    # Map rel_path -> sha256
    b_map = {f["rel_path"]: f["sha256"] for f in before_data.get("files", [])}
    a_map = {f["rel_path"]: f["sha256"] for f in after_data.get("files", [])}
    
    all_paths = set(b_map.keys()) | set(a_map.keys())
    
    added = []
    removed = []
    changed = []
    
    for p in sorted(all_paths):
        in_b = p in b_map
        in_a = p in a_map
        
        if in_b and not in_a:
            removed.append({"rel_path": p, "sha_before": b_map[p]})
        elif not in_b and in_a:
            added.append({"rel_path": p, "sha_after": a_map[p]})
        elif in_b and in_a:
            if b_map[p] != a_map[p]:
                changed.append({
                    "rel_path": p,
                    "sha_before": b_map[p],
                    "sha_after": a_map[p]
                })

    unchanged_count = len(all_paths) - (len(added) + len(removed) + len(changed))
    
    summary = {
        "added": len(added),
        "removed": len(removed),
        "changed": len(changed),
        "unchanged_count": unchanged_count,
        "total_impacted": len(added) + len(removed) + len(changed)
    }
    
    out_path = Path(args.out)
    if not out_path.is_absolute():
        out_path = (BASE_DIR / out_path).resolve()
        
    report = {
        "kind": "CODEBASE_DIFF_REPORT",
        "generated_local": now_local_iso(),
        "generated_utc": now_utc_iso_z(),
        "before_fingerprint": before_data.get("fingerprint_sha256"),
        "after_fingerprint": after_data.get("fingerprint_sha256"),
        "summary": summary,
        "details": {
            "added": added,
            "removed": removed,
            "changed": changed
        }
    }
    
    # Calculate self-hash (excluding self)
    report_json_bytes = json.dumps(report, ensure_ascii=False, sort_keys=True).encode("utf-8")
    report["report_sha256"] = sha256_bytes(report_json_bytes)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(f"OK: wrote {out_path.relative_to(BASE_DIR).as_posix()}")
    print(f"OK: summary={summary}")
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
