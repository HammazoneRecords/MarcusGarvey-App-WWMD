# RECEIPT SCHEMAS (V1)
(CANONICAL ? VERSION 1.0)

**Status:** Active  
**Supersedes:** None (initial version)  
**Last Updated:** 2025-12-26  
**Schema Version:** 1.0

---

## Purpose

Receipts are the Wrapper's evidence atoms.

A receipt is not "a note about what happened."  
A receipt is a **structured proof object** that can be validated and indexed.

This document defines the **minimum required fields** for each receipt class.

**Rule:**  
If a receipt does not validate against its schema, it is not a receipt.  
It is noise.

---

## Schema Philosophy

### 1) Stable core, flexible details
All receipts share a common base schema (identity + time + linkage + integrity).  
Each receipt type adds domain-specific payload.

### 2) Append-only thinking
Receipts must not be edited.  
Corrections are new receipts that reference prior receipts.

### 3) Hash-first integrity
When a receipt refers to an artifact, it must provide a `sha256` and a `path`.  
If you can't hash it, you can't prove it.

---

## Receipt ID & Naming

### `receipt_id`
Required format:
- `R_<UTCSTAMP>_<TYPE>_<SHORTTAG>`

Example:
- `R_20251226T052432Z_ANCHOR_UPGRADED_wai`

### File naming (recommended)
`evidence/<SID>/receipts/<receipt_id>.json`

---

## Time Fields

### `timestamp_utc`
RFC3339 / ISO8601 UTC string:
- `YYYY-MM-DDTHH:MM:SSZ`

### `occurred_utc` (optional)
If the event occurred earlier than receipt emission, record it here.

### Operator Timezone Reference
**Kingston, Jamaica:** UTC-5 (EST, no daylight saving time)

**Conversion example:**
- Local: `2025-12-26T01:46:09-05:00`
- UTC:   `2025-12-26T06:46:09Z`

**Rule:**  
All receipts MUST use UTC (`timestamp_utc` field).  
Local timestamps are for human-readable logs only.

See [TIMEZONE_REFERENCE.md](./TIMEZONE_REFERENCE.md) for complete timezone documentation.

---

## Base Schema (applies to ALL receipts)

**ReceiptBase (required fields):**
- `schema_version` (string) -> `"1.0"`
- `receipt_type` (string) -> one of enumerated receipt types
- `receipt_id` (string) -> see format above
- `session_id` (string) -> e.g. `S_20251226T052432Z_WAI_UPGRADE`
- `timestamp_utc` (string UTC ISO)
- `actor` (object) -> who/what emitted it
- `intent` (string) -> human purpose statement (short)
- `links` (object) -> references to related receipts / runs / manifests
- `integrity` (object) -> hashes and tamper-evidence fields

**Actor object:**
- `kind` (enum): `human | agent | script | system`
- `name` (string): e.g. `"Ovando"` or `"solob.ps1"` or `"IDE: Antigravity"`
- `host` (optional string): machine identity label (not secret)
- `tool_version` (optional string): version tag if known

**Integrity object:**
- `receipt_sha256` (optional initially; later computed)  
- `previous_receipt_sha256` (optional; for chaining later)
- `artifacts` (array) -> each artifact referenced with `path`, `sha256`, and optional metadata

**ArtifactRef object (used everywhere):**
- `path` (string, repo-relative or evidence-relative)
- `sha256` (string, 64 hex)
- `bytes` (optional integer)
- `mime` (optional string)
- `role` (optional string) e.g. `anchor`, `manifest`, `diff`, `bundle_index`

---

## Enumerated Receipt Types (V1)

This schema defines these receipt types:

### Class 1 ? State & Authority
- `STATE_TRANSITION`
- `SESSION_LOCK_CREATED`

### Class 2 ? Anchor Lifecycle
- `ANCHOR_ADDED`
- `ANCHOR_UPGRADED`
- `ANCHOR_STATUS_CHANGED`
- `ANCHOR_DEPRECATED` (reserved; Class 8 candidate but allowed)

### Class 3 ? Ingestion & Chunking
- `INGESTION_STARTED`
- `INGESTION_COMPLETED`
- `CHUNKING_COMPLETED`

### Class 4 ? Evidence & Index
- `EVIDENCE_INDEX_REBUILT`
- `EVIDENCE_BUNDLE_CREATED`

### Class 5 ? Change Control
- `CODEBASE_FINGERPRINT_BEFORE`
- `CODEBASE_FINGERPRINT_AFTER`
- `CODEBASE_DIFF_CREATED`

### Class 6 ? Interpretation & Derivation
- `DERIVATION_CREATED`
- `SUMMARY_CREATED`

### Class 7 ? Boundary & Epoch
- `SEAL_CREATED`
- `EPOCH_DECLARED`

### Class 8 ? Deprecation & Sunset (Future/Reserved)
- `ANCHOR_SUNSET`
- `FEATURE_DEPRECATED`
- `SUBSYSTEM_DECOMMISSIONED`

---

## JSON Schema (Draft 2020-12)

> NOTE: These schemas are designed to be enforced by `scripts/validate_receipt.py`.  
> They are intentionally strict on identity + hashes, and permissive on narrative fields.

### Common Definitions

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "solob://schemas/receipt/common.json",
  "title": "Solob Receipt Common Definitions",
  "type": "object",
  "definitions": {
    "Sha256": {
      "type": "string",
      "pattern": "^[a-f0-9]{64}$"
    },
    "UtcTimestamp": {
      "type": "string",
      "pattern": "^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$"
    },
    "ArtifactRef": {
      "type": "object",
      "required": ["path", "sha256"],
      "properties": {
        "path": { "type": "string", "minLength": 1 },
        "sha256": { "$ref": "#/definitions/Sha256" },
        "bytes": { "type": "integer", "minimum": 0 },
        "mime": { "type": "string" },
        "role": { "type": "string" }
      },
      "additionalProperties": false
    },
    "Actor": {
      "type": "object",
      "required": ["kind", "name"],
      "properties": {
        "kind": { "type": "string", "enum": ["human", "agent", "script", "system"] },
        "name": { "type": "string", "minLength": 1 },
        "host": { "type": "string" },
        "tool_version": { "type": "string" }
      },
      "additionalProperties": false
    },
    "Integrity": {
      "type": "object",
      "required": ["artifacts"],
      "properties": {
        "receipt_sha256": { "$ref": "#/definitions/Sha256" },
        "previous_receipt_sha256": { "$ref": "#/definitions/Sha256" },
        "artifacts": {
          "type": "array",
          "items": { "$ref": "#/definitions/ArtifactRef" }
        }
      },
      "additionalProperties": false
    },
    "Links": {
      "type": "object",
      "properties": {
        "related_receipt_ids": {
          "type": "array",
          "items": { "type": "string" }
        },
        "run_id": { "type": "string" },
        "manifest_id": { "type": "string" },
        "anchor_id": { "type": "string" }
      },
      "additionalProperties": true
    }
  }
}
```

---

## Receipt Base Schema

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "solob://schemas/receipt/base.json",
  "title": "Solob Receipt Base Schema",
  "type": "object",
  "required": [
    "schema_version",
    "receipt_type",
    "receipt_id",
    "session_id",
    "timestamp_utc",
    "actor",
    "intent",
    "links",
    "integrity"
  ],
  "properties": {
    "schema_version": { "type": "string", "enum": ["1.0"] },
    "receipt_type": {
      "type": "string",
      "enum": [
        "STATE_TRANSITION",
        "SESSION_LOCK_CREATED",

        "ANCHOR_ADDED",
        "ANCHOR_UPGRADED",
        "ANCHOR_STATUS_CHANGED",
        "ANCHOR_DEPRECATED",

        "INGESTION_STARTED",
        "INGESTION_COMPLETED",
        "CHUNKING_COMPLETED",

        "EVIDENCE_INDEX_REBUILT",
        "EVIDENCE_BUNDLE_CREATED",

        "CODEBASE_FINGERPRINT_BEFORE",
        "CODEBASE_FINGERPRINT_AFTER",
        "CODEBASE_DIFF_CREATED",

        "DERIVATION_CREATED",
        "SUMMARY_CREATED",

        "SEAL_CREATED",
        "EPOCH_DECLARED",

        "ANCHOR_SUNSET",
        "FEATURE_DEPRECATED",
        "SUBSYSTEM_DECOMMISSIONED"
      ]
    },
    "receipt_id": { "type": "string", "minLength": 10 },
    "session_id": { "type": "string", "minLength": 5 },
    "timestamp_utc": { "$ref": "solob://schemas/receipt/common.json#/definitions/UtcTimestamp" },
    "occurred_utc": { "$ref": "solob://schemas/receipt/common.json#/definitions/UtcTimestamp" },

    "actor": { "$ref": "solob://schemas/receipt/common.json#/definitions/Actor" },
    "intent": { "type": "string", "minLength": 3 },

    "links": { "$ref": "solob://schemas/receipt/common.json#/definitions/Links" },
    "integrity": { "$ref": "solob://schemas/receipt/common.json#/definitions/Integrity" },

    "notes": { "type": "string" }
  },
  "additionalProperties": true
}
```

---

## Type-Specific Schemas (V1)

### 1) ANCHOR_ADDED

Required:
- `anchor.anchor_id`
- `anchor.role`
- `anchor.source_path`
- `anchor.sha256`
- `anchor.status` (`canon` or `working`)
- `anchor.added_reason`

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "solob://schemas/receipt/anchor_added.json",
  "title": "Receipt: ANCHOR_ADDED",
  "allOf": [
    { "$ref": "solob://schemas/receipt/base.json" }
  ],
  "properties": {
    "receipt_type": { "const": "ANCHOR_ADDED" },
    "anchor": {
      "type": "object",
      "required": ["anchor_id", "role", "source_path", "sha256", "status", "added_reason"],
      "properties": {
        "anchor_id": { "type": "string", "minLength": 1 },
        "role": { "type": "string", "minLength": 1 },
        "source_path": { "type": "string", "minLength": 1 },
        "sha256": { "$ref": "solob://schemas/receipt/common.json#/definitions/Sha256" },
        "status": { "type": "string", "enum": ["canon", "working"] },
        "added_reason": { "type": "string", "minLength": 3 }
      },
      "additionalProperties": false
    }
  }
}
```

---

### 2) ANCHOR_UPGRADED

Required:
- `anchor.anchor_id`
- `previous` (path + sha256 + version)
- `next` (path + sha256 + version)
- `archive` (path + sha256)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "solob://schemas/receipt/anchor_upgraded.json",
  "title": "Receipt: ANCHOR_UPGRADED",
  "allOf": [
    { "$ref": "solob://schemas/receipt/base.json" }
  ],
  "properties": {
    "receipt_type": { "const": "ANCHOR_UPGRADED" },
    "anchor": {
      "type": "object",
      "required": ["anchor_id"],
      "properties": {
        "anchor_id": { "type": "string" }
      },
      "additionalProperties": true
    },
    "previous": {
      "type": "object",
      "required": ["path", "sha256", "version"],
      "properties": {
        "path": { "type": "string" },
        "sha256": { "$ref": "solob://schemas/receipt/common.json#/definitions/Sha256" },
        "version": { "type": "string" }
      },
      "additionalProperties": false
    },
    "next": {
      "type": "object",
      "required": ["path", "sha256", "version"],
      "properties": {
        "path": { "type": "string" },
        "sha256": { "$ref": "solob://schemas/receipt/common.json#/definitions/Sha256" },
        "version": { "type": "string" }
      },
      "additionalProperties": false
    },
    "archive": {
      "type": "object",
      "required": ["path", "sha256"],
      "properties": {
        "path": { "type": "string" },
        "sha256": { "$ref": "solob://schemas/receipt/common.json#/definitions/Sha256" }
      },
      "additionalProperties": false
    },
    "upgrade_reason": { "type": "string", "minLength": 3 }
  },
  "required": ["anchor", "previous", "next", "archive", "upgrade_reason"]
}
```

---

### 3) INGESTION_COMPLETED

Required:
- `anchor_id`
- `source_artifact` (path + sha)
- `output_artifacts` (chunks index / db snapshot / logs)
- `stats` (chunks_count at minimum)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "solob://schemas/receipt/ingestion_completed.json",
  "title": "Receipt: INGESTION_COMPLETED",
  "allOf": [
    { "$ref": "solob://schemas/receipt/base.json" }
  ],
  "properties": {
    "receipt_type": { "const": "INGESTION_COMPLETED" },
    "anchor_id": { "type": "string", "minLength": 1 },
    "source_artifact": { "$ref": "solob://schemas/receipt/common.json#/definitions/ArtifactRef" },
    "output_artifacts": {
      "type": "array",
      "items": { "$ref": "solob://schemas/receipt/common.json#/definitions/ArtifactRef" },
      "minItems": 1
    },
    "stats": {
      "type": "object",
      "required": ["chunks_count"],
      "properties": {
        "chunks_count": { "type": "integer", "minimum": 0 },
        "tokens_estimate": { "type": "integer", "minimum": 0 }
      },
      "additionalProperties": true
    }
  },
  "required": ["anchor_id", "source_artifact", "output_artifacts", "stats"]
}
```

---

### 4) CODEBASE_DIFF_CREATED

Required:
- `before_fingerprint` artifact
- `after_fingerprint` artifact
- `diff_report` artifact

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "solob://schemas/receipt/codebase_diff_created.json",
  "title": "Receipt: CODEBASE_DIFF_CREATED",
  "allOf": [
    { "$ref": "solob://schemas/receipt/base.json" }
  ],
  "properties": {
    "receipt_type": { "const": "CODEBASE_DIFF_CREATED" },
    "before_fingerprint": { "$ref": "solob://schemas/receipt/common.json#/definitions/ArtifactRef" },
    "after_fingerprint": { "$ref": "solob://schemas/receipt/common.json#/definitions/ArtifactRef" },
    "diff_report": { "$ref": "solob://schemas/receipt/common.json#/definitions/ArtifactRef" }
  },
  "required": ["before_fingerprint", "after_fingerprint", "diff_report"]
}
```

---

### 5) EVIDENCE_INDEX_REBUILT

Required:
- index artifact
- root evidence path label

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "solob://schemas/receipt/evidence_index_rebuilt.json",
  "title": "Receipt: EVIDENCE_INDEX_REBUILT",
  "allOf": [
    { "$ref": "solob://schemas/receipt/base.json" }
  ],
  "properties": {
    "receipt_type": { "const": "EVIDENCE_INDEX_REBUILT" },
    "evidence_root": { "type": "string", "minLength": 1 },
    "index_artifact": { "$ref": "solob://schemas/receipt/common.json#/definitions/ArtifactRef" }
  },
  "required": ["evidence_root", "index_artifact"]
}
```

---

### 6) ANCHOR_SUNSET (Future/Class 8)

**Purpose:** Record the intentional removal or deprecation of an anchor from active use.

Required:
- `anchor.anchor_id`
- `sunset_reason`
- `replacement_anchor_id` (optional, if superseded)
- `final_state` (archived/deleted/superseded)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "solob://schemas/receipt/anchor_sunset.json",
  "title": "Receipt: ANCHOR_SUNSET",
  "allOf": [
    { "$ref": "solob://schemas/receipt/base.json" }
  ],
  "properties": {
    "receipt_type": { "const": "ANCHOR_SUNSET" },
    "anchor": {
      "type": "object",
      "required": ["anchor_id"],
      "properties": {
        "anchor_id": { "type": "string", "minLength": 1 }
      },
      "additionalProperties": true
    },
    "sunset_reason": { "type": "string", "minLength": 10 },
    "replacement_anchor_id": { "type": "string" },
    "final_state": {
      "type": "string",
      "enum": ["archived", "deleted", "superseded", "deprecated"]
    },
    "last_known_artifact": { "$ref": "solob://schemas/receipt/common.json#/definitions/ArtifactRef" }
  },
  "required": ["anchor", "sunset_reason", "final_state"]
}
```

---

### 7) FEATURE_DEPRECATED (Future/Class 8)

**Purpose:** Record the deprecation of a system feature, script, or capability.

Required:
- `feature_name`
- `deprecation_reason`
- `removal_timeline` (when it will be removed)
- `migration_path` (how users should adapt)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "solob://schemas/receipt/feature_deprecated.json",
  "title": "Receipt: FEATURE_DEPRECATED",
  "allOf": [
    { "$ref": "solob://schemas/receipt/base.json" }
  ],
  "properties": {
    "receipt_type": { "const": "FEATURE_DEPRECATED" },
    "feature_name": { "type": "string", "minLength": 1 },
    "feature_type": {
      "type": "string",
      "enum": ["script", "api_endpoint", "cli_command", "config_option", "subsystem"]
    },
    "deprecation_reason": { "type": "string", "minLength": 10 },
    "removal_timeline": { "type": "string" },
    "migration_path": { "type": "string", "minLength": 10 },
    "affected_artifacts": {
      "type": "array",
      "items": { "$ref": "solob://schemas/receipt/common.json#/definitions/ArtifactRef" }
    }
  },
  "required": ["feature_name", "feature_type", "deprecation_reason", "removal_timeline", "migration_path"]
}
```

---

### 8) SUBSYSTEM_DECOMMISSIONED (Future/Class 8)

**Purpose:** Record the complete removal of a major subsystem or component.

Required:
- `subsystem_name`
- `decommission_reason`
- `final_snapshot` (backup/archive reference)
- `dependencies_resolved` (boolean)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "solob://schemas/receipt/subsystem_decommissioned.json",
  "title": "Receipt: SUBSYSTEM_DECOMMISSIONED",
  "allOf": [
    { "$ref": "solob://schemas/receipt/base.json" }
  ],
  "properties": {
    "receipt_type": { "const": "SUBSYSTEM_DECOMMISSIONED" },
    "subsystem_name": { "type": "string", "minLength": 1 },
    "decommission_reason": { "type": "string", "minLength": 10 },
    "final_snapshot": { "$ref": "solob://schemas/receipt/common.json#/definitions/ArtifactRef" },
    "dependencies_resolved": { "type": "boolean" },
    "affected_components": {
      "type": "array",
      "items": { "type": "string" }
    },
    "migration_complete": { "type": "boolean" }
  },
  "required": ["subsystem_name", "decommission_reason", "final_snapshot", "dependencies_resolved"]
}
```

---

## Minimum Compliance Rule

A receipt is valid if:

1. It validates against `base.json`
2. It validates against its type schema
3. Every `sha256` is exactly 64 lowercase hex characters
4. Every artifact referenced exists at the time of sealing (enforced later by tools)

---

## Validation Checklist (for `validate_receipt.py`)

A receipt validator must check:

- [ ] JSON is well-formed
- [ ] `schema_version` == "1.0"
- [ ] `receipt_type` is in enumerated list
- [ ] `receipt_id` matches format `R_<TIMESTAMP>_<TYPE>_<TAG>`
- [ ] `session_id` exists and follows SID format
- [ ] `timestamp_utc` is valid ISO8601 UTC
- [ ] `actor.kind` is one of: human, agent, script, system
- [ ] All `sha256` fields are exactly 64 lowercase hex chars
- [ ] All referenced artifacts exist (path validation)
- [ ] Type-specific required fields present
- [ ] No extra top-level fields (unless `additionalProperties: true`)

---

## Appendix A: Real Receipt Examples

### Example 1: ANCHOR_UPGRADED (WAI v1.0 -> v1.1)

```json
{
  "schema_version": "1.0",
  "receipt_type": "ANCHOR_UPGRADED",
  "receipt_id": "R_20251226T052432Z_ANCHOR_UPGRADED_wai",
  "session_id": "S_20251226T052432Z_WAI_UPGRADE",
  "timestamp_utc": "2025-12-26T05:24:32Z",
  
  "actor": {
    "kind": "human",
    "name": "Ovando",
    "host": "local-dev",
    "tool_version": "Antigravity IDE"
  },
  
  "intent": "Upgrade WAI to v1.1: Add INVARIANT 14 (Archive Rule) + enhance PDF extraction guidance",
  
  "anchor": {
    "anchor_id": "wai_invariants"
  },
  
  "previous": {
    "path": "wrapper_anchor_invariants/WAI.md",
    "sha256": "89c5b5d294d10e99aa055866ad4b21a093f72ebfb2b50856b656f3a24b4457a8",
    "version": "v1.0"
  },
  
  "next": {
    "path": "wrapper_anchor_invariants/WAI.md",
    "sha256": "d749677b1e4b8136af48cf754e15cc46050733696178a92d6971269649196628",
    "version": "v1.1"
  },
  
  "archive": {
    "path": "wrapper_anchor_invariants/archive/WAI_v1.0_2025-12-19.md",
    "sha256": "64e7d7e345a8914ca0dd0bc042f40059324626a2c0274a4c094a8936fc96ca94"
  },
  
  "upgrade_reason": "Added INVARIANT 14 (versioning protocol for invariant files) and enhanced INVARIANT 12 (PDF/text extraction must not silently correct source)",
  
  "links": {
    "manifest_id": "anchors_manifest_20251226T052432Z.json",
    "anchor_id": "wai_invariants"
  },
  
  "integrity": {
    "artifacts": [
      {
        "path": "wrapper_anchor_invariants/WAI.md",
        "sha256": "d749677b1e4b8136af48cf754e15cc46050733696178a92d6971269649196628",
        "bytes": 7281,
        "role": "anchor"
      },
      {
        "path": "wrapper_anchor_invariants/archive/WAI_v1.0_2025-12-19.md",
        "sha256": "64e7d7e345a8914ca0dd0bc042f40059324626a2c0274a4c094a8936fc96ca94",
        "bytes": 4243,
        "role": "archive"
      }
    ]
  }
}
```

---

### Example 2: INGESTION_COMPLETED (Lexicon A)

**Note:** This is adapted from the actual receipt format currently in use.

```json
{
  "schema_version": "1.0",
  "receipt_type": "INGESTION_COMPLETED",
  "receipt_id": "R_20251225T045341Z_INGESTION_COMPLETED_lexicon_a",
  "session_id": "S_20251224T233858Z_LEXICON_AZ_FULL",
  "timestamp_utc": "2025-12-25T04:53:41Z",
  
  "actor": {
    "kind": "script",
    "name": "import_lexicon_chunks_v1_1.py",
    "tool_version": "v1.1"
  },
  
  "intent": "Ingest Lexicon A chunks into database",
  
  "anchor_id": "lexicon_A",
  
  "source_artifact": {
    "path": "anchors/canon/definitions/Lexical Canon Anchors/A/A.json",
    "sha256": "88cdf371e82e59e7c2e097e99bf38e76b805c0031e5953f20470141b998cd95c",
    "role": "anchor"
  },
  
  "output_artifacts": [
    {
      "path": "evidence/S_20251224T233858Z_LEXICON_AZ_FULL/RECEIPT_LEXICON_A.json",
      "sha256": "placeholder_hash_for_receipt",
      "role": "receipt"
    }
  ],
  
  "stats": {
    "chunks_count": 102,
    "format_mode": "top_level_dict_entries",
    "row_index_derived": false,
    "started_utc": "2025-12-25T04:53:41Z",
    "ended_utc": "2025-12-25T04:53:41Z"
  },
  
  "links": {
    "anchor_id": "lexicon_A",
    "manifest_id": "anchors_manifest_20251226T052432Z.json"
  },
  
  "integrity": {
    "artifacts": [
      {
        "path": "anchors/canon/definitions/Lexical Canon Anchors/A/A.json",
        "sha256": "88cdf371e82e59e7c2e097e99bf38e76b805c0031e5953f20470141b998cd95c",
        "role": "source"
      }
    ]
  }
}
```

---

### Example 3: EVIDENCE_BUNDLE_CREATED (Lexicon A-Z Coverage Ledger)

**Note:** This is adapted from the actual ledger receipt.

```json
{
  "schema_version": "1.0",
  "receipt_type": "EVIDENCE_BUNDLE_CREATED",
  "receipt_id": "R_20251225T205521Z_EVIDENCE_BUNDLE_lexicon_az",
  "session_id": "S_20251225T075155Z_STATE_RECORD",
  "timestamp_utc": "2025-12-25T20:55:21Z",
  
  "actor": {
    "kind": "script",
    "name": "prosecutor_lexicon_az_coverage.py",
    "tool_version": "v1.0"
  },
  
  "intent": "PROSECUTOR_LEXICON_AZ_COVERAGE_LEDGER: Verify all 26 lexicon anchors A-Z are ingested with correct chunk counts",
  
  "evidence_root": "evidence",
  
  "index_artifact": {
    "path": "evidence/S_20251225T075155Z_STATE_RECORD/RECEIPT_LEXICON_AZ_COVERAGE_LEDGER.json",
    "sha256": "placeholder_hash_for_ledger",
    "bytes": 2794,
    "role": "bundle_index"
  },
  
  "bundle_stats": {
    "lexicon_total_chunks": 1625,
    "letters_verified": 26,
    "all_status_ok": true
  },
  
  "links": {
    "related_receipt_ids": [
      "R_20251225T045341Z_INGESTION_COMPLETED_lexicon_a",
      "R_20251225T045342Z_INGESTION_COMPLETED_lexicon_b"
    ]
  },
  
  "integrity": {
    "artifacts": [
      {
        "path": "evidence/S_20251225T075155Z_STATE_RECORD/RECEIPT_LEXICON_AZ_COVERAGE_LEDGER.json",
        "sha256": "placeholder_hash_for_ledger",
        "role": "ledger"
      }
    ]
  }
}
```

---

## Related Documents

- [The 7 Classes of Receipts](./The%207%20Classes%20Of%20Receipts.md) ? Conceptual framework
- [CHANGE_CONTROL.md](./CHANGE_CONTROL.md) ? How receipts enforce change discipline
- [WAI.md](../anchors/wrapper_anchor_invariants/WAI.md) ? Anchor invariants that receipts enforce
- [STATE_TRANSITIONS.md](./STATE_TRANSITIONS.md) ? State discipline that receipts witness

---

## V1 Notes / Known Future Extensions

* Receipt chaining (`previous_receipt_sha256`) is reserved but optional in V1.
* Digital signing is not required in V1.
* Class 8 "Sunset / Deprecation" schemas are defined but not yet enforced.
* Validation tooling (`validate_receipt.py`) to be implemented in next phase.

---

END OF RECEIPT SCHEMAS ? V1.0
