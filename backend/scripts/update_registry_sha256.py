#!/usr/bin/env python3
"""
Calculate and add SHA256 hashes for STABLE scripts in registry.
"""

import json
import hashlib
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
REGISTRY_PATH = BASE_DIR / "docs" / "SCRIPT_STATE_REGISTRY.json"

def calculate_sha256(filepath: Path) -> str:
    """Calculate SHA256 hash of a file"""
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def main():
    # Load registry
    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    
    updates = []
    
    # Find STABLE scripts without SHA256
    for rel_path, info in registry["files"].items():
        if not rel_path.endswith(".py"):
            continue
        
        if info.get("state") == "STABLE":
            script_path = BASE_DIR / rel_path
            
            if script_path.exists():
                sha256 = calculate_sha256(script_path)
                if info.get("sha256") != sha256:
                    info["sha256"] = sha256
                    updates.append(rel_path)
                    print(f"[OK] Updated {rel_path}")
                    print(f"  SHA256: {sha256}")
            else:
                print(f"[ERROR] {rel_path} - FILE NOT FOUND")
    
    # Save updated registry
    if updates:
        REGISTRY_PATH.write_text(
            json.dumps(registry, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8"
        )
        print(f"\n[OK] Updated {len(updates)} STABLE scripts with SHA256 hashes")
    else:
        print("\nNo STABLE scripts needed SHA256 updates")
    
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
