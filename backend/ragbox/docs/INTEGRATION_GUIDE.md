# RAGBox AI Integration Guide
**Instructions for the Operating AI**

**Version**: 1.0  
**Target Audience**: AI Agent taking ownership of this RAGBox

---

## 🛑 STOP & READ: Integration Requirements

You have received a portable RAG system ("RAGBox"). It contains the **core logic** and **templates**, but it is **NOT** configured for your specific environment yet.

Follow these steps to make it functional.

---

## 1. Create Required Directory Structure

You must create these directories in the `ragbox/` root to support the scripts:

```bash
ragbox/
├── anchors/           # [REQUIRED] Place source documents (PDFs) here
├── evidence/          # [REQUIRED] Audit reports will be generated here
├── tools/             # [REQUIRED] Place audit scripts here
└── utils/             # [REQUIRED] Helper scripts (sid.py is here)
```

**Instruction to AI**: Run `mkdir anchors evidence tools` immediately.

---

## 2. Install Critical Dependencies

The `requirements.txt` provided is minimal. You **MUST** add `PyMuPDF` if you plan to ingest PDFs.

**Instruction to AI**:
1.  Open `requirements.txt`.
2.  Add `pymupdf>=1.22.0`.
3.  Run `pip install -r requirements.txt`.

---

## 3. Create Custom Scripts

The included `ingest_marcus_unified.py` is a **TEMPLATE**. Do not run it blindly. You must create your own ingestion script tailored to your corpus.

### A. Create `scripts/ingest_my_corpus.py`

Create a new script based on `ingest_marcus_unified.py` but modify:

1.  **`MARCUS_PDFS` List**: Replace with your own list of files.
    ```python
    # REPLACE THIS:
    # MARCUS_PDFS = [...]
    
    # WITH THIS:
    MY_CORPUS = [
        ("doc_id_001", "my_document.pdf", "My Document Title"),
        # ...
    ]
    ```

2.  **Paths**: Update `MARCUS_BOX` variable to point to `ragbox/anchors/`.

3.  **Namespace**: Change `CHUNK_NAMESPACE_PREFIX` to match your project (e.g., `MYPROJECT|V1|CHUNK`).

---

## 4. Add Audit Tools (The "Prosecutor")

To verify your system integrity, you need the "Court Sweep" suite. These are NOT included by default to keep the box light, but are highly recommended.

**Instruction to AI**: Create or copy these files into `ragbox/tools/`:

1.  **`tools/court_sweep.py`**
    *   *Purpose*: Runs all system checks.
    *   *Source*: Ask user for the "Court Sweep" template.

2.  **`scripts/validate_receipt_v2.py`**
    *   *Purpose*: Validates ingestion receipts.
    *   *Source*: Ask user for the "V2 Receipt Validator".

3.  **`tools/validate_state_history_format.py`**
    *   *Purpose*: Ensures `docs/STATE_HISTORY.md` is valid.

---

## 5. Initialize State

The system prevents "silent mutation" by tracking session IDs.

**Instruction to AI**:
1.  Create `docs/STATE.json` with a dummy session ID if none exists:
    ```json
    {
      "active_session_id": "S_20250101T000000Z_INIT",
      "mode": "OBSERVE"
    }
    ```

---

## Summary Checklist for the Operating AI

- [ ] Created `anchors/` and `evidence/` folders.
- [ ] Added `pymupdf` to `requirements.txt`.
- [ ] Created `scripts/ingest_my_corpus.py` (customized from template).
- [ ] Created `docs/STATE.json`.
- [ ] (Optional) Added `tools/court_sweep.py` for verification.

**Status**: Once these are done, the RAGBox is live.
