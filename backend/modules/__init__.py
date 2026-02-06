"""
Modules package for ritual-based ingestion

This package contains ingestion modules that implement specific patterns.
Each module must inherit from BaseIngestionModule and register itself.
"""

# Import all modules to trigger registration
from modules import json_ingestion, lexicon_ingestion, pdf_ingestion, registry_ingestion

__all__ = ["json_ingestion", "lexicon_ingestion", "pdf_ingestion", "registry_ingestion"]
