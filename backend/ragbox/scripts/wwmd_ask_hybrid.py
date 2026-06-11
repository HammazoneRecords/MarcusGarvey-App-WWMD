#!/usr/bin/env python3
"""
Marcus Garvey ARK - RAG Agent - JSON CONTRACT MODE
Version: 5.0 (Grok-powered)

Features:
1. JSON Output Contract (frontend-ready)
2. Quality Scoring for Citations
3. Session Vault (saves every run to sessions/YYYY-MM-DD/)
4. Configurable Expansion via ENV
5. Callable as a module
"""

import sys
import os
import argparse
import json
import time
import sqlite3
from datetime import datetime, timezone, timedelta
from pathlib import Path

# Windows console safety
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Import utilities
try:
    from .hybrid_retriever import retrieve_hybrid, build_hybrid_context, fetch_all_lines_for_parents
    from .citation_injector import get_citations, inject_citations_text
except ImportError:
    from hybrid_retriever import retrieve_hybrid, build_hybrid_context, fetch_all_lines_for_parents
    from citation_injector import get_citations, inject_citations_text

# =========================
# CONFIG & SETUP
# =========================

BASE_DIR = Path(__file__).resolve().parent.parent
ARK_CONFIG_PATH = BASE_DIR.parent.parent / ".ark"
SESSIONS_DIR = BASE_DIR.parent / "sessions"
DB_PATH = BASE_DIR / "data" / "memory.db"

CITATION_EXPAND_MAX_LINES = int(os.environ.get("CITATION_EXPAND_MAX_LINES", 1500))
CITATION_MAX_DISPLAY = int(os.environ.get("CITATION_MAX_DISPLAY", 15))

GROK_BASE_URL = "https://api.x.ai/v1"
GROK_MODEL = os.environ.get("GROK_MODEL", "grok-3")


def ensure_conversations_table():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_conv_session ON conversations(session_id)")
    conn.commit()
    conn.close()


def load_conversation_history(session_id, limit=6):
    """Returns last `limit` messages for session_id as a formatted string."""
    if not session_id:
        return ""
    try:
        ensure_conversations_table()
        conn = sqlite3.connect(str(DB_PATH))
        rows = conn.execute(
            "SELECT role, content FROM conversations WHERE session_id = ? ORDER BY id DESC LIMIT ?",
            (session_id, limit)
        ).fetchall()
        conn.close()
        if not rows:
            return ""
        rows = list(reversed(rows))
        lines = [f"{role.capitalize()}: {content}" for role, content in rows]
        return "\n".join(lines)
    except Exception:
        return ""


def save_conversation_turn(session_id, role, content):
    if not session_id:
        return
    try:
        ensure_conversations_table()
        kingston_tz = timezone(timedelta(hours=-5))
        ts = datetime.now(kingston_tz).isoformat()
        conn = sqlite3.connect(str(DB_PATH))
        conn.execute(
            "INSERT INTO conversations (session_id, role, content, timestamp) VALUES (?, ?, ?, ?)",
            (session_id, role, content, ts)
        )
        conn.commit()
        conn.close()
    except Exception:
        pass


def resolve_anchor_meta(anchor_ids):
    if not DB_PATH.exists() or not anchor_ids:
        return {}
    try:
        conn = sqlite3.connect(str(DB_PATH))
        conn.row_factory = sqlite3.Row
        placeholders = ",".join("?" * len(anchor_ids))
        rows = conn.execute(
            f"SELECT anchor_id, title, canonical_path FROM anchors WHERE anchor_id IN ({placeholders})",
            anchor_ids
        ).fetchall()
        conn.close()
        return {row["anchor_id"]: {"title": row["title"], "canonical_path": row["canonical_path"]} for row in rows}
    except Exception:
        return {}


def load_ark_config(key_name):
    env_val = os.environ.get(key_name)
    if env_val and env_val.strip():
        return env_val.strip()

    if ARK_CONFIG_PATH.exists():
        import re
        content = ARK_CONFIG_PATH.read_text(encoding="utf-8")
        matches = re.findall(rf'{key_name}\s*=\s*"?([^"\n]+)"?', content)
        if matches:
            return matches[-1].strip()
    return None


def save_to_session_vault(query, response_data):
    kingston_tz = timezone(timedelta(hours=-5))
    now = datetime.now(kingston_tz)
    date_dir = SESSIONS_DIR / now.strftime("%Y-%m-%d")
    date_dir.mkdir(parents=True, exist_ok=True)
    slug = "".join([c if c.isalnum() else '_' for c in query[:30]])
    filename = f"{now.strftime('%H%M%S')}_{slug}.json"
    filepath = date_dir / filename
    filepath.write_text(json.dumps(response_data, indent=2), encoding="utf-8")
    return filepath


# =========================
# GROK GENERATION CLIENT
# =========================

def get_grok_api_key():
    key = load_ark_config('GROK_API_KEY') or load_ark_config('grok_api_key')
    if not key:
        raise RuntimeError("GROK_API_KEY not found in environment or .ark config")
    return key


def call_grok(prompt, system_prompt=None):
    """Call Grok API (non-streaming). Returns response text."""
    import urllib.request
    import urllib.error

    api_key = get_grok_api_key()
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    data = json.dumps({
        "model": GROK_MODEL,
        "messages": messages,
        "temperature": 0.3,
        "max_tokens": 4096,
        "stream": False
    }).encode("utf-8")

    req = urllib.request.Request(
        f"{GROK_BASE_URL}/chat/completions",
        data=data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
    )

    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            return result["choices"][0]["message"]["content"]
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        return f"ERROR: Grok API error {e.code}: {body[:200]}"
    except Exception as e:
        return f"ERROR: Grok request failed — {type(e).__name__}: {e}"


def call_grok_stream(prompt, system_prompt=None):
    """
    Generator yielding text tokens from Grok streaming API.
    Each yield is a string token.
    """
    import urllib.request
    import urllib.error

    api_key = get_grok_api_key()
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    data = json.dumps({
        "model": GROK_MODEL,
        "messages": messages,
        "temperature": 0.3,
        "max_tokens": 4096,
        "stream": True
    }).encode("utf-8")

    req = urllib.request.Request(
        f"{GROK_BASE_URL}/chat/completions",
        data=data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
    )

    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            for line in resp:
                line = line.decode("utf-8").strip()
                if not line or not line.startswith("data:"):
                    continue
                payload = line[5:].strip()
                if payload == "[DONE]":
                    break
                try:
                    chunk = json.loads(payload)
                    delta = chunk["choices"][0].get("delta", {})
                    token = delta.get("content", "")
                    if token:
                        yield token
                except (json.JSONDecodeError, KeyError):
                    continue
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        yield f"ERROR: Grok API {e.code}: {body[:200]}"
    except Exception as e:
        yield f"ERROR: {type(e).__name__}: {e}"


def call_generation(prompt, **kwargs):
    """Main generation entry point — routes to Grok."""
    return call_grok(prompt)


# =========================
# PROMPT TEMPLATES
# =========================

HYBRID_PROMPT_TEMPLATE = """You are Marcus Garvey, speaking directly with {user_name}. Your wisdom flows from a deep archive of your own writings, speeches, and the history of the U.N.I.A. — but this is a conversation, not a lecture.

## THE PROSECUTOR'S STANDARD
1. Admissible Evidence Only for FACTS: Never invent quotes, dates, names, or events. If a fact isn't in the chunks, don't state it as fact.
2. Fidelity: Speak in your own voice, first person — the tone and conviction of Marcus Garvey.
3. No Hallucinations: Never invent archival facts.

## CONTEXT from ARK
{context}

## PRIOR CONVERSATION
{conversation_history}

## {user_name}'S MESSAGE
"{query}"

## HOW TO RESPOND — read the message first and pick ONE mode:

- **Greeting / banter / short check-in** (e.g. "wah gwan", "yo marcus", "thanks", "ok"): Reply briefly and warmly, 1-3 sentences, in your own voice. Do NOT launch into an essay or cite the archive unless asked.

- **Pushback that history "can't help" today** (e.g. "it's 2026, that can't help me", "things are different now"): Acknowledge the point directly — do not dodge it by repeating more dates and names. Then BRIDGE: name the underlying PRINCIPLE from the archive (self-reliance, collective ownership, organization, controlling our own institutions) and translate it to its modern equivalent in plain terms — where I had Liberty Hall and The Negro World, di people today have community groups, group chats, co-ops, social media, online businesses. You may reason about how a timeless principle applies to modern tools WITHOUT inventing specific 2026 facts you have no evidence for — speak generally of "today" and "now". Keep this to 1-2 short paragraphs, then ask {user_name} what THEIR situation is so you can speak to it directly.

- **A real question or situation they want guidance on**: THIS is when you give the fuller answer — comprehensive (2-4 paragraphs), grounded in the archive, with specific evidence woven in. Build it: principle → historical grounding → practical application to {user_name}'s situation today → 2-3 concrete action steps. Each step should be specific and implementable, and explain WHY it matters based on your philosophy.

## GENERAL RULES
- Always speak in first person, as yourself. Never refer to "Garvey" or yourself in the third person.
- Do NOT add citation footnotes yourself; the system will handle citation formatting.
- If the archive is silent on a factual point, say so plainly rather than inventing.
- Weave Jamaican Patois naturally — 'wah gwan', 'wi must rise', 'di people dem', 'bredren', 'tek note', 'babylon' — as you'd speak to a yard audience. Don't force it into every line.
- Match your length to the message: short messages get short replies. Save the fuller answer for when {user_name} actually brings a real question or situation.
- Address {user_name} by name occasionally, naturally — not in every message.

Answer:
"""

LENS_PROMPT_TEMPLATE = """You ARE Marcus Garvey. {user_name} has come to you and asked, in effect: "What would YOU do if you were me, facing this?"

Answer as Marcus Garvey himself — first person, direct, personal. Not an analyst describing "Garvey's principles" from the outside. YOU are speaking. Use "I would...", "If I stood in your shoes, I...", "In my own work building the U.N.I.A., I...". Never refer to yourself in the third person ("Garvey believed...", "his philosophy holds...") — that is forbidden.

Consider this through the {mode} LENS.

## CONTEXT from ARK
{context}

## {user_name}'S SITUATION
"{situation}"

## INSTRUCTIONS
Output a valid JSON object strictly following this schema:
{{
  "principle": "Your direct, first-person answer to 'what would I do?' — state plainly and personally what YOU (Marcus) would do in this exact situation, and the conviction behind it. Grounded in the context provided.",
  "historicalAnalogy": "A moment from YOUR own life or the U.N.I.A.'s work, told in first person ('When I...', 'In my time...'), that mirrors {user_name}'s situation and shows why you'd act as you describe. Include specific details from the context.",
  "actionSteps": [
    {{"id": "1", "text": "Here is what I would have you do first — specific, actionable, grounded in the archive philosophy", "completed": false}},
    {{"id": "2", "text": "Here is what I would do next — specific, actionable, grounded in the archive philosophy", "completed": false}},
    {{"id": "3", "text": "Here is what I would do after that — specific, actionable, grounded in the archive philosophy", "completed": false}}
  ],
  "mirrorQuestions": [
    "A question YOU (Marcus) put directly to {user_name}, challenging their approach?",
    "A question YOU ask about their long-term commitment and alignment with self-determination?"
  ]
}}

- Do NOT include markdown code blocks (```json). Just the raw JSON string.
- Speak in first person throughout EVERY field. You are Marcus Garvey answering directly — not a narrator describing him.
- Each action step is something YOU would personally do or have the user do — grounded in the context and citations provided. State WHY, in your own voice.
- Steps must be practical and implementable, reflecting self-determination, economic independence, and organizational excellence.
- Ground your answer in the principles evident in the archive, not external knowledge.
- If the context does not give you enough to answer plainly, say so honestly in the principle field, in your own voice ("The archives before me are silent on this exact matter, but...").
- Weave approximately 10% Jamaican Patois naturally into the principle and historicalAnalogy fields — expressions like 'wi must rise', 'di people dem', 'bredren' — as you might speak to a yard audience.
"""


# =========================
# MAIN QUERY FUNCTIONS
# =========================

def ask_marcus(query, debug_mode='expand', output_file=None, user_name=None, session_id=None, **kwargs):
    """
    Main entry point for asking a question.
    Returns the JSON response dict.
    """
    start_time = time.time()
    user_name = user_name or "friend"

    # 1. Retrieval
    results = retrieve_hybrid(query, max_results=25)

    # 2. Context Building & Expansion
    context_data = build_hybrid_context(results)

    expanded_lines = []
    if debug_mode == 'expand':
        parent_ids = list(set(r['parent_chunk_id'] for r in results))
        expanded_lines = fetch_all_lines_for_parents(parent_ids)
        expanded_lines = expanded_lines[:CITATION_EXPAND_MAX_LINES]
    elif debug_mode == 'strict':
        expanded_lines = [{'text': r['line_content'], 'locator': r['line_locator'], 'source': r['anchor_id']} for r in results]

    # 3. AI Generation via Grok
    conversation_history = load_conversation_history(session_id)
    save_conversation_turn(session_id, "user", query)
    prompt = HYBRID_PROMPT_TEMPLATE.format(
        context=context_data['context'],
        query=query,
        conversation_history=conversation_history or "None",
        user_name=user_name
    )
    raw_response = call_grok(prompt)
    save_conversation_turn(session_id, "assistant", raw_response[:2000])

    # 4. Citation Discovery & Scoring
    query_terms = query.lower().split()
    citations = get_citations(raw_response, expanded_lines, query_terms)
    top_citations = citations[:CITATION_MAX_DISPLAY]

    # 5. Build JSON Contract
    kingston_tz = timezone(timedelta(hours=-5))
    timestamp = datetime.now(kingston_tz).isoformat()

    json_output = {
        "query": query,
        "mode": "garvey_lens",
        "answer": raw_response,
        "citations": top_citations,
        "meta": {
            "chunks_found": len(results),
            "citation_search_space": len(expanded_lines),
            "timestamp": timestamp,
            "latency_ms": int((time.time() - start_time) * 1000),
            "model": GROK_MODEL
        }
    }

    # 6. Session Vault
    save_to_session_vault(query, json_output)

    if output_file:
        Path(output_file).write_text(json.dumps(json_output, indent=2), encoding="utf-8")

    return json_output


def ask_marcus_lens_stream(situation, mode="Personal", user_name=None, session_id=None, **kwargs):
    """
    Generator yielding SSE events for WWMD lens analysis.
    Fires 'retrieved' immediately after SQLite query, 'generating' heartbeats
    while Grok streams, then 'done' with the full parsed JSON.

    Events:
        {"type": "retrieved", "chunks": N}
        {"type": "generating", "chars": N}
        {"type": "done", "data": {...}}
        {"type": "error", "message": "..."}
    """
    user_name = user_name or "friend"

    # 1. Retrieval
    search_query = f"{situation} {mode}"
    results = retrieve_hybrid(search_query, max_results=20)
    context_data = build_hybrid_context(results)

    yield f"data: {json.dumps({'type': 'retrieved', 'chunks': len(results)})}\n\n"

    save_conversation_turn(session_id, "user", situation)

    # 2. Build prompt
    prompt = LENS_PROMPT_TEMPLATE.format(
        context=context_data['context'],
        situation=situation,
        mode=mode,
        user_name=user_name
    )

    # 3. Stream from Grok
    full_text = ""
    last_heartbeat = 0
    try:
        for token in call_grok_stream(prompt):
            if token.startswith("ERROR:"):
                yield f"data: {json.dumps({'type': 'error', 'message': token})}\n\n"
                return
            full_text += token
            if len(full_text) - last_heartbeat >= 200:
                last_heartbeat = len(full_text)
                yield f"data: {json.dumps({'type': 'generating', 'chars': len(full_text)})}\n\n"
    except Exception as e:
        yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
        return

    # 4. Parse JSON + build receipts
    try:
        cleaned = full_text.replace('```json', '').replace('```', '').strip()
        data_out = json.loads(cleaned)

        top_results = results[:10]
        anchor_ids = list(set(r['anchor_id'] for r in top_results))
        anchor_meta = resolve_anchor_meta(anchor_ids)

        receipts = []
        for r in top_results:
            loc = r['line_locator']
            page = loc.split(':')[-1] if ':' in loc else "0"
            meta = anchor_meta.get(r['anchor_id'], {})
            title = meta.get('title') or r['anchor_id']
            receipts.append({
                "id": r['anchor_id'],
                "anchorId": r['anchor_id'],
                "title": title,
                "type": "archive",
                "excerpt": r['line_content'],
                "year": None,
                "page": page,
                "locator": loc,
                "canonicalPath": meta.get('canonical_path') or None,
            })

        data_out['receipts'] = receipts
        save_conversation_turn(session_id, "assistant", data_out.get('principle', '')[:500])
        yield f"data: {json.dumps({'type': 'done', 'data': data_out})}\n\n"

    except json.JSONDecodeError:
        fallback = {
            "principle": "Parse Error",
            "historicalAnalogy": "The oracle spoke in riddles. Raw: " + full_text[:200],
            "receipts": [],
            "actionSteps": [],
            "mirrorQuestions": []
        }
        yield f"data: {json.dumps({'type': 'done', 'data': fallback})}\n\n"


def ask_marcus_lens(situation, mode="Personal", user_name=None, session_id=None, **kwargs):
    """
    Analyzes a situation through Garvey's lens. Returns structured JSON.
    """
    start_time = time.time()
    user_name = user_name or "friend"

    search_query = f"{situation} {mode} organization success"
    results = retrieve_hybrid(search_query, max_results=20)
    context_data = build_hybrid_context(results)

    save_conversation_turn(session_id, "user", situation)

    prompt = LENS_PROMPT_TEMPLATE.format(
        context=context_data['context'],
        situation=situation,
        mode=mode,
        user_name=user_name
    )

    raw_response = call_grok(prompt)
    save_conversation_turn(session_id, "assistant", raw_response[:500])

    try:
        cleaned = raw_response.replace('```json', '').replace('```', '').strip()
        data = json.loads(cleaned)

        top_results = results[:10]
        anchor_ids = list(set(r['anchor_id'] for r in top_results))
        anchor_meta = resolve_anchor_meta(anchor_ids)

        receipts = []
        for r in top_results:
            loc = r['line_locator']
            page = loc.split(':')[-1] if ':' in loc else "0"
            meta = anchor_meta.get(r['anchor_id'], {})
            title = meta.get('title') or r['anchor_id']
            receipts.append({
                "id": r['anchor_id'],
                "anchorId": r['anchor_id'],
                "title": title,
                "type": "archive",
                "excerpt": r['line_content'],
                "year": None,
                "page": page,
                "locator": loc,
                "canonicalPath": meta.get('canonical_path') or None,
            })

        data['receipts'] = receipts
        return data

    except json.JSONDecodeError:
        return {
            "principle": "Protocol Error",
            "historicalAnalogy": "The system could not structure the answer. Raw: " + raw_response[:100],
            "receipts": [],
            "actionSteps": [],
            "mirrorQuestions": []
        }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("query", help="User question")
    parser.add_argument("--json", action="store_true", help="Output JSON only")
    parser.add_argument("--out", help="Save JSON to specific file")
    parser.add_argument("--debug", type=str, choices=['expand', 'strict', 'off'], default='expand')
    args = parser.parse_args()

    response = ask_marcus(args.query, args.debug, args.out)

    if args.json:
        print(json.dumps(response, indent=2))
    else:
        print("\n" + "="*60)
        print("MARCUS GARVEY ARK ANSWER")
        print("="*60 + "\n")
        print(inject_citations_text(response['answer'], response['citations']))


if __name__ == "__main__":
    main()
