from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Tuple

BASE_DIR = Path(__file__).resolve().parent.parent

def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def load_json(p: Path) -> Dict:
    return json.loads(p.read_text(encoding="utf-8"))

def normalize_manifest_files(files) -> List[Tuple[str, str]]:
    # JSON stores lists, our code may use tuples; normalize to tuples
    out: List[Tuple[str, str]] = []
    for pair in files:
        if not isinstance(pair, (list, tuple)) or len(pair) != 2:
            raise ValueError("Manifest files must be [rel_path, sha256] pairs.")
        out.append((str(pair[0]), str(pair[1])))
    return sorted(out, key=lambda x: x[0].lower())

def main() -> int:
    ap = argparse.ArgumentParser(description="Verify Prosecutor evidence bundle consistency.")
    ap.add_argument("--bundle", required=True, help="Evidence bundle dir, e.g. evidence/<SID>")
    ap.add_argument("--sid", required=True, help="import_session_id expected in receipt")
    ap.add_argument("--db", default="data/memory.db")
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--registry", required=True)
    args = ap.parse_args()

    bundle_dir = (BASE_DIR / args.bundle).resolve()
    db_path = (BASE_DIR / args.db).resolve()
    manifest_path = (BASE_DIR / args.manifest).resolve()
    registry_path = (BASE_DIR / args.registry).resolve()

    if not bundle_dir.exists():
        raise SystemExit(f"AUDIT FAILED: bundle missing: {bundle_dir}")
    if not db_path.exists():
        raise SystemExit(f"AUDIT FAILED: db missing: {db_path}")
    if not manifest_path.exists():
        raise SystemExit(f"AUDIT FAILED: manifest missing: {manifest_path}")
    if not registry_path.exists():
        raise SystemExit(f"AUDIT FAILED: registry missing: {registry_path}")

    # Expected files
    batch_receipt = bundle_dir / "BATCH_RECEIPT.json"
    if not batch_receipt.exists():
        raise SystemExit("AUDIT FAILED: missing BATCH_RECEIPT.json in bundle")

    receipt = load_json(batch_receipt)

    if receipt.get("import_session_id") != args.sid:
        raise SystemExit(f"AUDIT FAILED: SID mismatch. receipt={receipt.get('import_session_id')} expected={args.sid}")

    # Verify hashes match reality
    db_sha = sha256_file(db_path)
    manifest_sha = sha256_file(manifest_path)

    if receipt.get("db_sha256") != db_sha:
        raise SystemExit("AUDIT FAILED: db_sha256 mismatch (bundle receipt vs actual db file).")
    if receipt.get("manifest_sha256") != manifest_sha:
        raise SystemExit("AUDIT FAILED: manifest_sha256 mismatch (bundle receipt vs actual manifest file).")

    # Verify registry entries align with DB anchors
    reg = json.loads(registry_path.read_text(encoding="utf-8"))
    if not isinstance(reg, list):
        raise SystemExit("AUDIT FAILED: registry must be a JSON array.")

    reg_ids = sorted([str(x.get("anchor_id","")) for x in reg])
    if any(not x for x in reg_ids):
        raise SystemExit("AUDIT FAILED: registry contains blank anchor_id.")

    conn = sqlite3.connect(str(db_path))
    try:
        conn.execute("PRAGMA foreign_keys = ON;")
        db_ids = sorted([r[0] for r in conn.execute("SELECT anchor_id FROM anchors ORDER BY anchor_id;")])
        if db_ids != reg_ids:
            raise SystemExit("AUDIT FAILED: DB anchors do not match registry anchor_id list.")

        # Verify DB anchors count matches receipt
        db_anchor_n = conn.execute("SELECT COUNT(*) FROM anchors;").fetchone()[0]
        if int(receipt.get("anchors_in_batch", -1)) != int(db_anchor_n):
            raise SystemExit("AUDIT FAILED: anchors_in_batch mismatch vs DB.")
    finally:
        conn.close()

    # Verify manifest file list matches what bundle believes (optional: compare by rel_path)
    m = load_json(manifest_path)
    mf = normalize_manifest_files(m.get("files", []))
    if int(receipt.get("receipts_written", -1)) != int(receipt.get("anchors_in_batch", -2)):
        raise SystemExit("AUDIT FAILED: receipts_written != anchors_in_batch in receipt (internal inconsistency).")
    if int(receipt.get("anchors_in_batch", -1)) != len(reg_ids):
        raise SystemExit("AUDIT FAILED: anchors_in_batch != len(registry).")

    print("PROSECUTOR VERIFY: PASS")
    print(f"OK: sid={args.sid}")
    print(f"OK: db_sha256={db_sha}")
    print(f"OK: manifest_sha256={manifest_sha}")
    print(f"OK: anchors={len(reg_ids)} manifest_files={len(mf)} bundle={bundle_dir.as_posix()}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
