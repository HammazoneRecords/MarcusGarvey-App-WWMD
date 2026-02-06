#!/usr/bin/env python3
"""
Generic JSON Ingestion Module

Handles flexible JSON file ingestion with template-based chunk IDs.
"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

from modules.base_module import BaseIngestionModule, IngestionResult, register_module


def now_utc_iso_z() -> str:
    """Get current UTC timestamp"""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class JSONIngestionModule(BaseIngestionModule):
    """Generic JSON ingestion with template support"""
    
    def validate(self) -> bool:
        """Validate prerequisites"""
        # Check anchor exists
        anchor_id = self.get_anchor_id()
        if not anchor_id:
            self.errors.append("Missing anchor_id in config")
            return False
        
        if not self.check_anchor_exists(anchor_id):
            self.enforce_strict_rule("missing_anchor", f"Anchor not found: {anchor_id}")
            return False
        
        # Check source file exists
        source_path = self.get_source_path()
        if not source_path.exists():
            self.errors.append(f"Source file not found: {source_path}")
            return False
        
        # Try to parse JSON
        try:
            json.loads(source_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            self.errors.append(f"Invalid JSON: {e}")
            return False
        
        return True
    
    def execute(self, dry_run: bool = False) -> IngestionResult:
        """Execute JSON ingestion"""
        # Get database counts before
        counts_before = self.get_db_counts()
        chunks_before = counts_before["chunks"]
        
        # Load JSON
        source_path = self.get_source_path()
        data = json.loads(source_path.read_text(encoding="utf-8"))
        
        # Handle both list and dict formats
        if isinstance(data, list):
            entries = data
        elif isinstance(data, dict) and "entries" in data:
            entries = data["entries"]
        else:
            return IngestionResult(
                success=False,
                chunks_inserted=0,
                chunks_before=chunks_before,
                chunks_after=chunks_before,
                delta=0,
                errors=["JSON must be a list or dict with 'entries' key"],
                warnings=[],
                metadata={}
            )
        
        # Get config
        anchor_id = self.get_anchor_id()
        chunk_id_template = self.get_chunk_id_template()
        locator_template = self.get_locator_template()
        truth_type = self.get_truth_type()
        
        # Insert chunks
        inserted = 0
        errors = []
        
        for idx, entry in enumerate(entries):
            if not isinstance(entry, dict):
                errors.append(f"Entry {idx} is not a dict")
                continue
            
            # Generate chunk ID and locator
            chunk_id = self.interpolate_template(chunk_id_template, entry, idx)
            locator = self.interpolate_template(locator_template, entry, idx)
            
            # Serialize content
            content = json.dumps(entry, ensure_ascii=False, sort_keys=True)
            
            # Insert chunk
            if not dry_run:
                try:
                    self.conn.execute(
                        """
                        INSERT INTO chunks (
                            chunk_id, anchor_id, anchor_locator,
                            content, truth_type, mutation_mode,
                            import_session_id, created_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?);
                        """,
                        (
                            chunk_id,
                            anchor_id,
                            locator,
                            content,
                            truth_type,
                            "append-only",
                            self.session_id,
                            now_utc_iso_z(),
                        ),
                    )
                    inserted += 1
                except sqlite3.IntegrityError as e:
                    self.enforce_strict_rule("chunk_collision", f"Chunk ID collision: {chunk_id}")
            else:
                # Dry-run: just count
                inserted += 1
        
        # Commit
        if not dry_run:
            self.conn.commit()
        
        # Get counts after
        counts_after = self.get_db_counts()
        chunks_after = counts_after["chunks"]
        delta = chunks_after - chunks_before
        
        # Verify delta
        if not dry_run and delta != inserted:
            errors.append(f"Database delta mismatch: expected={inserted}, actual={delta}")
        
        return IngestionResult(
            success=len(errors) == 0,
            chunks_inserted=inserted,
            chunks_before=chunks_before,
            chunks_after=chunks_after if not dry_run else chunks_before,
            delta=delta if not dry_run else 0,
            errors=errors,
            warnings=self.warnings,
            metadata={
                "total_entries": len(entries),
                "source_type": "json",
            }
        )
    
    def get_chunk_id_template(self) -> str:
        """Get chunk ID template from config"""
        for step in self.config.get("steps", []):
            if step.get("type") == "ingest_chunks":
                return step.get("chunk_id_template", "{anchor_id}:{index}")
        return "{anchor_id}:{index}"
    
    def get_locator_template(self) -> str:
        """Get locator template from config"""
        for step in self.config.get("steps", []):
            if step.get("type") == "ingest_chunks":
                return step.get("locator_template", "json:entry:{index}")
        return "json:entry:{index}"
    
    def get_truth_type(self) -> str:
        """Get truth type from config"""
        for step in self.config.get("steps", []):
            if step.get("type") == "ingest_chunks":
                return step.get("truth_type", "record")
        return "record"
    
    def interpolate_template(self, template: str, entry: Dict[str, Any], index: int) -> str:
        """
        Interpolate template variables
        
        Variables:
            {anchor_id} - Anchor ID from config
            {index} - Entry index (0-based)
            {row_index} - Entry index (1-based)
            {foo} - entry["foo"] if exists
        """
        result = template
        
        # Built-in variables
        result = result.replace("{anchor_id}", self.get_anchor_id())
        result = result.replace("{index}", str(index))
        result = result.replace("{row_index}", str(index + 1))
        
        # Entry fields
        for key, value in entry.items():
            placeholder = f"{{{key}}}"
            if placeholder in result:
                result = result.replace(placeholder, str(value))
        
        return result


# Register module
register_module("json", JSONIngestionModule)
