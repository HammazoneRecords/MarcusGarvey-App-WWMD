#!/usr/bin/env python3
"""
WWMD (What Would Marcus Do) RAG Agent
Version: 1.0 (Strict Constructionist)

Implements "The Prosecutor's Standard":
1. Retrieval from ARK memory.db
2. Strict Context-Only Prompting
3. Citation Requirement

Usage:
  python scripts/wwmd_ask.py "What is the view on economic independence?"
"""

import sqlite3
import sys
import os
import argparse
import re
from pathlib import Path

# =========================
# CONFIG & SETUP
# =========================

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "memory.db"

# Use standard .env file at project root
ENV_PATH = BASE_DIR.parent / ".env"

def load_api_key():
    """Parse .env for Gemini API Key."""
    if not ENV_PATH.exists():
        print(f"ERROR: .env not found at {ENV_PATH}")
        print("Please create it with: GEMINI_API_KEY=\"AIza...\"")
        sys.exit(1)
        
    content = ENV_PATH.read_text(encoding="utf-8")
    
    # Try finding all matches for GEMINI_API_KEY = "..." or gemini api key : ...
    # We prioritize the new format: GEMINI_API_KEY ="..."
    
    # Pattern 1: GEMINI_API_KEY\s*=\s*"([^"]+)"
    matches = re.findall(r'GEMINI_API_KEY\s*=\s*"([^"]+)"', content)
    if matches:
        # Take the last one (as user appended the new key at the bottom)
        return matches[-1]

    # Fallback to old pattern
    match = re.search(r"gemini\s+api\s+key\s*:\s*([A-Za-z0-9\-_]+)", content, re.IGNORECASE)
    if match:
        return match.group(1)
        
    print("ERROR: Could not parse 'GEMINI_API_KEY' from env.local")
    sys.exit(1)

# =========================
# GENERATION CLIENT
# =========================

def call_gemini(api_key, system_instruction, user_prompt):
    """
    Call Gemini API using REST fallback.
    Tries multiple model variants if 404 occurs.
    """
    full_prompt = f"{system_instruction}\n\nUSER QUERY: {user_prompt}"
    
    # Use the model verified via ListModels API
    # Fallback to other models if primary fails
    models = [
        "gemini-2.5-flash",
        "gemini-2.0-flash-exp",
        "gemini-2.5-pro"
    ]
    
    for model in models:
        print(f"  Attempting model: {model}...")
        result = call_gemini_rest(api_key, full_prompt, model)
        if not result.startswith("ERROR"):
            return result
        
        if "404" not in result:
             # If it's not a 404 (e.g. 403 Key Invalid), stop trying
            return result
            
        print(f"  {model} failed (404), trying next...")
        
    return "ERROR: All models failed."

def call_gemini_rest(api_key, full_text, model_name):
    import json
    import urllib.request
    import urllib.error
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
    
    headers = {"Content-Type": "application/json"}
    data = {
        "contents": [{
            "parts": [{"text": full_text}]
        }]
    }
    
    try:
        req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers=headers)
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            try:
                return result['candidates'][0]['content']['parts'][0]['text']
            except (KeyError, IndexError):
                return f"ERROR: Unexpected response format: {result}"
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        return f"ERROR: API call failed: HTTP {e.code} - {error_body}"
    except Exception as e:
        return f"ERROR: Connection failed: {e}"

# =========================
# RETRIEVAL LOGIC
# =========================

def retrieve_context(query_terms):
    """Retreieve chunks from SQLite using FTS or LIKE."""
    conn = sqlite3.connect(DB_PATH)
    
    # Simple keyword scoring
    # Find chunks containing any of the terms
    # Score = count of terms present
    
    # Sanitize terms
    terms = [t for t in query_terms.split() if len(t) > 3]
    if not terms:
         terms = [query_terms]

    # Construct dynamic query
    conditions = []
    params = []
    for term in terms:
        conditions.append("content LIKE ?")
        params.append(f"%{term}%")
    
    where_clause = " OR ".join(conditions)
    
    sql = f"""
    SELECT chunk_id, anchor_id, anchor_locator, content
    FROM chunks
    WHERE {where_clause}
    LIMIT 15
    """
    
    cursor = conn.execute(sql, params)
    rows = cursor.fetchall()
    conn.close()
    
    return rows

def format_context(rows):
    """Format chunks for the evidence board."""
    evidence = ""
    for i, row in enumerate(rows, 1):
        cid, anchor_id, locator, content = row
        # Clean content (remove newlines usually)
        clean_content = content.replace("\n", " ").strip()
        evidence += f"[ID:{i}] [Source:{anchor_id} Loc:{locator}]\n{clean_content}\n\n"
    return evidence

# =========================
# MAIN AGENT
# =========================

SYSTEM_PROMPT_TEMPLATE = """You are the Voice of the Marcus Garvey ARK.
You are provided with a set of Reference Chunks (EVIDENCE BOARD).

CORE DIRECTIVES ("The Prosecutor's Standard"):
1. Answer the user's question using **ONLY** the provided Reference Chunks.
2. If the answer is not in the chunks, state: "The provided sources do not contain information on this topic."
3. Do NOT use your prior knowledge. Do NOT hallucinate quotes.
4. Every response must be traceable back to the ark database.

CITATION RULE:
You must append a citation `[Source: <Title>, Locator: <Loc>]` to every distinct claim.

EVIDENCE BOARD:
{context}
"""

def main():
    parser = argparse.ArgumentParser(description="WWMD RAG Agent")
    parser.add_argument("query", help="User question")
    args = parser.parse_args()
    
    # 1. Setup
    api_key = load_api_key()
    
    # 2. Retrieve
    print(f"Searching ARK for: '{args.query}'...")
    chunks = retrieve_context(args.query)
    
    if not chunks:
        print("No relevant documents found in ARK.")
        return
    
    print(f"Found {len(chunks)} relevant chunks.")
    
    # 3. Assemble Context
    context_str = format_context(chunks)
    
    # 4. Construct Prompt
    final_system_prompt = SYSTEM_PROMPT_TEMPLATE.format(context=context_str)
    
    # 5. Generate
    print("Consulting Gemini...")
    answer = call_gemini(api_key, final_system_prompt, f"User Question: {args.query}")
    
    print("\n" + "="*60)
    print("WWMD ANSWER")
    print("="*60 + "\n")
    print(answer)
    print("\n" + "="*60)

if __name__ == "__main__":
    main()
