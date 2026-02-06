#!/usr/bin/env python3
"""
WWMD (What Would Marcus Do) RAG Agent - JSON CONTRACT MODE
Version: 4.1 (Flask-Ready, Refined Persona)

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
    # Fallback for running as script
    from hybrid_retriever import retrieve_hybrid, build_hybrid_context, fetch_all_lines_for_parents
    from citation_injector import get_citations, inject_citations_text

# =========================
# CONFIG & SETUP
# =========================

BASE_DIR = Path(__file__).resolve().parent.parent
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR.parent.parent / ".env"
SESSIONS_DIR = BASE_DIR.parent / "sessions"

# Config from Env
CITATION_EXPAND_MAX_LINES = int(os.environ.get("CITATION_EXPAND_MAX_LINES", 500))
CITATION_MAX_DISPLAY = int(os.environ.get("CITATION_MAX_DISPLAY", 8))

def load_api_key():
    """Parse .env for Gemini API Key."""
    # Try looking in multiple locations
    potential_paths = [
        ENV_PATH,
        BASE_DIR.parent / ".env",
        Path("d:/PROJECTS IN MOTION/MarcusGarvey App WWMD/.env")
    ]
    
    target_path = None
    for p in potential_paths:
        if p.exists():
            target_path = p
            break
            
    if not target_path:
        print(f"DEBUG: .env not found in {potential_paths}")
        return None
        
    import re
    content = target_path.read_text(encoding="utf-8")
    # Handle both quoted and unquoted values
    # Match GEMINI_API_KEY=value or GEMINI_API_KEY="value"
    matches = re.findall(r'GEMINI_API_KEY\s*=\s*"?([^"\n]+)"?', content)
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
Your goal is to answer the user's question using **ONLY** the provided Reference Chunks.

## THE PROSECUTOR'S STANDARD
1. Admissible Evidence Only: Do not use outside knowledge. If the answer is not in the chunks, state so.
2. Fidelity: Reflect the tone, philosophy, and precise language of Marcus Garvey.
3. No Hallucinations: Do not invent quotes or facts.

## CONTEXT
{context}

## USER QUESTION
{query}

## INSTRUCTIONS
- Provide a comprehensive, eloquent answer in the voice of Marcus Garvey.
- Do NOT add citation footnotes yourself; the system will handle that.
- If the text supports it, be bold, visionary, and empowering.
- If the text is silent, say: "The archives are silent on this specific matter."

Answer:
"""

def ask_marcus(query, debug_mode='expand', output_file=None):
    """
    Main entry point for asking a question.
    Returns the JSON response dict.
    """
    start_time = time.time()
    api_key = load_api_key()
    
    # 1. Retrieval
    results = retrieve_hybrid(query, max_results=15)
    
    # 2. Context Building & Expansion
    context_data = build_hybrid_context(results)
    
    expanded_lines = []
    if debug_mode == 'expand':
        parent_ids = list(set(r['parent_chunk_id'] for r in results))
        expanded_lines = fetch_all_lines_for_parents(parent_ids)
        # Limit expansion
        expanded_lines = expanded_lines[:CITATION_EXPAND_MAX_LINES]
    elif debug_mode == 'strict':
        expanded_lines = [{'text': r['line_content'], 'locator': r['line_locator'], 'source': r['anchor_id']} for r in results]
    
    # 3. AI Generation
    prompt = HYBRID_PROMPT_TEMPLATE.format(context=context_data['context'], query=query)
    raw_response = call_gemini_rest(api_key, prompt)
    
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
            "latency_ms": int((time.time() - start_time) * 1000)
        }
    }
    
    # 6. Session Vault
    vault_path = save_to_session_vault(query, json_output)
    
    # Add vault path to meta logic if needed, but for now we return the object
    # If called via CLI, we might print or save
    if output_file:
         Path(output_file).write_text(json.dumps(json_output, indent=2), encoding="utf-8")
         
    return json_output

# =========================
# WWMD LENS MODE
# =========================

LENS_PROMPT_TEMPLATE = """You are the Voice of the Marcus Garvey ARK.
Analyze the following user situation through the {mode} LENS of Marcus Garvey's philosophy.

## CONTEXT from ARK
{context}

## USER SITUATION
"{situation}"

## INSTRUCTIONS
Output a valid JSON object strictly following this schema:
{{
  "principle": "The specific Garveyite principle that applies here (e.g., self-reliance, industrial organization).",
  "historicalAnalogy": "A relevant historical parallel from the U.N.I.A. or Garvey's life based on the context.",
  "actionSteps": [
    {{"id": "1", "text": "Specific, actionable advice step 1", "completed": false}},
    {{"id": "2", "text": "Specific, actionable advice step 2", "completed": false}},
    {{"id": "3", "text": "Specific, actionable advice step 3", "completed": false}}
  ],
  "mirrorQuestions": [
    "A reflective question challenging the user's approach?",
    "A question about long-term impact?"
  ]
}}

- Do NOT include markdown code blocks (```json). Just the raw JSON string.
- Ensure the advice is practical but grounded in the 1920s philosophy of independence.
"""

def ask_marcus_lens(situation, mode="Personal"):
    """
    Analyzes a situation and returns structured JSON for WWMD page.
    """
    start_time = time.time()
    api_key = load_api_key()
    
    # 1. Retrieval (Treat situation as query)
    search_query = f"{situation} {mode} organization success"
    results = retrieve_hybrid(search_query, max_results=10)
    
    # 2. Context
    context_data = build_hybrid_context(results)
    
    # 3. AI Generation
    prompt = LENS_PROMPT_TEMPLATE.format(
        context=context_data['context'], 
        situation=situation,
        mode=mode
    )
    
    raw_response = call_gemini_rest(api_key, prompt)
    
    # 4. Clean and Parse JSON
    try:
        cleaned = raw_response.replace('```json', '').replace('```', '').strip()
        data = json.loads(cleaned)
        
        # Inject receipts (citations)
        receipts = []
        for r in results[:3]:
            loc = r['line_locator']
            page = loc.split(':')[-1] if ':' in loc else "0"
            receipts.append({
                "id": r['anchor_id'],
                "anchorId": r['anchor_id'],
                "title": f"Source {r['anchor_id']}",
                "type": "archive",
                "excerpt": r['line_content'],
                "year": 1920,
                "page": page,
                "locator": loc
            })
            
        data['receipts'] = receipts
        return data
        
    except json.JSONDecodeError:
        return {
            "principle": "Protocol Error",
            "historicalAnalogy": "The system could not structure the answer correctly. Raw: " + raw_response[:100],
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
        # Legacy Text Output
        print("\n" + "="*60)
        print("WWMD ANSWER (JSON-Powered)")
        print("="*60 + "\n")
        print(inject_citations_text(response['answer'], response['citations']))
        print(f"\n[Vault]: Saved to session vault")

if __name__ == "__main__":
    main()
