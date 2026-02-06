-- Testing Panel persistence (SQLite)
-- One row per storage_key (e.g. marcus-garvey-testing-panel).
-- checked: JSON array of item keys; notes: JSON array of note lines.

CREATE TABLE IF NOT EXISTS testing_panel_state (
    storage_key TEXT PRIMARY KEY,
    checked_json TEXT NOT NULL DEFAULT '[]',
    notes_json TEXT NOT NULL DEFAULT '[]',
    updated_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_testing_panel_updated ON testing_panel_state(updated_at);
