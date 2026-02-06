#!/usr/bin/env python3
"""
validate_receipt.py - Sovereign Receipt Validator

Validates receipt JSON files against the schemas defined in docs/RECEIPT_SCHEMAS.md.

Usage:
    python scripts/validate_receipt.py <receipt.json>

Exit codes:
    0 - Receipt is valid
    1 - Receipt is invalid (validation errors)
    2 - File not found or JSON parse error
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Import hash utilities from chain constitution
try:
    sys.path.insert(0, str(BASE_DIR / "core"))
    from chain_constitution import compute_payload_hash
except ImportError:
    # Fallback if chain_constitution not available
    import hashlib
    def compute_payload_hash(data: Any) -> str:
        """Fallback hash function"""
        canonical = json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


# Schema version
SCHEMA_VERSION = "1.0"

# Enumerated receipt types (from RECEIPT_SCHEMAS.md)
VALID_RECEIPT_TYPES = {
    # Class 1 ? State & Authority
    "STATE_TRANSITION",
    "SESSION_LOCK_CREATED",
    
    # Class 2 ? Anchor Lifecycle
    "ANCHOR_ADDED",
    "ANCHOR_UPGRADED",
    "ANCHOR_STATUS_CHANGED",
    "ANCHOR_DEPRECATED",
    
    # Class 3 ? Ingestion & Chunking
    "INGESTION_STARTED",
    "INGESTION_COMPLETED",
    "CHUNKING_COMPLETED",
    
    # Class 4 ? Evidence & Index
    "EVIDENCE_INDEX_REBUILT",
    "EVIDENCE_BUNDLE_CREATED",
    
    # Class 5 ? Change Control
    "CODEBASE_FINGERPRINT_BEFORE",
    "CODEBASE_FINGERPRINT_AFTER",
    "CODEBASE_DIFF_CREATED",
    
    # Class 6 ? Interpretation & Derivation
    "DERIVATION_CREATED",
    "SUMMARY_CREATED",
    
    # Class 7 ? Boundary & Epoch
    "SEAL_CREATED",
    "EPOCH_DECLARED",
    
    # Class 8 ? Deprecation & Sunset (Future/Reserved)
    "ANCHOR_SUNSET",
    "FEATURE_DEPRECATED",
    "SUBSYSTEM_DECOMMISSIONED",
}

# Actor kinds
VALID_ACTOR_KINDS = {"human", "agent", "script", "system"}

# Regex patterns
SHA256_PATTERN = re.compile(r"^[a-f0-9]{64}$")
UTC_TIMESTAMP_PATTERN = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$")
RECEIPT_ID_PATTERN = re.compile(r"^R_[0-9]{8}T[0-9]{6}Z_[A-Z_]+_[a-z0-9_]+$")


class ValidationError(Exception):
    """Receipt validation error"""
    pass


def validate_sha256(value: str, field_name: str) -> None:
    """Validate SHA256 hash format"""
    if not isinstance(value, str):
        raise ValidationError(f"{field_name}: must be string, got {type(value).__name__}")
    if not SHA256_PATTERN.match(value):
        raise ValidationError(f"{field_name}: must be 64 lowercase hex chars, got '{value}'")


def validate_utc_timestamp(value: str, field_name: str) -> None:
    """Validate UTC timestamp format (ISO8601)"""
    if not isinstance(value, str):
        raise ValidationError(f"{field_name}: must be string, got {type(value).__name__}")
    if not UTC_TIMESTAMP_PATTERN.match(value):
        raise ValidationError(f"{field_name}: must be ISO8601 UTC (YYYY-MM-DDTHH:MM:SSZ), got '{value}'")


def validate_artifact_ref(artifact: Dict[str, Any], context: str) -> None:
    """Validate ArtifactRef object"""
    if not isinstance(artifact, dict):
        raise ValidationError(f"{context}: artifact must be object, got {type(artifact).__name__}")
    
    # Required fields
    if "path" not in artifact:
        raise ValidationError(f"{context}: missing required field 'path'")
    if "sha256" not in artifact:
        raise ValidationError(f"{context}: missing required field 'sha256'")
    
    # Validate path
    if not isinstance(artifact["path"], str) or len(artifact["path"]) < 1:
        raise ValidationError(f"{context}: 'path' must be non-empty string")
    
    # Validate sha256
    validate_sha256(artifact["sha256"], f"{context}.sha256")
    
    # Optional fields
    if "bytes" in artifact:
        if not isinstance(artifact["bytes"], int) or artifact["bytes"] < 0:
            raise ValidationError(f"{context}: 'bytes' must be non-negative integer")
    
    if "mime" in artifact and not isinstance(artifact["mime"], str):
        raise ValidationError(f"{context}: 'mime' must be string")
    
    if "role" in artifact and not isinstance(artifact["role"], str):
        raise ValidationError(f"{context}: 'role' must be string")


def validate_actor(actor: Dict[str, Any]) -> None:
    """Validate Actor object"""
    if not isinstance(actor, dict):
        raise ValidationError(f"actor: must be object, got {type(actor).__name__}")
    
    # Required fields
    if "kind" not in actor:
        raise ValidationError("actor: missing required field 'kind'")
    if "name" not in actor:
        raise ValidationError("actor: missing required field 'name'")
    
    # Validate kind
    if actor["kind"] not in VALID_ACTOR_KINDS:
        raise ValidationError(f"actor.kind: must be one of {VALID_ACTOR_KINDS}, got '{actor['kind']}'")
    
    # Validate name
    if not isinstance(actor["name"], str) or len(actor["name"]) < 1:
        raise ValidationError("actor.name: must be non-empty string")
    
    # Optional fields
    if "host" in actor and not isinstance(actor["host"], str):
        raise ValidationError("actor.host: must be string")
    
    if "tool_version" in actor and not isinstance(actor["tool_version"], str):
        raise ValidationError("actor.tool_version: must be string")


def validate_integrity(integrity: Dict[str, Any]) -> None:
    """Validate Integrity object"""
    if not isinstance(integrity, dict):
        raise ValidationError(f"integrity: must be object, got {type(integrity).__name__}")
    
    # Required field
    if "artifacts" not in integrity:
        raise ValidationError("integrity: missing required field 'artifacts'")
    
    # Validate artifacts array
    if not isinstance(integrity["artifacts"], list):
        raise ValidationError(f"integrity.artifacts: must be array, got {type(integrity['artifacts']).__name__}")
    
    for i, artifact in enumerate(integrity["artifacts"]):
        validate_artifact_ref(artifact, f"integrity.artifacts[{i}]")
    
    # Optional fields
    if "receipt_sha256" in integrity:
        validate_sha256(integrity["receipt_sha256"], "integrity.receipt_sha256")
    
    if "previous_receipt_sha256" in integrity:
        validate_sha256(integrity["previous_receipt_sha256"], "integrity.previous_receipt_sha256")


def validate_links(links: Dict[str, Any]) -> None:
    """Validate Links object"""
    if not isinstance(links, dict):
        raise ValidationError(f"links: must be object, got {type(links).__name__}")
    
    # All fields are optional, but validate types if present
    if "related_receipt_ids" in links:
        if not isinstance(links["related_receipt_ids"], list):
            raise ValidationError("links.related_receipt_ids: must be array")
        for i, rid in enumerate(links["related_receipt_ids"]):
            if not isinstance(rid, str):
                raise ValidationError(f"links.related_receipt_ids[{i}]: must be string")
    
    if "run_id" in links and not isinstance(links["run_id"], str):
        raise ValidationError("links.run_id: must be string")
    
    if "manifest_id" in links and not isinstance(links["manifest_id"], str):
        raise ValidationError("links.manifest_id: must be string")
    
    if "anchor_id" in links and not isinstance(links["anchor_id"], str):
        raise ValidationError("links.anchor_id: must be string")


def validate_chain_fields(receipt: Dict[str, Any]) -> List[str]:
    """
    Validate optional chain fields (if present).
    Returns list of warnings (non-fatal issues).
    """
    warnings = []
    
    # Chain fields are OPTIONAL - only validate if present
    if "chain_id" in receipt:
        if not isinstance(receipt["chain_id"], str) or len(receipt["chain_id"]) < 1:
            raise ValidationError("chain_id: must be non-empty string")
    
    if "sequence" in receipt:
        if not isinstance(receipt["sequence"], int) or receipt["sequence"] < 0:
            raise ValidationError("sequence: must be non-negative integer")
    
    if "payload_hash" in receipt:
        validate_sha256(receipt["payload_hash"], "payload_hash")
    
    if "sealed" in receipt:
        if not isinstance(receipt["sealed"], bool):
            raise ValidationError("sealed: must be boolean")
    
    if "previous_receipt_hash" in receipt:
        validate_sha256(receipt["previous_receipt_hash"], "previous_receipt_hash")
    
    return warnings


def validate_base_schema(receipt: Dict[str, Any]) -> None:
    """Validate base receipt schema (applies to ALL receipts)"""
    
    # Required fields
    required_fields = [
        "schema_version",
        "receipt_type",
        "receipt_id",
        "session_id",
        "timestamp_utc",
        "actor",
        "intent",
        "links",
        "integrity",
    ]
    
    for field in required_fields:
        if field not in receipt:
            raise ValidationError(f"Missing required field: '{field}'")
    
    # Validate schema_version
    if receipt["schema_version"] != SCHEMA_VERSION:
        raise ValidationError(f"schema_version: expected '{SCHEMA_VERSION}', got '{receipt['schema_version']}'")
    
    # Validate receipt_type
    if receipt["receipt_type"] not in VALID_RECEIPT_TYPES:
        raise ValidationError(f"receipt_type: unknown type '{receipt['receipt_type']}'")
    
    # Validate receipt_id format
    if not isinstance(receipt["receipt_id"], str) or len(receipt["receipt_id"]) < 10:
        raise ValidationError("receipt_id: must be string with at least 10 characters")
    
    # Validate session_id
    if not isinstance(receipt["session_id"], str) or len(receipt["session_id"]) < 5:
        raise ValidationError("session_id: must be string with at least 5 characters")
    
    # Validate timestamp_utc
    validate_utc_timestamp(receipt["timestamp_utc"], "timestamp_utc")
    
    # Validate occurred_utc (optional)
    if "occurred_utc" in receipt:
        validate_utc_timestamp(receipt["occurred_utc"], "occurred_utc")
    
    # Validate actor
    validate_actor(receipt["actor"])
    
    # Validate intent
    if not isinstance(receipt["intent"], str) or len(receipt["intent"]) < 3:
        raise ValidationError("intent: must be string with at least 3 characters")
    
    # Validate links
    validate_links(receipt["links"])
    
    # Validate integrity
    validate_integrity(receipt["integrity"])
    
    # Validate notes (optional)
    if "notes" in receipt and not isinstance(receipt["notes"], str):
        raise ValidationError("notes: must be string")


def validate_type_specific(receipt: Dict[str, Any]) -> None:
    """Validate type-specific required fields"""
    receipt_type = receipt["receipt_type"]
    
    # ANCHOR_ADDED
    if receipt_type == "ANCHOR_ADDED":
        if "anchor" not in receipt:
            raise ValidationError("ANCHOR_ADDED: missing required field 'anchor'")
        anchor = receipt["anchor"]
        required = ["anchor_id", "role", "source_path", "sha256", "status", "added_reason"]
        for field in required:
            if field not in anchor:
                raise ValidationError(f"ANCHOR_ADDED: anchor.{field} is required")
        if anchor["status"] not in ["canon", "working"]:
            raise ValidationError(f"ANCHOR_ADDED: anchor.status must be 'canon' or 'working'")
        validate_sha256(anchor["sha256"], "anchor.sha256")
    
    # ANCHOR_UPGRADED
    elif receipt_type == "ANCHOR_UPGRADED":
        required_top = ["anchor", "previous", "next", "archive", "upgrade_reason"]
        for field in required_top:
            if field not in receipt:
                raise ValidationError(f"ANCHOR_UPGRADED: missing required field '{field}'")
        
        # Validate previous/next/archive structures
        for section in ["previous", "next"]:
            for field in ["path", "sha256", "version"]:
                if field not in receipt[section]:
                    raise ValidationError(f"ANCHOR_UPGRADED: {section}.{field} is required")
            validate_sha256(receipt[section]["sha256"], f"{section}.sha256")
        
        for field in ["path", "sha256"]:
            if field not in receipt["archive"]:
                raise ValidationError(f"ANCHOR_UPGRADED: archive.{field} is required")
        validate_sha256(receipt["archive"]["sha256"], "archive.sha256")
    
    # INGESTION_COMPLETED
    elif receipt_type == "INGESTION_COMPLETED":
        required_top = ["anchor_id", "source_artifact", "output_artifacts", "stats"]
        for field in required_top:
            if field not in receipt:
                raise ValidationError(f"INGESTION_COMPLETED: missing required field '{field}'")
        
        validate_artifact_ref(receipt["source_artifact"], "source_artifact")
        
        if not isinstance(receipt["output_artifacts"], list) or len(receipt["output_artifacts"]) < 1:
            raise ValidationError("INGESTION_COMPLETED: output_artifacts must be non-empty array")
        
        for i, artifact in enumerate(receipt["output_artifacts"]):
            validate_artifact_ref(artifact, f"output_artifacts[{i}]")
        
        if "chunks_count" not in receipt["stats"]:
            raise ValidationError("INGESTION_COMPLETED: stats.chunks_count is required")
    
    # Add more type-specific validations as needed
    # For now, other types pass if they have base schema


def validate_receipt(receipt_path: Path) -> tuple[bool, List[str], List[str]]:
    """
    Validate a receipt file.
    
    Returns:
        (is_valid, errors, warnings)
    """
    errors = []
    warnings = []
    
    try:
        # Load JSON
        with open(receipt_path, "r", encoding="utf-8") as f:
            receipt = json.load(f)
        
        # Validate base schema
        validate_base_schema(receipt)
        
        # Validate type-specific fields
        validate_type_specific(receipt)
        
        # Validate optional chain fields
        chain_warnings = validate_chain_fields(receipt)
        warnings.extend(chain_warnings)
        
        return (True, [], warnings)
        
    except json.JSONDecodeError as e:
        errors.append(f"JSON parse error: {e}")
        return (False, errors, warnings)
    
    except ValidationError as e:
        errors.append(str(e))
        return (False, errors, warnings)
    
    except Exception as e:
        errors.append(f"Unexpected error: {e}")
        return (False, errors, warnings)


def main() -> int:
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Validate receipt JSON against Solob receipt schemas",
        epilog="Exit codes: 0=valid, 1=invalid, 2=file error"
    )
    parser.add_argument("receipt", type=Path, help="Path to receipt JSON file")
    parser.add_argument("--quiet", "-q", action="store_true", help="Suppress output (exit code only)")
    
    args = parser.parse_args()
    
    # Check file exists
    if not args.receipt.exists():
        if not args.quiet:
            print(f"ERROR: File not found: {args.receipt}", file=sys.stderr)
        return 2
    
    # Validate
    is_valid, errors, warnings = validate_receipt(args.receipt)
    
    if not args.quiet:
        if is_valid:
            print(f"[OK] VALID: {args.receipt}")
            if warnings:
                print(f"  Warnings: {len(warnings)}")
                for warning in warnings:
                    print(f"    - {warning}")
        else:
            print(f"[FAIL] INVALID: {args.receipt}", file=sys.stderr)
            print(f"  Errors: {len(errors)}", file=sys.stderr)
            for error in errors:
                print(f"    - {error}", file=sys.stderr)
    
    return 0 if is_valid else 1


if __name__ == "__main__":
    sys.exit(main())
