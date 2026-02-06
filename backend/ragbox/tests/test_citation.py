#!/usr/bin/env python3
"""
Tests for citation injection functionality.
"""

import sys
from pathlib import Path

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from citation_injector import score_citation, find_text_matches, get_citations

def test_score_citation():
    """Test citation scoring."""
    
    # Test with query terms
    line = "Unity is the foundation of success"
    query_terms = ["unity", "foundation"]
    score = score_citation(line, query_terms)
    
    # Should get +3 for each query term = 6
    assert score >= 6
    
    print("✓ test_score_citation passed")

def test_score_citation_directive():
    """Test scoring with directive language."""
    
    line = "You must build a strong foundation"
    query_terms = ["foundation"]
    score = score_citation(line, query_terms)
    
    # Should get +3 for "foundation" and +2 for "must" = 5
    assert score >= 5
    
    print("✓ test_score_citation_directive passed")

def test_find_text_matches_exact():
    """Test exact match citation finding."""
    
    ai_response = "The foundation of success is unity and strength."
    
    line_data = [
        {
            'text': 'The foundation of success is unity',
            'locator': 'test:page:1:line:1',
            'source': 'test_doc'
        },
        {
            'text': 'Unrelated line',
            'locator': 'test:page:1:line:2',
            'source': 'test_doc'
        }
    ]
    
    matches = find_text_matches(ai_response, line_data, ['foundation', 'unity'])
    
    assert len(matches) >= 1
    assert matches[0]['match_type'] in ['exact', 'partial_ngram', 'fuzzy_set']
    
    print("✓ test_find_text_matches_exact passed")

def test_find_text_matches_no_duplicates():
    """Test that duplicate locators are not returned."""
    
    ai_response = "Unity is important. Unity is the foundation."
    
    line_data = [
        {
            'text': 'Unity is important',
            'locator': 'test:page:1:line:1',
            'source': 'test_doc'
        },
        {
            'text': 'Unity is important',  # Duplicate
            'locator': 'test:page:1:line:1',  # Same locator
            'source': 'test_doc'
        }
    ]
    
    matches = find_text_matches(ai_response, line_data, ['unity'])
    
    # Should only get one match despite duplicate
    assert len(matches) == 1
    
    print("✓ test_find_text_matches_no_duplicates passed")

if __name__ == "__main__":
    test_score_citation()
    test_score_citation_directive()
    test_find_text_matches_exact()
    test_find_text_matches_no_duplicates()
    print("\n✓ All citation tests passed!")
