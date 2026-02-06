# TMS (To My Son) Ingestion Guide

## Issue

Canon anchor `to_my_son_v1` has 0 chunks despite having a valid PDF (5.2 MB).

**Root cause:** Previous ingestion attempt failed because PyPDF/PyMuPDF was not installed.

**Evidence:**
```json
# From INGESTION_COMPLETED receipt:
"intent": "Completed ingestion: to_my_son_v1 (artifact only, pypdf missing)"
"chunk_count": 0
```

---

## Solution: STGRAIL-Aligned Ingestion

### Prerequisites

1. **Install PyMuPDF (if missing):**
```powershell
pip install PyMuPDF
```

2. **Verify PDF integrity:**
```powershell
# File exists at: anchors/canon/to_my_son/TMS.pdf
# Expected SHA256: 9a65b9221c7b025340cc93b17edaffa6fefb5686098f8a9f13983744771663a8
```

---

### Ingestion Process (RECORD State Required)

**Step 1: Enter RECORD State**
```powershell
.\tools\solob.ps1 record -note "ingest to_my_son_v1 PDF to resolve canon anchor without chunks"
```

**Step 2: Run Ingestion**
```powershell
python scripts/chunk_tms_pages_pilot.py
```

**Expected output:**
```
Extracting pages from anchors/canon/to_my_son/TMS.pdf...
Extracted N pages
Prepared N non-empty page chunks
Inserting N chunks...

[OK] OK: inserted N PDF page chunks for to_my_son_v1
[OK] OK: receipt written: evidence/<SID>/RECEIPTS/RECEIPT_CHUNKS_to_my_son_v1_PDF_PAGES_PILOT.json
```

**Step 3: Verify Chunks**
```powershell
python scripts/audit_anchor_coherence.py
```

**Expected:**
- `to_my_son_v1` should appear in "Canon anchors WITH chunks"
- Total chunk count should increase by N

**Step 4: Return to OBSERVE**
```powershell
.\tools\solob.ps1 observe -note "completed: to_my_son_v1 now has N chunks"
```

---

## Script Details

**File:** `scripts/chunk_tms_pages_pilot.py`

**What it does:**
1. Verifies PDF SHA256 matches manifest
2. Extracts text from each PDF page using PyMuPDF
3. Creates one chunk per non-empty page
4. Uses deterministic chunk IDs (namespace: `SOLOB|V2|CHUNK|PDF_PAGE|TO_MY_SON`)
5. Writes receipt to evidence/<SID>/

**Collision Protection:**
- Chunk IDs are based on: namespace + anchor_id + PDF SHA256 + page_number
- Pre-flight collision check before any inserts
- Atomic transaction (all-or-nothing)

**Truth Type:** `interpretive` (letter content is interpretive, not empirical)

---

## Troubleshooting

### If PyMuPDF is missing:
```
STOP: PyMuPDF (fitz) not available.
Install with: pip install PyMuPDF
```

**Solution:** Install PyMuPDF as shown in prerequisites

### If SHA256 mismatch:
```
STOP: PDF SHA256 mismatch.
Expected: 9a65b9221c7b025340cc93b17edaffa6fefb5686098f8a9f13983744771663a8
Actual:   <different hash>
```

**Solution:** PDF file has been modified. Verify integrity or update manifest.

### If already ingested:
```
STOP: chunk_id collision detected (N). Likely already ingested.
```

**Solution:** Chunks already exist. Run `python scripts/inspect_anchor_chunks.py --anchor to_my_son_v1` to verify.

---

## After Ingestion

The system should show:
- [OK] All 31 canon anchors have chunks
- [OK] No files with data but missing chunks
- [OK] Full proof harness passes

This completes the canon anchor coverage and resolves the "red issue" from the coherence audit.
