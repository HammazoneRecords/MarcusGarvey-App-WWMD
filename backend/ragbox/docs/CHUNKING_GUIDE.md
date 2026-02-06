# RAGBox Chunking Guide
**Production-Grade Ingestion Procedures**

**Version**: 1.0  
**Source**: Marcus Garvey App WWMD ARK System

---

## Overview

RAGBox now includes the **production-grade chunking scripts** used in the main ARK system. These allow you to ingest:

1.  **PDF Documents** (Page-level chunking with optional line-level splitting)
2.  **JSON Lexicons** (Structured data ingestion)
3.  **Unified Corpus** (Batch ingestion of multiple sources)

---

## Core Scripts

### 1. `register_anchors_from_registry.py`
**Purpose**: Registers source documents (anchors) into the database before chunking.
**Input**: `docs/ANCHOR_REGISTRY_PLAN.json` (You must create this file)
**Usage**:
```bash
python scripts/register_anchors_from_registry.py
```

### 2. `chunk_bos_pages_pilot.py` (PDF Chunking)
**Purpose**: specialized script for chunking PDF pages. 
**Logic**: 
- Extracts text from PDF pages
- Creates Parent Chunks (one per page)
- Creates Line Chunks (splitting page content by newline)
**Usage**:
```bash
python scripts/chunk_bos_pages_pilot.py
```

### 3. `import_lexicon_chunks_v1_1.py` (JSON Lexicon)
**Purpose**: Ingests structured JSON data (e.g., dictionary, glossary).
**Logic**:
- Reads JSON file
- Creates chunks based on items/definitions
- Derives "Row Index" for precise verification
**Usage**:
```bash
python scripts/import_lexicon_chunks_v1_1.py
```

### 4. `ingest_marcus_unified.py` (Unified Pipeline)
**Purpose**: Orchestrates the entire ingestion process for the Marcus Garvey corpus.
**Flow**:
1. Checks pre-flight conditions
2. Registers anchors
3. runs PDF ingestion
4. runs Lexicon ingestion
5. Generates evidence bundles
**Usage**:
```bash
python scripts/ingest_marcus_unified.py
```

---

## Setup Requirements

To use these production scripts, you typically need to set up the following directory structure in your `ragbox` (or project root):

1.  **`docs/ANCHOR_REGISTRY_PLAN.json`**:
    A JSON file listing all documents to be ingested.
    ```json
    {
      "anchors": [
        {
          "anchor_id": "doc_001",
          "title": "My Document",
          "author": "Author Name",
          "year": 2025,
          "source_type": "pdf",
          "rel_path": "data/corpus/my_doc.pdf"
        }
      ]
    }
    ```

2.  **`data/corpus/`**:
    Directory containing your actual source files (PDFs, JSONs).

---

## Customizing for Your Data

These scripts are tuned for the Marcus Garvey corpus. To use them for your own data:

1.  **Edit `chunk_bos_pages_pilot.py`**:
    - Change the `PDF_PATH` variable to point to your PDF.
    - Adjust regex patterns if your PDF has specific headers/footers to ignore.

2.  **Edit `import_lexicon_chunks_v1_1.py`**:
    - Change the input JSON path.
    - map your JSON fields to the `content` column of the `chunks` table.

3.  **Edit `ingest_marcus_unified.py`**:
    - Update the list of scripts it calls or the paths it verifies.

---

## Troubleshooting

-   **"File not found"**: Ensure `data/corpus/` exists and contains your files.
-   **"Anchor not found"**: Run `register_anchors_from_registry.py` first.
-   **"Import session error"**: Ensure you have a valid `import_session_id` (the scripts generate one automatically, but check if they rely on a specific environment variable).

