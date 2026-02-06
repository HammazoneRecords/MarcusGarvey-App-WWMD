#!/usr/bin/env python3
"""
Base Module Interface for Ritual Engine

Defines the contract that all ingestion modules must implement.
Modules are responsible for executing specific ingestion patterns (lexicon, PDF, etc).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional
import sqlite3


@dataclass
class IngestionResult:
    """Result of module execution"""
    success: bool
    chunks_inserted: int
    chunks_before: int
    chunks_after: int
    delta: int
    errors: List[str]
    warnings: List[str]
    metadata: Dict[str, Any]


class BaseIngestionModule(ABC):
    """Base class for all ingestion modules"""
    
    def __init__(
        self,
        config: Dict[str, Any],
        conn: sqlite3.Connection,
        session_id: str,
        base_dir: Path
    ):
        """
        Initialize module with config and context
        
        Args:
            config: Ritual configuration dict
            conn: Database connection (with foreign keys enabled)
            session_id: Current import session ID
            base_dir: Repository base directory
        """
        self.config = config
        self.conn = conn
        self.session_id = session_id
        self.base_dir = base_dir
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    @abstractmethod
    def validate(self) -> bool:
        """
        Validate prerequisites before execution
        
        Returns:
            True if validation passes, False otherwise
        
        Side effects:
            Populates self.errors with validation failures
        """
        pass
    
    @abstractmethod
    def execute(self, dry_run: bool = False) -> IngestionResult:
        """
        Execute the ingestion
        
        Args:
            dry_run: If True, validate but don't insert into database
        
        Returns:
            IngestionResult with operation details
        """
        pass
    
    def get_anchor_id(self) -> str:
        """Get anchor_id from config"""
        return self.config.get("anchor_id", "")
    
    def get_source_path(self) -> Path:
        """Get resolved source file path"""
        source_config = self.config.get("source", {})
        rel_path = source_config.get("path", "")
        return (self.base_dir / rel_path).resolve()
    
    def get_strict_rules(self) -> Dict[str, str]:
        """Get strict failure rules"""
        return self.config.get("strict_rules", {})
    
    def check_anchor_exists(self, anchor_id: str) -> bool:
        """Check if anchor exists in database"""
        result = self.conn.execute(
            "SELECT 1 FROM anchors WHERE anchor_id = ? LIMIT 1",
            (anchor_id,)
        ).fetchone()
        return result is not None
    
    def get_db_counts(self) -> Dict[str, int]:
        """Get current database counts"""
        chunks = self.conn.execute("SELECT COUNT(*) FROM chunks").fetchone()[0]
        anchors = self.conn.execute("SELECT COUNT(*) FROM anchors").fetchone()[0]
        return {"chunks": chunks, "anchors": anchors}
    
    def enforce_strict_rule(self, rule_name: str, error_msg: str) -> None:
        """
        Enforce a strict rule
        
        Args:
            rule_name: Name of the rule (e.g., 'missing_anchor')
            error_msg: Error message to display
        
        Raises:
            RuntimeError if rule action is 'STOP'
        """
        rules = self.get_strict_rules()
        action = rules.get(rule_name, "STOP")
        
        if action == "STOP":
            raise RuntimeError(f"STOP: {rule_name} - {error_msg}")
        elif action == "WARN":
            self.warnings.append(f"WARN: {rule_name} - {error_msg}")
        # IGNORE: do nothing


# Module registry (populated by modules as they're loaded)
MODULE_REGISTRY: Dict[str, type[BaseIngestionModule]] = {}


def register_module(name: str, module_class: type[BaseIngestionModule]) -> None:
    """Register a module for use in rituals"""
    MODULE_REGISTRY[name] = module_class


def get_module(name: str) -> Optional[type[BaseIngestionModule]]:
    """Get a registered module by name"""
    return MODULE_REGISTRY.get(name)
