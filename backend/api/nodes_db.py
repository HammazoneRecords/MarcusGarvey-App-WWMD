"""
Nodes DB: SQLite store for nodes/sources/claims linked to RAG anchors and chunks.
Init, migrate, seed from frontend db.json, and serve library payload for GET /api/library.
"""
import json
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BASE_DIR.parent
NODES_DB_PATH = BASE_DIR / "data" / "nodes.db"
MIGRATIONS_DIR = BASE_DIR / "migrations"
DB_JSON_PATH = PROJECT_ROOT / "frontend" / "src" / "mock" / "db.json"

DEFAULT_NODE_ID = "WWD-CAR-1887-001"


def _run_migration(conn, filename):
    path = MIGRATIONS_DIR / filename
    if not path.exists():
        return
    sql = path.read_text(encoding="utf-8")
    # 001: run as script (CREATE TABLE IF NOT EXISTS)
    if "001" in filename:
        conn.executescript(sql)
        return
    # 002: run each statement (strip comment lines first; ignore duplicate column / already exists)
    lines = [line for line in sql.splitlines() if not line.strip().startswith("--")]
    clean_sql = "\n".join(lines)
    for stmt in clean_sql.split(";"):
        stmt = stmt.strip()
        if not stmt:
            continue
        try:
            conn.execute(stmt)
        except sqlite3.OperationalError as e:
            if "duplicate column" not in str(e).lower() and "already exists" not in str(e).lower():
                raise


def init_db():
    """Create nodes.db and run migrations if needed."""
    NODES_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(NODES_DB_PATH))
    try:
        cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='nodes'")
        if cur.fetchone() is None:
            _run_migration(conn, "001_whirlwinddb_node_specification_sqlite.sql")
        _run_migration(conn, "002_whirlwinddb_anchor_chunk_links_sqlite.sql")
        conn.commit()
    finally:
        conn.close()


def seed_from_db_json():
    """Load frontend db.json and populate nodes/sources/claims/claim_sources. Idempotent by external_id."""
    if not DB_JSON_PATH.exists():
        return
    data = json.loads(DB_JSON_PATH.read_text(encoding="utf-8"))
    sources_data = data.get("sources", [])
    facts_data = data.get("facts", [])

    conn = sqlite3.connect(str(NODES_DB_PATH))
    conn.row_factory = sqlite3.Row
    try:
        cur = conn.execute("SELECT id FROM nodes LIMIT 1")
        if cur.fetchone() is None:
            conn.execute(
                """INSERT INTO nodes (id, display_number, name, short_name, region, birth_year, death_year, summary)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (DEFAULT_NODE_ID, "WWD-CAR-1887-001", "Marcus Garvey", "Garvey", "Jamaica", 1887, 1940,
                 "Founder of the UNIA and advocate for Black economic and cultural self-determination.")
            )

        external_id_to_source_id = {}
        for s in sources_data:
            ext_id = s.get("id") or ""
            cur = conn.execute("SELECT id FROM sources WHERE external_id = ?", (ext_id,))
            row = cur.fetchone()
            if row is not None:
                external_id_to_source_id[ext_id] = row["id"]
                continue
            conn.execute(
                """INSERT INTO sources (node_id, external_id, title, author, year, source_type, url, excerpt, anchor_id)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    DEFAULT_NODE_ID,
                    ext_id,
                    s.get("title", ""),
                    s.get("author"),
                    s.get("year"),
                    s.get("type"),
                    s.get("url"),
                    s.get("excerpt"),
                    s.get("anchorId"),
                ),
            )
            external_id_to_source_id[ext_id] = conn.execute("SELECT last_insert_rowid()").fetchone()[0]

        for f in facts_data:
            ext_id = f.get("id") or ""
            cur = conn.execute("SELECT id FROM claims WHERE external_id = ?", (ext_id,))
            if cur.fetchone() is not None:
                continue
            receipt_ids = f.get("receiptIds") or []
            source_id = external_id_to_source_id.get(receipt_ids[0]) if receipt_ids else None
            conn.execute(
                """INSERT INTO claims (node_id, external_id, source_id, claim_text, context, impact_trail, categories, reading_time_sec, confidence)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    DEFAULT_NODE_ID,
                    ext_id,
                    source_id,
                    f.get("claim", ""),
                    f.get("context"),
                    json.dumps(f.get("impactTrail", [])),
                    json.dumps(f.get("categories", [])),
                    f.get("readingTimeSec"),
                    f.get("confidence"),
                ),
            )
            claim_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
            for rid in receipt_ids:
                sid = external_id_to_source_id.get(rid)
                if sid is not None:
                    try:
                        conn.execute("INSERT OR IGNORE INTO claim_sources (claim_id, source_id) VALUES (?, ?)", (claim_id, sid))
                    except sqlite3.IntegrityError:
                        pass
        conn.commit()
    finally:
        conn.close()


def get_library(filters=None):
    """
    Return { sources: [...], facts: [...] } in the shape the frontend expects.
    Each source has id (external_id), title, author, year, type, excerpt, url, anchorId.
    Each fact has id (external_id), claim, context, impactTrail, categories, readingTimeSec, confidence, receipts: [SourceRef].
    """
    init_db()
    seed_from_db_json()

    conn = sqlite3.connect(str(NODES_DB_PATH))
    conn.row_factory = sqlite3.Row
    try:
        # All sources for the default node
        cur = conn.execute(
            """SELECT id, external_id, title, author, year, source_type, url, excerpt, anchor_id
               FROM sources WHERE node_id = ? ORDER BY id""",
            (DEFAULT_NODE_ID,),
        )
        rows = cur.fetchall()
        source_by_id = {}
        sources_payload = []
        for r in rows:
            sid = r["external_id"] or f"src-{r['id']}"
            source_by_id[r["id"]] = {
                "id": sid,
                "title": r["title"] or "",
                "author": r["author"] or "",
                "year": r["year"],
                "type": (r["source_type"] or "archive").lower() if r["source_type"] else "archive",
                "excerpt": r["excerpt"] or "",
                "url": r["url"] or "",
            }
            if r["anchor_id"]:
                source_by_id[r["id"]]["anchorId"] = r["anchor_id"]
            sources_payload.append(source_by_id[r["id"]])

        # All claims with their source ids (receipts)
        cur = conn.execute(
            """SELECT c.id, c.external_id, c.claim_text, c.context, c.impact_trail, c.categories, c.reading_time_sec, c.confidence
               FROM claims c WHERE c.node_id = ? ORDER BY c.id""",
            (DEFAULT_NODE_ID,),
        )
        claims_rows = cur.fetchall()
        claim_receipts = {}
        for c in claims_rows:
            cur2 = conn.execute(
                "SELECT source_id FROM claim_sources WHERE claim_id = ?",
                (c["id"],),
            )
            claim_receipts[c["id"]] = [row["source_id"] for row in cur2.fetchall()]

        facts_payload = []
        for c in claims_rows:
            receipt_sources = []
            for sid in claim_receipts.get(c["id"], []):
                if sid in source_by_id:
                    receipt_sources.append(source_by_id[sid])
            fact_id = c["external_id"] or f"fact-{c['id']}"
            impact_trail = []
            categories = []
            try:
                if c["impact_trail"]:
                    impact_trail = json.loads(c["impact_trail"])
            except Exception:
                pass
            try:
                if c["categories"]:
                    categories = json.loads(c["categories"])
            except Exception:
                pass
            facts_payload.append({
                "id": fact_id,
                "claim": c["claim_text"] or "",
                "context": c["context"] or "",
                "impactTrail": impact_trail,
                "categories": categories,
                "readingTimeSec": c["reading_time_sec"] or 0,
                "confidence": (c["confidence"] or "high").lower(),
                "receipts": receipt_sources,
            })

        if filters:
            search = (filters.get("search") or "").strip().lower()
            category = (filters.get("category") or "").strip()
            confidence = (filters.get("confidence") or "").strip()
            if search:
                facts_payload = [f for f in facts_payload if search in (f.get("claim") or "").lower() or search in (f.get("context") or "").lower()]
            if category:
                facts_payload = [f for f in facts_payload if category in (f.get("categories") or [])]
            if confidence:
                facts_payload = [f for f in facts_payload if (f.get("confidence") or "") == confidence]

        return {"sources": sources_payload, "facts": facts_payload}
    finally:
        conn.close()
