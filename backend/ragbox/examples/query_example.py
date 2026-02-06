#!/usr/bin/env python3
"""
Example: Basic RAG Query
Demonstrates how to query the RAG system with a simple question.
"""

import sys
import json
from pathlib import Path

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from wwmd_ask_hybrid import main as rag_query

def example_basic_query():
    """Run a basic query and print results."""
    
    # Set up query
    query = "What is the foundation of success?"
    
    print(f"Query: {query}\n")
    print("="*60)
    
    # Run query (this will use command-line args)
    # For programmatic use, you'd import and call functions directly
    sys.argv = ["query_example.py", query, "--json"]
    
    try:
        rag_query()
    except SystemExit:
        pass  # Ignore sys.exit() from main

if __name__ == "__main__":
    example_basic_query()
