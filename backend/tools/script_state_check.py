from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import sys

REG_PATH = Path("docs") / "SCRIPT_STATE_REGISTRY.json"


@dataclass
class CheckResult:
    path: str
    exists: bool
    state: str
    sha256_expected: str | None
    sha256_actual: str | None
    status: str  # OK | MISSING | DRIFT | UNSTAMPED


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def load_registry() -> dict:
    if not REG_PATH.exists():
        raise FileNotFoundError(f"Registry not found: {REG_PATH}")
    raw = REG_PATH.read_text(encoding="utf-8")
    return json.loads(raw)


def main(argv: list[str]) -> int:
    root = Path.cwd()
    out_dir = root / "evidence" / "audits"
    out_dir.mkdir(parents=True, exist_ok=True)

    mode = "check"
    if "--stamp" in argv:
        mode = "stamp"  # prints a patch suggestion (does not edit files)

    reg = load_registry()
    files = reg.get("files", {})

    results: list[CheckResult] = []
    for rel, meta in files.items():
        state = meta.get("state", "OBSERVE")
        p = root / rel
        exists = p.exists()

        expected = meta.get("sha256")
        actual = sha256_file(p) if exists else None

        if not exists:
            status = "MISSING"
        elif state in ("HOLSTERED", "OBSERVE", "REPAIR", "DRAFT"):
            # These states don't require stamping
            status = "OK" if exists else "MISSING"
        elif expected in (None, "", "null"):
            status = "UNSTAMPED"
        elif expected != actual:
            status = "DRIFT"
        else:
            status = "OK"

        results.append(CheckResult(rel, exists, state, expected, actual, status))

    ts = utc_now()
    report = {
        "type": "script_state_check",
        "ts_utc": ts,
        "registry_path": str(REG_PATH),
        "results": [r.__dict__ for r in results],
        "summary": {
            "ok": sum(r.status == "OK" for r in results),
            "missing": sum(r.status == "MISSING" for r in results),
            "unstamped": sum(r.status == "UNSTAMPED" for r in results),
            "drift": sum(r.status == "DRIFT" for r in results)
        }
    }

    out_json = out_dir / f"SCRIPT_STATE_CHECK_{ts.replace(':','').replace('.','')}.json"
    out_md = out_dir / f"SCRIPT_STATE_CHECK_{ts.replace(':','').replace('.','')}.md"
    out_json.write_text(json.dumps(report, indent=2), encoding="utf-8")

    lines = []
    lines.append("# Script State Check\n")
    lines.append(f"- ts_utc: {ts}\n")
    lines.append("## Results\n")
    for r in results:
        lines.append(f"- {r.path} | state={r.state} | status={r.status}\n")
        if r.status in ("DRIFT", "UNSTAMPED") and r.exists:
            lines.append(f"  - sha256_actual: `{r.sha256_actual}`\n")
            if r.sha256_expected:
                lines.append(f"  - sha256_expected: `{r.sha256_expected}`\n")

    if mode == "stamp":
        lines.append("\n## Stamp Suggestions (manual apply)\n")
        lines.append("Update registry sha256 fields for FROZEN/STABLE files:\n")
        for r in results:
            if r.exists and r.state in ("FROZEN", "STABLE"):
                lines.append(f'- "{r.path}": sha256 => "{r.sha256_actual}"\n')

    out_md.write_text("".join(lines), encoding="utf-8")

    print(f"[OK] wrote:\n- {out_json}\n- {out_md}")
    print(json.dumps(report["summary"], indent=2))

    # Non-zero exit if drift or missing
    if report["summary"]["drift"] > 0 or report["summary"]["missing"] > 0:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
