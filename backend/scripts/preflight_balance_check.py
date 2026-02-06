#!/usr/bin/env python3
"""
Pre-Flight Balance Check

Purpose: Verify system balance before progression - ensures constitution integrity,
import stability, database coherence, and receipt validation.

Returns:
- Exit code 0 (GO) - All checks pass
- Exit code 1 (NO-GO) - Issues found

Sections:
[A] Constitution + Drift Tripwires
[B] Import Stability  
[C] Database Coherence
[D] Receipt Schema Compliance
[E] Balanced Level Summary

Author: Solob Wrapper Guardian System
"""

import sqlite3
import sys
import json
import subprocess
from pathlib import Path
from typing import List, Tuple, Dict

# Ensure repo root is in path
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def print_header(text: str):
    """Print section header with ASCII formatting"""
    print()
    print("=" * 70)
    print(text)
    print("=" * 70)
    print()


def print_section(letter: str, title: str):
    """Print subsection header"""
    print(f"[{letter}] {title}")
    print("-" * 70)


def check_constitution(repo_root: Path) -> Tuple[bool, List[str]]:
    """
    Check [A] Constitution + Drift Tripwires
    
    Returns: (pass_status, error_messages)
    """
    errors = []
    
    # Check if constitution file exists
    constitution_path = repo_root / "core" / "chain_constitution.py"
    if not constitution_path.exists():
        errors.append("Constitution file missing: core/chain_constitution.py")
        return False, errors
    
    # Try importing constitution
    try:
        from core import chain_constitution
        
        # Verify required exports
        required_exports = [
            'CHAIN_SPEC_VERSION',
            'PAYLOAD_HASH_MODE',
            'compute_payload_hash',
            'compute_receipt_hash',
        ]
        
        missing = [exp for exp in required_exports if not hasattr(chain_constitution, exp)]
        if missing:
            errors.append(f"Missing required exports: {', '.join(missing)}")
    
    except ImportError as e:
        errors.append(f"Cannot import chain_constitution: {e}")
        return False, errors
    
    # Check identity lock (direct aliases)
    try:
        from utils import receipt_chain
        from core.chain_constitution import compute_payload_hash as const_hash
        
        # Verify it's a direct alias, not a wrapper
        if receipt_chain.compute_payload_hash is not const_hash:
            errors.append("Identity lock broken: receipt_chain.compute_payload_hash is not a direct alias")
    except ImportError:
        # receipt_chain might not exist yet, skip this check
        pass
    
    return len(errors) == 0, errors


def check_import_stability(repo_root: Path) -> Tuple[bool, List[str]]:
    """
    Check [B] Import Stability
    
    Returns: (warning_status, warning_messages)
    Note: This generates warnings, not failures
    """
    warnings = []
    
    # Scan for ad-hoc sys.path.insert usage
    script_dirs = ['scripts', 'tools', 'utils', 'core']
    ad_hoc_scripts = []
    
    for dir_name in script_dirs:
        script_dir = repo_root / dir_name
        if not script_dir.exists():
            continue
        
        for py_file in script_dir.rglob("*.py"):
            try:
                content = py_file.read_text(encoding='utf-8')
                for line_num, line in enumerate(content.splitlines(), start=1):
                    if 'sys.path.insert' in line and not line.strip().startswith('#'):
                        ad_hoc_scripts.append(f"{py_file.relative_to(repo_root)}:{line_num}")
            except Exception:
                continue
    
    if ad_hoc_scripts:
        count = len(ad_hoc_scripts)
        warnings.append(f"{count} scripts with ad-hoc sys.path")
        # Show first 3
        for script in ad_hoc_scripts[:3]:
            warnings.append(f"  - {script}")
        if count > 3:
            warnings.append(f"  ... and {count - 3} more")
    
    # Warnings don't fail the check
    return True, warnings


def check_database_coherence(repo_root: Path) -> Tuple[bool, List[str]]:
    """
    Check [C] Database Coherence
    
    Returns: (pass_status, error_messages)
    """
    errors = []
    
    db_path = repo_root / "data" / "memory.db"
    
    # Check if canonical DB exists
    if not db_path.exists():
        errors.append("Canonical database missing: data/memory.db")
        return False, errors
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Count anchors
        cursor.execute("SELECT COUNT(*) FROM anchors")
        anchor_count = cursor.fetchone()[0]
        
        # Count chunks
        cursor.execute("SELECT COUNT(*) FROM chunks")
        chunk_count = cursor.fetchone()[0]
        
        # Check for canon anchors without chunks
        cursor.execute("""
            SELECT COUNT(DISTINCT a.anchor_id)
            FROM anchors a
            LEFT JOIN chunks c ON a.anchor_id = c.anchor_id
            WHERE c.chunk_id IS NULL
        """)
        orphaned_anchors = cursor.fetchone()[0]
        
        if orphaned_anchors > 0:
            errors.append(f"Canon anchors without chunks: {orphaned_anchors} (expected 0)")
        
        # Check for orphaned chunks (chunks without anchors)
        cursor.execute("""
            SELECT COUNT(*)
            FROM chunks c
            LEFT JOIN anchors a ON c.anchor_id = a.anchor_id
            WHERE a.anchor_id IS NULL
        """)
        orphaned_chunks = cursor.fetchone()[0]
        
        if orphaned_chunks > 0:
            errors.append(f"Orphaned chunks: {orphaned_chunks} (not linked to anchors)")
        
        conn.close()
        
        # Check for ghost DB files
        data_dir = repo_root / "data"
        for db_file in data_dir.glob("*.db"):
            if db_file.name != "memory.db":
                # Check if it's in checkpoints or orphans
                if not any(parent.name in ['checkpoints', 'orphans'] for parent in db_file.parents):
                    errors.append(f"Ghost DB file: data/{db_file.name} (should be in orphans/)")
        
        # Store counts for summary
        if not errors:
            return True, [f"{anchor_count} anchors, {chunk_count} chunks, 0 orphans"]
        
    except sqlite3.Error as e:
        errors.append(f"Database error: {e}")
        return False, errors
    
    return len(errors) == 0, errors


def check_receipts(repo_root: Path) -> Tuple[bool, List[str]]:
    """
    Check [D] Receipt Schema Compliance
    
    Returns: (pass_status, messages)
    """
    errors = []
    evidence_dir = repo_root / "evidence"
    
    if not evidence_dir.exists():
        errors.append("Evidence directory missing")
        return False, errors
    
    # Find all receipt JSON files
    receipt_files = list(evidence_dir.rglob("*.json"))
    
    if len(receipt_files) == 0:
        # No receipts is not necessarily an error
        return True, ["0 receipts found (system may be clean-slate)"]
    
    valid_count = 0
    invalid_count = 0
    invalid_details = []
    
    for receipt_file in receipt_files:
        try:
            with open(receipt_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Basic schema validation
            required_fields = ['timestamp', 'type']
            missing = [field for field in required_fields if field not in data]
            
            if missing:
                invalid_count += 1
                rel_path = receipt_file.relative_to(repo_root)
                invalid_details.append(f"{rel_path}: Missing fields: {', '.join(missing)}")
            else:
                valid_count += 1
        
        except json.JSONDecodeError:
            invalid_count += 1
            rel_path = receipt_file.relative_to(repo_root)
            invalid_details.append(f"{rel_path}: Invalid JSON")
        except Exception as e:
            invalid_count += 1
            rel_path = receipt_file.relative_to(repo_root)
            invalid_details.append(f"{rel_path}: {str(e)}")
    
    total = valid_count + invalid_count
    
    if invalid_count > 0:
        errors.append(f"{valid_count}/{total} valid ({invalid_count} failed)")
        # Show first 3 failures
        for detail in invalid_details[:3]:
            errors.append(f"  - {detail}")
        if len(invalid_details) > 3:
            errors.append(f"  ... and {len(invalid_details) - 3} more failures")
        return False, errors
    else:
        return True, [f"{valid_count}/{total} valid"]


def main():
    """Run all pre-flight checks"""
    repo_root = Path(__file__).parent.parent
    
    print_header("PRE-FLIGHT BALANCE CHECK")
    
    # Track overall status
    all_pass = True
    has_warnings = False
    
    # [A] Constitution
    print_section("A", "Constitution + Drift Tripwires")
    const_pass, const_msgs = check_constitution(repo_root)
    
    if const_pass:
        print("[OK] Constitution: All exports present")
        if const_msgs:
            for msg in const_msgs:
                print(f"      {msg}")
    else:
        print("[FAIL] Constitution:")
        for msg in const_msgs:
            print(f"  - {msg}")
        all_pass = False
    print()
    
    # [B] Import Stability
    print_section("B", "Import Stability")
    import_pass, import_msgs = check_import_stability(repo_root)
    
    if import_msgs:
        print("[WARN] Imports:", import_msgs[0] if import_msgs else "")
        for msg in import_msgs[1:]:
            print(msg)
        has_warnings = True
    else:
        print("[OK] Imports: No ad-hoc sys.path usage detected")
    print()
    
    # [C] Database
    print_section("C", "Database Coherence")
    db_pass, db_msgs = check_database_coherence(repo_root)
    
    if db_pass:
        print("[OK] Database:", db_msgs[0] if db_msgs else "Coherent")
    else:
        print("[FAIL] Database:")
        for msg in db_msgs:
            print(f"  - {msg}")
        all_pass = False
    print()
    
    # [D] Receipts
    print_section("D", "Receipt Schema Compliance")
    receipt_pass, receipt_msgs = check_receipts(repo_root)
    
    if receipt_pass:
        print("[OK] Receipts:", receipt_msgs[0] if receipt_msgs else "Valid")
    else:
        print("[FAIL] Receipts:")
        for msg in receipt_msgs:
            print(msg if msg.startswith("  ") else f"  - {msg}")
        all_pass = False
    print()
    
    # [E] Summary
    print_header("DECISION")
    
    if all_pass:
        if has_warnings:
            print("GO - System balanced (warnings present)")
        else:
            print("GO - System balanced")
        print("=" * 70)
        return 0
    else:
        print("NO-GO - Fix issues before proceeding")
        print("=" * 70)
        return 1


if __name__ == "__main__":
    sys.exit(main())
