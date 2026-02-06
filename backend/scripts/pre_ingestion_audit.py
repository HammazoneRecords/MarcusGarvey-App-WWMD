# scripts/pre_ingestion_audit.py
from __future__ import annotations

import json
import os
import sqlite3
import sys
from pathlib import Path

from hash_utils import sha256_manifest
from state_guard import require_allowed

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "memory.db"
SNAPSHOTS_DIR = DATA_DIR / "snapshots"
ANCHORS_DIR = BASE_DIR / "anchors"
LOGS_DIR = BASE_DIR / "logs"
LEDGER_PATH = LOGS_DIR / "ops_ledger.jsonl"


def audit() -> None:
    # 1) Must refuse unrecorded runs
    if os.environ.get("SOLOB_RECORDED_RUN") != "1":
        raise RuntimeError(
            "BLOCKED: pre_ingestion_audit.py must be run via scripts/run_recorded.py"
        )

    # 2) Must enforce STGRAIL
    require_allowed("run_script")

    # A) Check DB file exists
    if not DB_PATH.exists():
        raise FileNotFoundError(f"DB not found at: {DB_PATH}")

    # Connect read-only
    db_uri = f"file:{DB_PATH.as_posix()}?mode=ro"
    conn = sqlite3.connect(db_uri, uri=True)
    cursor = conn.cursor()

    try:
        # B) Integrity check
        cursor.execute("PRAGMA integrity_check;")
        res = cursor.fetchone()[0]
        if res != "ok":
            raise RuntimeError(f"DB integrity check failed: {res}")

        # C) Foreign key check
        cursor.execute("PRAGMA foreign_key_check;")
        fk_errors = cursor.fetchall()
        if fk_errors:
            raise RuntimeError(f"Foreign key violations found: {fk_errors}")

        # D) Required tables
        req_tables = {"anchors", "chunks", "provenance_notes", "runs", "run_citations"}
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        existing_tables = {row[0] for row in cursor.fetchall()}
        missing_tables = req_tables - existing_tables
        if missing_tables:
            raise RuntimeError(f"Missing tables: {missing_tables}")

        # E) Required indexes
        req_indexes = {
            "idx_chunks_anchor_id",
            "idx_runs_created_at",
            "idx_prov_target",
            "idx_run_citations_chunk",
        }
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index';")
        existing_indexes = {row[0] for row in cursor.fetchall()}
        missing_indexes = req_indexes - existing_indexes
        if missing_indexes:
            raise RuntimeError(f"Missing indexes: {missing_indexes}")

        # F) Confirm zero rows pre-ingestion
        for table in ["anchors", "chunks", "runs", "run_citations"]:
            cursor.execute(f"SELECT COUNT(*) FROM {table};")
            count = cursor.fetchone()[0]
            if count != 0:
                raise RuntimeError(f"Table {table} is NOT empty (count={count})")

    finally:
        conn.close()

    # G) Manifest fidelity
    manifest_files = sorted(SNAPSHOTS_DIR.glob("anchors_manifest_*.json"))
    if not manifest_files:
        raise RuntimeError("No manifest files found in data/snapshots/")

    newest_manifest = manifest_files[-1]
    print(f"Auditing manifest: {newest_manifest.name}")

    manifest = json.loads(newest_manifest.read_text(encoding="utf-8"))

    def normalize_pairs(pairs):
        """
        Normalize [('a','b'), ['a','b']] -> [('a','b'), ('a','b')]
        and enforce deterministic ordering.
        """
        out = []
        for item in pairs:
            if not isinstance(item, (list, tuple)) or len(item) != 2:
                raise RuntimeError(f"AUDIT FAILED: invalid manifest entry: {item!r}")
            out.append((str(item[0]), str(item[1])))
        return sorted(out)

    # manifest_files comes from JSON => list of lists
    manifest_files_raw = manifest.get("files", [])
    manifest_files = normalize_pairs(manifest_files_raw)

    # fs_files comes from hash_utils => list of tuples
    fs_files_raw = sha256_manifest(ANCHORS_DIR)
    fs_files = normalize_pairs(fs_files_raw)

    if manifest_files != fs_files:
        # Show the first difference to make debugging deterministic
        set_m = set(manifest_files)
        set_f = set(fs_files)
        only_in_manifest = sorted(set_m - set_f)[:5]
        only_on_disk = sorted(set_f - set_m)[:5]
        raise RuntimeError(
            "AUDIT FAILED: Manifest mismatch after normalization.\n"
            f"Only in manifest (up to 5): {only_in_manifest}\n"
            f"Only on disk (up to 5): {only_on_disk}\n"
            f"Counts: manifest={len(manifest_files)}, filesystem={len(fs_files)}"
        )

    # H) Ledger coherence
    if not LEDGER_PATH.exists():
        raise FileNotFoundError(f"Ledger not found at: {LEDGER_PATH}")

    ledger_lines = LEDGER_PATH.read_text(encoding="utf-8").splitlines()
    recent_lines = ledger_lines[-20:]

    for line in recent_lines:
        if not line.strip():
            continue
        entry = json.loads(line)
        if entry.get("action") == "run_script":
            arts = entry.get("artifacts", {})
            if "exit_code" not in arts or arts["exit_code"] is None:
                raise RuntimeError(f"Ledger entry missing exit_code: {line}")

            # Verify log paths if they exist
            for key in ["stdout_path", "stderr_path"]:
                if key in arts and arts[key]:
                    p = Path(arts[key])
                    if not p.exists():
                        raise RuntimeError(f"Log path in ledger does not exist: {p}")

    print("PRE-INGESTION AUDIT: PASS")


if __name__ == "__main__":
    try:
        audit()
    except Exception as e:
        print(f"AUDIT FAILED: {e}", file=sys.stderr)
        sys.exit(1)
