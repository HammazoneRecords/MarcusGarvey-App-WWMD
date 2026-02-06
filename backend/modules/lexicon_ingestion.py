#!/usr/bin/env python3
"""
Lexicon Ingestion Module

Handles lexicon JSON file ingestion with row index derivation support.
Based on import_lexicon_chunks_v1_1.py logic.
"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from modules.base_module import BaseIngestionModule, IngestionResult, register_module


def now_utc_iso_z() -> str:
    """Get current UTC timestamp"""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class LexiconIngestionModule(BaseIngestionModule):
    """Lexicon-specific ingestion with letter and row index handling"""
    
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
        
        # Validate JSON format
        try:
            data = json.loads(source_path.read_text(encoding="utf-8"))
            if isinstance(data, list):
                pass  # Legacy format OK
            elif isinstance(data, dict) and "entries" in data:
                pass  # Current format OK
            else:
                self.errors.append("Lexicon JSON must be a list or dict with 'entries' key")
                return False
        except json.JSONDecodeError as e:
            self.errors.append(f"Invalid JSON: {e}")
            return False
        
        return True
    
    def execute(self, dry_run: bool = False) -> IngestionResult:
        """Execute lexicon ingestion"""
        # Get database counts before
        counts_before = self.get_db_counts()
        chunks_before = counts_before["chunks"]
        
        # Load JSON
        source_path = self.get_source_path()
        raw = json.loads(source_path.read_text(encoding="utf-8"))
        
        # Handle both formats
        if isinstance(raw, list):
            entries = raw
        elif isinstance(raw, dict) and "entries" in raw:
            entries = raw["entries"]
        else:
            return IngestionResult(
                success=False, chunks_inserted=0, chunks_before=chunks_before,
                chunks_after=chunks_before, delta=0,
                errors=["Invalid lexicon format"], warnings=[], metadata={}
            )
        
        # Get config
        anchor_id = self.get_anchor_id()
        letter = self.get_letter()
        chunk_id_template = self.get_chunk_id_template()
        locator_template = self.get_locator_template()
        truth_type = self.get_truth_type()
        derive_row_index = self.get_derive_row_index()
        
        # Insert chunks
        inserted = 0
        errors = []
        
        for idx, entry in enumerate(entries):
            if not isinstance(entry, dict):
                errors.append(f"Entry {idx} is not a dict")
                continue
            
            # Get or derive row index
            row_index = self.find_row_index(entry, idx, derive_row_index)
            if row_index is None:
                errors.append(f"Entry {idx}: missing row_index and --derive-row-index not set")
                continue
            
            # Build context for templates
            context = {
                "anchor_id": anchor_id,
                "letter": letter,
                "row_index": row_index,
                "index": idx,
                **entry  # Include all entry fields
            }
            
            # Generate chunk ID and locator
            chunk_id = self.interpolate_template(chunk_id_template, context)
            locator = self.interpolate_template(locator_template, context)
            
            # Get lexicon word
            lexicon_word = entry.get("word", entry.get("term", ""))
            
            # Serialize content
            content = json.dumps(entry, ensure_ascii=False, sort_keys=True)
            
            # Insert chunk
            if not dry_run:
                try:
                    self.conn.execute(
                        """
                        INSERT INTO chunks (
                            chunk_id, anchor_id, anchor_locator, lexicon_word,
                            content, truth_type, mutation_mode,
                            import_session_id, created_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
                        """,
                        (
                            chunk_id, anchor_id, locator, lexicon_word,
                            content, truth_type, "append-only",
                            self.session_id, now_utc_iso_z(),
                        ),
                    )
                    inserted += 1
                except sqlite3.IntegrityError as e:
                    self.enforce_strict_rule("chunk_collision", f"Chunk ID collision: {chunk_id}")
            else:
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
                "letter": letter,
                "source_type": "lexicon",
            }
        )
    
    def get_letter(self) -> str:
        """Get letter from config or source"""
        # Check ritual config first
        for step in self.config.get("steps", []):
            if "letter" in step:
                return step["letter"]
        
        # Check source config
        return self.config.get("source", {}).get("letter", "")
    
    def get_derive_row_index(self) -> bool:
        """Check if row index derivation is enabled"""
        return self.config.get("options", {}).get("derive_row_index", False)
    
    def get_chunk_id_template(self) -> str:
        """Get chunk ID template"""
        for step in self.config.get("steps", []):
            if step.get("type") == "ingest_chunks":
                return step.get("chunk_id_template", "{anchor_id}:{letter}:{row_index}")
        return "{anchor_id}:{letter}:{row_index}"
    
    def get_locator_template(self) -> str:
        """Get locator template"""
        for step in self.config.get("steps", []):
            if step.get("type") == "ingest_chunks":
                return step.get("locator_template", "lexicon:{letter}:row:{row_index}")
        return "lexicon:{letter}:row:{row_index}"
    
    def get_truth_type(self) -> str:
        """Get truth type"""
        for step in self.config.get("steps", []):
            if step.get("type") == "ingest_chunks":
                return step.get("truth_type", "definition")
        return "definition"
    
    def find_row_index(self, entry: Dict[str, Any], array_index: int, derive: bool) -> int | None:
        """Find row index from entry or derive from position"""
        # Try common row index keys
        for key in ["row_index", "row", "index", "id"]:
            if key in entry:
                try:
                    return int(entry[key])
                except (ValueError, TypeError):
                    pass
        
        # Derive from array position if enabled
        if derive:
            return array_index + 1  # 1-based
        
        return None
    
    def interpolate_template(self, template: str, context: Dict[str, Any]) -> str:
        """Interpolate template with context"""
        result = template
        for key, value in context.items():
            placeholder = f"{{{key}}}"
            if placeholder in result:
                result = result.replace(placeholder, str(value))
        return result


# Register module
register_module("lexicon", LexiconIngestionModule)
