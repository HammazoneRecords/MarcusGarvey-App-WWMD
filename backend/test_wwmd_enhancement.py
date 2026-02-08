#!/usr/bin/env python3
"""
Test script to verify WWMD enhancement - longer responses with more citations
"""

import requests
import json
import sys
from pathlib import Path

# Add backend path
sys.path.insert(0, str(Path(__file__).parent))

from ragbox.scripts.wwmd_ask_hybrid import ask_marcus

def test_wwmd_response():
    """Test the WWMD response generation locally"""
    
    test_queries = [
        "What did Marcus Garvey teach about economic independence and self-reliance?",
        "How should a leader inspire and mobilize their community?",
        "What is the path to true liberation and self-determination?"
    ]
    
    print("\n" + "="*80)
    print("TESTING WWMD ENHANCEMENT - LONGER RESPONSES WITH MORE CITATIONS")
    print("="*80 + "\n")
    
    for query in test_queries:
        print(f"\n✓ Query: {query}")
        print("-" * 80)
        
        try:
            response = ask_marcus(query, debug_mode='expand')
            
            # Display metrics
            answer_text = response.get('answer', '')
            citations = response.get('citations', [])
            
            print(f"Response Length: {len(answer_text)} characters (~{len(answer_text)//50} paragraphs)")
            print(f"Number of Citations: {len(citations)}")
            print(f"Answer Preview: {answer_text[:200]}...")
            
            print(f"\nTop Citations:")
            for i, cite in enumerate(citations[:3], 1):
                print(f"  {i}. [{cite['loc']}] Score: {cite.get('score', 'N/A')}")
                print(f"     {cite['excerpt'][:100]}...")
                
            print("\n" + "-" * 80)
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            import traceback
            traceback.print_exc()

def test_api_endpoint():
    """Test via HTTP if backend is running"""
    print("\n" + "="*80)
    print("TESTING VIA API ENDPOINT")
    print("="*80 + "\n")
    
    try:
        url = "http://localhost:5000/api/ask-marcus"
        payload = {
            "question": "What is Marcus Garvey's vision for economic independence?"
        }
        
        response = requests.post(url, json=payload, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            answer = data.get('answer', '')
            citations = data.get('citations', [])
            
            print(f"✓ Response Status: {response.status_code}")
            print(f"✓ Answer Length: {len(answer)} characters")
            print(f"✓ Citations Count: {len(citations)}")
            print(f"\nAnswer Preview:\n{answer[:300]}...\n")
            
            if citations:
                print(f"Sample Citations:")
                for i, cite in enumerate(citations[:3], 1):
                    print(f"  {i}. {cite['loc']}: {cite['excerpt'][:80]}...")
        else:
            print(f"❌ API Error: {response.status_code}")
            print(response.text)
            
    except requests.exceptions.ConnectionError:
        print("⚠ Backend server not running. Run: python backend/api/app.py")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    # Test locally first
    test_wwmd_response()
    
    # Then try API
    print("\n")
    test_api_endpoint()
    
    print("\n" + "="*80)
    print("ENHANCEMENT SUMMARY")
    print("="*80)
    print("""
✓ CITATION_MAX_DISPLAY: 8 → 15 (show more citations)
✓ CITATION_EXPAND_MAX_LINES: 500 → 1500 (more context for citation detection)
✓ Main Query Retrieval: 15 → 25 results (more source material)
✓ Lens Mode Retrieval: 10 → 20 results
✓ Lens Mode Citations: 3 → 10 citations shown
✓ Enhanced Prompt: Requests 3-5 paragraphs, multiple supporting passages, layered structure
✓ Improved Citation Scoring: Better selection of substantive, relevant quotes
    """)
