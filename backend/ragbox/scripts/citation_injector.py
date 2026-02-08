#!/usr/bin/env python3
"""
Citation Injector - Post-processes AI response to find citations
Returns structured data and handles scoring.
"""
import re
from typing import List, Dict, Tuple, Any

def is_metadata_or_frontmatter(line_text: str) -> bool:
    """
    Detect if a line is publisher metadata, copyright, or frontmatter.
    Returns True if the line should be excluded from citations.
    
    Filters out:
    - Copyright statements, publisher info, ISBN
    - Environmental/printing statements
    - Table of contents, indices, headers
    - Question headers (e.g., "How successful was...?")
    - Fragments and incomplete sentences
    - Single words or very short labels
    """
    text_lower = line_text.lower().strip()
    text_stripped = text_lower.strip()
    
    # Copyright and publication metadata
    metadata_patterns = [
        'copyright ©',
        'all rights reserved',
        'dover publications',
        'dover thrift',
        'isbn',
        'published by',
        'printed in',
        'earth-friendly',
        'environmental defense',
        'recycled paper',
        'post-consumer waste',
        'international freight',
        'global air pollution',
        'manufacturing books',
        'printing on recycled',
        'fossil fuels',
        'consumption of trees',
        'paper calculator',
        'thrift editions',
        'contents',
        'table of contents',
        'index of',
        'page number',
    ]
    
    # Check for metadata patterns
    for pattern in metadata_patterns:
        if pattern in text_lower:
            return True
    
    # Filter out question headers (lines starting with How, What, Why, Where, Who)
    question_starters = ['how ', 'what ', 'why ', 'where ', 'who ', 'when ']
    if any(text_lower.startswith(q) for q in question_starters):
        # If it ends with a question mark AND is short, it's likely a question header, not a citation
        if text_lower.endswith('?') and len(text_lower) < 100:
            return True
    
    # Very short lines are likely labels, headers, or fragments
    if len(text_stripped) < 15:
        return True
    
    # Lines that are obviously fragments (start with lowercase, don't form complete thought)
    # e.g., "together to rebuild their great nation" (continuation from previous line)
    if text_stripped and text_stripped[0].islower() and not any(text_lower.startswith(word) for word in ['the ', 'a ', 'an ', 'and ', 'or ', 'but ']):
        # If starts with lowercase word that's not an article/conjunction, likely a fragment
        first_word = text_stripped.split()[0] if text_stripped.split() else ''
        # Check if this looks like a continuation (starts with verb ending or unusual word)
        if first_word.endswith('er') or first_word.endswith('ing') or first_word in ['together', 'still', 'also', 'never', 'always']:
            return True
    
    # Check for typical copyright year pattern (© 2004)
    if re.search(r'©\s*\d{4}', text_lower):
        return True
    
    return False

def score_citation(line_text: str, query_terms: List[str]) -> int:
    """
    Score a potential citation based on relevance and quality.
    
    Scoring heuristic:
    - Query term matches: +6 per unique match (high relevance)
    - Complete sentence (ends with . ? !): +5 bonus
    - Directive/authoritative language: +3 per instance
    - Substantive length (100+ chars): +2-4 points
    - Garveyite vocabulary: +4 per term
    - Capital letter start (complete thought): +2
    
    Penalties:
    - Too short (<50 chars): -5
    - Lowercase start (fragment): -3
    - No period/punctuation (incomplete): -4
    - No query relevance: -2
    - Metadata: -100 (skip entirely)
    """
    score = 0
    text_lower = line_text.lower()
    text_stripped = line_text.strip()
    words = line_text.split()
    length = len(line_text)
    
    # SKIP if metadata
    if is_metadata_or_frontmatter(line_text):
        return -100  # Signal to skip this entirely
    
    # Query term matches (high weight for relevance)
    query_matches = sum(1 for term in query_terms if term in text_lower and len(term) > 2)
    if query_matches > 0:
        score += (6 * query_matches)  # Increased weight
    else:
        # If no query term match, slightly penalize (it's tangential)
        score -= 2
    
    # Complete sentence structure is crucial
    if text_stripped.endswith(('.', '?', '!')):
        score += 5  # Increased bonus for complete sentences
    else:
        score -= 4  # Heavy penalty for fragments
    
    # Starts with capital letter = likely complete thought
    if text_stripped and text_stripped[0].isupper():
        score += 2
    else:
        score -= 3  # Likely a fragment or continuation
    
    # Substantive length (longer = more informative)
    if length >= 150:
        score += 4  # Very substantive
    elif length >= 100:
        score += 2  # Substantial
    elif length >= 60:
        score += 1  # Moderate
    elif length < 50:
        score -= 5  # Too short, likely fragment
    
    # Directive/authoritative language
    directives = ['must', 'foundation', 'salvation', 'program', 'essential', 'imperative', 'duty', 
                  'shall', 'will', 'organization', 'movement', 'universal', 'nation', 'race',
                  'liberate', 'emancipate', 'commerce', 'self-reliance', 'independent', 'establish']
    directive_count = sum(1 for d in directives if d in text_lower)
    score += (3 * directive_count)
    
    # Garveyite/historical vocabulary
    garvey_vocab = ['garvey', 'unia', 'race', 'negro', 'africa', 'back-to-africa', 
                    'self-determination', 'black nationalism', 'industrial', 'economic',
                    'liberty', 'independence', 'people', 'build', 'establish', 'create',
                    'diaspora', 'organization', 'movement']
    vocab_count = sum(1 for v in garvey_vocab if v in text_lower)
    score += (4 * vocab_count)
    
    # Multiple short words in sequence = likely fragment
    # "You can shackle the hands" - dramatic but not substantive
    if len(words) > 0 and len(words) <= 8 and all(len(w) <= 7 for w in words):
        if score < 15:  # Only penalize if not highly relevant
            score -= 3
    
    return max(-100, score)  # Allow negative scores to signal skip or poor quality

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
        
        # SKIP metadata/publisher information entirely
        if is_metadata_or_frontmatter(line_text):
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
