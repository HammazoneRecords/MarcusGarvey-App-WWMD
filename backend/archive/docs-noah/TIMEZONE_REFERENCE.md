# TIMEZONE REFERENCE
**Version:** 1.0  
**Status:** Active  
**Last Updated:** 2025-12-26

---

## Purpose

This document defines the timezone conventions used throughout the Solob Wrapper system and provides reference information for operators working in Kingston, Jamaica.

---

## Operator Timezone

**Location:** Kingston, Jamaica  
**Timezone:** UTC-5 (Eastern Standard Time)  
**Daylight Saving Time:** NOT observed  
**IANA Timezone:** `America/Jamaica`

### Conversion Examples

| Local Time (Kingston) | UTC Time | Format |
|----------------------|----------|--------|
| 2025-12-26T01:46:09-05:00 | 2025-12-26T06:46:09Z | ISO8601 |
| Dec 26, 2025 1:46 AM | Dec 26, 2025 6:46 AM | Human-readable |

**Quick conversion:**  
Local Time + 5 hours = UTC Time

---

## System Timezone Philosophy

### UTC-First Principle

> **All canonical timestamps MUST be stored in UTC.**

**Rationale:**
- UTC is timezone-independent
- No daylight saving time complications
- Unambiguous across geographic boundaries
- Sortable and comparable without conversion

### Where UTC is Required

**Mandatory UTC storage:**
- All receipt `timestamp_utc` fields
- All manifest `ts_utc` fields
- All session IDs (`S_<YYYYMMDDTHHMMSSZ>`)
- All database timestamp columns
- All evidence bundle timestamps
- All state transition records

**Format:** ISO8601 with `Z` suffix  
**Example:** `2025-12-26T06:46:09Z`

---

### Where Local Time is Acceptable

**Human-readable logs only:**
- `STATE_HISTORY.md` transition notes
- Console output during script execution
- Audit report summaries
- Debug logs

**Format:** ISO8601 with timezone offset  
**Example:** `2025-12-26T01:46:09-05:00`

**Rule:**  
Local timestamps are for **display only**, never for storage or comparison.

---

## Implementation Guidelines

### Python Code

**Correct (UTC):**
```python
from datetime import datetime, timezone

# For receipts, manifests, canonical timestamps
utc_now = datetime.now(timezone.utc)
utc_string = utc_now.strftime("%Y-%m-%dT%H:%M:%SZ")
# Result: "2025-12-26T06:46:09Z"
```

**Correct (Local for display):**
```python
# For human-readable logs only
local_now = datetime.now().astimezone()
local_string = local_now.isoformat(timespec="seconds")
# Result: "2025-12-26T01:46:09-05:00"
```

**Incorrect (timezone-naive):**
```python
# NEVER DO THIS - no timezone information
naive_now = datetime.now()  # [ERROR] WRONG
```

---

### PowerShell Scripts

**UTC timestamp:**
```powershell
$utc = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
# Result: "2025-12-26T06:46:09Z"
```

**Local timestamp:**
```powershell
$local = (Get-Date).ToString("yyyy-MM-ddTHH:mm:sszzz")
# Result: "2025-12-26T01:46:09-05:00"
```

---

## Receipt Schema Compliance

All receipts must include:

```json
{
  "timestamp_utc": "2025-12-26T06:46:09Z",
  "occurred_utc": "2025-12-26T06:46:09Z"
}
```

**Validation rules:**
- Must end with `Z` (UTC indicator)
- Must match pattern: `YYYY-MM-DDTHH:MM:SSZ`
- Must be exactly 64 characters for SHA256 hashes
- Must be sortable lexicographically

See [RECEIPT_SCHEMAS.md](./RECEIPT_SCHEMAS.md) for full schema.

---

## Common Pitfalls

### [ERROR] Pitfall 1: Storing Local Time
**Problem:** Storing `2025-12-26T01:46:09-05:00` in a receipt  
**Why it's wrong:** Receipts must be timezone-independent  
**Fix:** Convert to UTC before storage

### [ERROR] Pitfall 2: Timezone-Naive Datetime
**Problem:** Using `datetime.now()` without timezone  
**Why it's wrong:** Ambiguous, can't be compared reliably  
**Fix:** Always use `datetime.now(timezone.utc)` or `datetime.now().astimezone()`

### [ERROR] Pitfall 3: Comparing Mixed Timezones
**Problem:** Comparing UTC timestamp with local timestamp  
**Why it's wrong:** Will produce incorrect results  
**Fix:** Convert both to UTC before comparison

### [ERROR] Pitfall 4: Hardcoding Timezone Offset
**Problem:** Assuming `-05:00` everywhere  
**Why it's wrong:** Breaks if operator moves or DST changes  
**Fix:** Use `astimezone()` to get system timezone automatically

---

## Verification Checklist

When creating or modifying time-handling code:

- [ ] All canonical timestamps use UTC
- [ ] All datetime objects are timezone-aware
- [ ] Receipt timestamps end with `Z`
- [ ] Local time is only used for display
- [ ] No hardcoded timezone offsets
- [ ] ISO8601 format is used consistently
- [ ] Timestamp parsing validates timezone presence

---

## Related Documents

- [RECEIPT_SCHEMAS.md](./RECEIPT_SCHEMAS.md) ? Receipt timestamp requirements
- [v1-scope.md](./v1-scope.md) ? System conventions
- [WAI.md](../anchors/wrapper_anchor_invariants/WAI.md) ? Anchor invariants
- [STATE_TRANSITIONS.md](./STATE_TRANSITIONS.md) ? State discipline

---

## Audit Trail

**System Audit Date:** 2025-12-26  
**Audit Result:** [OK] PASS ? All scripts use UTC correctly  
**Audit Report:** [TIMEZONE_AUDIT_REPORT.md](./TIMEZONE_AUDIT_REPORT.md)

---

END OF TIMEZONE REFERENCE ? V1.0
