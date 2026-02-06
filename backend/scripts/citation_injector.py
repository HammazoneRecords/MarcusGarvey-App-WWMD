#!/usr/bin/env python3
"""
Citation Injector - Post-processes AI response to find citations
Returns structured data and handles scoring.
"""
import re
from typing import List, Dict, Tuple, Any

def score_citation(line_text: str, query_terms: List[str]) -> int:
    """
    Score a potential citation based on relevance and quality.
    
    Heuristic:
    +3 if matches query key terms
    +2 if contains directive language (must, foundation, program)
    -2 if generic/short
    """
    score = 0
    text_lower = line_text.lower()
    
    # Check query terms
    for term in query_terms:
        if term in text_lower:
            score += 3
            
    # Check directive language
    directives = ['must', 'foundation', 'salvation', 'program', 'essential', 'imperative', 'duty']
    if any(d in text_lower for d in directives):
        score += 2
        
    # Penalize short/generic lines
    if len(line_text) < 40:
        score -= 2
        
    return score

def find_text_matches(ai_response: str, line_data: List[Dict], query_terms: List[str] = None) -> List[Dict]:
    """
    Find which lines from the evidence were referenced.
    Returns list of dicts: {text, locator, source, score, match_type}
    """
    matches = []
    ai_response_lower = ai_response.lower()
    
    # Deduplication set
    seen_locators = set()
    
    for line_info in line_data:
        line_text = line_info['text']
        locator = line_info['locator']
        
        if locator in seen_locators:
            continue
            
        line_lower = line_text.lower()
        matched = False
        match_type = ""
        
        # 1. Exact substring match
        if line_lower in ai_response_lower:
            matched = True
            match_type = "exact"
            
        if not matched:
            # 2. Significant overlap (Sliding Window)
            words = line_text.split()
            if len(words) >= 4:
                # Try finding a 5-gram or 6-gram
                for n in range(min(len(words), 8), 3, -1):
                    if matched: break
                    for i in range(len(words) - n + 1):
                        phrase = ' '.join(words[i:i+n])
                        if phrase.lower() in ai_response_lower:
                            matched = True
                            match_type = "partial_ngram"
                            break
                            
        if not matched:
            # 3. Fuzzy Set Match
            stopwords = {'the', 'was', 'to', 'of', 'and', 'in', 'is', 'a', 'so', 'they', 'could', 'their'}
            line_tokens = set(w.lower() for w in words if w.lower() not in stopwords)
            if len(line_tokens) >= 3:
                response_tokens = set(ai_response_lower.split())
                common = line_tokens.intersection(response_tokens)
                if len(common) / len(line_tokens) > 0.75:
                    matched = True
                    match_type = "fuzzy_set"

        if matched:
            score = score_citation(line_text, query_terms or [])
            matches.append({
                "excerpt": line_text,
                "loc": locator,
                "source_id": line_info.get('source', 'Unknown'),
                "score": score,
                "match_type": match_type
            })
            seen_locators.add(locator)

    # Sort by score descending
    matches.sort(key=lambda x: x['score'], reverse=True)
    return matches

def get_citations(ai_response: str, line_data: List[Dict], query_terms: List[str] = None) -> List[Dict]:
    """Main entry point to get structured citations."""
    return find_text_matches(ai_response, line_data, query_terms)

def inject_citations_text(ai_response: str, citations: List[Dict]) -> str:
    """Legacy helper: format citations as text block."""
    if not citations:
        return ai_response + "\n\n⚠ Note: No direct citations could be automatically generated."
    
    citation_key = "\n\n" + "="*60 + "\n"
    citation_key += "CITATIONS (Quality Scored)\n"
    citation_key += "="*60 + "\n"
    
    for i, c in enumerate(citations, 1):
        citation_key += f"\n[{i}] {c['loc']} (Score: {c['score']})\n"
        citation_key += f"    Source: {c['source_id']}\n"
        citation_key += f"    \"{c['excerpt'][:100]}{'...' if len(c['excerpt']) > 100 else ''}\"\n"
        
    return ai_response + citation_key
