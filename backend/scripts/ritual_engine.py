#!/usr/bin/env python3
"""
Ritual Engine - Config-Driven Ingestion Framework

Reality 5 (The Product Builder): Transform one-off scripts into reusable ritual patterns.

Purpose:
- Execute ingestion rituals from JSON config files
- Automatic V2 receipt generation
- Database state tracking (before/after/delta)
- Strict failure rules enforcement
- Dry-run mode support

Usage:
    python scripts/ritual_engine.py --config config/rituals/my_ritual.json [--dry-run]

Exit Codes:
    0 = Success
    1 = User error (bad config, missing files)
    2 = Strict rule violation (data integrity)
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

# Add modules to path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

# Import modules package to trigger registration
import modules
from modules.base_module import BaseIngestionModule, get_module
from utils.sid import get_active_sid


def now_utc_iso_z() -> str:
    """Get current UTC timestamp in ISO format with Z suffix"""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class RitualEngine:
    """Executes ingestion rituals from config"""
    
    def __init__(self, config_path: Path):
        """
        Initialize ritual engine
        
        Args:
            config_path: Path to ritual config JSON file
        """
        self.config_path = config_path
        self.config: Dict[str, Any] = {}
        self.session_id: str = ""
        self.db_path = BASE_DIR / "data" / "memory.db"
        self.conn: Optional[sqlite3.Connection] = None
        
    def load_config(self) -> bool:
        """
        Load and validate ritual config
        
        Returns:
            True if config is valid, False otherwise
        """
        if not self.config_path.exists():
            print(f"ERROR: Config file not found: {self.config_path}", file=sys.stderr)
            return False
        
        try:
            self.config = json.loads(self.config_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            print(f"ERROR: Invalid JSON in config: {e}", file=sys.stderr)
            return False
        
        # Validate required fields
        required = ["ritual_version", "ritual_name", "intent", "anchor_id", "source", "steps", "strict_rules"]
        missing = [f for f in required if f not in self.config]
        
        if missing:
            print(f"ERROR: Missing required config fields: {missing}", file=sys.stderr)
            return False
        
        # Validate ritual version
        if self.config["ritual_version"] not in ["1.0"]:
            print(f"ERROR: Unsupported ritual version: {self.config['ritual_version']}", file=sys.stderr)
            return False
        
        return True
    
    def get_session_id(self) -> str:
        """Get active session ID"""
        try:
            return get_active_sid()
        except Exception as e:
            print(f"ERROR: Failed to get active SID: {e}", file=sys.stderr)
            sys.exit(1)
    
    def connect_db(self) -> bool:
        """Connect to database"""
        if not self.db_path.exists():
            print(f"ERROR: Database not found: {self.db_path}", file=sys.stderr)
            return False
        
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.execute("PRAGMA foreign_keys = ON;")
            return True
        except Exception as e:
            print(f"ERROR: Failed to connect to database: {e}", file=sys.stderr)
            return False
    
    def determine_module(self) -> Optional[str]:
        """
        Determine which module to use based on config
        
        Returns:
            Module name or None if cannot determine
        """
        # For now, we'll use source type + format as hints
        source = self.config.get("source", {})
        source_type = source.get("type", "")
        source_format = source.get("format", "")
        
        # Simple heuristics (will expand as we add modules)
        if source_format and "lexicon" in source_format.lower():
            return "lexicon"
        elif source_type == "pdf":
            return "pdf"
        elif source_type == "json":
            return "json"
        
        # Default to generic JSON module
        return "json"
    
    def execute(self, dry_run: bool = False) -> int:
        """
        Execute the ritual
        
        Args:
            dry_run: If True, validate but don't insert into database
        
        Returns:
            Exit code (0=success, 1=user error, 2=strict rule violation)
        """
        print(f"[Ritual Engine] Starting ritual: {self.config.get('ritual_name', 'unknown')}")
        print(f"[Ritual Engine] Intent: {self.config.get('intent', 'unknown')}")
        print(f"[Ritual Engine] Session ID: {self.session_id}")
        print(f"[Ritual Engine] Dry-run: {dry_run}")
        print()
        
        # Determine module
        module_name = self.determine_module()
        if not module_name:
            print("ERROR: Could not determine ingestion module from config", file=sys.stderr)
            return 1
        
        print(f"[Ritual Engine] Module: {module_name}")
        
        # Get module class
        module_class = get_module(module_name)
        if not module_class:
            print(f"ERROR: Module not found: {module_name}", file=sys.stderr)
            print(f"Available modules: {list(get_module.__globals__.get('MODULE_REGISTRY', {}).keys())}", file=sys.stderr)
            return 1
        
        # Instantiate module
        module = module_class(
            config=self.config,
            conn=self.conn,
            session_id=self.session_id,
            base_dir=BASE_DIR
        )
        
        # Validate
        print("[Ritual Engine] Validating prerequisites...")
        if not module.validate():
            print("ERROR: Validation failed:", file=sys.stderr)
            for error in module.errors:
                print(f"  - {error}", file=sys.stderr)
            return 1
        
        if module.warnings:
            print("WARNINGS:")
            for warning in module.warnings:
                print(f"  - {warning}")
        
        print("[Ritual Engine] Validation: PASS")
        print()
        
        # Execute
        print(f"[Ritual Engine] Executing ingestion{'(DRY-RUN)' if dry_run else ''}...")
        try:
            result = module.execute(dry_run=dry_run)
        except RuntimeError as e:
            if "STOP:" in str(e):
                print(f"STRICT RULE VIOLATION: {e}", file=sys.stderr)
                return 2
            raise
        except Exception as e:
            print(f"ERROR: Execution failed: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc()
            return 1
        
        # Check result
        if not result.success:
            print("ERROR: Ingestion failed:", file=sys.stderr)
            for error in result.errors:
                print(f"  - {error}", file=sys.stderr)
            return 1
        
        # Report
        print()
        print("=" * 60)
        print("INGESTION COMPLETE")
        print("=" * 60)
        print(f"Chunks inserted: {result.chunks_inserted}")
        print(f"Database delta: {result.delta} (before={result.chunks_before}, after={result.chunks_after})")
        
        if result.warnings:
            print(f"Warnings: {len(result.warnings)}")
            for warning in result.warnings[:5]:  # Show first 5
                print(f"  - {warning}")
        
        if not dry_run:
            # Generate receipt
            receipt_path = self.generate_receipt(result)
            if receipt_path:
                print(f"Receipt: {receipt_path.relative_to(BASE_DIR)}")
        else:
            print("[DRY-RUN] No receipt generated")
        
        print()
        return 0
    
    def generate_receipt(self, result) -> Optional[Path]:
        """
        Generate V2 receipt for this ritual execution
        
        Args:
            result: IngestionResult from module execution
        
        Returns:
            Path to generated receipt or None if failed
        """
        # Construct receipt
        receipt = {
            "receipt_version": "V2",
            "intent": self.config.get("intent", "RITUAL_EXECUTION"),
            "generated_utc": now_utc_iso_z(),
            "import_session_id": self.session_id,
            "anchor_id": self.config.get("anchor_id", ""),
            "ritual": {
                "name": self.config.get("ritual_name", ""),
                "version": self.config.get("ritual_version", ""),
                "config_path": str(self.config_path.relative_to(BASE_DIR)),
            },
            "source_path": self.config.get("source", {}).get("path", ""),
            "db": {
                "path": "data/memory.db",
                "chunks_before": result.chunks_before,
                "chunks_after": result.chunks_after,
                "delta": result.delta,
            },
            "strict_rules": self.config.get("strict_rules", {}),
            "result": {
                "success": result.success,
                "chunks_inserted": result.chunks_inserted,
                "warnings_count": len(result.warnings),
                "metadata": result.metadata,
            },
        }
        
        # Determine receipt path
        receipt_dir = BASE_DIR / "evidence" / self.session_id / "RECEIPTS"
        receipt_dir.mkdir(parents=True, exist_ok=True)
        
        ritual_name = self.config.get("ritual_name", "unknown")
        receipt_path = receipt_dir / f"RECEIPT_RITUAL_{ritual_name}.json"
        
        # Write receipt
        try:
            receipt_path.write_text(
                json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                encoding="utf-8"
            )
            return receipt_path
        except Exception as e:
            print(f"WARNING: Failed to write receipt: {e}", file=sys.stderr)
            return None


def main() -> int:
    """Main entry point"""
    ap = argparse.ArgumentParser(description="Ritual Engine - Config-Driven Ingestion")
    ap.add_argument("--config", required=True, help="Path to ritual config JSON")
    ap.add_argument("--dry-run", action="store_true", help="Validate without executing")
    args = ap.parse_args()
    
    config_path = Path(args.config)
    if not config_path.is_absolute():
        config_path = (BASE_DIR / config_path).resolve()
    
    # Initialize engine
    engine = RitualEngine(config_path)
    
    # Load config
    if not engine.load_config():
        return 1
    
    # Get session ID
    engine.session_id = engine.get_session_id()
    
    # Connect to database
    if not engine.connect_db():
        return 1
    
    # Execute
    try:
        exit_code = engine.execute(dry_run=args.dry_run)
        return exit_code
    finally:
        if engine.conn:
            engine.conn.close()


if __name__ == "__main__":
    sys.exit(main())
