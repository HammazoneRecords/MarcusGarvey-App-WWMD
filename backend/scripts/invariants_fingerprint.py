from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path

from state_guard import require_allowed

BASE_DIR = Path(__file__).resolve().parent.parent


def require_recorded_run() -> None:
    if os.environ.get("SOLOB_RECORDED_RUN") != "1":
        raise RuntimeError(
            "BLOCKED: invariants_fingerprint.py must be executed via scripts/run_recorded.py"
        )


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def utc_z_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def extract_version_line(text: str) -> str:
    # Best-effort: look for "CANONICAL vX" in first ~30 lines
    lines = text.splitlines()[:30]
    for ln in lines:
        if "CANONICAL" in ln and "v" in ln:
            return ln.strip()
    return ""


def main() -> int:
    require_recorded_run()
    require_allowed("run_script")

    ap = argparse.ArgumentParser(description="Fingerprint docs/invariants.md and lock it.")
    ap.add_argument("--file", required=True, help="Path to invariants markdown")
    ap.add_argument("--out", required=True, help="Path to invariants.lock.json")
    ap.add_argument(
        "--update-lock",
        action="store_true",
        help="Overwrite lock (requires --confirm YES_I_MEAN_IT).",
    )
    ap.add_argument(
        "--confirm",
        default="",
        help="Safety latch for --update-lock. Must be EXACTLY: YES_I_MEAN_IT",
    )
    args = ap.parse_args()

    fpath = Path(args.file)
    if not fpath.is_absolute():
        fpath = (BASE_DIR / fpath).resolve()
    if not fpath.exists():
        raise FileNotFoundError(f"Missing file: {fpath}")

    out = Path(args.out)
    if not out.is_absolute():
        out = (BASE_DIR / out).resolve()

    content = fpath.read_text(encoding="utf-8", errors="strict")
    version_hint = extract_version_line(content)
    file_sha = sha256_file(fpath)
    size_bytes = fpath.stat().st_size

    payload = {
        "kind": "INVARIANTS_LOCK",
        "lock_version": "V1",
        "generated_utc": utc_z_now(),
        "file_rel": fpath.relative_to(BASE_DIR).as_posix(),
        "sha256": file_sha,
        "bytes": size_bytes,
        "version_hint": version_hint,
    }

    if out.exists() and not args.update_lock:
        old = json.loads(out.read_text(encoding="utf-8"))
        old_sha = str(old.get("sha256", ""))
        if old_sha != file_sha:
            raise SystemExit(
                "AUDIT FAILED: invariants lock mismatch.\n"
                f"expected_sha256={old_sha}\n"
                f"actual_sha256={file_sha}\n"
                "If you intentionally changed invariants, re-run with --update-lock --confirm YES_I_MEAN_IT"
            )
        print("INVARIANTS LOCK: PASS")
        print(f"OK: {payload['file_rel']} sha256={file_sha}")
        return 0

    if out.exists() and args.update_lock:
        if args.confirm != "YES_I_MEAN_IT":
            raise SystemExit("Blocked: --confirm must be exactly YES_I_MEAN_IT to update lock.")

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"OK: wrote {out.relative_to(BASE_DIR).as_posix()}")
    print(f"OK: sha256={file_sha} bytes={size_bytes}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
