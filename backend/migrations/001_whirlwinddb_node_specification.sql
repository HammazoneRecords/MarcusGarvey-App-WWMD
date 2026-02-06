-- WhirlwindDB Node Specification Schema
-- Append-only, provenance-first. No silent deletes.
-- Node ID format: WWD-<REGION>-<YEAR>-<SEQ> (e.g. WWD-CAR-1887-004)

-- Optional schema (use public if you prefer)
-- CREATE SCHEMA IF NOT EXISTS whirlwind;

-- Nodes: historically verifiable figures, movements, or institutions
CREATE TABLE IF NOT EXISTS nodes (
    id              TEXT PRIMARY KEY,
    display_number  TEXT NOT NULL,
    name            TEXT NOT NULL,
    short_name      TEXT,
    region          TEXT,
    birth_year      INT,
    death_year      INT,
    summary         TEXT,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Sources: primary source citations (receipts)
CREATE TABLE IF NOT EXISTS sources (
    id              SERIAL PRIMARY KEY,
    node_id         TEXT NOT NULL REFERENCES nodes(id),
    title           TEXT NOT NULL,
    author          TEXT,
    year            INT,
    source_type     TEXT,
    url             TEXT,
    content_hash    TEXT,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Claims: source-backed statements per node
CREATE TABLE IF NOT EXISTS claims (
    id              SERIAL PRIMARY KEY,
    node_id         TEXT NOT NULL REFERENCES nodes(id),
    source_id       INT REFERENCES sources(id),
    claim_text      TEXT NOT NULL,
    context         TEXT,
    confidence      TEXT,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Disputed claims (visually distinct in UI)
CREATE TABLE IF NOT EXISTS disputed_claims (
    id              SERIAL PRIMARY KEY,
    claim_id        INT NOT NULL REFERENCES claims(id),
    reason          TEXT,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Actions: verifiable events/actions per node
CREATE TABLE IF NOT EXISTS actions (
    id              SERIAL PRIMARY KEY,
    node_id         TEXT NOT NULL REFERENCES nodes(id),
    source_id       INT REFERENCES sources(id),
    action_text     TEXT NOT NULL,
    year            INT,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Consequences: outcomes linked to actions
CREATE TABLE IF NOT EXISTS consequences (
    id              SERIAL PRIMARY KEY,
    action_id       INT NOT NULL REFERENCES actions(id),
    node_id         TEXT NOT NULL REFERENCES nodes(id),
    consequence_text TEXT NOT NULL,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Relationships between nodes
CREATE TABLE IF NOT EXISTS relationships (
    id              SERIAL PRIMARY KEY,
    from_node_id    TEXT NOT NULL REFERENCES nodes(id),
    to_node_id      TEXT NOT NULL REFERENCES nodes(id),
    relationship_type TEXT NOT NULL,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Tags for filtering
CREATE TABLE IF NOT EXISTS node_tags (
    node_id         TEXT NOT NULL REFERENCES nodes(id),
    tag             TEXT NOT NULL,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (node_id, tag)
);

CREATE INDEX IF NOT EXISTS idx_claims_node ON claims(node_id);
CREATE INDEX IF NOT EXISTS idx_sources_node ON sources(node_id);
CREATE INDEX IF NOT EXISTS idx_actions_node ON actions(node_id);
CREATE INDEX IF NOT EXISTS idx_relationships_from ON relationships(from_node_id);
CREATE INDEX IF NOT EXISTS idx_relationships_to ON relationships(to_node_id);
