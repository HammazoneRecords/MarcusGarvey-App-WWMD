# TMS Ingestion Workflow (STGRAIL-Compliant)

## Pre-Flight Verified [OK]

**Anchor:** `to_my_son_v1`  
**Source:** `anchors/canon/to_my_son/TMS.pdf`  
**Status:** Registered in DB, file exists (5.26 MB), 0 chunks  
**SHA256:** (computed in step 2 below)

---

## Step-by-Step Execution

### 1. Fix PowerShell Encoding

```powershell
$OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
```

### 2. Verify PDF SHA256

```powershell
certutil -hashfile anchors\canon\to_my_son\TMS.pdf SHA256
```

**Copy the 64-character hex hash.** Use this in payload files below.

### 3. Enter RECORD State

```powershell
.\tools\solob.ps1 record -note "ingest: fix unchunked canon anchor to_my_son_v1 (TMS.pdf)"
```

### 4. Emit INGESTION_STARTED Receipt

Create `payload_tms_ingestion_started.json`:
```json
{
  "anchor_id": "to_my_son_v1",
  "source_artifact": {
    "path": "anchors/canon/to_my_son/TMS.pdf",
    "sha256": "PASTE_REAL_SHA256_HERE"
  }
}
```

Emit receipt:
```powershell
python scripts/emit_receipt.py `
  --type INGESTION_STARTED `
  --intent "Start ingestion for to_my_son_v1 to resolve canon anchor with 0 chunks" `
  --file payload_tms_ingestion_started.json
```

### 5. Run TMS Ingestion

```powershell
python scripts/chunk_tms_pages_pilot.py
```

**Expected output:**
- "Extracting pages from..."
- "Extracted N pages"
- "Prepared N non-empty page chunks"
- "Inserting N chunks..."
- "[OK] OK: inserted N PDF page chunks for to_my_son_v1"

### 6. Verify Chunk Count

```powershell
python -c "import sqlite3; c=sqlite3.connect('data/memory.db'); print(c.execute(\"select count(*) from chunks where anchor_id='to_my_son_v1'\").fetchone()[0])"
```

**Note the number** (e.g., 312) for the next step.

### 7. Emit INGESTION_COMPLETED Receipt

Create `payload_tms_ingestion_completed.json`:
```json
{
  "anchor_id": "to_my_son_v1",
  "source_artifact": {
    "path": "anchors/canon/to_my_son/TMS.pdf",
    "sha256": "PASTE_REAL_SHA256_HERE"
  },
  "output_artifacts": [],
  "stats": {
    "chunks_count": 312
  }
}
```

**Replace `312` with actual count from step 6.**
**Replace `PASTE_REAL_SHA256_HERE` with hash from step 2.**

Emit receipt:
```powershell
python scripts/emit_receipt.py `
  --type INGESTION_COMPLETED `
  --intent "Completed ingestion for to_my_son_v1; canon anchor now chunked" `
  --file payload_tms_ingestion_completed.json
```

### 8. Victory Lap - Re-Audit

```powershell
python scripts/audit_anchor_coherence.py
```

**Expected:**
- [OK] Canon anchors WITHOUT chunks: 0
- [OK] Total chunks: 2,999 + N (increased)
- [OK] All 31 canon anchors have chunks

### 9. Return to OBSERVE

```powershell
.\tools\solob.ps1 observe -note "complete: to_my_son_v1 ingested; coherence restored (31/31 chunked)"
```

---

## Success Criteria

[OK] All 31 canon anchors have chunks  
[OK] to_my_son_v1 has N chunks (one per PDF page)  
[OK] INGESTION_STARTED receipt exists  
[OK] INGESTION_COMPLETED receipt exists  
[OK] Coherence audit shows 0 canon anchors without chunks  

---

## Troubleshooting

### If PyMuPDF missing:
```powershell
pip install PyMuPDF
```

### If SHA256 mismatch:
Update `MANIFEST_ENTRY_SHA256` in `scripts/chunk_tms_pages_pilot.py` with real hash from step 2.

### If already ingested:
Check for collision error. Verify with:
```powershell
python scripts/_inspect_anchor.py --anchor-id to_my_son_v1
```

---

**Ready to execute when you're in RECORD state.**
