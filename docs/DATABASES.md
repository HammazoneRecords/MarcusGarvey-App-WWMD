# Data Stores and Databases

Overview of where data lives in **Whirlwind KB** and when to add or consolidate.

---

## Current Data Stores

### 1. **Testing Panel DB** (new)

| What | Where | Purpose |
|------|--------|--------|
| **DB** | `backend/data/testing_panel.db` (SQLite) | Persist testing checklist + notes server-side |
| **Schema** | `backend/data/testing_panel_schema.sql` | Table: `testing_panel_state` (storage_key, checked_json, notes_json, updated_at) |
| **API** | `GET /api/testing-panel?storage_key=...`, `POST /api/testing-panel` | Read/write state; frontend uses when `VITE_API_BASE_URL` is set, else localStorage |

Use this when the backend is running so checklist and notes are stored in one DB and can be shared or backed up.

---

### 2. **Frontend mock / Library data** (`db.json`)

| What | Where | Purpose |
|------|--------|--------|
| **Data** | `frontend/src/mock/db.json` | Static JSON: sources, facts, daily items, templates |
| **Usage** | `frontend/src/mock/data.ts` → `api.ts` (getFacts, getDailyItem, etc.) | Library, Home, Fact detail, Toolkit |

No real database; bundled with the app. Good for static content; not editable at runtime.

---

### 3. **RAG / Memory DB** (SQLite)

| What | Where | Purpose |
|------|--------|--------|
| **DB** | `backend/data/memory.db` | RAG spine: anchors, chunks, runs, citations |
| **Schema** | `backend/data/schema.sql` | anchors, chunks, provenance_notes, runs, run_citations |
| **Usage** | Backend RAG scripts, `GET /api/source/<anchor_id>` | Ingestion, retrieval, source viewer |

Source of truth for ingested documents and citations. Do not replace with JSON.

---

### 4. **WhirlwindDB node spec** (PostgreSQL-style, optional)

| What | Where | Purpose |
|------|--------|--------|
| **Schema** | `backend/migrations/001_whirlwinddb_node_specification.sql` | nodes, sources, claims, disputed_claims, actions, consequences, relationships, node_tags |
| **Usage** | Not wired yet; designed for a separate Postgres (or compatible) DB | Structured “nodes” (e.g. Marcus Garvey) with claims, sources, actions |

Conceptually aligns with Library content (facts = claims, sources = sources). Not required for current app unless you adopt a full node DB.

---

### 5. **Sessions (file vault)**

| What | Where | Purpose |
|------|--------|--------|
| **Files** | `sessions/` (project root), `backend/sessions/` | JSON session files (chat history, WWMD runs) |
| **API** | `GET /api/latest`, `/api/history`, `/api/session` | Read-only session listing and content |

File-based exchange, not a database. Fine for single-server; move to DB only if you need querying or multi-instance.

---

### 6. **Evidence / receipts (files)**

| What | Where | Purpose |
|------|--------|--------|
| **Files** | `backend/evidence/` (RECEIPTS, INDEX, bundles) | Ingestion receipts, audit trail |
| **Usage** | RAG pipeline, validation scripts | Provenance, not user-facing CRUD |

Keep as files; no need to put in SQLite.

---

### 7. **LocalStorage (frontend)**

| What | Where | Purpose |
|------|--------|--------|
| **Keys** | `{storageKey}:checked`, `{storageKey}:notes` | Testing panel checklist and notes |
| **Usage** | Testing panel when backend is not used | Fallback when no API; always written in addition to API when API is used |

Redundant with Testing Panel DB when backend is running; that’s intentional for offline/fallback.

---

## Do We Need More Databases?

- **No** for current scope. You have:
  - **Testing panel** → SQLite (`testing_panel.db`)
  - **RAG / citations** → SQLite (`memory.db`)
  - **Library/facts** → static `db.json` (could later move to a DB; see below)

---

## Consolidation Recommendations

1. **Testing panel**  
   - **Keep** the new Testing Panel DB and API.  
   - **Keep** localStorage as fallback when backend is unavailable.  
   - No consolidation needed.

2. **Library (facts/sources)**  
   - **Option A (minimal):** Leave as `db.json`. Easiest; no backend change.  
   - **Option B (single backend DB):** Add tables to `memory.db` (or a second SQLite) for sources + facts and add a small API; frontend calls it when `VITE_API_BASE_URL` is set.  
   - **Option C (full node model):** Stand up Postgres (or SQLite) with `001_whirlwinddb_node_specification.sql`, migrate facts/sources from `db.json` into nodes/sources/claims, and point the app at that DB.  

   Recommendation: stay with **Option A** until you need editable Library content or multi-app reuse; then move to B or C.

3. **Sessions**  
   - Keep as file vault unless you need search, retention, or multi-server. Then add a “sessions” table (e.g. in `memory.db`) or a dedicated DB and have the API read/write there instead of the vault.

4. **RAG (memory.db) vs WhirlwindDB spec**  
   - **Do not merge** RAG tables (anchors, chunks, runs) with the node spec (nodes, claims, actions). Different roles: RAG = ingestion and retrieval; node spec = structured biography/claims.  
   - You can have both: `memory.db` for RAG and, if you adopt it, a separate DB (or schema) for the node spec that the Library UI could use.

---

## Summary

| Store | Type | Consolidate? |
|-------|------|--------------|
| Testing Panel | SQLite `testing_panel.db` | No; use as-is with API + localStorage fallback. |
| Library (facts/sources) | `frontend/src/mock/db.json` | Optional later: move to SQLite/Postgres if you want editable or shared Library data. |
| RAG / citations | SQLite `memory.db` | No; keep separate from app/content DBs. |
| WhirlwindDB spec | Migration SQL only | Use only if you introduce a node/claims DB; keep separate from RAG. |
| Sessions | JSON files | Keep unless you need DB-backed sessions. |
| Evidence | Files | Keep as files. |
| LocalStorage | Browser | Keep as fallback for testing panel. |
