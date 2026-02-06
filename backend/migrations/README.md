# WhirlwindDB Migrations

PostgreSQL (or SQLite) migrations for the Node Specification schema. Use when you add a node backend so nodes point to accurate RAG sources and chunks.

## Running migrations (PostgreSQL)

1. Ensure PostgreSQL 12+ is running.
2. Create a database and (optional) schema:
   ```sql
   CREATE DATABASE whirlwinddb;
   -- Optional: CREATE SCHEMA whirlwind;
   ```
3. Run in order:
   ```bash
   psql -d whirlwinddb -f 001_whirlwinddb_node_specification.sql
   psql -d whirlwinddb -f 002_whirlwinddb_anchor_chunk_links.sql
   ```

## Running migrations (SQLite)

If you keep nodes in SQLite (e.g. same DB as RAG or a separate `nodes.db`):

```bash
sqlite3 nodes.db < 001_whirlwinddb_node_specification.sql
sqlite3 nodes.db < 002_whirlwinddb_anchor_chunk_links_sqlite.sql
```

Run each file once; omit the SQLite 002 file if you already added the anchor/chunk columns.

## Files

- `001_whirlwinddb_node_specification.sql` – Nodes, claims, sources, actions, relationships (append-only, provenance-first).
- `002_whirlwinddb_anchor_chunk_links.sql` – **Postgres:** sources.anchor_id / anchor_locator; claims.chunk_id; claim_chunk_citations; actions.chunk_id.
- `002_whirlwinddb_anchor_chunk_links_sqlite.sql` – **SQLite:** same columns/tables for linking nodes to RAG anchors and chunks.

## Linking nodes to RAG

- **sources.anchor_id** = `anchor_id` from `memory.db` anchors (e.g. `marcus_garvey_philosophy_opinions_amy_edit`). Use this so each node source points to an ingested document.
- **sources.anchor_locator** = optional page/section (e.g. `pdf:page:0010`) when the source is a specific section.
- **claims.chunk_id** = `chunk_id` from `memory.db` chunks so each claim cites the exact chunk that backs it.
- **claim_chunk_citations** = use when one claim is backed by multiple chunks (e.g. one chunk per sentence).
- **actions.chunk_id** = optional chunk that documents the action.

See `docs/NODE_ANCHOR_CHUNK_LINKS.md` for how to populate these from existing data (db.json, RAG receipts).
