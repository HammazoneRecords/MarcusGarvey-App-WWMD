-- =========================================================
-- Solob Wrapper V1.1 — Canonical SQLite Schema
-- Purpose: Anchor-referential, audit-first memory spine
-- Database role: Index + provenance ledger (NOT source of truth)
-- =========================================================

PRAGMA foreign_keys = ON;

-- =========================================================
-- TABLE: anchors
-- Indexes external, read-only anchor sources (PDF, JSON, text)
-- =========================================================
CREATE TABLE anchors (
    anchor_id TEXT PRIMARY KEY,
    anchor_type TEXT NOT NULL CHECK (anchor_type IN ('lexicon', 'book', 'letter', 'other')),
    title TEXT NOT NULL,
    source_path TEXT NOT NULL,           -- filesystem path to anchor
    source_format TEXT NOT NULL CHECK (source_format IN ('json', 'pdf', 'txt')),
    status TEXT NOT NULL CHECK (status IN ('canon', 'working')),
    provenance TEXT NOT NULL,            -- human-entered source description
    import_session_id TEXT NOT NULL,     -- ingestion batch identifier
    created_at TEXT NOT NULL             -- ISO-8601 timestamp
);


-- =========================================================
-- TABLE: chunks
-- Atomic, referenceable statements extracted from anchors
-- =========================================================
CREATE TABLE chunks (
    chunk_id TEXT PRIMARY KEY,
    anchor_id TEXT NOT NULL,
    anchor_locator TEXT NOT NULL,        -- page, section, lexicon row, etc.
    lexicon_word TEXT,                   -- headword if lexicon-derived (NULL otherwise)
    content TEXT NOT NULL,               -- exact extracted text (no mutation)

    truth_type TEXT NOT NULL CHECK (
        truth_type IN (
            'definition',
            'event',
            'empirical',
            'interpretive',
            'causal',
            'relational'
        )
    ),

    mutation_mode TEXT NOT NULL CHECK (
        mutation_mode IN (
            'append-only',
            'versioned',
            'time-bounded',
            're-index-only'
        )
    ),

    confidence REAL CHECK (
        confidence IS NULL
        OR (confidence >= 0 AND confidence <= 1)
    ),

    import_session_id TEXT NOT NULL,     -- ingestion batch identifier
    created_at TEXT NOT NULL,

    FOREIGN KEY (anchor_id)
        REFERENCES anchors(anchor_id)
        ON DELETE RESTRICT
);

-- =========================================================
-- TABLE: provenance_notes
-- Non-mutative annotations and corrections
-- =========================================================
CREATE TABLE provenance_notes (
    note_id TEXT PRIMARY KEY,
    target_type TEXT NOT NULL CHECK (target_type IN ('anchor', 'chunk')),
    target_id TEXT NOT NULL,
    note TEXT NOT NULL,
    author TEXT NOT NULL,
    created_at TEXT NOT NULL
);

-- =========================================================
-- TABLE: runs
-- Logged system queries and outputs (audit trail)
-- =========================================================
CREATE TABLE runs (
    run_id TEXT PRIMARY KEY,
    input_query TEXT NOT NULL,
    output_text TEXT NOT NULL,
    created_at TEXT NOT NULL,
    verdict TEXT NOT NULL CHECK (
        verdict IN ('ok', 'unknown', 'flagged')
    )
);

-- =========================================================
-- TABLE: run_citations
-- Normalized citation graph between runs and chunks
-- =========================================================
CREATE TABLE run_citations (
    run_id TEXT NOT NULL,
    chunk_id TEXT NOT NULL,

    PRIMARY KEY (run_id, chunk_id),

    FOREIGN KEY (run_id)
        REFERENCES runs(run_id)
        ON DELETE CASCADE,

    FOREIGN KEY (chunk_id)
        REFERENCES chunks(chunk_id)
        ON DELETE RESTRICT
);

-- =========================================================
-- INDEXES (AFTER TABLES EXIST)
-- =========================================================
CREATE INDEX IF NOT EXISTS idx_chunks_anchor_id ON chunks(anchor_id);
CREATE INDEX IF NOT EXISTS idx_runs_created_at ON runs(created_at);
CREATE INDEX IF NOT EXISTS idx_prov_target ON provenance_notes(target_type, target_id);
CREATE INDEX IF NOT EXISTS idx_run_citations_chunk ON run_citations(chunk_id);

-- Optional but useful
-- CREATE INDEX IF NOT EXISTS idx_run_citations_run ON run_citations(run_id);

-- =========================================================
-- END OF SCHEMA — V1.1
-- =========================================================
