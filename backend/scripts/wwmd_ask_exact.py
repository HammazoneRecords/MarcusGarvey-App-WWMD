#!/usr/bin/env python3
"""
WWMD (What Would Marcus Do) RAG Agent - EXACT QUOTE MODE
Version: 2.0 (Citation-Accurate with Verification)

Two-Phase Approach:
1. Script extracts exact quotes with verified citations
2. AI expands on those quotes (cannot modify citations)
3. Verification checks quotes weren't changed

Usage:
  python scripts/wwmd_ask_exact.py "What is the view on economic independence?"
"""

import sqlite3
import sys
import os
import argparse
from pathlib import Path

# Windows console safety
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Import our utilities
from quote_extractor import extract_keywords, extract_quote_from_chunk, build_evidence_bundle
from quote_verifier import verify_quotes, format_verification_report

# =========================
# CONFIG & SETUP
# =========================

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "memory.db"
ENV_PATH = BASE_DIR.parent / ".env"

def load_api_key():
    """Parse .env for Gemini API Key."""
    if not ENV_PATH.exists():
        print(f"ERROR: .env not found at {ENV_PATH}")
        print("Please create it with: GEMINI_API_KEY=\"AIza...\"")
        sys.exit(1)
        
    import re
    content = ENV_PATH.read_text(encoding="utf-8")
    matches = re.findall(r'GEMINI_API_KEY\s*=\s*"([^"]+)"', content)
    if matches:
        return matches[-1]
    
    print("ERROR: Could not parse 'GEMINI_API_KEY' from .env")
    sys.exit(1)

# =========================
# GENERATION CLIENT
# =========================

def call_gemini_rest(api_key, full_text, model_name="gemini-2.5-flash"):
    """Call Gemini API using REST."""
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
    """Retrieve chunks from SQLite using LIKE."""
    conn = sqlite3.connect(DB_PATH)
    
    terms = extract_keywords(query_terms)
    if not terms:
        terms = [query_terms]

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
    
    # Convert to dict format
    chunks = []
    for row in rows:
        chunks.append({
            'chunk_id': row[0],
            'anchor_id': row[1],
            'anchor_locator': row[2],
            'content': row[3]
        })
    
    return chunks

# =========================
# TWO-PHASE RAG
# =========================

EXACT_QUOTE_PROMPT_TEMPLATE = """You are the Voice of the Marcus Garvey ARK.

You are provided with EXACT QUOTES from the archive with VERIFIED CITATIONS.

STRICT RULES - READ CAREFULLY:
1. When referencing these quotes, use them WORD-FOR-WORD inside double quotes ""
2. Use ONLY the citations provided - copy them EXACTLY as [CITATION X]
3. You may EXPAND and EXPLAIN the quotes in your own words OUTSIDE the quotes
4. DO NOT paraphrase or modify the quoted text
5. If a quote doesn't fully answer the question, state what's covered and what's not

FORMAT YOUR RESPONSE:
- Start with the exact quote(s) in double quotes ""
- Add [CITATION X] immediately after each quote
- Then expand/explain in your own words
- Connect multiple quotes if relevant

VERIFIED QUOTES:
{evidence_bundle}

USER QUESTION: {query}

Your answer should:
1. Quote the exact text relevant to the question (in double quotes)
2. Cite using [CITATION X] format
3. Expand on what the quote means
"""

def main():
    parser = argparse.ArgumentParser(description="WWMD RAG Agent (Exact Quote Mode)")
    parser.add_argument("query", help="User question")
    parser.add_argument("--skip-verification", action="store_true", 
                       help="Skip post-processing verification")
    args = parser.parse_args()
    
    # 1. Setup
    api_key = load_api_key()
    
    # 2. Retrieve chunks
    print(f"Searching ARK for: '{args.query}'...")
    chunks = retrieve_context(args.query)
    
    if not chunks:
        print("No relevant documents found in ARK.")
        return
    
    print(f"Found {len(chunks)} relevant chunks.")
    
    # 3. Extract exact quotes from chunks
    print("Extracting exact quotes...")
    keywords = extract_keywords(args.query)
    quotes = []
    for chunk in chunks:
        quote_data = extract_quote_from_chunk(chunk, keywords)
        quotes.append(quote_data)
    
    # Sort by keyword matches
    quotes.sort(key=lambda x: x['keyword_matches'], reverse=True)
    
    # Take top 5 most relevant quotes
    top_quotes = quotes[:5]
    
    print(f"Selected {len(top_quotes)} most relevant quotes.")
    
    # 4. Build evidence bundle
    evidence_bundle = build_evidence_bundle(top_quotes)
    
    # 5. Call AI with exact quotes
    print("Consulting Gemini for expansion...")
    final_prompt = EXACT_QUOTE_PROMPT_TEMPLATE.format(
        evidence_bundle=evidence_bundle,
        query=args.query
    )
    
    answer = call_gemini_rest(api_key, final_prompt)
    
    # 6. Display answer
    print("\n" + "="*60)
    print("WWMD ANSWER (Citation-Verified)")
    print("="*60 + "\n")
    print(answer)
    print("\n" + "="*60)
    
    # 7. Verify quotes weren't modified
    if not args.skip_verification:
        print("\nVerifying quote accuracy...")
        verification = verify_quotes(answer, top_quotes)
        
        report = format_verification_report(verification)
        print(report)
        
        if not verification['is_valid']:
            print("⚠⚠⚠ WARNING: Quote modifications detected! See report above.")
            print("The AI may have altered the original quotes.")
            sys.exit(1)
        else:
            print("✓ Citation verification passed!")

if __name__ == "__main__":
    main()
