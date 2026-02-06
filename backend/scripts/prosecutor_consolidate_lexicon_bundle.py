# scripts/prosecutor_consolidate_lexicon_bundle.py
"""
Consolidate Lexicon A?Z evidence into one uniform "Supreme Bundle" SID folder.

- Collects exactly one receipt per letter: RECEIPT_LEXICON_<L>*.json
- Collects exactly one stamp per letter:  LEXICON_STAMP_<L>*.json
- Prefers sources from an A?Z SID (LEXICON_AZ) when multiple exist.
- Emits:
    evidence/<NEW_SID>/RECEIPTS/
    evidence/<NEW_SID>/STAMPS/
    evidence/<NEW_SID>/BUNDLE.json
    evidence/<NEW_SID>/INDEX.json   (sha256 for all files in the new bundle folder)

Safe: read-only on existing evidence; only writes new bundle folder.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

RE_SID = re.compile(r"^S_\d{8}T\d{6}Z_")
RECEIPT_PAT = re.compile(r"^RECEIPT_LEXICON_([A-Z]).*\.json$")
STAMP_PAT = re.compile(r"^LEXICON_STAMP_([A-Z]).*\.json$")

def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def utc_now_compact() -> str:
    # 20251225T062802Z format
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

@dataclass
class Pick:
    letter: str
    src: Path
    reason: str

def score_path(p: Path) -> Tuple[int, str]:
    """
    Higher score = preferred.
    We prefer:
      1) paths containing 'LEXICON_AZ' or 'LEXICON_AZ_FULL'
      2) then any path containing 'LEXICON'
      3) then everything else
    Secondary sort: lexical path (stable)
    """
    s = str(p).upper()
    score = 0
    if "LEXICON_AZ" in s:
        score += 100
    if "LEXICON_AZ_FULL" in s:
        score += 10
    if "LEXICON" in s:
        score += 5
    return score, s

def choose_best(candidates: List[Path]) -> Path:
    candidates = sorted(candidates, key=lambda p: score_path(p), reverse=True)
    return candidates[0]

def find_sid_dirs(evidence_dir: Path) -> List[Path]:
    out = []
    for child in evidence_dir.iterdir():
        if child.is_dir() and RE_SID.match(child.name):
            out.append(child)
    return sorted(out)

def find_candidates(evidence_dir: Path) -> Tuple[Dict[str, List[Path]], Dict[str, List[Path]]]:
    receipts: Dict[str, List[Path]] = {chr(c): [] for c in range(ord("A"), ord("Z") + 1)}
    stamps: Dict[str, List[Path]] = {chr(c): [] for c in range(ord("A"), ord("Z") + 1)}

    for sid_dir in find_sid_dirs(evidence_dir):
        for p in sid_dir.iterdir():
            if not p.is_file():
                continue
            m = RECEIPT_PAT.match(p.name)
            if m:
                receipts[m.group(1)].append(p)
                continue
            m = STAMP_PAT.match(p.name)
            if m:
                stamps[m.group(1)].append(p)
                continue

    return receipts, stamps

def write_json(p: Path, obj) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=True)

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--evidence-dir", default="evidence", help="Evidence root (default: evidence)")
    ap.add_argument("--out-sid", default=None, help="Override output SID folder name")
    ap.add_argument("--include-db-checkpoint", action="store_true", help="Copy DB_CHECKPOINT.json from preferred LEXICON_AZ folder if present")
    args = ap.parse_args()

    evidence_dir = Path(args.evidence_dir).resolve()
    if not evidence_dir.exists():
        raise SystemExit(f"evidence dir not found: {evidence_dir}")

    out_sid = args.out_sid
    if not out_sid:
        out_sid = f"S_{utc_now_compact()}_SUPREME_LEXICON_BUNDLE"

    out_dir = evidence_dir / out_sid
    receipts_dir = out_dir / "RECEIPTS"
    stamps_dir = out_dir / "STAMPS"

    if out_dir.exists():
        raise SystemExit(f"Refusing to overwrite existing bundle folder: {out_dir}")

    rec_cands, stamp_cands = find_candidates(evidence_dir)

    picks_receipts: List[Pick] = []
    picks_stamps: List[Pick] = []
    missing: List[str] = []

    for L in rec_cands.keys():
        if not rec_cands[L]:
            missing.append(f"receipt:{L}")
        else:
            best = choose_best(rec_cands[L])
            picks_receipts.append(Pick(L, best, "best_by_preference"))

        if not stamp_cands[L]:
            missing.append(f"stamp:{L}")
        else:
            best = choose_best(stamp_cands[L])
            picks_stamps.append(Pick(L, best, "best_by_preference"))

    if missing:
        print("Missing required A-Z items:")
        for x in missing:
            print("  -", x)
        return 2

    # Copy files
    receipts_dir.mkdir(parents=True, exist_ok=True)
    stamps_dir.mkdir(parents=True, exist_ok=True)

    copied: List[Dict[str, str]] = []
    for pk in picks_receipts:
        dst = receipts_dir / pk.src.name
        shutil.copy2(pk.src, dst)
        copied.append({"type": "receipt", "letter": pk.letter, "src": str(pk.src), "dst": str(dst)})

    for pk in picks_stamps:
        dst = stamps_dir / pk.src.name
        shutil.copy2(pk.src, dst)
        copied.append({"type": "stamp", "letter": pk.letter, "src": str(pk.src), "dst": str(dst)})

    # Optionally pull DB_CHECKPOINT.json from best lexicon AZ SID folder
    db_checkpoint_copy: Optional[Path] = None
    if args.include_db_checkpoint:
        sid_dirs = find_sid_dirs(evidence_dir)
        az = [d for d in sid_dirs if "LEXICON_AZ" in d.name.upper()]
        az = sorted(az, key=lambda d: d.name, reverse=True)
        for d in az:
            cand = d / "DB_CHECKPOINT.json"
            if cand.exists():
                db_dir = out_dir / "DB"
                db_dir.mkdir(parents=True, exist_ok=True)
                dst = db_dir / "DB_CHECKPOINT.json"
                shutil.copy2(cand, dst)
                db_checkpoint_copy = dst
                break

    # Build SID-local index
    files_index: List[Dict[str, str]] = []
    for p in out_dir.rglob("*"):
        if p.is_file():
            rel = p.relative_to(out_dir).as_posix()
            files_index.append({"path": rel, "sha256": sha256_file(p)})

    index_obj = {
        "index_version": 1,
        "sid": out_sid,
        "generated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "file_count": len(files_index),
        "files": files_index,
    }
    write_json(out_dir / "INDEX.json", index_obj)

    # Bundle contract
    bundle_obj = {
        "bundle_version": 1,
        "sid": out_sid,
        "reality": "PROSECUTOR",
        "scope": "lexicon_az_consolidation",
        "created_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "contents": {
            "receipts": 26,
            "stamps": 26,
            "db_checkpoint_included": bool(db_checkpoint_copy),
        },
        "sources": copied,
        "index": {"path": "INDEX.json", "sha256": sha256_file(out_dir / "INDEX.json")},
    }
    write_json(out_dir / "BUNDLE.json", bundle_obj)

    print(f"OK: created supreme lexicon bundle at: {out_dir}")
    print("OK: receipts=26 stamps=26")
    print(f"OK: index file_count={index_obj['file_count']}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
