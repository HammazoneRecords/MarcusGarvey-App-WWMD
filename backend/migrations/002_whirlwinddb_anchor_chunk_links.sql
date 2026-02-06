-- WhirlwindDB: link nodes/sources/claims to RAG anchors and chunks
-- Run after 001. Sources point to anchors; claims point to chunks (exact citation).
-- chunk_id / anchor_id reference backend/data/memory.db (RAG spine).

-- Sources: point to an ingested anchor (and optional page/section)
ALTER TABLE sources ADD COLUMN IF NOT EXISTS anchor_id TEXT;
ALTER TABLE sources ADD COLUMN IF NOT EXISTS anchor_locator TEXT;
COMMENT ON COLUMN sources.anchor_id IS 'RAG anchor_id from memory.db anchors table';
COMMENT ON COLUMN sources.anchor_locator IS 'Optional page/section e.g. pdf:page:0010';

CREATE INDEX IF NOT EXISTS idx_sources_anchor_id ON sources(anchor_id);

-- Claims: optional single primary chunk that backs this claim
ALTER TABLE claims ADD COLUMN IF NOT EXISTS chunk_id TEXT;
COMMENT ON COLUMN claims.chunk_id IS 'RAG chunk_id from memory.db chunks table';

CREATE INDEX IF NOT EXISTS idx_claims_chunk_id ON claims(chunk_id);

-- Many-to-many: a claim can cite multiple chunks (e.g. one per sentence)
CREATE TABLE IF NOT EXISTS claim_chunk_citations (
    claim_id   INTEGER NOT NULL,
    chunk_id   TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (claim_id, chunk_id)
    -- claim_id REFERENCES claims(id) when nodes live in same DB
    -- chunk_id lives in memory.db; no FK across DBs
);

CREATE INDEX IF NOT EXISTS idx_claim_chunk_citations_chunk ON claim_chunk_citations(chunk_id);

-- Actions: optional chunk that documents this action
ALTER TABLE actions ADD COLUMN IF NOT EXISTS chunk_id TEXT;
CREATE INDEX IF NOT EXISTS idx_actions_chunk_id ON actions(chunk_id);
