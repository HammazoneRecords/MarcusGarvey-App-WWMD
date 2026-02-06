-- WhirlwindDB anchor/chunk links (SQLite)
-- Run after 001. Sources -> anchors; claims/actions -> chunks.
-- Use when nodes live in SQLite (e.g. same DB as RAG or separate nodes.db).

-- Sources: point to RAG anchor (memory.db anchors table)
-- Run each ALTER once; omit if column already exists.
ALTER TABLE sources ADD COLUMN anchor_id TEXT;
ALTER TABLE sources ADD COLUMN anchor_locator TEXT;

CREATE INDEX IF NOT EXISTS idx_sources_anchor_id ON sources(anchor_id);

-- Claims: optional primary chunk that backs this claim
ALTER TABLE claims ADD COLUMN chunk_id TEXT;

CREATE INDEX IF NOT EXISTS idx_claims_chunk_id ON claims(chunk_id);

-- Many-to-many: claim can cite multiple chunks
CREATE TABLE IF NOT EXISTS claim_chunk_citations (
    claim_id   INTEGER NOT NULL,
    chunk_id   TEXT NOT NULL,
    created_at TEXT DEFAULT (datetime('now')),
    PRIMARY KEY (claim_id, chunk_id)
);

CREATE INDEX IF NOT EXISTS idx_claim_chunk_citations_chunk ON claim_chunk_citations(chunk_id);

-- Actions: optional chunk that documents this action
ALTER TABLE actions ADD COLUMN chunk_id TEXT;

CREATE INDEX IF NOT EXISTS idx_actions_chunk_id ON actions(chunk_id);
