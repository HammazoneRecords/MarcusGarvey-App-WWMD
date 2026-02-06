from __future__ import annotations

import argparse
import json
import os
import shutil
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

from hash_utils import sha256_file

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "memory.db"
LEDGER_PATH = BASE_DIR / "logs" / "ops_ledger.jsonl"

def utc_now_z() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def require_recorded_run() -> None:
    if os.environ.get("SOLOB_RECORDED_RUN") != "1":
        raise RuntimeError("Blocked: must run via scripts/run_recorded.py (recorded run only).")

def load_manifest(manifest_path: Path) -> Dict[str, str]:
    d = json.loads(manifest_path.read_text(encoding="utf-8"))
    # manifest["files"] is list of [rel_path, sha256] after JSON round-trip
    files = d.get("files", [])
    out: Dict[str, str] = {}
    for pair in files:
        if not isinstance(pair, list) or len(pair) != 2:
            raise ValueError("Manifest files must be a list of [rel_path, sha256].")
        out[str(pair[0])] = str(pair[1])
    return out

def iter_ledger_events() -> List[Dict[str, Any]]:
    if not LEDGER_PATH.exists():
        return []
    out = []
    for line in LEDGER_PATH.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except Exception:
            # keep going; corrupted line shouldn't kill Prosecutor
            continue
    return out

def source_path_to_manifest_rel(source_path: str) -> str:
    # DB source_path is like: anchors/canon/...
    # Manifest rel_path is like: canon/...
    s = source_path.replace("\\", "/")
    if s.startswith("anchors/"):
        return s[len("anchors/") :]
    return s

def main() -> int:
    require_recorded_run()

    ap = argparse.ArgumentParser()
    ap.add_argument("--sid", required=True, help="import_session_id to bundle (e.g., S_..._MONK)")
    ap.add_argument("--manifest", required=True, help="Path to anchors_manifest_*.json")
    ap.add_argument("--out", required=True, help="Output folder for evidence bundle")
    args = ap.parse_args()

    sid = args.sid.strip()
    manifest_path = (BASE_DIR / args.manifest).resolve() if not Path(args.manifest).is_absolute() else Path(args.manifest)
    out_dir = (BASE_DIR / args.out).resolve() if not Path(args.out).is_absolute() else Path(args.out)

    if not DB_PATH.exists():
        raise FileNotFoundError(f"DB missing: {DB_PATH}")
    if not manifest_path.exists():
        raise FileNotFoundError(f"Manifest missing: {manifest_path}")

    out_dir.mkdir(parents=True, exist_ok=True)
    # V2 Layout: RECEIPTS/ subdirectory instead of anchors_receipts/
    (out_dir / "RECEIPTS").mkdir(parents=True, exist_ok=True)
    (out_dir / "MANIFESTS").mkdir(parents=True, exist_ok=True)

    manifest_map = load_manifest(manifest_path)
    db_sha = sha256_file(DB_PATH)
    manifest_sha = sha256_file(manifest_path)

    # Pull DB anchors for this sid
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")

    anchors = conn.execute(
        """
        SELECT anchor_id, anchor_type, title, source_path, source_format, status, provenance, import_session_id, created_at
        FROM anchors
        WHERE import_session_id = ?
        ORDER BY anchor_id;
        """,
        (sid,),
    ).fetchall()

    # Ledger subset for this sid (by substring match in human_intent)
    events = iter_ledger_events()
    sid_events = []
    for e in events:
        hi = str(e.get("human_intent", "") or "")
        if sid in hi:
            sid_events.append(e)

    ts_list = []
    for e in sid_events:
        t = e.get("ts_utc")
        if isinstance(t, str) and t:
            ts_list.append(t)

    batch_start_utc = min(ts_list) if ts_list else None
    batch_end_utc = max(ts_list) if ts_list else None

    # Write anchor receipts
    receipts_written = 0
    for row in anchors:
        (anchor_id, anchor_type, title, source_path, source_format, status, provenance, import_session_id, created_at) = row
        rel = source_path_to_manifest_rel(source_path)
        file_sha = manifest_map.get(rel)

        chunks_for_anchor_sid = conn.execute(
            "SELECT COUNT(*) FROM chunks WHERE anchor_id = ? AND import_session_id = ?;",
            (anchor_id, sid),
        ).fetchone()[0]

        receipt = {
            "receipt_version": "V1",
            "generated_utc": utc_now_z(),
            "import_session_id": sid,
            "batch_start_ts_utc": batch_start_utc,
            "batch_end_ts_utc": batch_end_utc,
            "db": {"path": str(DB_PATH.as_posix()), "sha256": db_sha},
            "manifest": {
                "path": str(manifest_path.as_posix()),
                "sha256": manifest_sha,
                "entry_rel_path": rel,
                "entry_sha256": file_sha,
            },
            "anchor": {
                "anchor_id": anchor_id,
                "anchor_type": anchor_type,
                "title": title,
                "source_path": source_path,
                "source_format": source_format,
                "status": status,
                "provenance": provenance,
                "created_at": created_at,
            },
            "counts": {
                "chunks_for_anchor_in_this_batch": int(chunks_for_anchor_sid),
            },
            "strict_rules": {
                "missing_anchor_file_hash_in_manifest": "STOP",
                "chunk_collision": "STOP",
                "schema_mismatch": "STOP",
            },
        }

        if file_sha is None:
            raise SystemExit(f"AUDIT FAILED: anchor {anchor_id} missing from manifest rel_path={rel}")

        # V2 Layout: RECEIPTS/RECEIPT_ANCHOR_<anchor_id>.json
        (out_dir / "RECEIPTS" / f"RECEIPT_ANCHOR_{anchor_id}.json").write_text(
            json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        receipts_written += 1

    # V2 Layout: LEDGER_SUBSET.jsonl and MANIFESTS/ directory
    (out_dir / "LEDGER_SUBSET.jsonl").write_text(
        "\n".join(json.dumps(e, ensure_ascii=False, sort_keys=True) for e in sid_events) + ("\n" if sid_events else ""),
        encoding="utf-8",
    )
    shutil.copy2(manifest_path, out_dir / "MANIFESTS" / manifest_path.name)

    # V2 Layout: INDEX.json (was BATCH_RECEIPT.json)
    index = {
        "bundle_version": "V2",
        "bundle_type": "ingestion",
        "bundle_id": sid,
        "generated_utc": utc_now_z(),
        "import_session_id": sid,
        "summary": {
            "anchors_in_batch": len(anchors),
            "receipts_written": receipts_written,
            "ledger_events_matched": len(sid_events),
        },
        "db_sha256": db_sha,
        "manifest_sha256": manifest_sha,
        "batch_start_ts_utc": batch_start_utc,
        "batch_end_ts_utc": batch_end_utc,
        "note": "Evidence bundle (V2 layout). Anchor receipts are deterministic references.",
    }
    (out_dir / "INDEX.json").write_text(
        json.dumps(index, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    # V2 Layout: REPORT.md (human-readable)
    report_md = f"""# Ingestion Bundle Report

**Bundle ID**: {sid}  
**Generated**: {utc_now_z()}  
**Bundle Version**: V2

## Summary

Successfully created evidence bundle for ingestion session `{sid}`.

## Key Metrics

- **Anchors in Batch**: {len(anchors)}
- **Receipts Written**: {receipts_written}
- **Ledger Events**: {len(sid_events)}
- **DB SHA256**: `{db_sha[:16]}...`
- **Manifest SHA256**: `{manifest_sha[:16]}...`
- **Batch Start**: {batch_start_utc or 'N/A'}
- **Batch End**: {batch_end_utc or 'N/A'}

## Bundle Structure

```
{sid}/
??? INDEX.json (bundle metadata)
??? REPORT.md (this file)
??? RECEIPTS/ ({receipts_written} anchor receipts)
??? LEDGER_SUBSET.jsonl ({len(sid_events)} events)
??? MANIFESTS/ (copied manifest)
```

## Anchors

{chr(10).join(f"- {row[0]} ({row[1]})" for row in anchors)}

---

Generated by prosecutor_emit_evidence_bundle.py (V2)
"""
    (out_dir / "REPORT.md").write_text(report_md, encoding="utf-8")

    conn.close()

    print(f"OK: wrote evidence bundle => {out_dir}")
    print(f"OK: anchors={len(anchors)} receipts={receipts_written} ledger_events={len(sid_events)}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
