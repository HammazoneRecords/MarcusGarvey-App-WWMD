# QUARANTINE_TOMBSTONES.md

**Purpose**: Read-only ledger tracking quarantined files with tombstone markers and replacement file references.

**Philosophy**: *"Sankofa without amnesia ? we remember what was corrupted, we record why, we move forward clean."*

**Last Updated**: 2025-12-27T23:23:24-05:00

---

## Tombstone Policy

- **NO RESTORATION**: Files in quarantine NEVER return to active codebase
- **RECREATION ONLY**: If functionality needed, recreate cleanly with new file + new hash
- **TOMBSTONE REQUIRED**: Every quarantined file tracked here with reason and replacement (if applicable)
- **APPEND-ONLY**: This ledger never removes entries; history is permanent

---

## Encoding Corruption Quarantine (2025-12-27)

### Origin Event
- **Date**: 2025-12-27T13:43:00-05:00
- **Session**: `S_20251225T075155Z_STATE_RECORD`
- **Root Cause**: Repository-wide UTF-16/UTF-8 binary-level encoding mismatch
- **Pattern**: Ghost question mark corruption (`?i?m?p?o?r?t?`)

### Quarantined Files

#### scripts/artisan_emit_anchors_map_ascii.py
- **Quarantine Path**: `data/orphans/2025-12-27_encoding-recovery-pivot/quarantined_files/artisan_emit_anchors_map_ascii.py`
- **Reason**: Critical encoding corruption (ghost character pattern throughout)
- **Replacement File**: `scripts/cartographer_emit_anchors_map.py` (ASCII-safe variant already exists)
- **Status**: TOMBSTONED ? do not restore; use `cartographer_emit_anchors_map.py` instead
- **Date**: 2025-12-27T13:43:00-05:00

#### utils/ingest_flow_check.py
- **Quarantine Path**: `data/orphans/2025-12-27_encoding-recovery-pivot/quarantined_files/ingest_flow_check.py`
- **Reason**: Critical encoding corruption (ghost character pattern throughout)
- **Replacement File**: None created (functionality absorbed into `scripts/preflight_balance_check.py`)
- **Status**: TOMBSTONED ? do not restore; recreate if needed using CHANGELOG as reference
- **Date**: 2025-12-27T13:43:00-05:00

#### scripts/SCRIPT-LEVEL INVARIANTS.md
- **Quarantine Path**: `data/orphans/2025-12-27_encoding-recovery-pivot/quarantined_files/SCRIPT-LEVEL INVARIANTS.md`
- **Reason**: Critical encoding corruption (ghost character pattern throughout)
- **Replacement File**: None created yet
- **Status**: TOMBSTONED ? do not restore; recreate cleanly if needed
- **Date**: 2025-12-27T13:43:00-05:00
- **Note**: Documentation file; content may be reconstructable from other docs

---

## Orphaned Scripts (2025-12-27)

### Origin Event
- **Date**: 2025-12-27T13:43:00-05:00
- **Session**: `S_20251225T075155Z_STATE_RECORD`
- **Root Cause**: Encoding automation scripts abandoned (self-referential corruption issues)

### Orphaned Files

#### scripts/_fix_encoding.py
- **Orphan Path**: `data/orphans/2025-12-27_encoding-recovery-pivot/removed_scripts/_fix_encoding.py`
- **Reason**: Automated encoding fix approach abandoned; manual repair safer
- **Replacement File**: `docs/MANUAL_ENCODING_REPAIR.md` (workflow guide)
- **Status**: ORPHANED ? superseded by manual approach
- **Date**: 2025-12-27T13:43:00-05:00

#### scripts/_fix_ghost_question_marks.py
- **Orphan Path**: `data/orphans/2025-12-27_encoding-recovery-pivot/removed_scripts/_fix_ghost_question_marks.py`
- **Reason**: Automated encoding fix approach abandoned; manual repair safer
- **Replacement File**: `docs/MANUAL_ENCODING_REPAIR.md` (workflow guide)
- **Status**: ORPHANED ? superseded by manual approach
- **Date**: 2025-12-27T13:43:00-05:00

#### tools/encoding_defaults.ps1
- **Orphan Path**: `data/orphans/2025-12-27_encoding-recovery-pivot/removed_scripts/encoding_defaults.ps1`
- **Reason**: Automated encoding fix approach abandoned
- **Replacement File**: `.vscode/settings.json` (UTF-8 enforcement)
- **Status**: ORPHANED ? superseded by VSCode settings
- **Date**: 2025-12-27T13:43:00-05:00

#### tools/encoding_report.ps1
- **Orphan Path**: `data/orphans/2025-12-27_encoding-recovery-pivot/removed_scripts/encoding_report.ps1`
- **Reason**: Automated encoding fix approach abandoned
- **Replacement File**: `tools/encoding_report.ps1` (non-destructive audit version exists as active script)
- **Status**: ORPHANED ? check if active version in `tools/` is clean
- **Date**: 2025-12-27T13:43:00-05:00
- **Note**: Active `tools/encoding_report.ps1` may be clean; verify before use

---

## Invalid Receipt Quarantine (2025-12-26)

### Origin Event
- **Date**: 2025-12-26T20:45:53-05:00
- **Session**: `S_20251225T075155Z_STATE_RECORD`
- **Root Cause**: Receipt schema non-compliance (pre-v1, partial chain fields, missing base fields)

### Quarantine Structure
```
evidence/_quarantine/
??? legacy_pre_v1/          (old schema versions)
??? partial_chain_fields/   (incomplete chain metadata)
??? missing_base_field/     (required fields missing)
??? json_parse_error/       (cannot parse JSON)
??? other/                  (uncategorized)
```

### Statistics
- **Total Quarantined Receipts**: 42
- **Replacement Policy**: Receipts NOT recreated; evidence preserved as-is in quarantine
- **Philosophy**: *"You do not rewrite testimony. You change jurisdiction."*
- **Status**: ARCHIVED ? historical receipts preserved; future receipts must comply with current schema
- **Date**: 2025-12-26T20:45:53-05:00

---

## Tombstone Template (For Future Use)

```markdown
#### [filename]
- **Quarantine/Orphan Path**: [full path]
- **Reason**: [why quarantined/orphaned]
- **Replacement File**: [new file path or "None created"]
- **Status**: TOMBSTONED / ORPHANED / ARCHIVED
- **Date**: [YYYY-MM-DDTHH:MM:SS?HH:MM]
- **SID**: [Session ID if applicable]
- **Note**: [additional context]
```

---

## Usage Notes

**Adding Tombstones**: When quarantining files, append entry to appropriate section
**Never Remove**: Tombstone entries are permanent historical record
**Grep-Friendly**: Use `TOMBSTONED`, `ORPHANED`, `ARCHIVED` for status searches
**Forward Only**: If you need the functionality, recreate cleanly ? never restore corrupted originals

---

## Tombstone Entry 4: artisan_emit_anchors_map_ascii.py (False Positive)

**Date Quarantined**: 2025-12-28T01:39:02-05:00  
**Original Location**: `scripts/artisan_emit_anchors_map_ascii.py`  
**Quarantine Location**: `data/orphans/2025-12-28_false-positive-encoding/artisan_emit_anchors_map_ascii.py.QUARANTINED`  
**Reason**: Encoding audit flagged as suspicious (contains `\ufffd` replacement character)  
**Root Cause**: **FALSE POSITIVE** - Script intentionally contains replacement character to replace it in output  
**Restoration Policy**: **DO NOT RESTORE** - Sankofa Forward (recreate cleanly if needed)  
**Evidence**: `evidence/audits/ENCODING_AUDIT_20251228T063115Z.md`

---

## Tombstone Entry 5: encoding_audit.py (Archived - Contains Test Patterns)

**Date Archived**: 2025-12-28T01:39:02-05:00  
**Original Location**: `tools/encoding_audit.py`  
**Archive Location**: `archive/encoding_audit.py.ARCHIVED_2025-12-28_contains-test-patterns`  
**Reason**: Encoding audit flagged itself (contains ghost pattern regex and replacement char constant)  
**Root Cause**: **FALSE POSITIVE** - Script defines the patterns it searches for  
**Restoration Policy**: **ARCHIVE ONLY** - Keep for reference, recreate if needed  
**Evidence**: `evidence/audits/ENCODING_AUDIT_20251228T063115Z.md`

---

**END OF QUARANTINE TOMBSTONES LEDGER**
