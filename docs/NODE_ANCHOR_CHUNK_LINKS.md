# Linking Nodes to Accurate Sources and Chunks

Nodes (figures, movements, institutions) should point to **RAG anchors** (ingested documents) and **chunks** (exact text) so every claim is traceable to a real source.

---

## What Gets Linked

| Node schema | RAG (memory.db) | Purpose |
|-------------|-----------------|--------|
| **sources.anchor_id** | anchors.anchor_id | This “source” = this ingested document (e.g. Philosophy and Opinions). |
| **sources.anchor_locator** | — | Optional page/section (e.g. `pdf:page:0010`) when the source is a specific section. |
| **claims.chunk_id** | chunks.chunk_id | This claim is backed by this exact chunk. |
| **claim_chunk_citations** | chunks.chunk_id | One claim can cite many chunks. |
| **actions.chunk_id** | chunks.chunk_id | Optional chunk that documents the action. |

---

## Where RAG IDs Come From

- **anchor_id** – From ingestion: each PDF/book in `backend/anchors/canon/` is ingested and gets an `anchor_id` (e.g. `marcus_garvey_philosophy_opinions_amy_edit`). Stored in `memory.db` **anchors** and in evidence RECEIPTS (e.g. `RECEIPT_marcus_garvey_philosophy_opinions_amy_edit.json`).
- **chunk_id** – Each page/section becomes a row in **chunks** with a unique `chunk_id`. Your ingestion script (e.g. `ingest_marcus_unified.py`) generates these (e.g. `CHUNK|anchor_id|file_sha|page_num`).

To list anchors and chunks:

```bash
sqlite3 backend/data/memory.db "SELECT anchor_id, title FROM anchors;"
sqlite3 backend/data/memory.db "SELECT chunk_id, anchor_id, anchor_locator FROM chunks LIMIT 20;"
```

---

## Populating the Links

### 1. Map node sources to RAG anchors

When you insert (or migrate) **sources** in the node DB, set **anchor_id** (and optionally **anchor_locator**) from RAG:

- Use the same IDs you already have in `frontend/src/mock/db.json`: e.g. `src-pao-1923` has `anchorId: "marcus_garvey_philosophy_opinions_amy_edit"`. That string is the RAG **anchor_id**.
- So when creating a node source row for “Philosophy and Opinions, Vol. 1”, set:
  - `anchor_id = 'marcus_garvey_philosophy_opinions_amy_edit'`
  - `anchor_locator = NULL` (whole book) or e.g. `'pdf:page:0010'` for a specific page.

### 2. Map claims to chunks

For each **claim** (or action) that should be backed by exact text:

- Find the chunk(s) that contain that text in `memory.db`:
  - Query by content: `SELECT chunk_id, anchor_id, anchor_locator, content FROM chunks WHERE content LIKE '%Black Star Line%' LIMIT 5;`
  - Or use the receipt/locator from your RAG pipeline (e.g. page number → `anchor_locator` → chunk_id).
- Set **claims.chunk_id** to the primary backing chunk, and/or insert rows into **claim_chunk_citations** (claim_id, chunk_id) for multiple chunks.

### 3. Migrating from db.json

Today Library facts use **receiptIds** (source ids like `src-bsl-records`). Sources in db.json already have **anchorId** on some (e.g. Philosophy and Opinions, Message to the People). To move to nodes + RAG links:

1. Create one **node** (e.g. Marcus Garvey, id `WWD-CAR-1887-001`).
2. For each **source** in db.json: insert a row in node **sources** with the same title/author/year/url and set **anchor_id** = that source’s `anchorId` when present (otherwise leave NULL until you ingest that document).
3. For each **fact** in db.json: insert a **claim** linked to the node and to the corresponding source(s). Optionally set **chunk_id** (or rows in claim_chunk_citations) by looking up chunks in memory.db that contain the claim text or the cited page.

---

## Using the Links in the App

- **Source viewer:** When the UI shows a source, use **sources.anchor_id** (and **anchor_locator** if set) to call `GET /api/source/<anchor_id>?locator=...` and show the exact page/section from RAG.
- **Claim citation:** When showing a claim, use **claims.chunk_id** (or claim_chunk_citations) to fetch that chunk’s content from memory.db and display “Backed by: [excerpt]” or open the source viewer at that locator.

Once nodes point to anchors and chunks, you can drive accurate, citable UI from the node DB while still using RAG for retrieval and display.
