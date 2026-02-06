#!/usr/bin/env python3
"""
Registry Ingestion Module

Handles anchor registration from JSON registry files.
Based on register_anchors_from_registry.py logic.
"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

from modules.base_module import BaseIngestionModule, IngestionResult, register_module


def now_utc_iso_z() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class RegistryIngestionModule(BaseIngestionModule):
    """Anchor registration from JSON registry"""
    
    def validate(self) -> bool:
        """Validate prerequisites"""
        source_path = self.get_source_path()
        if not source_path.exists():
            self.errors.append(f"Registry file not found: {source_path}")
            return False
        
        try:
            data = json.loads(source_path.read_text(encoding="utf-8"))
            if not isinstance(data, list):
                self.errors.append("Registry must be a JSON array of anchor definitions")
                return False
        except json.JSONDecodeError as e:
            self.errors.append(f"Invalid JSON: {e}")
            return False
        
        return True
    
    def execute(self, dry_run: bool = False) -> IngestionResult:
        """Execute anchor registration"""
        # Get counts before
        anchors_before = self.conn.execute("SELECT COUNT(*) FROM anchors").fetchone()[0]
        
        source_path = self.get_source_path()
        registry = json.loads(source_path.read_text(encoding="utf-8"))
        
        inserted = 0
        skipped = 0
        errors = []
        
        for entry in registry:
            if not isinstance(entry, dict):
                errors.append(f"Invalid entry: not a dict")
                continue
            
            anchor_id = entry.get("anchor_id", "")
            if not anchor_id:
                errors.append("Entry missing anchor_id")
                continue
            
            # Check if already exists
            exists = self.conn.execute(
                "SELECT 1 FROM anchors WHERE anchor_id = ? LIMIT 1",
                (anchor_id,)
            ).fetchone()
            
            if exists:
                skipped += 1
                self.warnings.append(f"Anchor already exists: {anchor_id}")
                continue
            
            # Validate source file exists if path provided
            source_file = entry.get("source_path", "")
            if source_file:
                full_path = self.base_dir / source_file
                if not full_path.exists():
                    self.enforce_strict_rule("missing_source_file", f"Source not found: {source_file}")
                    continue
            
            if not dry_run:
                try:
                    self.conn.execute(
                        """
                        INSERT INTO anchors (
                            anchor_id, anchor_type, title, source_path,
                            source_format, status, provenance,
                            import_session_id, created_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
                        """,
                        (
                            anchor_id,
                            entry.get("anchor_type", "document"),
                            entry.get("title", anchor_id),
                            source_file,
                            entry.get("source_format", "unknown"),
                            entry.get("status", "active"),
                            entry.get("provenance", "ritual_registry"),
                            self.session_id,
                            now_utc_iso_z(),
                        ),
                    )
                    inserted += 1
                except sqlite3.IntegrityError as e:
                    self.enforce_strict_rule("anchor_collision", f"Anchor ID collision: {anchor_id}")
            else:
                inserted += 1
        
        if not dry_run:
            self.conn.commit()
        
        anchors_after = self.conn.execute("SELECT COUNT(*) FROM anchors").fetchone()[0]
        delta = anchors_after - anchors_before
        
        return IngestionResult(
            success=len(errors) == 0,
            chunks_inserted=inserted,  # Using chunks_inserted for anchors here
            chunks_before=anchors_before,
            chunks_after=anchors_after if not dry_run else anchors_before,
            delta=delta if not dry_run else 0,
            errors=errors,
            warnings=self.warnings,
            metadata={
                "total_entries": len(registry),
                "anchors_inserted": inserted,
                "anchors_skipped": skipped,
                "source_type": "registry",
            }
        )


register_module("registry", RegistryIngestionModule)
