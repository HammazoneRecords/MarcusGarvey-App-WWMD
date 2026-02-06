#!/usr/bin/env python3
"""
Changelog Helper
Adds entries to CHANGELOG.md with UTC-5 timestamps.
Usage:
    python backend/scripts/add_changelog_entry.py "Type" "Description"
    Type examples: Feat, Fix, Docs, Refactor, Test
"""
import sys
import argparse
from datetime import datetime, timezone, timedelta
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
CHANGELOG_PATH = BASE_DIR / "CHANGELOG.md"

# UTC-5 Timezone
TZ = timezone(timedelta(hours=-5))

def init_changelog():
    if not CHANGELOG_PATH.exists():
        header = """# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]
"""
        CHANGELOG_PATH.write_text(header, encoding="utf-8")
        print("✅ Created new CHANGELOG.md")

def add_entry(entry_type, description):
    init_changelog()
    
    now = datetime.now(TZ)
    date_str = now.strftime("%Y-%m-%d")
    
    entry = f"- **{entry_type}**: {description} ({date_str})"
    
    lines = CHANGELOG_PATH.read_text(encoding="utf-8").splitlines()
    
    # Insert after "## [Unreleased]"
    try:
        idx = lines.index("## [Unreleased]")
        lines.insert(idx + 1, "") # Empty line
        lines.insert(idx + 2, entry)
        
        CHANGELOG_PATH.write_text("\n".join(lines), encoding="utf-8")
        print(f"✅ Added {entry_type} entry to CHANGELOG.md")
    except ValueError:
        print("❌ Error: Could not find '## [Unreleased]' section in CHANGELOG.md")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Add changelog entry")
    parser.add_argument("type", help="Type of change (Feat, Fix, etc)")
    parser.add_argument("description", help="Description of change")
    args = parser.parse_args()
    
    add_entry(args.type, args.description)
