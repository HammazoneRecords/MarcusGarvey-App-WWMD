-- WhirlwindDB Node Specification (SQLite)
-- Run this first; then 002_whirlwinddb_anchor_chunk_links_sqlite.sql
-- Node ID format: WWD-<REGION>-<YEAR>-<SEQ> (e.g. WWD-CAR-1887-001)

CREATE TABLE IF NOT EXISTS nodes (
    id              TEXT PRIMARY KEY,
    display_number  TEXT NOT NULL,
    name            TEXT NOT NULL,
    short_name      TEXT,
    region          TEXT,
    birth_year      INT,
    death_year      INT,
    summary         TEXT,
    created_at      TEXT DEFAULT (datetime('now')),
    updated_at      TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS sources (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    node_id         TEXT NOT NULL REFERENCES nodes(id),
    external_id     TEXT,
    title           TEXT NOT NULL,
    author          TEXT,
    year            INT,
    source_type     TEXT,
    url             TEXT,
    excerpt         TEXT,
    content_hash    TEXT,
    created_at      TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS claims (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    node_id         TEXT NOT NULL REFERENCES nodes(id),
    external_id     TEXT,
    source_id       INT REFERENCES sources(id),
    claim_text      TEXT NOT NULL,
    context         TEXT,
    impact_trail    TEXT,
    categories      TEXT,
    reading_time_sec INT,
    confidence      TEXT,
    created_at      TEXT DEFAULT (datetime('now'))
);

-- One claim can have many sources (receipts)
CREATE TABLE IF NOT EXISTS claim_sources (
    claim_id        INTEGER NOT NULL REFERENCES claims(id),
    source_id       INTEGER NOT NULL REFERENCES sources(id),
    PRIMARY KEY (claim_id, source_id)
);

CREATE TABLE IF NOT EXISTS disputed_claims (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    claim_id        INTEGER NOT NULL REFERENCES claims(id),
    reason          TEXT,
    created_at      TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS actions (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    node_id         TEXT NOT NULL REFERENCES nodes(id),
    source_id       INT REFERENCES sources(id),
    action_text     TEXT NOT NULL,
    year            INT,
    created_at      TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS consequences (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    action_id       INTEGER NOT NULL REFERENCES actions(id),
    node_id         TEXT NOT NULL REFERENCES nodes(id),
    consequence_text TEXT NOT NULL,
    created_at      TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS relationships (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    from_node_id    TEXT NOT NULL REFERENCES nodes(id),
    to_node_id      TEXT NOT NULL REFERENCES nodes(id),
    relationship_type TEXT NOT NULL,
    created_at      TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS node_tags (
    node_id         TEXT NOT NULL REFERENCES nodes(id),
    tag             TEXT NOT NULL,
    created_at      TEXT DEFAULT (datetime('now')),
    PRIMARY KEY (node_id, tag)
);

CREATE INDEX IF NOT EXISTS idx_claims_node ON claims(node_id);
CREATE INDEX IF NOT EXISTS idx_claims_external ON claims(external_id);
CREATE INDEX IF NOT EXISTS idx_sources_node ON sources(node_id);
CREATE INDEX IF NOT EXISTS idx_sources_external ON sources(external_id);
CREATE INDEX IF NOT EXISTS idx_actions_node ON actions(node_id);
CREATE INDEX IF NOT EXISTS idx_claim_sources_claim ON claim_sources(claim_id);
CREATE INDEX IF NOT EXISTS idx_claim_sources_source ON claim_sources(source_id);
CREATE INDEX IF NOT EXISTS idx_relationships_from ON relationships(from_node_id);
CREATE INDEX IF NOT EXISTS idx_relationships_to ON relationships(to_node_id);
