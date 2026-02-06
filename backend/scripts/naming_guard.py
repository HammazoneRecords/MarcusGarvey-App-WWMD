from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import List, Tuple, Dict, Any

BASE_DIR = Path(__file__).resolve().parent.parent
ANCHORS_CANON = BASE_DIR / "anchors" / "canon"
DEFAULT_REGISTRY = BASE_DIR / "docs" / "ANCHOR_REGISTRY_PLAN.json"
DEFAULT_ALLOWLIST = BASE_DIR / "docs" / "NAMING_ALLOWLIST.json"

# allow A?Z too (legacy), but still NO spaces
NAME_RE = re.compile(r"^[A-Za-z0-9_.]+$")
ANCHOR_ID_RE = re.compile(r"^[A-Za-z0-9_]+$")


def norm_posix(p: str) -> str:
    return (p or "").replace("\\", "/").strip()


def load_allowlist(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {"allowed_path_contains": [], "allowed_exact_paths": [], "allowed_anchor_ids": []}
    d = json.loads(path.read_text(encoding="utf-8"))
    return {
        "allowed_path_contains": list(d.get("allowed_path_contains") or []),
        "allowed_exact_paths": list(d.get("allowed_exact_paths") or []),
        "allowed_anchor_ids": list(d.get("allowed_anchor_ids") or []),
    }


def allowlisted_path(rel_path: str, allow: Dict[str, Any]) -> bool:
    rp = norm_posix(rel_path).rstrip("/")

    exacts = {norm_posix(x).rstrip("/") for x in allow["allowed_exact_paths"]}
    if rp in exacts:
        return True

    for frag in allow["allowed_path_contains"]:
        f = norm_posix(frag).rstrip("/")
        if f and f in rp:
            return True

    return False



def offenders_in_canon(allow: Dict[str, Any]) -> List[Tuple[str, str]]:
    bad: List[Tuple[str, str]] = []
    if not ANCHORS_CANON.exists():
        return [("canon_missing", str(ANCHORS_CANON))]

    for p in sorted(ANCHORS_CANON.rglob("*")):
        rel = p.relative_to(BASE_DIR).as_posix()
        if allowlisted_path(rel, allow):
            continue

        name = p.name
        if not NAME_RE.match(name):
            bad.append(("bad_dirname" if p.is_dir() else "bad_filename", rel))
    return bad


def offenders_in_registry(registry_path: Path, allow: Dict[str, Any]) -> List[Tuple[str, str]]:
    bad: List[Tuple[str, str]] = []
    reg = json.loads(registry_path.read_text(encoding="utf-8"))
    if not isinstance(reg, list):
        return [("registry_format", "Registry must be a JSON array")]

    for i, a in enumerate(reg):
        if not isinstance(a, dict):
            bad.append(("registry_entry", f"entry[{i}] not an object"))
            continue

        aid = str(a.get("anchor_id", "")).strip()
        sp = norm_posix(str(a.get("source_path", "")).strip())

        if aid and aid in set(allow.get("allowed_anchor_ids", [])):
            pass
        else:
            if not aid or not ANCHOR_ID_RE.match(aid):
                bad.append(("bad_anchor_id", f"entry[{i}] anchor_id='{aid}'"))

        if not sp:
            bad.append(("missing_source_path", f"entry[{i}] anchor_id='{aid}'"))
            continue

        # path policy: check each part unless allowlisted
        rel = sp
        for part in [x for x in rel.split("/") if x]:
            if not NAME_RE.match(part):
                # allowlist can excuse legacy paths with spaces
                if allowlisted_path(rel, allow):
                    break
                bad.append(("bad_source_path", f"entry[{i}] anchor_id='{aid}' source_path='{sp}'"))
                break

    return bad


def main() -> int:
    ap = argparse.ArgumentParser(description="Read-only naming audit with allowlist grandfathering.")
    ap.add_argument("--registry", default=str(DEFAULT_REGISTRY))
    ap.add_argument("--allowlist", default=str(DEFAULT_ALLOWLIST))
    args = ap.parse_args()

    reg_path = Path(args.registry)
    if not reg_path.is_absolute():
        reg_path = (BASE_DIR / reg_path).resolve()
    if not reg_path.exists():
        print(f"AUDIT FAILED: missing registry: {reg_path}", file=sys.stderr)
        return 2

    allow_path = Path(args.allowlist)
    if not allow_path.is_absolute():
        allow_path = (BASE_DIR / allow_path).resolve()

    allow = load_allowlist(allow_path)

    bad: List[Tuple[str, str]] = []
    bad.extend(offenders_in_canon(allow))
    bad.extend(offenders_in_registry(reg_path, allow))

    if bad:
        print("AUDIT FAILED: naming invariant violations found:")
        for kind, detail in bad:
            print(f"- {kind}: {detail}")
        return 1

    print("NAMING AUDIT: PASS (with allowlist grandfathering)")
    if allow_path.exists():
        print(f"OK: allowlist={allow_path.relative_to(BASE_DIR).as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())