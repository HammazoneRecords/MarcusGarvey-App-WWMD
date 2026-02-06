#!/usr/bin/env python3
"""
Quote Verification Utilities
Verifies that AI didn't modify the original quotes
"""
import re
from typing import List, Dict, Tuple
from difflib import SequenceMatcher

def extract_quoted_text(response: str) -> List[str]:
    """
    Extract all quoted text from AI response.
    Finds text between double quotes.
    """
    # Find all text between double quotes
    quoted = re.findall(r'"([^"]+)"', response)
    return quoted

def fuzzy_match(str1: str, str2: str, threshold: float = 0.95) -> Tuple[bool, float]:
    """
    Check if two strings are similar enough (allows minor whitespace/punctuation differences).
    Returns (is_match, similarity_score)
    """
    # Normalize whitespace
    s1 = ' '.join(str1.split())
    s2 = ' '.join(str2.split())
    
    ratio = SequenceMatcher(None, s1.lower(), s2.lower()).ratio()
    return (ratio >= threshold, ratio)

def verify_quotes(ai_response: str, original_quotes: List[Dict[str, str]]) -> Dict[str, any]:
    """
    Verify that all quotes in AI response match original quotes.
    
    Args:
        ai_response: The AI's generated response
        original_quotes: List of original quote dicts with 'text' field
    
    Returns:
        {
            'is_valid': bool,
            'violations': List of detected quote modifications,
            'summary': str
        }
    """
    # Extract quotes from AI response
    ai_quotes = extract_quoted_text(ai_response)
    
    original_texts = [q['text'] for q in original_quotes]
    
    violations = []
    unmatched_ai_quotes = []
    
    for ai_quote in ai_quotes:
        # Check if this AI quote matches any original quote
        matched = False
        
        for i, orig_text in enumerate(original_texts):
            # First check exact match
            is_match, similarity = fuzzy_match(ai_quote, orig_text)
            
            if is_match:
                matched = True
                break
            
            # Check if AI quote is a substring of the original
            # (AI correctly extracted a sentence from a larger chunk)
            if ai_quote in orig_text or orig_text in ai_quote:
                matched = True
                break
            
            # Check if original is substring of AI quote (allow minor additions)
            if len(ai_quote) > 20 and orig_text in ai_quote:
                matched = True
                break
                
            # Partial match - possible modification
            if similarity > 0.7:
                violations.append({
                    'type': 'MODIFIED_QUOTE',
                    'original': orig_text[:100] + '...' if len(orig_text) > 100 else orig_text,
                    'ai_version': ai_quote[:100] + '...' if len(ai_quote) > 100 else ai_quote,
                    'similarity': f"{similarity:.2%}"
                })
                matched = True
                break
        
        if not matched and len(ai_quote) > 20:  # Ignore short phrases
            unmatched_ai_quotes.append(ai_quote)
    
    # Check for invented quotes
    for unmatched in unmatched_ai_quotes:
        violations.append({
            'type': 'INVENTED_QUOTE',
            'ai_version': unmatched[:150] + '...' if len(unmatched) > 150 else unmatched,
            'warning': 'This quote was not in the original evidence bundle'
        })
    
    is_valid = len(violations) == 0
    
    # Build summary
    if is_valid:
        summary = f"✓ All {len(ai_quotes)} quotes verified - no modifications detected"
    else:
        summary = f"⚠ {len(violations)} quote violation(s) detected:\n"
        for v in violations:
            if v['type'] == 'MODIFIED_QUOTE':
                summary += f"  - Modified quote (similarity: {v['similarity']})\n"
            elif v['type'] == 'INVENTED_QUOTE':
                summary += f"  - Invented quote: \"{v['ai_version'][:50]}...\"\n"
    
    return {
        'is_valid': is_valid,
        'violations': violations,
        'summary': summary,
        'total_ai_quotes': len(ai_quotes),
        'total_original_quotes': len(original_quotes)
    }

def format_verification_report(verification: Dict) -> str:
    """Format verification results for display."""
    report = "\n" + "="*60 + "\n"
    report += "QUOTE VERIFICATION REPORT\n"
    report += "="*60 + "\n\n"
    
    report += verification['summary'] + "\n"
    
    if not verification['is_valid'] and verification['violations']:
        report += "\nDETAILS:\n"
        for i, v in enumerate(verification['violations'], 1):
            report += f"\n{i}. {v['type']}:\n"
            if 'original' in v:
                report += f"   Original: \"{v['original']}\"\n"
                report += f"   AI Version: \"{v['ai_version']}\"\n"
                report += f"   Similarity: {v['similarity']}\n"
            else:
                report += f"   Quote: \"{v['ai_version']}\"\n"
                report += f"   {v['warning']}\n"
    
    report += "\n" + "="*60 + "\n"
    return report
