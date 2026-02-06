#!/usr/bin/env python3
"""
Script State Lookout - Proactive Governance Monitoring

Reality 6 (The Guardian): Continuous monitoring of script alignment with governance registry.
Detects drift, unauthorized modifications, and compliance violations.

Purpose:
- Verify FROZEN scripts remain unchanged (SHA256 verification)
- Verify STABLE scripts remain unchanged
- Detect unauthorized scripts not in registry
- Alert on compliance violations with severity levels

Usage:
    python tools/script_state_lookout.py [--json]

Exit Codes:
    0 = PASS (all checks passed)
    1 = WARN (warnings present)
    2 = FAIL (critical alerts)
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any

BASE_DIR = Path(__file__).resolve().parent.parent
REGISTRY_PATH = BASE_DIR / "docs" / "SCRIPT_STATE_REGISTRY.json"

# Directories to scan for scripts
SCRIPT_DIRS = [
    BASE_DIR / "scripts",
    BASE_DIR / "tools",
    BASE_DIR / "modules",
    BASE_DIR / "core"
]


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def calculate_sha256(filepath: Path) -> str:
    """Calculate SHA256 hash of a file"""
    sha256_hash = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except Exception as e:
        return f"ERROR: {str(e)}"


def load_registry() -> Dict[str, Any]:
    """Load script state registry and convert to internal format"""
    if not REGISTRY_PATH.exists():
        return {"scripts": []}
    
    try:
        raw_registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
        
        # Support existing registry format with "files" dict
        if "files" in raw_registry:
            scripts = []
            for rel_path, info in raw_registry["files"].items():
                scripts.append({
                    "path": rel_path,
                    "state": info.get("state"),
                    "sha256": info.get("sha256"),
                    "reason": info.get("reason")
                })
            return {"scripts": scripts}
        
        # Support new array format
        return raw_registry
        
    except Exception as e:
        print(f"Error loading registry: {e}", file=sys.stderr)
        return {"scripts": []}


def find_all_scripts() -> List[Path]:
    """Find all Python scripts in monitored directories"""
    scripts = []
    for dir_path in SCRIPT_DIRS:
        if not dir_path.exists():
            continue
        for script_path in dir_path.rglob("*.py"):
            if script_path.is_file():
                scripts.append(script_path)
    return scripts


def verify_frozen_scripts(registry: Dict[str, Any]) -> Dict[str, Any]:
    """Verify FROZEN scripts remain unchanged (CRITICAL if modified)"""
    frozen_scripts = [s for s in registry.get("scripts", []) if s.get("state") == "FROZEN"]
    
    verified = 0
    alerts = []
    
    for script_info in frozen_scripts:
        rel_path = script_info.get("path")
        expected_sha = script_info.get("sha256")
        
        if not rel_path or not expected_sha:
            continue
        
        script_path = BASE_DIR / rel_path
        
        if not script_path.exists():
            alerts.append({
                "severity": "CRITICAL",
                "script": rel_path,
                "issue": "FROZEN script missing from filesystem",
                "remediation": f"Restore {rel_path} from backup immediately"
            })
            continue
        
        actual_sha = calculate_sha256(script_path)
        
        if actual_sha.startswith("ERROR"):
            alerts.append({
                "severity": "CRITICAL",
                "script": rel_path,
                "issue": f"Cannot read FROZEN script: {actual_sha}",
                "remediation": "Check file permissions"
            })
            continue
        
        if actual_sha != expected_sha:
            alerts.append({
                "severity": "CRITICAL",
                "script": rel_path,
                "issue": "FROZEN script modified",
                "expected_sha": expected_sha,
                "actual_sha": actual_sha,
                "remediation": f"IMMEDIATE: Restore {rel_path} from backup and investigate breach"
            })
        else:
            verified += 1
    
    return {
        "frozen_count": len(frozen_scripts),
        "verified": verified,
        "alerts": alerts
    }


def verify_stable_scripts(registry: Dict[str, Any]) -> Dict[str, Any]:
    """Verify STABLE scripts remain unchanged (WARN if modified)"""
    stable_scripts = [s for s in registry.get("scripts", []) if s.get("state") == "STABLE"]
    
    verified = 0
    alerts = []
    
    for script_info in stable_scripts:
        rel_path = script_info.get("path")
        expected_sha = script_info.get("sha256")
        
        if not rel_path:
            continue
        
        # STABLE scripts may not have SHA256 tracked
        if not expected_sha:
            continue
        
        script_path = BASE_DIR / rel_path
        
        if not script_path.exists():
            alerts.append({
                "severity": "WARN",
                "script": rel_path,
                "issue": "STABLE script missing from filesystem",
                "remediation": f"Verify intentional deletion or restore {rel_path}"
            })
            continue
        
        actual_sha = calculate_sha256(script_path)
        
        if actual_sha.startswith("ERROR"):
            alerts.append({
                "severity": "WARN",
                "script": rel_path,
                "issue": f"Cannot read STABLE script: {actual_sha}",
                "remediation": "Check file permissions"
            })
            continue
        
        if actual_sha != expected_sha:
            alerts.append({
                "severity": "WARN",
                "script": rel_path,
                "issue": "STABLE script modified",
                "expected_sha": expected_sha,
                "actual_sha": actual_sha,
                "remediation": f"If intentional, update registry SHA256 for {rel_path}. If unintentional, restore from backup."
            })
        else:
            verified += 1
    
    return {
        "stable_count": len(stable_scripts),
        "verified": verified,
        "alerts": alerts
    }


def detect_unauthorized_scripts(registry: Dict[str, Any]) -> Dict[str, Any]:
    """Find scripts not in registry (WARN)"""
    # Build set of registered script paths
    registered_paths = set()
    for script_info in registry.get("scripts", []):
        rel_path = script_info.get("path")
        if rel_path:
            registered_paths.add(str(BASE_DIR / rel_path))
    
    # Find all scripts on filesystem
    all_scripts = find_all_scripts()
    
    # Identify unauthorized scripts
    unauthorized = []
    for script_path in all_scripts:
        if str(script_path) not in registered_paths:
            unauthorized.append({
                "severity": "WARN",
                "script": str(script_path.relative_to(BASE_DIR)),
                "issue": "Script not in governance registry",
                "remediation": "Review script purpose and add to registry with appropriate state (FROZEN/STABLE/OBSERVE/HOLSTERED)"
            })
    
    return {
        "unauthorized_count": len(unauthorized),
        "alerts": unauthorized
    }


def check_registry_alignment(registry: Dict[str, Any]) -> Dict[str, Any]:
    """Verify all registry entries point to existing files"""
    alerts = []
    
    for script_info in registry.get("scripts", []):
        rel_path = script_info.get("path")
        if not rel_path:
            continue
        
        script_path = BASE_DIR / rel_path
        
        if not script_path.exists():
            state = script_info.get("state", "UNKNOWN")
            severity = "CRITICAL" if state == "FROZEN" else "WARN"
            
            alerts.append({
                "severity": severity,
                "script": rel_path,
                "issue": f"{state} script in registry but missing from filesystem",
                "remediation": f"Restore {rel_path} or remove from registry"
            })
    
    return {
        "alignment_alerts": alerts
    }


def generate_report(frozen_result: Dict, stable_result: Dict, unauthorized_result: Dict, alignment_result: Dict) -> Dict[str, Any]:
    """Generate comprehensive lookout report"""
    # Collect all alerts
    all_alerts = []
    all_alerts.extend(frozen_result.get("alerts", []))
    all_alerts.extend(stable_result.get("alerts", []))
    all_alerts.extend(unauthorized_result.get("alerts", []))
    all_alerts.extend(alignment_result.get("alignment_alerts", []))
    
    # Count by severity
    critical_count = len([a for a in all_alerts if a.get("severity") == "CRITICAL"])
    warn_count = len([a for a in all_alerts if a.get("severity") == "WARN"])
    
    # Determine overall status
    if critical_count > 0:
        status = "FAIL"
        reason = f"{critical_count} CRITICAL alert(s) - FROZEN scripts compromised"
    elif warn_count > 0:
        status = "WARN"
        reason = f"{warn_count} warning(s) - Script drift or unauthorized scripts detected"
    else:
        status = "PASS"
        reason = "All scripts aligned with governance registry"
    
    return {
        "ts_utc": utc_now(),
        "status": status,
        "reason": reason,
        "summary": {
            "frozen_scripts_checked": frozen_result.get("frozen_count", 0),
            "frozen_scripts_verified": frozen_result.get("verified", 0),
            "stable_scripts_checked": stable_result.get("stable_count", 0),
            "stable_scripts_verified": stable_result.get("verified", 0),
            "unauthorized_scripts": unauthorized_result.get("unauthorized_count", 0),
            "critical_alerts": critical_count,
            "warn_alerts": warn_count
        },
        "alerts": all_alerts
    }


def print_human_readable(report: Dict[str, Any]):
    """Print human-readable report"""
    print(f"[LOOKOUT] Script State Lookout - {report['ts_utc']}")
    print()
    
    summary = report.get("summary", {})
    
    # FROZEN scripts
    frozen_checked = summary.get("frozen_scripts_checked", 0)
    frozen_verified = summary.get("frozen_scripts_verified", 0)
    if frozen_verified == frozen_checked:
        print(f"[OK] FROZEN scripts: {frozen_verified}/{frozen_checked} verified")
    else:
        print(f"[CRITICAL] FROZEN scripts: {frozen_verified}/{frozen_checked} verified ({frozen_checked - frozen_verified} COMPROMISED)")
    
    # STABLE scripts
    stable_checked = summary.get("stable_scripts_checked", 0)
    stable_verified = summary.get("stable_scripts_verified", 0)
    if stable_verified == stable_checked:
        print(f"[OK] STABLE scripts: {stable_verified}/{stable_checked} verified")
    else:
        print(f"[WARN] STABLE scripts: {stable_verified}/{stable_checked} verified ({stable_checked - stable_verified} modified)")
    
    # Unauthorized scripts
    unauthorized = summary.get("unauthorized_scripts", 0)
    if unauthorized == 0:
        print(f"[OK] Unauthorized scripts: 0")
    else:
        print(f"[WARN] Unauthorized scripts: {unauthorized} found")
    
    # Alerts
    alerts = report.get("alerts", [])
    if alerts:
        print()
        print("=== ALERTS ===")
        for alert in alerts:
            severity = alert.get("severity", "UNKNOWN")
            script = alert.get("script", "unknown")
            issue = alert.get("issue", "unknown")
            
            print(f"\n[{severity}] {script}")
            print(f"  Issue: {issue}")
            
            if "expected_sha" in alert:
                print(f"  Expected SHA256: {alert['expected_sha']}")
                print(f"  Actual SHA256:   {alert['actual_sha']}")
            
            if "remediation" in alert:
                print(f"  Remediation: {alert['remediation']}")
    
    print()
    print(f"[VERDICT] {report['status']}")
    print(f"[REASON]  {report['reason']}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Script State Lookout - Governance Monitoring")
    parser.add_argument("--json", action="store_true", help="Output JSON format")
    args = parser.parse_args()
    
    # Load registry
    registry = load_registry()
    
    # Run checks
    frozen_result = verify_frozen_scripts(registry)
    stable_result = verify_stable_scripts(registry)
    unauthorized_result = detect_unauthorized_scripts(registry)
    alignment_result = check_registry_alignment(registry)
    
    # Generate report
    report = generate_report(frozen_result, stable_result, unauthorized_result, alignment_result)
    
    # Output
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print_human_readable(report)
    
    # Exit code
    status = report.get("status")
    if status == "FAIL":
        return 2    # CRITICAL alerts
    elif status == "WARN":
        return 1    # Warnings
    else:
        return 0    # PASS


if __name__ == "__main__":
    raise SystemExit(main())
