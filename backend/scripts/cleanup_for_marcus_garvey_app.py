#!/usr/bin/env python3
"""
Codebase Cleanup for Marcus Garvey App

Removes irrelevant files while preserving all scripts and core functionality.
This is a FORK of the original ARK - no backup needed.
"""

import shutil
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

def remove_directory(dir_path: Path, name: str):
    """Remove directory if it exists."""
    if dir_path.exists():
        print(f"[DELETE] {name}: {dir_path.relative_to(BASE_DIR)}")
        shutil.rmtree(dir_path)
        print(f"  ✓ Removed")
    else:
        print(f"[SKIP] {name} not found: {dir_path.relative_to(BASE_DIR)}")

def remove_file(file_path: Path, name: str):
    """Remove file if it exists."""
    if file_path.exists():
        print(f"[DELETE] {name}: {file_path.relative_to(BASE_DIR)}")
        file_path.unlink()
        print(f"  ✓ Removed")

def cleanup_temp_files():
    """Remove temporary audit/output files from root."""
    patterns = [
        "*_output.txt", "*_audit.txt", "*_results.txt", 
        "*_sweep.txt", "*_log.txt", "*.ps1"
    ]
    
    for pattern in patterns:
        for file_path in BASE_DIR.glob(pattern):
            if file_path.is_file():
                remove_file(file_path, f"Temp file ({pattern})")

def main():
    print("=" * 60)
    print("Marcus Garvey App - Codebase Cleanup")
    print("=" * 60)
    print()
    
    # 1. Remove frontend
    frontend_dir = BASE_DIR / "frontend"
    remove_directory(frontend_dir, "Frontend")
    
    # 2. Remove lexicon anchors
    lexicon_dir = BASE_DIR / "anchors" / "canon" / "definitions"
    remove_directory(lexicon_dir, "Lexicon anchors")
    
    # 3. Remove old evidence bundles
    evidence_dir = BASE_DIR / "evidence"
    remove_directory(evidence_dir, "Old evidence bundles")
    
    # 4. Remove logs
    logs_dir = BASE_DIR / "logs"
    remove_directory(logs_dir, "Logs")
    
    # 5. Remove temp files
    print()
    print("[CLEANUP] Temporary files...")
    cleanup_temp_files()
    
    # 6. Recreate evidence directory (empty)
    evidence_dir.mkdir(exist_ok=True)
    print()
    print(f"[CREATE] Empty evidence/ directory")
    
    print()
    print("=" * 60)
    print("Cleanup Complete")
    print("=" * 60)
    print()
    print("PRESERVED:")
    print("  ✓ scripts/ (ALL 58 scripts)")
    print("  ✓ tools/, modules/, core/, utils/")
    print("  ✓ api/, ingestion/, retrieval/, runs/")
    print("  ✓ docs/, config/, archive/")
    print("  ✓ anchors/canon/Marcus BOX/")
    print("  ✓ anchors/canon/book_of_solobility/")
    print()
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
