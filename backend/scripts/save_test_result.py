#!/usr/bin/env python3
"""
Test Result Logger
Saves test outputs to a dedicated folder and logs the creation.
Usage: 
    python backend/scripts/save_test_result.py "test_name" "content"
    Or pipe content: command | python backend/scripts/save_test_result.py "test_name"
"""
import sys
import os
import argparse
from datetime import datetime, timezone, timedelta
from pathlib import Path

# Setup paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
TEST_DIR = BASE_DIR / "backend" / "test_results"
LOG_FILE = TEST_DIR / "test_log.txt"

# UTC-5 Timezone
TZ = timezone(timedelta(hours=-5))

def get_timestamp():
    now = datetime.now(TZ)
    file_ts = now.strftime("%Y-%m-%d_%H%M%S")
    log_ts = now.strftime("%Y-%m-%d %H:%M:%S UTC-5")
    return file_ts, log_ts

def save_test(name, content):
    TEST_DIR.mkdir(parents=True, exist_ok=True)
    
    file_ts, log_ts = get_timestamp()
    safe_name = "".join([c if c.isalnum() or c in ('-', '_') else '_' for c in name])
    filename = f"{file_ts}_{safe_name}.txt"
    filepath = TEST_DIR / filename
    
    # Write content
    filepath.write_text(content, encoding="utf-8")
    
    # Log entry
    log_entry = f"[{log_ts}] Created: {filename} | Test: {name}\n"
    
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_entry)
        
    print(f"✅ Saved test result to: {filepath}")
    print(f"📝 Logged in: {LOG_FILE}")
    return filepath

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Save test results")
    parser.add_argument("name", help="Name of the test")
    parser.add_argument("content", nargs="?", help="Content (optional, reads from stdin if empty)")
    args = parser.parse_args()
    
    content = args.content
    if not content:
        if not sys.stdin.isatty():
            content = sys.stdin.read()
        else:
            print("Error: No content provided and no piping detected.")
            sys.exit(1)
            
    save_test(args.name, content)
