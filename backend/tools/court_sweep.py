from __future__ import annotations

import json
import sqlite3
import re
import subprocess
import sys
import hashlib
import os
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path

EPOCH_TS = "2025-12-25T07:51:59Z"  # witness epoch per your report

def utc_ts() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

def read_text(p: Path) -> str:
    return p.read_text(encoding="utf-8", errors="replace")

def exists(p: Path) -> bool:
    return p.exists()

def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def audit_db_counts(root: Path) -> dict:
    db = root / "data" / "memory.db"
    if not db.exists():
        return {"status": "FAIL", "reason": "missing data/memory.db", "path": str(db)}

    try:
        con = sqlite3.connect(str(db))
        cur = con.cursor()
        anchors = cur.execute("SELECT COUNT(*) FROM anchors;").fetchone()[0]
        chunks = cur.execute("SELECT COUNT(*) FROM chunks;").fetchone()[0]
        con.close()
        return {"status": "PASS", "db": str(db), "anchors": anchors, "chunks": chunks}
    except Exception as e:
        return {"status": "FAIL", "db": str(db), "error": repr(e)}

def audit_state_history_witness(root: Path) -> dict:
    p = root / "docs" / "STATE_HISTORY.md"
    if not p.exists():
        return {"status": "FAIL", "reason": "missing docs/STATE_HISTORY.md"}

    txt = read_text(p)
    # heuristic: post-epoch entries must contain "SID" and "witness" markers
    post_epoch = []
    blocks = re.split(r"\n(?=## )", txt)
    for b in blocks:
        if EPOCH_TS in b or "2025-12-25" in b or "2025-12-26" in b or "2025-12-27" in b or "2025-12-28" in b:
            post_epoch.append(b)

    unwitnessed = []
    for b in post_epoch:
        if ("SID" not in b) or (("witness" not in b.lower()) and ("WITNESS" not in b)):
            unwitnessed.append(b[:180].replace("\n", "\\n"))

    status = "PASS" if len(unwitnessed) == 0 else "FAIL"
    return {
        "status": status,
        "epoch": EPOCH_TS,
        "checked_blocks": len(post_epoch),
        "unwitnessed_blocks": len(unwitnessed),
        "samples": unwitnessed[:5],
    }

def audit_evidence_index(root: Path) -> dict:
    p = root / "evidence" / "INDEX.json"
    if not p.exists():
        return {"status": "FAIL", "reason": "missing evidence/INDEX.json"}
    try:
        data = json.loads(read_text(p))
        return {"status": "PASS", "path": str(p), "keys": sorted(list(data.keys()))[:30]}
    except Exception as e:
        return {"status": "FAIL", "path": str(p), "error": repr(e)}

def audit_bundle_uniformity(root: Path, current_ts: str = None) -> dict:
    bundles = root / "evidence" / "bundles"
    if not bundles.exists():
        return {"status": "WARN", "reason": "no evidence/bundles directory", "path": str(bundles)}

    required = {"INDEX.json"}
    missing = {}
    checked = 0

    for d in bundles.iterdir():
        if not d.is_dir():
            continue
        # Skip the current Court Sweep bundle (it hasn't written INDEX.json yet)
        if current_ts and f"S_{current_ts}_COURT_SWEEP" in d.name:
            continue
        # Skip all system audit bundles (COURT_SWEEP and FULL_COURT_PRESS)
        if "COURT_SWEEP" in d.name or "FULL_COURT_PRESS" in d.name:
            continue
        checked += 1
        miss = [x for x in required if not (d / x).exists()]
        if miss:
            missing[str(d)] = miss

    if checked == 0:
        return {"status": "WARN", "reason": "no bundles found"}
    return {"status": "PASS" if not missing else "FAIL", "checked": checked, "missing": missing}

def audit_encoding_reports_present(root: Path) -> dict:
    audits = root / "evidence" / "audits"
    if not audits.exists():
        return {"status": "FAIL", "reason": "missing evidence/audits"}
    enc = sorted(audits.glob("ENCODING_AUDIT_*.md"))
    comp = sorted(audits.glob("COMPILE_AUDIT_*.json"))
    status = "PASS" if enc and comp else "FAIL"
    return {"status": status, "encoding_reports": len(enc), "compile_reports": len(comp)}

def audit_receipt_validation(root: Path) -> dict:
    """Validate all V2 receipts using forensic subprocess execution"""
    evidence = root / "evidence"
    if not evidence.exists():
        return {"status": "FAIL", "reason": "missing evidence directory"}

    validator = root / "scripts" / "validate_receipt_v2.py"
    if not validator.exists():
        return {"status": "WARN", "reason": "validate_receipt_v2.py not found", "path": str(validator)}

    # Create forensic output directory
    ts_audit = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    debug_dir = root / "evidence" / "audits" / "validation_debug" / ts_audit
    debug_dir.mkdir(parents=True, exist_ok=True)

    receipts = list(evidence.glob("**/RECEIPTS/RECEIPT_*.json"))
    if not receipts:
        return {"status": "WARN", "reason": "no receipts found", "scanned": 0}

    validated = 0
    invalid = []
    errors = []

    env = os.environ.copy()
    env["PYTHONUTF8"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"
    
    # Pre-hash validator for report
    validator_hash = sha256_file(validator)

    for receipt_path in receipts:
        # Unique ID for this run
        r_id = hashlib.md5(str(receipt_path).encode()).hexdigest()[:8]
        out_base = debug_dir / f"val_{r_id}"
        
        cmd = [
            sys.executable,
            "-X", "utf8",
            str(validator),
            str(receipt_path),
        ]

        try:
            r = subprocess.run(
                cmd,
                cwd=str(root),
                env=env,
                capture_output=True,
                timeout=30,
            )
            
            # Save raw output
            stdout_txt = r.stdout.decode("utf-8", errors="replace")
            stderr_txt = r.stderr.decode("utf-8", errors="replace")
            
            (out_base.with_suffix(".stdout.txt")).write_text(stdout_txt, encoding="utf-8")
            (out_base.with_suffix(".stderr.txt")).write_text(stderr_txt, encoding="utf-8")

            info = {
                "cmd": cmd,
                "returncode": r.returncode,
                "validator": str(validator),
                "validator_sha256": validator_hash,
                "receipt": str(receipt_path),
                "receipt_sha256": sha256_file(receipt_path),
                "cwd": str(root),
                "stdout_file": str(out_base.with_suffix(".stdout.txt").relative_to(root)),
                "stderr_file": str(out_base.with_suffix(".stderr.txt").relative_to(root))
            }

            if r.returncode == 0:
                validated += 1
            else:
                info["error_head"] = stderr_txt[:1000]
                invalid.append(info)
                
        except Exception as e:
            err_file = out_base.with_suffix(".exception.txt")
            err_file.write_text(repr(e), encoding="utf-8")
            errors.append({
                "receipt": str(receipt_path.relative_to(root)),
                "error": repr(e),
                "debug_file": str(err_file.relative_to(root))
            })

    status = "PASS" if len(invalid) == 0 and len(errors) == 0 else "FAIL"
    return {
        "status": status,
        "total_receipts": len(receipts),
        "validated": validated,
        "invalid": invalid[:10],
        "errors": errors[:10],
        "debug_dir": str(debug_dir.relative_to(root)),
        "validator_sha256": validator_hash
    }

def audit_orphan_chunks(root: Path) -> dict:
    """Detect chunks without import_session_id or missing receipts"""
    db = root / "data" / "memory.db"
    if not db.exists():
        return {"status": "FAIL", "reason": "missing data/memory.db"}

    try:
        conn = sqlite3.connect(str(db))
        cur = conn.cursor()

        # Find chunks with NULL import_session_id
        null_sid = cur.execute(
            "SELECT chunk_id, anchor_id FROM chunks WHERE import_session_id IS NULL LIMIT 100"
        ).fetchall()

        # Count total orphans (more efficient than fetching all)
        total_null = cur.execute(
            "SELECT COUNT(*) FROM chunks WHERE import_session_id IS NULL"
        ).fetchone()[0]

        conn.close()

        status = "PASS" if total_null == 0 else "FAIL"
        return {
            "status": status,
            "orphan_chunks_null_sid": total_null,
            "samples": [{"chunk_id": c[0][:50], "anchor_id": c[1]} for c in null_sid[:10]],
        }
    except Exception as e:
        return {"status": "FAIL", "error": repr(e)}

def audit_bundle_layout(root: Path, current_ts: str = None) -> dict:
    """Validate evidence bundle layout compliance (V2 spec)"""
    bundles_dir = root / "evidence" / "bundles"
    if not bundles_dir.exists():
        return {"status": "WARN", "reason": "no evidence/bundles directory"}

    total_bundles = 0
    v2_compliant = 0
    v1_legacy = 0
    non_compliant = []
    court_sweep_skipped = 0

    for bundle_path in bundles_dir.iterdir():
        if not bundle_path.is_dir():
            continue
        
        # Skip all system audit bundles (COURT_SWEEP and FULL_COURT_PRESS)
        if "COURT_SWEEP" in bundle_path.name or "FULL_COURT_PRESS" in bundle_path.name:
            court_sweep_skipped += 1
            continue
        
        total_bundles += 1
        
        # Required files for V2
        has_index = (bundle_path / "INDEX.json").exists()
        has_report = (bundle_path / "REPORT.md").exists()
        
        # V1 indicators
        has_batch_receipt = (bundle_path / "BATCH_RECEIPT.json").exists()
        
        if has_index and has_report:
            # Validate INDEX.json schema
            try:
                index = json.loads((bundle_path / "INDEX.json").read_text(encoding="utf-8"))
                bundle_version = index.get("bundle_version", "unknown")
                if bundle_version == "V2":
                    v2_compliant += 1
                else:
                    v1_legacy += 1
            except Exception as e:
                non_compliant.append({"bundle": bundle_path.name, "error": "invalid INDEX.json"})
        elif has_batch_receipt:
            # V1 bundle (legacy)
            v1_legacy += 1
        else:
            # Missing required files
            missing = []
            if not has_index and not has_batch_receipt:
                missing.append("INDEX.json or BATCH_RECEIPT.json")
            if not has_report:
                missing.append("REPORT.md")
            non_compliant.append({"bundle": bundle_path.name, "missing": missing})

    # Verdict: PASS if all V2 or grandfathered V1, WARN if some V1, FAIL if non-compliant
    # Note: If only COURT_SWEEP bundles exist, that's OK (they're excluded from check)
    if total_bundles == 0:
        status = "PASS"  # All bundles are COURT_SWEEP (excluded), this is OK
    elif non_compliant:
        status = "FAIL"
    elif v1_legacy > 0:
        status = "WARN"  # V1 bundles are deprecated but valid
    else:
        status = "PASS"

    return {
        "status": status,
        "total_bundles": total_bundles,
        "v2_compliant": v2_compliant,
        "v1_legacy": v1_legacy,
        "court_sweep_skipped": court_sweep_skipped,
        "non_compliant": non_compliant[:10],  # Show up to 10
    }

def audit_state_history_format(root: Path) -> dict:
    """Validate STATE_HISTORY.md format compliance"""
    validator = root / "tools" / "validate_state_history_format.py"
    if not validator.exists():
        return {"status": "WARN", "reason": "validator not found", "path": str(validator)}

    try:
        env = os.environ.copy()
        env["PYTHONUTF8"] = "1"
        env["PYTHONIOENCODING"] = "utf-8"

        result = subprocess.run(
            [sys.executable, str(validator), "--state-history", "docs/STATE_HISTORY.md"],
            capture_output=True,
            timeout=10,
            cwd=str(root),
            env=env
        )
        
        # Parse output for metrics
        output = result.stdout.decode("utf-8", errors="replace")
        violations = 0
        warnings = 0
        
        for line in output.splitlines():
            if "VIOLATIONS:" in line:
                try:
                    violations = int(line.split(":")[1].strip())
                except:
                    pass
            elif "WARNINGS:" in line:
                try:
                    warnings = int(line.split(":")[1].strip())
                except:
                    pass
        
        if result.returncode == 0:
            status = "PASS" if warnings == 0 else "WARN"
        else:
            status = "FAIL"
        
        return {
            "status": status,
            "violations": violations,
            "warnings": warnings,
            "exit_code": result.returncode
        }
    except Exception as e:
        return {"status": "FAIL", "error": repr(e)}

def audit_script_state_lookout(root: Path) -> dict:
    """Run Script State Lookout monitoring (9th check)"""
    try:
        # Run lookout in JSON mode
        result = subprocess.run(
            [sys.executable, str(root / "tools" / "script_state_lookout.py"), "--json"],
            capture_output=True,
            text=True,
            cwd=root
        )
        
        if result.returncode > 2:  # Unexpected error
            return {"status": "FAIL", "error": f"Lookout failed with exit code {result.returncode}"}
        
        try:
            report = json.loads(result.stdout)
        except json.JSONDecodeError:
            return {"status": "FAIL", "error": "Invalid JSON from lookout"}
        
        # Map lookout status to check status
        lookout_status = report.get("status", "UNKNOWN")
        if lookout_status == "FAIL":
            check_status = "FAIL"  # CRITICAL alerts (FROZEN scripts compromised)
        elif lookout_status == "WARN":
            check_status = "WARN"  # STABLE drift or unauthorized scripts
        elif lookout_status == "PASS":
            check_status = "PASS"
        else:
            check_status = "FAIL"
        
        summary = report.get("summary", {})
        return {
            "status": check_status,
            "frozen_verified": summary.get("frozen_scripts_verified", 0),
            "stable_verified": summary.get("stable_scripts_verified", 0),
            "unauthorized": summary.get("unauthorized_scripts", 0),
            "critical_alerts": summary.get("critical_alerts", 0),
            "warn_alerts": summary.get("warn_alerts", 0),
            "reason": report.get("reason", "Unknown")
        }
    except Exception as e:
        return {"status": "FAIL", "error": repr(e)}

def main() -> int:
    root = Path.cwd().resolve()
    ts = utc_ts()

    bundle_dir = root / "evidence" / "bundles" / f"S_{ts}_COURT_SWEEP"
    bundle_dir.mkdir(parents=True, exist_ok=True)

    report = {
        "type": "court_sweep",
        "ts_utc": ts,
        "mode": "OBSERVE",
        "bundle_version": "V2",
        "checks": {
            "db_counts": audit_db_counts(root),
            "state_history_witness": audit_state_history_witness(root),
            "evidence_index": audit_evidence_index(root),
            "bundle_uniformity": audit_bundle_uniformity(root, ts),
            "encoding_reports_present": audit_encoding_reports_present(root),
            "receipt_validation": audit_receipt_validation(root),
            "orphan_chunks": audit_orphan_chunks(root),
            "bundle_layout": audit_bundle_layout(root, ts),
            "state_history_format": audit_state_history_format(root),
            "script_state_lookout": audit_script_state_lookout(root),
        }
    }

    # overall verdict logic
    statuses = [c.get("status") for c in report["checks"].values()]
    all_pass = all(s == "PASS" for s in statuses)
    
    # Identify failures and warnings
    failures = [k for k, v in report["checks"].items() if v.get("status") == "FAIL"]
    warnings = [k for k, v in report["checks"].items() if v.get("status") == "WARN"]
    
    if all_pass:
        verdict = "PASS"
        reason = "All checks passed"
    else:
        # Construct detailed NO-GO reason
        if failures:
            verdict = "NO-GO"
            reason = f"Failures: {', '.join(failures)}"
            if warnings:
                reason += f" | Warnings: {', '.join(warnings)}"
        elif warnings:
            verdict = "PASS (WARN)" # Strictly speaking, warnings don't block, but let's be explicit
            reason = f"Warnings: {', '.join(warnings)}"
        else:
            verdict = "NO-GO" # Fallback
            reason = "Unknown failure"

    report["verdict"] = verdict
    report["verdict_reason"] = reason

    (bundle_dir / "INDEX.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    md = []
    md.append(f"# Court Sweep Report")
    md.append(f"- ts_utc: {ts}")
    md.append(f"- verdict: **{verdict}**")
    md.append(f"- reason: {reason}")
    md.append("")
    
    for name, c in report["checks"].items():
        status_icon = "[PASS]" if c.get('status') == 'PASS' else "[WARN]" if c.get('status') == 'WARN' else "[FAIL]"
        md.append(f"## {status_icon} {name}")
        md.append(f"- status: **{c.get('status')}**")
        if "error" in c:
            md.append(f"- error: `{c['error']}`")
        if "reason" in c:
            md.append(f"- reason: `{c['reason']}`")
            
        md.append(f"- details: `{json.dumps(c, ensure_ascii=False)[:400]}`")
        md.append("")
        
    (bundle_dir / "REPORT.md").write_text("\n".join(md), encoding="utf-8")

    print(f"[OK] Court sweep bundle: {bundle_dir}")
    print(f"[VERDICT] {verdict}")
    print(f"[REASON]  {reason}")
    for f in failures:
        print(f"  [FAIL] {f}")
    for w in warnings:
        print(f"  [WARN] {w}")
        
    return 0 if verdict.startswith("PASS") else 2

if __name__ == "__main__":
    raise SystemExit(main())
