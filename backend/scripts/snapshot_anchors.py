# scripts/snapshot_anchors.py
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

from hash_utils import sha256_manifest
from ops_log import log_event
from state_guard import require_allowed

BASE_DIR = Path(__file__).resolve().parent.parent
ANCHORS_DIR = BASE_DIR / "anchors"
SNAP_DIR = BASE_DIR / "data" / "snapshots"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def safe_ts() -> str:
    # Example: 20251220T034500Z
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def require_recorded_run() -> None:
    if os.environ.get("SOLOB_RECORDED_RUN") != "1":
        raise RuntimeError(
            "BLOCKED: snapshot_anchors.py must be executed via scripts/run_recorded.py "
            "(NO UNRECORDED SHUFFLES)."
        )


def snapshot_anchors() -> Path:
    require_recorded_run()
    require_allowed("snapshot_anchors")

    if not ANCHORS_DIR.exists():
        raise FileNotFoundError(f"anchors/ folder not found at: {ANCHORS_DIR}")

    SNAP_DIR.mkdir(parents=True, exist_ok=True)
    out_path = SNAP_DIR / f"anchors_manifest_{safe_ts()}.json"

    manifest = {
        "ts_utc": utc_now_iso(),
        "root": str(ANCHORS_DIR.as_posix()),
        "files": sha256_manifest(ANCHORS_DIR),
    }

    out_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )

    intent = os.environ.get(
        "SOLOB_HUMAN_INTENT",
        "Record a read-only cryptographic snapshot of all anchor files before any DB initialization or ingestion.",
    )

    log_event(
        action="snapshot_anchors",
        human_intent=intent,
        payload={"anchors_dir": str(ANCHORS_DIR.as_posix())},
        artifacts={
            "manifest_path": str(out_path.as_posix()),
            "file_count": len(manifest["files"]),
        },
    )

    return out_path


if __name__ == "__main__":
    p = snapshot_anchors()
    print("Intent:", os.environ.get("SOLOB_HUMAN_INTENT", "(none)"))
    print(f"Anchor snapshot written: {p}")
