#!/usr/bin/env python3
"""
PDF Ingestion Module

Handles PDF page-by-page ingestion with SHA256 verification.
Based on chunk_bos_pages_pilot.py logic.
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from modules.base_module import BaseIngestionModule, IngestionResult, register_module


def now_utc_iso_z() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_file(path: Path) -> str:
    """Calculate SHA256 hash of a file"""
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_text(s: str) -> str:
    """Calculate SHA256 hash of text"""
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


class PDFIngestionModule(BaseIngestionModule):
    """PDF page-by-page ingestion with manifest verification"""
    
    def validate(self) -> bool:
        """Validate prerequisites"""
        anchor_id = self.get_anchor_id()
        if not anchor_id:
            self.errors.append("Missing anchor_id in config")
            return False
        
        if not self.check_anchor_exists(anchor_id):
            self.enforce_strict_rule("missing_anchor", f"Anchor not found: {anchor_id}")
            return False
        
        source_path = self.get_source_path()
        if not source_path.exists():
            self.errors.append(f"PDF file not found: {source_path}")
            return False
        
        # Verify SHA256 if manifest provided
        expected_sha = self.get_manifest_sha256()
        if expected_sha:
            actual_sha = sha256_file(source_path)
            if actual_sha != expected_sha:
                self.enforce_strict_rule(
                    "manifest_sha_mismatch",
                    f"SHA256 mismatch: expected={expected_sha[:16]}..., actual={actual_sha[:16]}..."
                )
                return False
        
        return True
    
    def execute(self, dry_run: bool = False) -> IngestionResult:
        """Execute PDF page ingestion"""
        counts_before = self.get_db_counts()
        chunks_before = counts_before["chunks"]
        
        source_path = self.get_source_path()
        
        # Extract pages
        try:
            pages = self.extract_pdf_pages(source_path)
        except Exception as e:
            return IngestionResult(
                success=False, chunks_inserted=0, chunks_before=chunks_before,
                chunks_after=chunks_before, delta=0,
                errors=[f"PDF extraction failed: {e}"], warnings=[], metadata={}
            )
        
        if not pages:
            return IngestionResult(
                success=False, chunks_inserted=0, chunks_before=chunks_before,
                chunks_after=chunks_before, delta=0,
                errors=["PDF yielded zero pages"], warnings=[], metadata={}
            )
        
        anchor_id = self.get_anchor_id()
        chunk_id_namespace = self.get_chunk_id_namespace()
        manifest_sha = self.get_manifest_sha256() or sha256_file(source_path)
        truth_type = self.get_truth_type()
        
        inserted = 0
        errors = []
        
        for page_num, content in enumerate(pages, start=1):
            if not content.strip():
                continue
            
            # Generate collision-proof chunk ID
            base = f"{chunk_id_namespace}|{anchor_id}|{manifest_sha}|{page_num}"
            chunk_id = sha256_text(base)
            locator = f"pdf:page:{page_num:04d}"
            
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
                            chunk_id, anchor_id, locator,
                            content, truth_type, "append-only",
                            self.session_id, now_utc_iso_z(),
                        ),
                    )
                    inserted += 1
                except sqlite3.IntegrityError:
                    self.enforce_strict_rule("chunk_collision", f"Chunk ID collision: {chunk_id[:16]}...")
            else:
                inserted += 1
        
        if not dry_run:
            self.conn.commit()
        
        counts_after = self.get_db_counts()
        chunks_after = counts_after["chunks"]
        delta = chunks_after - chunks_before
        
        return IngestionResult(
            success=len(errors) == 0,
            chunks_inserted=inserted,
            chunks_before=chunks_before,
            chunks_after=chunks_after if not dry_run else chunks_before,
            delta=delta if not dry_run else 0,
            errors=errors,
            warnings=self.warnings,
            metadata={
                "pages_total": len(pages),
                "pages_inserted": inserted,
                "source_type": "pdf",
            }
        )
    
    def extract_pdf_pages(self, pdf_path: Path) -> List[str]:
        """Extract text from each PDF page using PyMuPDF"""
        try:
            import fitz  # PyMuPDF
        except ImportError:
            raise RuntimeError("PyMuPDF (fitz) not available. Install with: pip install pymupdf")
        
        doc = fitz.open(pdf_path)
        pages = []
        for i in range(doc.page_count):
            text = doc.load_page(i).get_text("text") or ""
            pages.append(text.strip())
        doc.close()
        return pages
    
    def get_manifest_sha256(self) -> str:
        """Get expected SHA256 from config"""
        return self.config.get("source", {}).get("manifest_sha256", "")
    
    def get_chunk_id_namespace(self) -> str:
        """Get chunk ID namespace"""
        for step in self.config.get("steps", []):
            if step.get("type") == "ingest_chunks":
                return step.get("chunk_id_namespace", "SOLOB|V2|CHUNK|PDF_PAGE")
        return "SOLOB|V2|CHUNK|PDF_PAGE"
    
    def get_truth_type(self) -> str:
        for step in self.config.get("steps", []):
            if step.get("type") == "ingest_chunks":
                return step.get("truth_type", "empirical")
        return "empirical"


register_module("pdf", PDFIngestionModule)
