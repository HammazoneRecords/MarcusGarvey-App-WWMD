#!/usr/bin/env python3
"""
WWMD (What Would Marcus Do) RAG Agent - JSON CONTRACT MODE
Version: 4.0 (JSON Output, Session Vault, Quality Scoring)

Features:
1. JSON Output Contract (frontend-ready)
2. Quality Scoring for Citations
3. Session Vault (saves every run to sessions/YYYY-MM-DD/)
4. Configurable Expansion via ENV

Usage:
  python scripts/wwmd_ask_hybrid.py "Query" --json --out result.json
"""

import sys
import os
import argparse
import json
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

# Windows console safety
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Import utilities
from hybrid_retriever import retrieve_hybrid, build_hybrid_context, fetch_all_lines_for_parents
from citation_injector import get_citations, inject_citations_text

# =========================
# CONFIG & SETUP
# =========================

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR.parent / ".env"
SESSIONS_DIR = BASE_DIR.parent / "sessions"

# Config from Env
CITATION_EXPAND_MAX_LINES = int(os.environ.get("CITATION_EXPAND_MAX_LINES", 500))
CITATION_MAX_DISPLAY = int(os.environ.get("CITATION_MAX_DISPLAY", 8))

def load_api_key():
    """Parse .env for Gemini API Key."""
    if not ENV_PATH.exists():
        return None
        
    import re
    content = ENV_PATH.read_text(encoding="utf-8")
    matches = re.findall(r'GEMINI_API_KEY\s*=\s*"([^"]+)"', content)
    if matches:
        return matches[-1]
    return None

def save_to_session_vault(query, response_data):
    """Save JSON to sessions/YYYY-MM-DD/timestamp_slug.json"""
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
# GENERATION CLIENT
# =========================

def call_gemini_rest(api_key, full_text, model_name="gemini-2.5-flash"):
    """Call Gemini API using REST."""
    import urllib.request
    import urllib.error
    
    if not api_key:
        return "ERROR: Missing API Key"
        
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    data = {"contents": [{"parts": [{"text": full_text}]}]}
    
    try:
        req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers=headers)
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            try:
                return result['candidates'][0]['content']['parts'][0]['text']
            except (KeyError, IndexError):
                return f"ERROR: format {result}"
    except urllib.error.HTTPError as e:
        return f"ERROR: HTTP {e.code}"
    except Exception as e:
        return f"ERROR: {e}"

# =========================
# PROMPT
# =========================
HYBRID_PROMPT_TEMPLATE = """You are the Voice of the Marcus Garvey ARK.
Answer based ONLY on the provided context.

Context:
{context}

Question: {query}

Provide a comprehensive answer. Do not add citations.
"""

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("query", help="User question")
    parser.add_argument("--json", action="store_true", help="Output JSON only")
    parser.add_argument("--out", help="Save JSON to specific file")
    parser.add_argument("--debug", type=str, choices=['expand', 'strict', 'off'], default='expand')
    args = parser.parse_args()
    
    start_time = time.time()
    api_key = load_api_key()
    
    # 1. Retrieval
    results = retrieve_hybrid(args.query, max_results=15)
    
    # 2. Context Building & Expansion
    context_data = build_hybrid_context(results)
    
    expanded_lines = []
    if args.debug == 'expand':
        parent_ids = list(set(r['parent_chunk_id'] for r in results))
        expanded_lines = fetch_all_lines_for_parents(parent_ids)
        # Limit expansion
        expanded_lines = expanded_lines[:CITATION_EXPAND_MAX_LINES]
    elif args.debug == 'strict':
        expanded_lines = [{'text': r['line_content'], 'locator': r['line_locator'], 'source': r['anchor_id']} for r in results]
    
    # 3. AI Generation
    prompt = HYBRID_PROMPT_TEMPLATE.format(context=context_data['context'], query=args.query)
    raw_response = call_gemini_rest(api_key, prompt)
    
    # 4. Citation Discovery & Scoring
    query_terms = args.query.lower().split()
    citations = get_citations(raw_response, expanded_lines, query_terms)
    top_citations = citations[:CITATION_MAX_DISPLAY]
    
    # 5. Build JSON Contract
    kingston_tz = timezone(timedelta(hours=-5))
    timestamp = datetime.now(kingston_tz).isoformat()
    
    json_output = {
        "query": args.query,
        "mode": "garvey_lens",
        "answer": raw_response,
        "citations": top_citations,
        "meta": {
            "chunks_found": len(results),
            "citation_search_space": len(expanded_lines),
            "timestamp": timestamp,
            "latency_ms": int((time.time() - start_time) * 1000)
        }
    }
    
    # 6. Session Vault
    vault_path = save_to_session_vault(args.query, json_output)
    
    # 7. Output Handling
    if args.out:
        Path(args.out).write_text(json.dumps(json_output, indent=2), encoding="utf-8")
        
    if args.json:
        print(json.dumps(json_output, indent=2))
    else:
        # Legacy Text Output
        print("\n" + "="*60)
        print("WWMD ANSWER (JSON-Powered)")
        print("="*60 + "\n")
        print(inject_citations_text(raw_response, top_citations))
        print(f"\n[Vault]: Saved to {vault_path}")

if __name__ == "__main__":
    main()
