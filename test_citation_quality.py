#!/usr/bin/env python3
"""
Test the improved citation filtering to verify Dover Publications metadata is skipped.
"""

import sys
sys.path.insert(0, 'backend/ragbox/scripts')

from citation_injector import is_metadata_or_frontmatter, score_citation

# Test cases from the screenshot issue
test_cases = [
    # The problematic Dover metadata from the screenshot
    {
        "text": "At Dover Publications we're committed to producing books in an earth-friendly manner and to helping our customers make greener choices. Manufacturing books in the United States ensures compliance with strict environmental laws and eliminates the need for international freight shipping, a major contributor to global air pollution. And printing on recycled paper helps minimize our consumption of trees, water and fossil fuels.",
        "query": "How did I get new customers?",
        "expected": "SKIP (metadata)",
        "name": "Dover environmental statement"
    },
    # Good substantive Garvey content
    {
        "text": "The Universal Negro Improvement Association is a movement for the establishment of a nation of our own in Africa, for Negroes who are in America, and who have lost their nationality. The movement is to liberate the Negroes wherever they are, and to establish a government of their own.",
        "query": "How did I get new customers?",
        "expected": "HIGH SCORE (substantive organization content)",
        "name": "UNIA founding principle"
    },
    # Short fragment that shouldn't be cited
    {
        "text": "You can shackle the hands",
        "query": "How did I get new customers?",
        "expected": "LOW SCORE (fragment)",
        "name": "Short dramatic fragment"
    },
    # Question header from text (shouldn't be cited alone)
    {
        "text": "How successful was the Universal Negro Improvement Association?",
        "query": "Success of UNIA",
        "expected": "SKIP (question header)",
        "name": "Question header"
    },
    # Good content about economic empowerment
    {
        "text": "We must establish our own commercial and industrial systems. The foundation of our redemption must be based upon the establishment of our own enterprise. By supporting Negro business, we create wealth for our race and ensure the independence of our people.",
        "query": "How did I get new customers?",
        "expected": "HIGH SCORE (economic/business focus)",
        "name": "Economic empowerment principle"
    },
    # Fragment starting with lowercase
    {
        "text": "together to rebuild their great nation and restore the pride of the Negro people.",
        "query": "pride restoration",
        "expected": "LOW SCORE (lowercase start = fragment)",
        "name": "Lowercase fragment"
    },
    # Copyright notice
    {
        "text": "Copyright © 2004 Dover Publications, Inc. All rights reserved.",
        "query": "copyright",
        "expected": "SKIP (copyright metadata)",
        "name": "Copyright notice"
    },
]

print("=" * 80)
print("CITATION QUALITY TEST SUITE")
print("=" * 80)
print()

for i, test in enumerate(test_cases, 1):
    text = test["text"]
    query = test["query"]
    expected = test["expected"]
    name = test["name"]
    
    # Test metadata filter
    is_metadata = is_metadata_or_frontmatter(text)
    
    # Test scoring
    query_terms = query.lower().split()
    score = score_citation(text, query_terms)
    
    print(f"Test {i}: {name}")
    print(f"  Query: '{query}'")
    print(f"  Text: '{text[:80]}{'...' if len(text) > 80 else ''}'")
    print(f"  Is Metadata: {is_metadata}")
    print(f"  Score: {score}")
    print(f"  Expected: {expected}")
    
    # Evaluate result
    if "SKIP" in expected and (is_metadata or score == -100):
        result = "✓ PASS"
    elif "HIGH SCORE" in expected and score > 20:
        result = "✓ PASS"
    elif "LOW SCORE" in expected and score < 10:
        result = "✓ PASS"
    else:
        result = "✗ FAIL"
    
    print(f"  Result: {result}")
    print()

print("=" * 80)
print("TEST COMPLETE")
print("=" * 80)
