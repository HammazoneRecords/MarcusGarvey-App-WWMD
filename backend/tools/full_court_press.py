#!/usr/bin/env python3
"""
Full Court Press - Complete System Audit (including Merkle Chain)

Reality 6 (The Guardian): Production-grade audit with chain verification.

This is the MAIN AUDIT TOOL for production. It includes:
- Chain integrity verification (FIRST/CRITICAL check)
- All 9 court sweep checks

If chain verification fails, audit stops immediately (NO-GO).

Usage:
    python tools/full_court_press.py

Exit Codes:
    0 = PASS (all checks including chain)
    2 = NO-GO (chain broken or other critical failure)
"""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
BUNDLES_DIR = BASE_DIR / "evidence" / "bundles"


def utc_ts() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def audit_evidence_vault(root: Path) -> dict:
    """
    Evidence vault verification (LAYER 1 - PRIMARY CHECK).
    
    Verifies actual evidence files match vault hashes.
    If this fails, the entire audit is NO-GO.
    """
    try:
        result = subprocess.run(
            [sys.executable, str(root / "tools" / "verify_evidence_vault.py")],
            capture_output=True,
            text=True,
            cwd=root,
            encoding="utf-8",
            errors="replace"
        )
        
        if result.returncode == 0:
            return {
                "status": "PASS",
                "message": "Evidence vault intact",
                "stdout": result.stdout.strip() if result.stdout else "",
                "returncode": result.returncode
            }
        else:
            return {
                "status": "FAIL",
                "message": "Evidence vault compromised",
                "stdout": result.stdout.strip() if result.stdout else "",
                "stderr": result.stderr.strip() if result.stderr else "",
                "reason": "CRITICAL: Evidence files tampered or missing",
                "returncode": result.returncode
            }
    except Exception as e:
        return {
            "status": "FAIL",
            "error": repr(e),
            "reason": "Vault verification tool failed"
        }


def audit_chain_integrity(root: Path) -> dict:
    """
    Chain integrity verification (LAYER 2 - SECONDARY CHECK).
    
    Constitutional hash verification using FROZEN chain_constitution.py.
    """
    try:
        result = subprocess.run(
            [sys.executable, str(root / "tools" / "verify_chain_integrity.py"), "--chain-id", "ARK_MAIN"],
            capture_output=True,
            text=True,
            cwd=root,
            encoding="utf-8",
            errors="replace"
        )
        
        # Exit code 0 = chain intact, 1 = chain broken
        if result.returncode == 0:
            return {
                "status": "PASS",
                "message": "Chain ARK_MAIN intact",
                "stdout": result.stdout.strip() if result.stdout else "",
                "returncode": result.returncode
            }
        else:
            return {
                "status": "FAIL",
                "message": "Chain ARK_MAIN compromised",
                "stdout": result.stdout.strip() if result.stdout else "",
                "stderr": result.stderr.strip() if result.stderr else "",
                "reason": "CRITICAL: Merkle chain integrity violation",
                "returncode": result.returncode
            }
    except Exception as e:
        return {
            "status": "FAIL",
            "error": repr(e),
            "reason": "Chain verification tool failed"
        }


def run_court_sweep(root: Path) -> dict:
    """Run standard 9-check court sweep"""
    try:
        result = subprocess.run(
            [sys.executable, str(root / "tools" / "court_sweep.py")],
            capture_output=True,
            text=True,
            cwd=root
        )
        
        # Parse court sweep output to get verdict
        verdict = "UNKNOWN"
        for line in result.stdout.splitlines():
            if line.startswith("[VERDICT]"):
                verdict = line.split("[VERDICT]")[1].strip()
                break
        
        return {
            "exit_code": result.returncode,
            "verdict": verdict,
            "output": result.stdout
        }
    except Exception as e:
        return {
            "exit_code": -1,
            "verdict": "ERROR",
            "error": repr(e)
        }


def main() -> int:
    root = BASE_DIR
    ts = utc_ts()
    
    # Create bundle
    bundle_dir = BUNDLES_DIR / f"S_{ts}_FULL_COURT_PRESS"
    bundle_dir.mkdir(parents=True, exist_ok=True)
    
    print("[FULL COURT PRESS] Three-layer defense audit")
    print("[LAYERS] Evidence Vault -> Merkle Chain -> Court Sweep")
    print(f"[BUNDLE] {bundle_dir.relative_to(root)}")
    print()
    
    # LAYER 1: Evidence Vault (PRIMARY - Check actual files match vault hashes)
    print("[LAYER 1/3] Evidence Vault Verification (PRIMARY)...")
    vault_result = audit_evidence_vault(root)
    
    if vault_result["status"] == "FAIL":
        # Vault is compromised - IMMEDIATE NO-GO
        print(f"[FAIL] {vault_result.get('message', 'Vault verification failed')}")
        if "stdout" in vault_result:
            print(vault_result["stdout"])
        
        # Write minimal report
        report = {
            "type": "full_court_press",
            "ts_utc": ts,
            "bundle_version": "V2",
            "verdict": "NO-GO",
            "verdict_reason": "CRITICAL: Evidence vault compromised (Layer 1 failure)",
            "layers": {
                "1_evidence_vault": vault_result,
                "2_chain_integrity": "SKIPPED (vault failed)",
                "3_court_sweep": "SKIPPED (vault failed)"
            }
        }
        
        (bundle_dir / "INDEX.json").write_text(
            json.dumps(report, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8"
        )
        
        md = [
            "# Full Court Press Report",
            f"- ts_utc: {ts}",
            "- verdict: **NO-GO**",
            "- reason: CRITICAL: Evidence vault compromised",
            "",
            "## Layer 1: Evidence Vault (FAILED)",
            f"- status: **{vault_result['status']}**",
            f"- message: {vault_result.get('message', 'Unknown')}",
            "",
            "## Layer 2: Chain Integrity",
            "- SKIPPED (vault failed)",
            "",
            "## Layer 3: Court Sweep",
            "- SKIPPED (vault failed)",
            "",
            "---",
            "",
            "**CRITICAL FAILURE**: Evidence vault compromised. Files tampered or missing.",
            "Investigate vault breach immediately using tools/verify_evidence_vault.py."
        ]
        
        (bundle_dir / "REPORT.md").write_text("\n".join(md) + "\n", encoding="utf-8")
        
        print()
        print("[VERDICT] NO-GO")
        print("[REASON]  CRITICAL: Evidence vault compromised")
        print("[ACTION]  Investigate evidence tampering immediately")
        
        return 2
    
    # Vault passed - continue with chain
    print(f"[PASS] {vault_result.get('message', 'Vault intact')}")
    print()
    
    # LAYER 2: Chain Integrity (SECONDARY - Constitutional hash verification)
    print("[LAYER 2/3] Merkle Chain Verification (SECONDARY)...")
    chain_result = audit_chain_integrity(root)
    
    if chain_result["status"] == "FAIL":
        # Chain broken - NO-GO
        print(f"[FAIL] {chain_result.get('message', 'Chain verification failed')}")
        
        report = {
            "type": "full_court_press",
            "ts_utc": ts,
            "bundle_version": "V2",
            "verdict": "NO-GO",
            "verdict_reason": "CRITICAL: Merkle chain integrity violation (Layer 2 failure)",
            "layers": {
                "1_evidence_vault": vault_result,
                "2_chain_integrity": chain_result,
                "3_court_sweep": "SKIPPED (chain failed)"
            }
        }
        
        (bundle_dir / "INDEX.json").write_text(
            json.dumps(report, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8"
        )
        
        (bundle_dir / "REPORT.md").write_text(
            f"# Full Court Press Report\n\nVault passed, but chain failed.\n\n**Chain Status**: {chain_result.get('message')}\n",
            encoding="utf-8"
        )
        
        print()
        print("[VERDICT] NO-GO")
        print("[REASON]  CRITICAL: Merkle chain broken")
        
        return 2
    
    # Chain passed - continue with court sweep
    print(f"[PASS] {chain_result.get('message', 'Chain intact')}")
    print()
    
    # LAYER 3: Court Sweep (TERTIARY - 9 standard checks)
    print("[LAYER 3/3] Court Sweep (9 checks)...")
    print()
    
    court_sweep_result = run_court_sweep(root)
    
    # Print court sweep output
    print(court_sweep_result.get("output", ""))
    
    # Determine overall verdict
    if court_sweep_result["exit_code"] == 0:
        verdict = "PASS"
        reason = "All 3 layers passed (Vault + Chain + Court Sweep)"
    else:
        verdict = "NO-GO"
        reason = f"Court sweep failed: {court_sweep_result.get('verdict', 'UNKNOWN')}"
    
    # Write comprehensive report
    report = {
        "type": "full_court_press",
        "ts_utc": ts,
        "bundle_version": "V2",
        "verdict": verdict,
        "verdict_reason": reason,
        "layers": {
            "1_evidence_vault": {"status": vault_result["status"], "message": vault_result.get("message")},
            "2_chain_integrity": {"status": chain_result["status"], "message": chain_result.get("message")},
            "3_court_sweep": {
                "verdict": court_sweep_result.get("verdict"),
                "exit_code": court_sweep_result.get("exit_code")
            }
        }
    }
    
    (bundle_dir / "INDEX.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8"
    )
    
    md = [
        "# Full Court Press Report",
        f"- ts_utc: {ts}",
        f"- verdict: **{verdict}**",
        f"- reason: {reason}",
        "",
        "## Layer 1: Evidence Vault",
        f"- status: **{vault_result['status']}**",
        f"- message: {vault_result.get('message', 'Unknown')}",
        "",
        "## Layer 2: Merkle Chain",
        f"- status: **{chain_result['status']}**",
        f"- message: {chain_result.get('message', 'Unknown')}",
        "",
        "## Layer 3: Court Sweep",
        f"- verdict: **{court_sweep_result.get('verdict')}**",
        f"- exit_code: {court_sweep_result.get('exit_code')}",
        "",
        "---",
        "",
        "Three-layer defense complete."
    ]
    
    (bundle_dir / "REPORT.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    
    print()
    print(f"[BUNDLE] {bundle_dir.relative_to(root)}")
    print(f"[VERDICT] {verdict}")
    print(f"[REASON]  {reason}")
    
    return 0 if verdict == "PASS" else 2

if __name__ == "__main__":
    raise SystemExit(main())

