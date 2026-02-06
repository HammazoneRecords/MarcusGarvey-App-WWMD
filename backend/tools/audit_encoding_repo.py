from __future__ import annotations

import json
import re
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path

# Detect "?i?m?p?o?r?t?" style corruption (ghost chars)
GHOST_RE = re.compile(r"(?:\?[\w]){6,}")
NULL_RE = re.compile(r"\x00")
REPLACEMENT_CHAR = "\ufffd"  # "?"

EXCLUDE_DIR_PARTS = {
    ".git", ".venv", "venv", "node_modules", "__pycache__",
    "data", "archive", "evidence",  # keep audits out of scan by default
}

@dataclass
class Finding:
    path: str
    bytes_len: int
    has_nulls: bool
    ghost_hits: int
    replacement_hits: int
    question_marks: int
    sample: str

def utc_ts() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

def should_exclude(p: Path) -> bool:
    # exclude by folder parts
    if any(part in EXCLUDE_DIR_PARTS for part in p.parts):
        return True
    # exclude this tool itself (avoid self-referential noise)
    if p.name.lower() == "audit_encoding_repo.py":
        return True
    return False

def sample_around(text: str, idx: int, span: int = 120) -> str:
    if idx < 0:
        idx = 0
    start = max(idx - span, 0)
    end = min(idx + span, len(text))
    return text[start:end].replace("\n", "\\n")

def scan_one(p: Path) -> Finding | None:
    raw = p.read_bytes()
    txt = raw.decode("utf-8", errors="replace")

    has_nulls = bool(NULL_RE.search(txt))
    ghost_hits = len(GHOST_RE.findall(txt))
    repl_hits = txt.count(REPLACEMENT_CHAR)
    q_count = txt.count("?")

    suspicious = has_nulls or ghost_hits > 0 or repl_hits > 0
    if not suspicious:
        return None

    # point to something meaningful in sample
    idx = txt.find(REPLACEMENT_CHAR)
    if idx == -1:
        m = GHOST_RE.search(txt)
        idx = m.start() if m else -1
    if idx == -1 and has_nulls:
        idx = txt.find("\x00")

    return Finding(
        path=str(p),
        bytes_len=len(raw),
        has_nulls=has_nulls,
        ghost_hits=ghost_hits,
        replacement_hits=repl_hits,
        question_marks=q_count,
        sample=sample_around(txt, idx),
    )

def main() -> int:
    root = Path.cwd().resolve()
    py_files = [p for p in root.rglob("*.py") if not should_exclude(p)]

    findings: list[Finding] = []
    for p in py_files:
        f = scan_one(p)
        if f:
            findings.append(f)

    audits_dir = root / "evidence" / "audits"
    audits_dir.mkdir(parents=True, exist_ok=True)

    ts = utc_ts()
    out_json = audits_dir / f"ENCODING_AUDIT_{ts}.json"
    out_md = audits_dir / f"ENCODING_AUDIT_{ts}.md"

    payload = {
        "type": "encoding_audit",
        "ts_utc": ts,
        "root": str(root),
        "scanned": len(py_files),
        "suspicious": len(findings),
        "findings": [asdict(f) for f in findings],
    }
    out_json.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = []
    lines.append("# Encoding Audit\n")
    lines.append(f"- ts_utc: {ts}")
    lines.append(f"- scanned: {len(py_files)}")
    lines.append(f"- suspicious: {len(findings)}\n")

    if not findings:
        lines.append("PASS ? no corruption signatures detected.\n")
    else:
        lines.append("## Suspicious Files\n")
        for f in findings:
            lines.append(f"### {f.path}\n")
            lines.append(
                f"- bytes: {f.bytes_len}\n"
                f"- nulls: {f.has_nulls}\n"
                f"- ghost_hits: {f.ghost_hits}\n"
                f"- replacement_hits: {f.replacement_hits}\n"
                f"- '?' count: {f.question_marks}\n"
            )
            lines.append(f"- sample: `{f.sample}`\n")

    out_md.write_text("\n".join(lines), encoding="utf-8")

    print(f"[OK] wrote:\n- {out_json}\n- {out_md}")
    print(f"[RESULT] scanned={len(py_files)} suspicious={len(findings)}")
    return 0 if len(findings) == 0 else 2

if __name__ == "__main__":
    raise SystemExit(main())
