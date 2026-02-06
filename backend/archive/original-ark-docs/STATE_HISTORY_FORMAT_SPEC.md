# STATE_HISTORY Format Specification

**Version**: 1.0  
**Last Updated**: 2025-12-28T10:00:00-05:00  
**Status**: CANONICAL

---

## Purpose

This document defines the **canonical format** for `docs/STATE_HISTORY.md`, the append-only log of all state transitions in the Solob Wrapper system. This specification ensures:

- **Traceability**: Every state change is documented with timestamp, transition, and rationale
- **Witness Integrity**: Post-epoch transitions carry Session ID (SID) markers
- **Append-Only Discipline**: History is never edited, only extended
- **Machine Parsability**: Consistent format enables automated validation

---

## File Header

### Required Header Section

```markdown
# STATE_HISTORY.md (append-only)

Every time you change STATE.json, you also append:

timestamp

from -> to

who

reason (one line)
```

**Rules**:
- File MUST start with `# STATE_HISTORY.md (append-only)` heading
- Header provides human-readable instructions for manual entries
- Instructions remain stable across all versions

---

## Witness Epoch Declaration

### Required Section (Post-Epoch)

```markdown
## WITNESS EPOCH

The "Witness Epoch" marks the point where every state transition began to be automatically tagged with a canonical session ID (`sid=...`). Earlier entries may lack this field as the witness system was introduced mid-project.

Witness Epoch: 2025-12-25T07:51:59Z
WITNESS_EPOCH_START: 2025-12-25T07:51:59Z

### SID Witness Policy
1. Transition notes must include the canonical SID that witnessed the window.
2. The SID is generated during transition to `RECORD`.
3. The same SID is logged during the transition back to `OBSERVE` to seal the window.

### Verification Helper
To find transition lines after the epoch start that lack a SID witness:
`.\\tools\\verify_witness_epoch.ps1`
```

**Rules**:
- MUST appear after header, before first transition entry
- `Witness Epoch:` line is required for Python validator compatibility
- `WITNESS_EPOCH_START:` preserves legacy format
- Both timestamps MUST be identical and in UTC (ISO8601 with `Z` suffix)
- SID Witness Policy section documents the governance rules
- Verification helper reference enables self-audit

---

## State Transition Entry Format

### Standard Format (Post-Epoch)

```
- YYYY-MM-DDTHH:MM:SS-05:00 (UTC YYYY-MM-DDTHH:MM:SSZ) - FROM -> TO - reason text (sid=S_TIMESTAMP_DESCRIPTOR)
```

**Components**:

1. **Bullet Point**: Line MUST start with `- ` (dash + space)
2. **Local Timestamp**: ISO8601 with Kingston offset (`-05:00`)
3. **UTC Timestamp**: In parentheses, prefixed with `(UTC `, suffixed with `Z)`
4. **Transition**: `FROM -> TO` where FROM and TO are valid state names
5. **Separator**: ` - ` (space-dash-space) after UTC timestamp
6. **Reason**: Human-readable note explaining the transition
7. **SID Marker**: `(sid=S_TIMESTAMP_DESCRIPTOR)` at end of line (post-epoch only)

**Example**:
```
- 2025-12-28T09:26:00-05:00 (UTC 2025-12-28T14:26:00Z) - OBSERVE -> RECORD - Quick win: implement mw lint bundles (sid=S_20251225T075155Z_STATE_RECORD)
```

### Legacy Format (Pre-Epoch)

Pre-epoch entries MAY use various formats, including:
- Verbose multi-line sections with `##` headings
- Single-line entries without SID markers
- Different timestamp formats

**Legacy entries are preserved as-is** and documented in `STATE_HISTORY_LEGACY_SID_ADDENDUM.json`.

### Special Entry: NOTE Lines

```
- YYYY-MM-DDTHH:MM:SS-05:00 (UTC YYYY-MM-DDTHH:MM:SSZ)  NOTE  descriptive text
```

NOTE lines document important events that are not state transitions (e.g., epoch milestones, addendum references).

**Example**:
```
- 2025-12-25T16:06:00-05:00 (UTC 2025-12-25T21:06:00Z)  NOTE  SID Witness enforcement began on 2025-12-25. Transitions prior to this are documented in docs/STATE_HISTORY_LEGACY_SID_ADDENDUM.json.
```

---

## Valid State Names

The following state names are recognized:

- `OBSERVE` ? Read-only, no writes allowed (default safe state)
- `RECORD` ? Write-enabled, witnessed execution
- `EXECUTE` ? Active execution state (variant of RECORD)
- `REPAIR` ? Corrective action state

**Transitions**:
- `OBSERVE -> RECORD` ? Open write window
- `RECORD -> OBSERVE` ? Seal write window
- `OBSERVE -> EXECUTE` ? Special execution mode
- `OBSERVE -> REPAIR` ? Special repair mode
- `OBSERVE -> OBSERVE` ? No-op seal (historical artifact)

---

## Timestamp Requirements

### Local Time
- **Format**: `YYYY-MM-DDTHH:MM:SS-05:00`
- **Timezone**: Kingston, Jamaica (UTC-5, no DST)
- **Offset**: Always `-05:00`

### UTC Time
- **Format**: `YYYY-MM-DDTHH:MM:SSZ`
- **Suffix**: Always `Z` (Zulu time)
- **Placement**: In parentheses after local time: `(UTC ...)`

### Offset Calculation
Local time + 5 hours = UTC time

**Example**:
- Local: `2025-12-28T09:26:00-05:00`
- UTC: `2025-12-28T14:26:00Z`

---

## SID Marker Format

### Structure
```
(sid=S_TIMESTAMP_DESCRIPTOR)
```

**Components**:
- Prefix: `(sid=`
- SID Format: `S_<UTC_TIMESTAMP>_<DESCRIPTOR>`
- Timestamp: Compact UTC format (e.g., `20251225T075155Z`)
- Descriptor: Human-readable label (e.g., `STATE_RECORD`, `MONK`, `INGEST_PILOT`)
- Suffix: `)`

**Examples**:
- `(sid=S_20251225T075155Z_STATE_RECORD)`
- `(sid=S_20251221T201619Z_MONK)`
- `(sid=S_20251222T224740Z_INGEST_PILOT)`

### SID Witness Policy

**Post-Epoch (After 2025-12-25T07:51:59Z)**:
- Every state transition MUST include a SID marker
- Transitions without SID markers are **policy violations**
- Validator: `tools/verify_witness_epoch.py` (or `.ps1`)

**Pre-Epoch**:
- SID markers are optional
- Pre-epoch transitions documented in legacy addendum

---

## Append-Only Discipline

### Rules

1. **Never Edit**: Historical entries are NEVER modified
2. **Never Delete**: Historical entries are NEVER removed
3. **Only Append**: New entries added to end of file
4. **Corrections**: Errors corrected via new NOTE entries, not edits

### Rationale

- **Immutability**: History must be tamper-evident
- **Auditability**: All changes have a trail
- **Forensics**: Even mistakes become evidence

---

## Validation

### Automated Validators

**Witness Epoch Compliance**:
```bash
python tools/verify_witness_epoch.py --state-history docs/STATE_HISTORY.md
```

**Exit Codes**:
- `0` ? All post-epoch transitions have SID markers
- `2` ? Violations found
- `3` ? File missing or parsing error

### Manual Review

**Checklist**:
- [ ] All post-epoch entries have SID markers
- [ ] Timestamps are properly formatted (local + UTC)
- [ ] State names are valid
- [ ] Transitions use `->` separator (not Unicode arrows)
- [ ] No encoding artifacts (mojibake, smart quotes)

---

## Common Pitfalls

### [ERROR] Invalid: Unicode Arrow
```
- 2025-12-28T09:26:00-05:00 (UTC 2025-12-28T14:26:00Z) - OBSERVE -> RECORD
```

### [OK] Valid: ASCII Arrow
```
- 2025-12-28T09:26:00-05:00 (UTC 2025-12-28T14:26:00Z) - OBSERVE -> RECORD
```

### [ERROR] Invalid: Missing SID (Post-Epoch)
```
- 2025-12-28T09:26:00-05:00 (UTC 2025-12-28T14:26:00Z) - OBSERVE -> RECORD - work done
```

### [OK] Valid: SID Present
```
- 2025-12-28T09:26:00-05:00 (UTC 2025-12-28T14:26:00Z) - OBSERVE -> RECORD - work done (sid=S_20251225T075155Z_STATE_RECORD)
```

---

## Encoding Safety

### Requirements

- **File Encoding**: UTF-8 without BOM
- **Line Endings**: CRLF (Windows) or LF (Unix) ? both acceptable
- **Separators**: ASCII-safe only (no em-dashes, curly quotes, Unicode arrows)

### Tools

**Encoding Audit**:
```powershell
.\tools\encoding_report.ps1
```

**Expected**: 0 encoding issues in `docs/STATE_HISTORY.md`

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-12-28 | Initial specification based on current STATE_HISTORY.md format |

---

## Related Documents

- `docs/STATE_HISTORY.md` ? The canonical state history log
- `docs/STATE_HISTORY_LEGACY_SID_ADDENDUM.json` ? Pre-epoch transition records
- `docs/STATE.json` ? Current system state
- `docs/TIMEZONE_REFERENCE.md` ? Timezone handling conventions
- `tools/verify_witness_epoch.py` ? SID compliance validator

---

END OF SPECIFICATION
