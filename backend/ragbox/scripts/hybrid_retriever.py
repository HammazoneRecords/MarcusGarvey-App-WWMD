#!/usr/bin/env python3
"""
Hybrid Retrieval System
Retrieves line chunks + their parent chunks for context
"""
import os
import sqlite3
from pathlib import Path
from typing import List, Dict, Any

DB_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "memory.db"

def extract_keywords(query: str, min_length: int = 3) -> List[str]:
    """Extract keywords from query."""
    import re
    stopwords = {'what', 'is', 'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 
                 'to', 'for', 'of', 'with', 'by', 'from', 'did', 'say', 'about', 'how'}
    words = re.findall(r'\b\w+\b', query.lower())
    keywords = [w for w in words if w not in stopwords and len(w) >= min_length]
    
    # Enhanced expansion
    expanded = []
    for kw in keywords:
        expanded.append(kw)
        if kw == 'unity': expanded.append('unite')
        if kw == 'unite': expanded.append('unity')
        if kw == 'economic': expanded.append('economy')
        if kw == 'economy': expanded.append('economic')
        if kw == 'negro': expanded.extend(['black', 'race', 'african'])
        if kw == 'black': expanded.extend(['negro', 'race', 'african'])
        if kw == 'africa': expanded.extend(['motherland', 'home'])
        if kw == 'industry': expanded.extend(['industrial', 'commercial'])
    
    return list(set(expanded))

def retrieve_hybrid(query: str, max_results: int = 10) -> List[Dict[str, Any]]:
    """
    Retrieve line chunks + parent chunks.
    
    Returns list of:
    {
        'line_chunk_id': str,
        'line_content': str,
        'line_locator': str,
        'parent_chunk_id': str,
        'parent_content': str,
        'anchor_id': str
    }
    """
    conn = sqlite3.connect(DB_PATH)
    keywords = extract_keywords(query)
    
    if not keywords:
        keywords = [query]
    
    # Build WHERE clause for line search
    conditions = []
    params = []
    for kw in keywords:
        conditions.append("lc.content LIKE ?")
        params.append(f"%{kw}%")
    
    where_clause = " OR ".join(conditions)
    
    sql = f"""
    SELECT 
        lc.line_chunk_id,
        lc.content as line_content,
        lc.anchor_locator as line_locator,
        lc.parent_chunk_id,
        lc.line_number,
        c.content as parent_content,
        c.anchor_id
    FROM line_chunks lc
    JOIN chunks c ON lc.parent_chunk_id = c.chunk_id
    WHERE {where_clause}
    LIMIT ?
    """
    
    params.append(max_results)
    
    cursor = conn.execute(sql, params)
    rows = cursor.fetchall()
    conn.close()
    
    results = []
    for row in rows:
        results.append({
            'line_chunk_id': row[0],
            'line_content': row[1],
            'line_locator': row[2],
            'parent_chunk_id': row[3],
            'line_number': row[4],
            'parent_content': row[5],
            'anchor_id': row[6]
        })
    
    return results

def build_hybrid_context(results: List[Dict]) -> Dict[str, Any]:
    """
    Build context for AI with lines + parents.
    
    Returns:
    {
        'lines': [{'id': 1, 'text': '...', 'locator': '...'}],
        'context': str (full parent chunks)
    }
    """
    lines = []
    parent_contents = set()
    
    for i, result in enumerate(results, 1):
        lines.append({
            'id': i,
            'text': result['line_content'],
            'locator': result['line_locator'],
            'line_chunk_id': result['line_chunk_id']
        })
        parent_contents.add(result['parent_content'])
    
    # Combine unique parent contents — cap at ~4000 chars so the model has room to generate
    CONTEXT_CHAR_LIMIT = int(os.environ.get("RAG_CONTEXT_CHAR_LIMIT", "4000"))
    sorted_contents = sorted(parent_contents, key=len, reverse=True)
    kept, total = [], 0
    for chunk in sorted_contents:
        if total + len(chunk) > CONTEXT_CHAR_LIMIT:
            break
        kept.append(chunk)
        total += len(chunk)
    context = "\n\n---\n\n".join(kept) if kept else "\n\n---\n\n".join(list(parent_contents)[:3])
    
    return {
        'lines': lines,
        'context': context
    }

def fetch_all_lines_for_parents(parent_ids: List[str]) -> List[Dict[str, Any]]:
    """
    Fetch ALL lines belonging to the specified parent chunks.
    This ensures the citation injector knows about every line the AI can see.
    """
    if not parent_ids:
        return []
    
    conn = sqlite3.connect(DB_PATH)
    
    # Dynamically build placeholders for IN clause
    placeholders = ','.join(['?'] * len(parent_ids))
    
    sql = f"""
    SELECT 
        content,
        anchor_locator,
        anchor_id
    FROM line_chunks
    WHERE parent_chunk_id IN ({placeholders})
    """
    
    cursor = conn.execute(sql, parent_ids)
    rows = cursor.fetchall()
    conn.close()
    
    all_lines = []
    for row in rows:
        all_lines.append({
            'text': row[0],
            'locator': row[1],
            'source': row[2]
        })
    
    return all_lines
