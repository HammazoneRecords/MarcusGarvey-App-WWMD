# scripts/cartographer_emit_anchors_map.py
from __future__ import annotations

import argparse
import json
import os
import sqlite3
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple, Optional

from state_guard import require_allowed

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "memory.db"
DEFAULT_REGISTRY = BASE_DIR / "docs" / "ANCHOR_REGISTRY_PLAN.json"
SNAP_DIR = BASE_DIR / "data" / "snapshots"
DEFAULT_OUT = BASE_DIR / "docs" / "ANCHORS_MAP.md"
DEFAULT_OUT_ASCII = BASE_DIR / "docs" / "ANCHORS_MAP_ASCII.md"


def require_recorded_run() -> None:
    if os.environ.get("SOLOB_RECORDED_RUN") != "1":
        raise RuntimeError(
            "BLOCKED: cartographer_emit_anchors_map.py must be executed via scripts/run_recorded.py "
            "(NO UNRECORDED SHUFFLES)."
        )


def now_local_offset() -> datetime:
    return datetime.now().astimezone()


def utc_z(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def norm_rel(p: str) -> str:
    s = (p or "").strip().replace("\\", "/")
    if s.startswith("./"):
        s = s[2:]
    if s.lower().startswith("anchors/"):
        s = s[len("anchors/") :]
    return s


def pick_latest_manifest() -> Path:
    files = sorted(SNAP_DIR.glob("anchors_manifest_*.json"))
    if not files:
        raise FileNotFoundError(f"No anchors manifests found in: {SNAP_DIR}")
    return files[-1]


def load_manifest(path: Path) -> Dict[str, Any]:
    d = json.loads(path.read_text(encoding="utf-8"))
    if "files" not in d or not isinstance(d["files"], list):
        raise ValueError("Manifest invalid: expected key 'files' as list.")
    files: List[Tuple[str, str]] = []
    for item in d["files"]:
        if not (isinstance(item, (list, tuple)) and len(item) == 2):
            raise ValueError("Manifest invalid: each 'files' entry must be [rel_path, sha256].")
        rel, sha = str(item[0]), str(item[1])
        files.append((rel.replace("\\", "/"), sha))
    d["files_norm"] = files
    return d


def load_registry(path: Path) -> List[Dict[str, Any]]:
    reg = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(reg, list):
        raise ValueError("Registry must be a JSON array.")
    return reg


def read_db_anchors() -> Dict[str, Dict[str, Any]]:
    if not DB_PATH.exists():
        raise FileNotFoundError(f"DB not found at: {DB_PATH}")

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    try:
        rows = conn.execute(
            """
            SELECT anchor_id, anchor_type, title, source_path, source_format, status,
                   provenance, import_session_id, created_at
            FROM anchors
            ORDER BY anchor_id ASC;
            """
        ).fetchall()

        out: Dict[str, Dict[str, Any]] = {}
        for r in rows:
            out[str(r[0])] = {
                "anchor_id": r[0],
                "anchor_type": r[1],
                "title": r[2],
                "source_path": r[3],
                "source_format": r[4],
                "status": r[5],
                "provenance": r[6],
                "import_session_id": r[7],
                "created_at": r[8],
            }
        return out
    finally:
        conn.close()


def md_escape(s: str) -> str:
    return (s or "").replace("|", "\\|").replace("\n", " ").strip()


def to_ascii(s: str) -> str:
    if s is None:
        return ""
    x = str(s)
    # quick canonical replacements
    x = x.replace("?", "-").replace("?", "-").replace("?", "...")
    x = x.replace("?", '"').replace("?", '"').replace("?", "'").replace("?", "'")
    x = x.replace("\u00A0", " ")  # nbsp
    # strip accents deterministically
    x = unicodedata.normalize("NFKD", x)
    x = "".join(ch for ch in x if not unicodedata.combining(ch))
    # final clamp
    x = x.encode("ascii", "replace").decode("ascii")
    return x


def build_markdown(
    *,
    manifest_path: Path,
    registry_path: Path,
    manifest_files: List[Tuple[str, str]],
    registry: List[Dict[str, Any]],
    db_anchors: Dict[str, Dict[str, Any]],
    ascii_mode: bool,
) -> str:
    manifest_map: Dict[str, str] = {rel: sha for rel, sha in manifest_files}

    anchor_ids = sorted(set(db_anchors.keys()) | {str(a.get("anchor_id")) for a in registry if isinstance(a, dict)})

    dt_local = now_local_offset()
    local_str = dt_local.isoformat(timespec="seconds")
    utc_str = utc_z(dt_local)

    esc = (lambda s: md_escape(to_ascii(s))) if ascii_mode else md_escape

    lines: List[str] = []
    lines.append("# ANCHORS_MAP_ASCII" if ascii_mode else "# ANCHORS_MAP")
    lines.append("")
    lines.append("## Snapshot Context")
    lines.append(f"- Generated (local): `{esc(local_str)}`")
    lines.append(f"- Generated (UTC): `{esc(utc_str)}`")
    lines.append(f"- Manifest: `{esc(manifest_path.relative_to(BASE_DIR).as_posix())}`")
    lines.append(f"- Registry: `{esc(registry_path.relative_to(BASE_DIR).as_posix())}`")
    lines.append(f"- DB: `data/memory.db`")
    lines.append("")

    lines.append("## Anchors Table")
    lines.append("")
    lines.append("| anchor_id | type | status | source_path | manifest_rel_path | sha256 | format | title | import_session_id | created_at |")
    lines.append("|---|---|---|---|---|---|---|---|---|---|")

    missing_in_db: List[str] = []
    missing_in_manifest: List[str] = []

    for aid in anchor_ids:
        db = db_anchors.get(aid)

        if not db:
            missing_in_db.append(aid)
            reg_item = next((x for x in registry if isinstance(x, dict) and str(x.get("anchor_id")) == aid), None)
            src = str(reg_item.get("source_path")) if reg_item else ""
            rel = norm_rel(src)
            sha = manifest_map.get(rel)
            if sha is None and rel:
                missing_in_manifest.append(aid)

            lines.append(
                "| {aid} | {t} | {st} | {sp} | {mr} | {sha} | {fmt} | {title} | {sid} | {ca} |".format(
                    aid=esc(aid),
                    t="(unregistered)",
                    st="(n/a)",
                    sp=esc(src),
                    mr=esc(rel),
                    sha=esc(sha or "(no match)"),
                    fmt=esc(str(reg_item.get("source_format")) if reg_item else ""),
                    title=esc(str(reg_item.get("title")) if reg_item else ""),
                    sid="",
                    ca="",
                )
            )
            continue

        src_db = str(db["source_path"])
        rel = norm_rel(src_db)
        sha = manifest_map.get(rel)
        if sha is None:
            missing_in_manifest.append(aid)

        lines.append(
            "| {aid} | {t} | {st} | {sp} | {mr} | {sha} | {fmt} | {title} | {sid} | {ca} |".format(
                aid=esc(str(db["anchor_id"])),
                t=esc(str(db["anchor_type"])),
                st=esc(str(db["status"])),
                sp=esc(src_db),
                mr=esc(rel),
                sha=esc(sha or "(no match)"),
                fmt=esc(str(db["source_format"])),
                title=esc(str(db["title"])),
                sid=esc(str(db["import_session_id"])),
                ca=esc(str(db["created_at"])),
            )
        )

    lines.append("")
    lines.append("## Integrity Notes")
    lines.append("")
    lines.append(f"- DB anchors: `{len(db_anchors)}`")
    lines.append(f"- Manifest files: `{len(manifest_files)}`")
    lines.append(f"- Registry entries: `{len(registry)}`")
    lines.append("")

    if missing_in_db:
        lines.append(f"- WARNING: missing in DB: `{esc(', '.join(missing_in_db))}`")
    if missing_in_manifest:
        lines.append(f"- WARNING: no manifest sha match: `{esc(', '.join(sorted(set(missing_in_manifest))))}`")
    if not (missing_in_db or missing_in_manifest):
        lines.append("- OK: All DB anchors mapped to manifest sha256 successfully.")

    return "\n".join(lines) + "\n"


def main() -> int:
    require_recorded_run()
    require_allowed("run_script")

    ap = argparse.ArgumentParser(description="Emit ANCHORS_MAP.md (and optional ASCII version) from Registry + DB + Manifest.")
    ap.add_argument("--registry", default=str(DEFAULT_REGISTRY))
    ap.add_argument("--manifest", default=None)
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    ap.add_argument("--out-ascii", default=None, help="If set, also emit ASCII-safe map here.")
    args = ap.parse_args()

    reg_path = Path(args.registry)
    if not reg_path.is_absolute():
        reg_path = (BASE_DIR / reg_path).resolve()
    if not reg_path.exists():
        raise FileNotFoundError(f"Registry not found: {reg_path}")

    man_path = Path(args.manifest) if args.manifest else pick_latest_manifest()
    if not man_path.is_absolute():
        man_path = (BASE_DIR / man_path).resolve()
    if not man_path.exists():
        raise FileNotFoundError(f"Manifest not found: {man_path}")

    out_path = Path(args.out)
    if not out_path.is_absolute():
        out_path = (BASE_DIR / out_path).resolve()

    out_ascii_path: Optional[Path] = None
    if args.out_ascii:
        out_ascii_path = Path(args.out_ascii)
        if not out_ascii_path.is_absolute():
            out_ascii_path = (BASE_DIR / out_ascii_path).resolve()
    # default behavior: if user doesn?t pass out-ascii, we do nothing extra

    manifest = load_manifest(man_path)
    registry = load_registry(reg_path)
    db_anchors = read_db_anchors()

    md_utf8 = build_markdown(
        manifest_path=man_path,
        registry_path=reg_path,
        manifest_files=manifest["files_norm"],
        registry=registry,
        db_anchors=db_anchors,
        ascii_mode=False,
    )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(md_utf8, encoding="utf-8")

    print(f"OK: wrote {out_path.relative_to(BASE_DIR).as_posix()}")
    print(f"OK: db_anchors={len(db_anchors)} manifest_files={len(manifest['files_norm'])} registry_entries={len(registry)}")

    if out_ascii_path is not None:
        md_ascii = build_markdown(
            manifest_path=man_path,
            registry_path=reg_path,
            manifest_files=manifest["files_norm"],
            registry=registry,
            db_anchors=db_anchors,
            ascii_mode=True,
        )
        out_ascii_path.parent.mkdir(parents=True, exist_ok=True)
        out_ascii_path.write_text(md_ascii, encoding="utf-8")
        print(f"OK: wrote {out_ascii_path.relative_to(BASE_DIR).as_posix()} (ASCII-safe)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())