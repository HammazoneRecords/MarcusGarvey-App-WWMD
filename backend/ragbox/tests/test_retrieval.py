#!/usr/bin/env python3
"""
Tests for hybrid retrieval functionality.
"""

import sys
from pathlib import Path

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from hybrid_retriever import extract_keywords, retrieve_hybrid, build_hybrid_context

def test_extract_keywords():
    """Test keyword extraction."""
    query = "What did Marcus Garvey say about unity and strength?"
    keywords = extract_keywords(query)
    
    assert "marcus" in keywords
    assert "garvey" in keywords
    assert "unity" in keywords
    assert "strength" in keywords
    
    # Stopwords should be removed
    assert "what" not in keywords
    assert "did" not in keywords
    assert "about" not in keywords
    
    print("✓ test_extract_keywords passed")

def test_extract_keywords_min_length():
    """Test keyword minimum length filtering."""
    query = "AI is a tool"
    keywords = extract_keywords(query, min_length=3)
    
    assert "tool" in keywords
    # "AI" and "is" should be filtered (too short or stopword)
    assert "ai" not in keywords
    
    print("✓ test_extract_keywords_min_length passed")

def test_build_hybrid_context():
    """Test context building from results."""
    # Mock results
    results = [
        {
            'line_chunk_id': 'test:line:1',
            'line_content': 'This is line one.',
            'line_locator': 'test:page:1:line:1',
            'parent_chunk_id': 'test:chunk:1',
            'line_number': 1,
            'parent_content': 'This is line one.\nThis is line two.',
            'anchor_id': 'test_doc'
        },
        {
            'line_chunk_id': 'test:line:2',
            'line_content': 'This is line two.',
            'line_locator': 'test:page:1:line:2',
            'parent_chunk_id': 'test:chunk:1',
            'line_number': 2,
            'parent_content': 'This is line one.\nThis is line two.',
            'anchor_id': 'test_doc'
        }
    ]
    
    context_data = build_hybrid_context(results)
    
    assert 'lines' in context_data
    assert 'context' in context_data
    assert len(context_data['lines']) == 2
    assert context_data['lines'][0]['text'] == 'This is line one.'
    
    print("✓ test_build_hybrid_context passed")

if __name__ == "__main__":
    test_extract_keywords()
    test_extract_keywords_min_length()
    test_build_hybrid_context()
    print("\n✓ All retrieval tests passed!")
