# Ghost File Quarantine Protocol

## Principle

**"Never delete. Always quarantine with evidence."**

Files that shouldn't exist must be:
1. **Moved** to `data/orphans/` (not deleted)
2. **Renamed** with quarantine metadata
3. **Documented** in a quarantine receipt

This preserves audit trail and allows recovery if the "ghost" was actually valid.

---

## Process: Quarantine Ghost DB File

### Step 1: Verify Ghost Status

```powershell
# Check if file exists
Test-Path data\solob.db

# Get file info
Get-Item data\solob.db | Format-List
```

### Step 2: Create Quarantine Receipt (Before Moving)

**File:** `evidence/<SID>/RECEIPTS/QUARANTINE_solob_db.json`

```json
{
  "receipt_type": "FILE_QUARANTINED",
  "receipt_version": "V1",
  "timestamp_utc": "<ISO8601>",
  "session_id": "<current SID>",
  "intent": "Quarantine ghost database file (empty, no code references)",
  "file": {
    "original_path": "data/solob.db",
    "quarantine_path": "data/orphans/solob_GHOST_<timestamp>.db",
    "sha256": "<file hash>",
    "size_bytes": "<size>",
    "reason": "Empty database with no code references; canonical DB is memory.db"
  },
  "analysis": {
    "code_references": 0,
    "tables_count": 0,
    "canonical_db": "data/memory.db",
    "safe_to_quarantine": true
  }
}
```

### Step 3: Move to Orphans

```powershell
# Get timestamp for quarantine filename
$timestamp = Get-Date -Format "yyyyMMddTHHmmssZ" -AsUTC

# Move file to orphans with metadata
Move-Item data\solob.db `
  data\orphans\solob_GHOST_$timestamp.db
```

### Step 4: Verify Quarantine

```powershell
# Verify original is gone
Test-Path data\solob.db  # Should be False

# Verify orphan exists
Test-Path data\orphans\solob_GHOST_*.db  # Should be True

# List orphaned file
Get-ChildItem data\orphans\solob_GHOST_*.db
```

---

## Why This Matters

### [ERROR] Deletion (Wrong)
```powershell
Remove-Item data\solob.db  # No trail, no recovery
```

**Problems:**
- No evidence of what was deleted
- Can't verify it was actually empty
- Can't recover if it was needed
- Breaks audit chain

### [OK] Quarantine (Correct)
```powershell
# 1. Document
emit_receipt QUARANTINE_solob_db.json

# 2. Move (preserves file)
Move-Item data\solob.db data\orphans\solob_GHOST_<timestamp>.db

# 3. Verify
Test-Path data\solob.db  # False, as expected
```

**Benefits:**
- [OK] File preserved (can recover if needed)
- [OK] Receipt documents why it was quarantined
- [OK] Timestamp in filename shows when
- [OK] Audit trail complete

---

## Retroactive Fix (If Already Deleted)

If `solob.db` was already deleted without evidence:

**Create deletion confession receipt:**

```json
{
  "receipt_type": "FILE_DELETED_UNWITNESSED",
  "receipt_version": "V1",
  "timestamp_utc": "<when discovered>",
  "session_id": "<current SID>",
  "confession": {
    "file_path": "data/solob.db",
    "what_happened": "File was deleted without quarantine receipt",
    "when_deleted": "<approximate time>",
    "by_whom": "operator error during cleanup",
    "was_recoverable": false,
    "known_state_before_deletion": {
      "tables_count": 0,
      "size_bytes": "unknown",
      "code_references": 0
    }
  },
  "corrective_action": "Created this confession receipt to preserve audit trail",
  "future_prevention": "Always use quarantine protocol from docs/GHOST_FILE_QUARANTINE.md"
}
```

---

## Orphans Directory Structure

```
data/orphans/
??? README.md                          # Explains orphan quarantine
??? solob_GHOST_20251226T230000Z.db   # Quarantined ghost DB
??? backup_<old_timestamp>.db          # Old backups
??? <filename>_REASON_<timestamp>.ext  # Other quarantined files
```

**Naming convention:**
```
<original_name>_<REASON>_<timestamp>.<ext>

Reasons:
- GHOST: File that shouldn't exist
- CORRUPT: Damaged file
- DUPLICATE: Redundant copy
- STALE: Out-of-date backup
```

---

## Prevention

**Update cleanup scripts to use quarantine:**

```python
# DON'T:
os.remove("data/solob.db")

# DO:
import shutil
from datetime import datetime

def quarantine_file(filepath, reason="GHOST"):
    """Move file to orphans with metadata."""
    timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    filename = Path(filepath).name
    stem = Path(filepath).stem
    ext = Path(filepath).suffix
    
    quarantine_name = f"{stem}_{reason}_{timestamp}{ext}"
    quarantine_path = Path("data/orphans") / quarantine_name
    
    shutil.move(filepath, quarantine_path)
    return quarantine_path
```

---

## Summary

**Golden Rule:** Files don't disappear. They move to orphans.

1. **Before moving:** Create quarantine receipt
2. **Move:** Use descriptive rename (reason + timestamp)
3. **After moving:** Verify both absence and presence
4. **Document:** Why it was quarantined (receipt)

**"Evidence of absence is not absence of evidence."**  
Even ghost files leave traces when properly quarantined.
