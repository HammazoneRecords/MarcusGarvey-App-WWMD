# Source Access Plan: Popup + Actual Section

**Goal:** Ensure "Access Source" links to the real source and, where possible, show the file in a popup with the **actual section** (page or line) in view.

---

## 1. Current State

| Layer | What exists today |
|-------|-------------------|
| **Frontend** | `SourceItem` shows title, author, year, excerpt; "Access Source" button has **no href or onClick**. |
| **Types** | `SourceRef`: `id`, `title`, `author`, `year`, `url?`, `page?`, `excerpt?`, `type`. No `locator` for section-level targeting. |
| **Mock data** | `db.json` sources have `url` (often `#` or archive.org). No link to backend anchors or chunks. |
| **Backend** | RAG returns receipts with `anchor_id`, `line_locator` (e.g. `pdf:page:0010`), `line_content`. Chunks in SQLite: `anchor_id`, `anchor_locator`, `content`. Anchors table: `anchor_id`, `title`, `canonical_path`. |
| **Evidence** | Receipt JSONs under `evidence/.../RECEIPTS/` reference `anchor_id` and `source_path`; chunks are queryable by `anchor_id` + `anchor_locator`. |

So: we have the **data** (anchor + locator + content) on the backend, but the frontend does not yet (1) link "Access Source" to anything, or (2) show the actual section in a popup.

---

## 2. Desired Behavior

- **External URL** (e.g. archive.org): "Access Source" opens the URL in a new tab (or optionally in an iframe inside a modal).
- **Internal source** (anchor in our DB, e.g. from WWMD/Library): "Access Source" opens a **popup/modal** that:
  - Shows **source metadata** (title, author, year).
  - Shows the **actual section** (the page or line that backs the claim):
    - Either **fetched text** for that `anchor_id` + `locator` (from chunks/line_chunks), with the relevant sentence/paragraph emphasized or scrolled into view,  
    - Or a **link to open the PDF** at that page (if we serve or deep-link PDFs later).
- **Fallback:** If we only have an excerpt (no backend), show the excerpt in the modal and, if present, a "Open full source" link using `url`.

---

## 3. Data Model Changes

### 3.1 Frontend: Extend `SourceRef`

Add optional fields so we can request the right section from the backend and open external links:

```ts
// In frontend/src/types/index.ts
export interface SourceRef {
  id: string;
  title: string;
  author: string;
  year: number;
  url?: string;           // External link (archive.org, etc.)
  page?: string;          // Display only (e.g. "10")
  excerpt?: string;      // Quote already shown
  type: SourceType;
  // New (optional): for internal sources — backend can return content for this section
  locator?: string;      // e.g. "pdf:page:0010" — matches backend anchor_locator
  anchorId?: string;     // backend anchor_id (same as id when from RAG)
}
```

- **Library / mock facts:** Keep `id`, `url`, `excerpt`; add `locator`/`anchorId` when we have a mapping from source id → anchor (or when we move to API-backed facts).
- **WWMD receipts:** Backend already returns `id` (anchor_id), `page` (from line_locator), `excerpt` (line_content). Extend backend response to also send `locator` (e.g. `pdf:page:0010`) so the frontend can call the new "get section" API.

### 3.2 Backend: No schema change

We already have:

- `anchors`: `anchor_id`, `title`, `canonical_path`, …
- `chunks`: `anchor_id`, `anchor_locator`, `content`
- `line_chunks`: finer granularity with `anchor_locator`, `content`

We only add an **API** that reads from these tables.

---

## 4. Backend: Source Content API

### 4.1 Endpoint

- **GET** `/api/source/<anchor_id>`  
  - Query params: `locator` (optional). Example: `locator=pdf:page:0010`.

### 4.2 Behavior

1. **Resolve anchor:** Look up `anchors` by `anchor_id`; if not found, return 404.
2. **Get section content:**
   - If `locator` is provided: query `chunks` (or `line_chunks` if we want line-level) where `anchor_id = ?` and `anchor_locator = ?`; return that chunk’s `content` as the "section" text.
   - If `locator` is omitted: return the first chunk (or concatenate all chunks) for that anchor as "full document" preview (optional; we can limit size).
3. **Response JSON:**

```json
{
  "anchorId": "marcus_garvey_selected_writings",
  "title": "Selected Writings and Speeches of Marcus Garvey",
  "locator": "pdf:page:0010",
  "sectionContent": "… text for that page …",
  "pageLabel": "10",
  "canonicalPath": "anchors/canon/Marcus BOX/..."
}
```

- Do **not** stream raw PDF bytes from this endpoint; serve **extracted text** only. PDF download/view can be a separate endpoint or static file later.

### 4.3 Implementation details

- Reuse existing DB path (e.g. `backend/data/memory.db`) and the same `anchors` / `chunks` (and optionally `line_chunks`) schema.
- Optional: also return a **list of locators** for that anchor (e.g. all `anchor_locator` values) so the frontend can offer "Jump to page" in the modal later.

---

## 5. Frontend: Popup and "Access Source" Wiring

### 5.1 Source viewer modal

- **Component:** e.g. `SourceViewerModal.tsx` (in `components/facts/` or `components/ui/`).
- **Props:** `source: SourceRef`, `open: boolean`, `onClose: () => void`.
- **Behavior:**
  - If `source.url` is present and is external (http/https) and we are **not** using an internal anchor:
    - Show metadata + excerpt in modal; button "Open full source" → `window.open(source.url)`.
  - If we have `source.anchorId` (or `source.id` mapped to anchor) and/or `source.locator`:
    - On open, call **GET** `/api/source/<anchorId>?locator=<locator>`.
    - Show metadata + **section content** (or "Loading…" then content). Optionally highlight or scroll to the sentence that matches `source.excerpt` (e.g. simple string index or highlight with `<mark>`).
  - If we only have `excerpt` and no URL / no anchor:
    - Show metadata + excerpt only; no "Open full source" if no `url`.

### 5.2 Wire "Access Source" in `SourceItem`

- **Click** "Access Source":
  - If `source.url` and it’s external and we don’t have anchor content to show: open `source.url` in a new tab (current behavior can stay as fallback).
  - Else: open `SourceViewerModal` with this `source` (and let the modal decide whether to fetch section or show excerpt + link).

So: **either** new tab for plain URL **or** modal with section content (or excerpt fallback).

### 5.3 Where `SourceItem` is used

- **FactDetail:** receipts under a fact → each receipt is a `SourceItem`; "Access Source" opens modal or URL.
- **ResponseView (WWMD):** receipts for the lens response → same.

Ensure both pass the same `SourceRef` (including `locator`/`anchorId` when backend sends them).

---

## 6. Backend: Return `locator` in WWMD receipts

In `wwmd_ask_hybrid.py` (or wherever WWMD receipts are built), add `locator` to each receipt so the frontend can call `/api/source/<id>?locator=...`:

```python
receipts.append({
    "id": r['anchor_id'],
    "title": f"Source {r['anchor_id']}",
    "type": "archive",
    "excerpt": r['line_content'],
    "year": 1920,
    "page": r['line_locator'].split(':')[-1] if ':' in r['line_locator'] else "0",
    "locator": r['line_locator']   # e.g. "pdf:page:0010"
})
```

Frontend types already have `page` and `excerpt`; add `locator` (and optionally `anchorId`; can be same as `id`).

---

## 7. Implementation Order

| Step | Task | Owner |
|------|------|--------|
| 1 | Extend `SourceRef` with `locator?`, `anchorId?` in `frontend/src/types/index.ts`. | Frontend |
| 2 | Add **GET** `/api/source/<anchor_id>?locator=...` in backend (Flask); query chunks/anchors; return JSON above. | Backend |
| 3 | Add `locator` (and if needed `anchorId`) to WWMD receipt payload in `wwmd_ask_hybrid.py`. | Backend |
| 4 | Create `SourceViewerModal`: show metadata; if anchor+locator → fetch and show `sectionContent`; else if url → show excerpt + "Open full source"; else excerpt only. | Frontend |
| 5 | In `SourceItem`, add onClick: open modal (or new tab for external-only URL). Pass `source` into modal. | Frontend |
| 6 | (Optional) In modal, highlight or scroll to the sentence matching `excerpt` in the section text. | Frontend |
| 7 | (Optional) Serve PDF for download or "Open PDF at page" using `canonicalPath` or a safe static route. | Backend + Frontend |

---

## 8. Acceptance Criteria

- **External source:** Clicking "Access Source" for a source with a valid `url` opens that URL (new tab or via modal link).
- **Internal source (WWMD):** For a receipt that has `locator` (and anchor), clicking "Access Source" opens a popup that shows the **actual section text** from the backend for that anchor + locator.
- **Library / mock:** For facts that only have excerpt and no backend anchor yet, "Access Source" at least opens a modal with the excerpt and, if `url` exists, a link to the full source.
- **No regression:** Existing Library and WWMD pages still render; missing `locator`/anchor is handled gracefully (excerpt-only or URL-only behavior).

---

## 9. Files to Touch (Summary)

| File | Change |
|------|--------|
| `frontend/src/types/index.ts` | Add `locator?`, `anchorId?` to `SourceRef`. |
| `frontend/src/components/facts/SourceItem.tsx` | Add click handler; open modal or new tab. |
| `frontend/src/components/facts/SourceViewerModal.tsx` | **New.** Modal with metadata, fetch section or show excerpt/URL. |
| `frontend/src/services/api.ts` | Add `getSourceSection(anchorId, locator?)` → GET `/api/source/...`. |
| `backend/api/server.py` | Register GET `/api/source/<anchor_id>`, query DB, return JSON. |
| `backend/ragbox/scripts/wwmd_ask_hybrid.py` | Add `locator` (and optionally `anchorId`) to each receipt. |

Optional: `FactDetail.tsx` / `ResponseView.tsx` — only if we need to lift modal state (e.g. one shared modal at layout level); otherwise modal state can live in `SourceItem` or a small context.

---

This plan gets "Access Source" to point to the real source and, for internal anchors, to show the actual section in a popup. External links continue to work; internal ones gain a section-level view backed by the existing chunk store.
