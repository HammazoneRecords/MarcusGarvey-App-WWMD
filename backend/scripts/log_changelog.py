#!/usr/bin/env python3
"""
Changelog Entry Helper
Standardizes entry creation for CHANGELOG.MD according to the canonical format.
Automatically inserts new entries at the top of the file (after the header).
"""
import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
STATE_JSON_PATH = BASE_DIR / 'docs' / 'STATE.json'
CHANGELOG_PATH = BASE_DIR / 'CHANGELOG.MD'

def get_current_sid():
    """Load active session ID from STATE.json."""
    try:
        if STATE_JSON_PATH.exists():
            with open(STATE_JSON_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('active_session_id', 'NO_SID_FOUND')
    except Exception:
        pass
    return "UNKNOWN_SID"

def format_timestamp():
    """Generate local (-05:00) timestamp."""
    now_utc = datetime.now(timezone.utc)
    # Local Kingston time is UTC-5
    from datetime import timedelta
    now_local = now_utc - timedelta(hours=5)
    return now_local.strftime('%Y-%m-%dT%H:%M:%S-05:00')

def create_entry(summary, type_tag, files, why, evidence, roadblocks):
    ts = format_timestamp()
    sid = get_current_sid()
    
    lines = []
    lines.append(f"## {ts} | SID: {sid} | TYPE: {type_tag.upper()}")
    lines.append(f"SUMMARY: {summary}")
    lines.append("")
    
    lines.append("FILES:")
    for f in files:
        lines.append(f"- {f}")
    lines.append("")
    
    lines.append("WHY:")
    for w in why:
        lines.append(f"- {w}")
    lines.append("")
    
    if type_tag.upper() == "MAJOR" or evidence:
        lines.append("EVIDENCE (only if MAJOR):")
        if evidence:
            for ev in evidence:
                lines.append(f"- {ev}")
        else:
            lines.append("- (Pending evidence documentation)")
        lines.append("")
    
    if roadblocks:
        lines.append("ROADBLOCKS (if any):")
        for rb in roadblocks:
            lines.append(f"- {rb}")
        lines.append("")
    
    return "\n".join(lines) + "\n"

def main():
    parser = argparse.ArgumentParser(description="Add a structured entry to CHANGELOG.MD")
    parser.add_argument("--summary", required=True, help="One sentence summary of the change")
    parser.add_argument("--type", choices=['MAJOR', 'MINOR', 'DOC'], default='MINOR', help="Change type")
    parser.add_argument("--files", action='append', help="Files changed (repeat for multiple)")
    parser.add_argument("--why", action='append', help="Bullet points for why/what (repeat for multiple)")
    parser.add_argument("--evidence", action='append', help="Evidence links or notes (repeat for multiple)")
    parser.add_argument("--roadblocks", action='append', help="Roadblock notes (repeat for multiple)")
    
    args = parser.parse_args()
    
    if not args.files:
        print("Error: At least one --files entry is required.")
        return 1
    if not args.why:
        print("Error: At least one --why entry is required.")
        return 1

    entry = create_entry(
        args.summary, 
        args.type, 
        args.files, 
        args.why, 
        args.evidence or [], 
        args.roadblocks or []
    )
    
    # Read existing changelog
    if CHANGELOG_PATH.exists():
        content = CHANGELOG_PATH.read_text(encoding='utf-8')
    else:
        content = "# CHANGELOG.md (Append-only)\n"
    
    # Identify header (usually first line)
    lines = content.splitlines(keepends=True)
    header_found = False
    new_lines = []
    
    for i, line in enumerate(lines):
        new_lines.append(line)
        if line.strip().startswith("# CHANGELOG.md"):
            # Insert entry after header and its following newline
            if i + 1 < len(lines) and lines[i+1].strip() == "":
                new_lines.append(lines[i+1])
                new_lines.append(entry)
                new_lines.extend(lines[i+2:])
            else:
                new_lines.append("\n")
                new_lines.append(entry)
                new_lines.extend(lines[i+1:])
            header_found = True
            break
            
    if not header_found:
        # Fallback: Prepend if header not found
        content = "# CHANGELOG.md (Append-only)\n\n" + entry + "\n" + content
    else:
        content = "".join(new_lines)
    
    CHANGELOG_PATH.write_text(content, encoding='utf-8')
    print("Entry successfully added to CHANGELOG.MD")
    return 0

if __name__ == "__main__":
    exit(main())
