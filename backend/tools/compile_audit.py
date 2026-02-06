#!/usr/bin/env python3
"""
Compile Audit - Syntax validation for Python files.
Scans scripts/, tools/, core/ for Python syntax errors.
Outputs JSON report to evidence/audits/
"""
from __future__ import annotations

import ast
import json
from datetime import datetime, timezone
from pathlib import Path


def utc_ts() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def compile_audit(root: Path) -> dict:
    """Scan Python files for syntax errors."""
    scan_dirs = ["scripts", "tools", "core", "utils"]
    results = {
        "scanned": 0,
        "errors": [],
        "clean": []
    }
    
    for dir_name in scan_dirs:
        dir_path = root / dir_name
        if not dir_path.exists():
            continue
            
        for py_file in dir_path.rglob("*.py"):
            results["scanned"] += 1
            try:
                py_file.read_text(encoding="utf-8").encode("utf-8")
                ast.parse(py_file.read_text(encoding="utf-8"), filename=str(py_file))
                results["clean"].append(str(py_file.relative_to(root)))
            except SyntaxError as e:
                results["errors"].append({
                    "file": str(py_file.relative_to(root)),
                    "line": e.lineno,
                    "error": str(e)
                })
            except Exception as e:
                results["errors"].append({
                    "file": str(py_file.relative_to(root)),
                    "error": repr(e)
                })
    
    return results


def main() -> int:
    root = Path.cwd().resolve()
    ts = utc_ts()
    
    audit_dir = root / "evidence" / "audits"
    audit_dir.mkdir(parents=True, exist_ok=True)
    
    results = compile_audit(root)
    
    report = {
        "kind": "compile_audit",
        "version": "1.0",
        "ts_utc": ts,
        "root": str(root),
        "scanned": results["scanned"],
        "errors": results["errors"],
        "clean_count": len(results["clean"]),
        "status": "PASS" if len(results["errors"]) == 0 else "FAIL"
    }
    
    out_file = audit_dir / f"COMPILE_AUDIT_{ts}.json"
    out_file.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    
    print(f"[OK] Compile audit complete: {out_file}")
    print(f"[STATUS] {report['status']}")
    print(f"[SCANNED] {report['scanned']} files")
    print(f"[ERRORS] {len(results['errors'])} syntax errors")
    
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
