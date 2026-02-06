#!/usr/bin/env python3
"""
Quote Extraction Utilities
Extracts exact sentences/paragraphs from chunks with verified citations
"""
import re
from typing import List, Dict, Any

def extract_sentences(text: str) -> List[str]:
    """
    Extract complete sentences from text.
    Handles ., !, ? as sentence boundaries.
    """
    # Simple sentence boundary detection
    # Split on . ! ? followed by space or end of string
    sentences = re.split(r'(?<=[.!?])\s+', text)
    # Clean up empty strings and whitespace
    sentences = [s.strip() for s in sentences if s.strip()]
    return sentences

def find_matching_sentences(text: str, keywords: List[str], min_match: int = 1) -> List[str]:
    """
    Find sentences containing at least min_match keywords.
    Returns list of matching sentences.
    """
    sentences = extract_sentences(text)
    keywords_lower = [k.lower() for k in keywords]
    
    matching = []
    for sentence in sentences:
        sentence_lower = sentence.lower()
        matches = sum(1 for kw in keywords_lower if kw in sentence_lower)
        if matches >= min_match:
            matching.append(sentence)
    
    return matching

def extract_quote_from_chunk(chunk: Dict[str, Any], keywords: List[str]) -> Dict[str, Any]:
    """
    Extract the best matching quote from a chunk.
    
    Args:
        chunk: {chunk_id, anchor_id, anchor_locator, content}
        keywords: List of query keywords
    
    Returns:
        {chunk_id, text, source, locator, keyword_matches}
    """
    content = chunk['content']
    
    # Find matching sentences
    matching_sentences = find_matching_sentences(content, keywords, min_match=1)
    
    if not matching_sentences:
        # If no sentences match, return first few sentences as context
        all_sentences = extract_sentences(content)
        quote_text = ' '.join(all_sentences[:2]) if len(all_sentences) >= 2 else content[:300]
    else:
        # Return the sentence with most keyword matches
        def count_matches(sentence):
            return sum(1 for kw in keywords if kw.lower() in sentence.lower())
        
        best_sentence = max(matching_sentences, key=count_matches)
        quote_text = best_sentence
        
        # Add surrounding context if sentence is short
        if len(quote_text) < 100 and len(matching_sentences) > 1:
            quote_text = ' '.join(matching_sentences[:2])
    
    return {
        'chunk_id': chunk['chunk_id'],
        'text': quote_text.strip(),
        'source': chunk['anchor_id'],
        'locator': chunk['anchor_locator'],
        'keyword_matches': sum(1 for kw in keywords if kw.lower() in quote_text.lower())
    }

def build_evidence_bundle(quotes: List[Dict[str, Any]]) -> str:
    """
    Format quotes into structured evidence bundle for AI.
    Each quote gets a unique ID for tracking.
    """
    if not quotes:
        return "No quotes found."
    
    formatted = ""
    for i, quote in enumerate(quotes, 1):
        formatted += f"[QUOTE {i}]\n"
        formatted += f'"{quote["text"]}"\n'
        formatted += f"[CITATION {i}]: [Source: {quote['source']}, Locator: {quote['locator']}]\n"
        formatted += f"[CHUNK_ID {i}]: {quote['chunk_id'][:16]}...\n\n"
    
    return formatted

def extract_keywords(query: str, min_length: int = 3) -> List[str]:
    """
    Extract keywords from user query.
    Removes common stopwords and short words.
    """
    stopwords = {'what', 'is', 'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 
                 'to', 'for', 'of', 'with', 'by', 'from', 'did', 'say', 'about'}
    
    # Split and clean
    words = re.findall(r'\b\w+\b', query.lower())
    
    # Filter out stopwords and short words
    keywords = [w for w in words if w not in stopwords and len(w) >= min_length]
    
    return keywords
