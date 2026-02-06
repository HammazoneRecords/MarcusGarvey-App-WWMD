#!/usr/bin/env python3
"""
Example: Batch Query Processing
Demonstrates how to process multiple queries and save results.
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

def batch_query(questions, output_dir="batch_results"):
    """
    Process multiple queries and save results.
    
    Args:
        questions: List of question strings
        output_dir: Directory to save results
    """
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    results = []
    
    for i, question in enumerate(questions, 1):
        print(f"\n[{i}/{len(questions)}] Processing: {question}")
        print("="*60)
        
        # Create output file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = output_path / f"{timestamp}_q{i}.json"
        
        # Run query (would use subprocess or direct function call)
        # For this example, we'll create a placeholder
        result = {
            "query": question,
            "answer": f"[Answer would be generated for: {question}]",
            "citations": [],
            "meta": {
                "timestamp": datetime.now().isoformat(),
                "batch_index": i
            }
        }
        
        # Save result
        output_file.write_text(json.dumps(result, indent=2), encoding="utf-8")
        results.append(result)
        
        print(f"✓ Saved to: {output_file}")
    
    # Create summary
    summary_file = output_path / f"batch_summary_{timestamp}.json"
    summary = {
        "total_queries": len(questions),
        "timestamp": datetime.now().isoformat(),
        "results": results
    }
    summary_file.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    
    print(f"\n✓ Batch complete! Summary: {summary_file}")

def example_batch():
    """Run batch query example."""
    
    questions = [
        "What is the foundation of success?",
        "How should one approach challenges?",
        "What is the importance of unity?",
    ]
    
    batch_query(questions)

if __name__ == "__main__":
    example_batch()
