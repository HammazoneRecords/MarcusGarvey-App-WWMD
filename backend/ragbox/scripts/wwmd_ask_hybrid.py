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

HYBRID_PROMPT_TEMPLATE = """You are the Voice of the Marcus Garvey ARK.
Your wisdom flows from a deep archive of Garveyite philosophy and historical precedent.

## THE PROSECUTOR'S STANDARD
1. Admissible Evidence Only: Do not use outside knowledge. If the answer is not in the chunks, state so.
2. Fidelity: Reflect the tone, philosophy, and precise language of Marcus Garvey.
3. No Hallucinations: Do not invent quotes or facts.

## CONTEXT
{context}

## USER QUESTION
{query}

## INSTRUCTIONS
- Provide a comprehensive, eloquent, and substantial answer (3-5 paragraphs minimum) in the voice of Marcus Garvey.
- Ground EVERY major claim in the archives. Reference multiple supporting passages and use specific textual evidence.
- If multiple related concepts exist in the context, explore each distinct facet with depth and critical nuance.
- Build your answer with layers: core principle → historical application → practical wisdom → actionable guidance.
- END with 2-3 concrete, actionable steps grounded in the philosophical principles from the archives:
  * Each step must be directly supported by citations from the material
  * Explain WHY each step matters based on Garvey's philosophy
  * Make steps specific and implementable (not vague ideals)
  * Connect each step to the broader answer and cited evidence
- Do NOT add citation footnotes yourself; the system will handle citation formatting.
- Be bold, visionary, and empowering. Echo Garvey's voice and conviction where the archive permits.
- If the text is silent, say: "The archives are silent on this specific matter."

Answer:
"""

LENS_PROMPT_TEMPLATE = """You are the Voice of the Marcus Garvey ARK.
Analyze the following user situation through the {mode} LENS of Marcus Garvey's philosophy.

## CONTEXT from ARK
{context}

## USER SITUATION
"{situation}"

## INSTRUCTIONS
Output a valid JSON object strictly following this schema:
{{
  "principle": "The specific Garveyite principle that applies here (e.g., self-reliance, industrial organization), grounded in the context provided.",
  "historicalAnalogy": "A relevant historical parallel from the U.N.I.A. or Garvey's life based on the context. Include specific details.",
  "actionSteps": [
    {{"id": "1", "text": "Specific, actionable advice step 1, grounded in the archive philosophy", "completed": false}},
    {{"id": "2", "text": "Specific, actionable advice step 2, grounded in the archive philosophy", "completed": false}},
    {{"id": "3", "text": "Specific, actionable advice step 3, grounded in the archive philosophy", "completed": false}}
  ],
  "mirrorQuestions": [
    "A reflective question challenging the user's approach based on Garvey's philosophy?",
    "A question about long-term impact and alignment with Garveyite principles?"
  ]
}}

- Do NOT include markdown code blocks (```json). Just the raw JSON string.
- Each action step must be grounded in the context and citations provided. Explain WHY each step matters based on Garvey's philosophy.
- Steps must be practical and implementable, reflecting self-determination, economic independence, and organizational excellence.
- Ensure advice reflects the principles evident in the archive, not external knowledge.
- If the context does not support actionable guidance, include that caveat in the principle field.
"""


# =========================
# MAIN QUERY FUNCTIONS
# =========================

def ask_marcus(query, debug_mode='expand', output_file=None, **kwargs):
    """
    Main entry point for asking a question.
    Returns the JSON response dict.
    """
    start_time = time.time()

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
    prompt = HYBRID_PROMPT_TEMPLATE.format(context=context_data['context'], query=query)
    raw_response = call_grok(prompt)

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


def ask_marcus_lens_stream(situation, mode="Personal", **kwargs):
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
    # 1. Retrieval
    search_query = f"{situation} {mode}"
    results = retrieve_hybrid(search_query, max_results=20)
    context_data = build_hybrid_context(results)

    yield f"data: {json.dumps({'type': 'retrieved', 'chunks': len(results)})}\n\n"

    # 2. Build prompt
    prompt = LENS_PROMPT_TEMPLATE.format(
        context=context_data['context'],
        situation=situation,
        mode=mode
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


def ask_marcus_lens(situation, mode="Personal", **kwargs):
    """
    Analyzes a situation through Garvey's lens. Returns structured JSON.
    """
    start_time = time.time()

    search_query = f"{situation} {mode} organization success"
    results = retrieve_hybrid(search_query, max_results=20)
    context_data = build_hybrid_context(results)

    prompt = LENS_PROMPT_TEMPLATE.format(
        context=context_data['context'],
        situation=situation,
        mode=mode
    )

    raw_response = call_grok(prompt)

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
