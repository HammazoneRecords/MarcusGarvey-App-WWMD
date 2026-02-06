#!/usr/bin/env python3
"""
Coherence Report Generator for Solob Wrapper (Enhanced v2)
Generates timestamped reports comparing scope guarantees against state history.
Includes Reality Ladder progress, delta tracking, and improved evidence matching.
"""
import os
import re
import json
from datetime import datetime
from pathlib import Path
from collections import defaultdict

# Paths (relative to repo root)
SCOPE_PATH = os.path.join('docs', 'v1.9 -scope.md')
STATE_HISTORY_PATH = os.path.join('docs', 'STATE_HISTORY.md')
STATE_JSON_PATH = os.path.join('docs', 'STATE.json')
IMPLEMENTATION_DELTA_PATH = os.path.join('docs', 'IMPLEMENTATION_DELTA.md')
AUDIT_ROOT = os.path.join('evidence', 'audits', 'Coherence Reports')
LAST_TIMESTAMP_FILE = os.path.join(AUDIT_ROOT, 'last_report_timestamp.txt')

def load_file(path):
    """Load text file content."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return None

def load_json(path):
    """Load JSON file content."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return None

def extract_guarantees(text):
    """Extract guarantees from 'What V1 Guarantees' section with sub-bullets."""
    guarantees = []
    in_guarantees_section = False
    current_guarantee = None
    
    for line in text.splitlines():
        if '## 0) What V1 Guarantees' in line:
            in_guarantees_section = True
            continue
        if in_guarantees_section:
            if line.strip().startswith('---'):
                break
            # Main guarantee (starts with - **)
            if line.strip().startswith('- **'):
                if current_guarantee:
                    guarantees.append(current_guarantee)
                match = re.search(r'\*\*(.*?)\*\*', line)
                if match:
                    current_guarantee = {
                        'name': match.group(1),
                        'details': []
                    }
            # Sub-bullet (indented)
            elif current_guarantee and line.strip().startswith('-') and not line.strip().startswith('- **'):
                current_guarantee['details'].append(line.strip()[2:])  # Remove leading '- '
    
    if current_guarantee:
        guarantees.append(current_guarantee)
    
    return guarantees

def extract_core_guarantees(text):
    """Extract core guarantees from V1 Foundation Summary."""
    core_guarantees = []
    in_core_section = False
    
    for line in text.splitlines():
        if '### Core Guarantees' in line:
            in_core_section = True
            continue
        if in_core_section:
            if line.strip().startswith('###') or line.strip().startswith('##'):
                break
            match = re.match(r'^\d+\.\s+\*\*(.*?)\*\*\s+?\s+(.*)', line.strip())
            if match:
                core_guarantees.append({
                    'name': match.group(1),
                    'description': match.group(2)
                })
    
    return core_guarantees

def extract_reality_ladder(text):
    """Extract Reality Ladder stages from scope."""
    realities = []
    in_reality_section = False
    current_reality = None
    
    for line in text.splitlines():
        if '## 2) V1 Workflow: The "Reality Ladder"' in line:
            in_reality_section = True
            continue
        if in_reality_section:
            if line.strip().startswith('---'):
                if current_reality:
                    realities.append(current_reality)
                break
            # Reality heading - match format: "### Reality 1 ? Monk: Anchors-only"
            match = re.match(r'###\s+Reality\s+(\d+)\s+?\s+(.*?):\s+(.*)', line.strip())
            if match:
                if current_reality:
                    realities.append(current_reality)
                current_reality = {
                    'number': int(match.group(1)),
                    'name': match.group(2),
                    'tagline': match.group(3),
                    'goal': '',
                    'outputs': []
                }
            elif current_reality:
                if line.strip().startswith('Goal:'):
                    current_reality['goal'] = line.strip()[6:]
                elif line.strip().startswith('- '):
                    current_reality['outputs'].append(line.strip()[2:])
    
    return realities

def extract_state_transitions(text):
    """Extract all state transition entries."""
    transitions = []
    for line in text.splitlines():
        if re.search(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}', line):
            transitions.append(line.strip())
    return transitions

def get_recent_transitions(text, count=10):
    """Get the most recent N state transitions."""
    transitions = extract_state_transitions(text)
    return transitions[-count:] if len(transitions) > count else transitions

def check_guarantee_evidence(guarantee_name, details, state_text):
    """Check if there's evidence in state history for a guarantee."""
    evidence = []
    
    # Create search terms from guarantee name and details
    search_terms = guarantee_name.lower().split()
    for detail in details:
        search_terms.extend(detail.lower().split()[:3] )  # First 3 words of each detail
    
    # Remove common words
    common_words = {'is', 'the', 'a', 'an', 'to', 'of', 'for', 'with', 'in', 'on', 'at', 'by', 'from'}
    search_terms = [term for term in search_terms if term not in common_words and len(term) > 2]
    
    for line in state_text.splitlines():
        line_lower = line.lower()
        # Check if multiple search terms appear
        matching_terms = sum(1 for term in search_terms if term in line_lower)
        if matching_terms >= 2:
            evidence.append(line.strip())
    
    return (len(evidence) > 0, evidence[:5])  # Return up to 5 evidence lines

def find_new_files(since_timestamp, exclusion_patterns=None):
    """Find files modified since the given timestamp."""
    if exclusion_patterns is None:
        exclusion_patterns = [
            '.venv', '__pycache__', '.git', '.vs', 'node_modules',
            'evidence/audits/Coherence Reports'
        ]
    
    new_files = []
    for root, dirs, files in os.walk('.'):
        dirs[:] = [d for d in dirs if not any(excl in os.path.join(root, d) for excl in exclusion_patterns)]
        
        for f in files:
            if f.startswith('.'):
                continue
            full_path = os.path.join(root, f)
            if any(excl in full_path for excl in exclusion_patterns):
                continue
            
            try:
                mtime = os.path.getmtime(full_path)
                file_dt = datetime.fromtimestamp(mtime)
                if file_dt > since_timestamp:
                    new_files.append((full_path, file_dt))
            except Exception:
                pass
    
    new_files.sort(key=lambda x: x[1], reverse=True)
    return new_files

def main():
    # Load content
    scope_text = load_file(SCOPE_PATH)
    state_text = load_file(STATE_HISTORY_PATH)
    state_json = load_json(STATE_JSON_PATH)
    delta_text = load_file(IMPLEMENTATION_DELTA_PATH)
    
    if not scope_text or not state_text:
        print("[ERROR] Error: Could not load required files")
        return 1
    
    guarantees = extract_guarantees(scope_text)
    core_guarantees = extract_core_guarantees(scope_text)
    realities = extract_reality_ladder(scope_text)
    state_transitions = extract_state_transitions(state_text)
    recent_transitions = get_recent_transitions(state_text, 10)
    
    # Determine timestamp
    now = datetime.now()
    timestamp_str = now.strftime('%Y%m%d_%H%M%S-05')
    report_dir = os.path.join(AUDIT_ROOT, timestamp_str)
    os.makedirs(report_dir, exist_ok=True)
    report_path = os.path.join(report_dir, f"{timestamp_str}_coherence_report.md")
    
    # Load last timestamp
    last_ts = None
    if os.path.exists(LAST_TIMESTAMP_FILE):
        with open(LAST_TIMESTAMP_FILE, 'r') as f:
            last_ts_str = f.read().strip()
            try:
                last_ts = datetime.strptime(last_ts_str, '%Y%m%d_%H%M%S-05')
            except Exception:
                last_ts = datetime(2020, 1, 1)
    
    new_files = find_new_files(last_ts) if last_ts else []
    
    # Build report
    with open(report_path, 'w', encoding='utf-8') as rpt:
        rpt.write(f"# Coherence Report ? {timestamp_str}\n\n")
        rpt.write(f"**Generated**: {now.strftime('%Y-%m-%d %H:%M:%S')} (UTC-5)\n\n")
        rpt.write("---\n\n")
        
        # Current State
        rpt.write("## [STATS] Current State\n\n")
        if state_json:
            rpt.write(f"- **Current State**: `{state_json.get('state', state_json.get('current_state', 'UNKNOWN'))}`\n")
            rpt.write(f"- **Last Updated**: {state_json.get('recorded_at', state_json.get('last_updated', 'UNKNOWN'))}\n")
        else:
            rpt.write("- **Current State**: `UNKNOWN` (STATE.json not found)\n")
            rpt.write("- **Last Updated**: N/A\n")
        rpt.write(f"- **State Transitions Recorded**: {len(state_transitions)}\n")
        rpt.write(f"- **Scope Version**: v1.9 (Fully Manifested)\n\n")
        
        # Recent Transitions
        rpt.write("### Recent State Transitions (Last 10)\n\n")
        for trans in recent_transitions:
            rpt.write(f"- `{trans[:100]}{'...' if len(trans) > 100 else ''}`\n")
        rpt.write("\n---\n\n")
        
        # Reality Ladder Progress
        rpt.write("## [GOAL] Reality Ladder Progress\n\n")
        rpt.write("| Reality | Name | Status | Goal |\n")
        rpt.write("|---------|------|--------|------|\n")
        for reality in realities:
            # Simplify status check (could be enhanced with delta parsing)
            status = "[WIP] In Progress" if reality['number'] <= 5 else "[DONE] Complete"
            rpt.write(f"| **Reality {reality['number']}** | {reality['name']} | {status} | {reality['goal'][:50]}... |\n")
        rpt.write("\n---\n\n")
        
        # V1 Guarantees Check
        rpt.write("## [PASS] V1 Guarantees (Non-Negotiables)\n\n")
        rpt.write(f"Checking {len(guarantees)} guarantees from `docs/v1.9 -scope.md` against state history:\n\n")
        
        for guarantee in guarantees:
            has_evidence, evidence_lines = check_guarantee_evidence(
                guarantee['name'], 
                guarantee['details'], 
                state_text
            )
            status = "[PASS] Evidence Found" if has_evidence else "[WARN] Limited Evidence"
            rpt.write(f"### {guarantee['name']}\n\n")
            rpt.write(f"**Status**: {status}\n\n")
            
            if guarantee['details']:
                rpt.write("**Details**:\n")
                for detail in guarantee['details']:
                    rpt.write(f"- {detail}\n")
                rpt.write("\n")
            
            if evidence_lines:
                rpt.write("**Evidence** (sample):\n")
                for ev in evidence_lines:
                    rpt.write(f"- `{ev[:120]}{'...' if len(ev) > 120 else ''}`\n")
                rpt.write("\n")
            else:
                rpt.write("_No direct state history evidence found. This may indicate the guarantee is structural rather than transactional._\n\n")
        
        rpt.write("---\n\n")
        
        # Core Guarantees Summary
        if core_guarantees:
            rpt.write("## [CORE] Core Guarantees Summary\n\n")
            rpt.write("From **V1 Foundation Summary**:\n\n")
            for idx, cg in enumerate(core_guarantees, 1):
                has_evidence, _ = check_guarantee_evidence(cg['name'], [cg['description']], state_text)
                status = "[PASS]" if has_evidence else "[WARN]"
                rpt.write(f"{idx}. {status} **{cg['name']}** ? {cg['description']}\n")
            rpt.write("\n---\n\n")
        
        # New Files Since Last Report
        rpt.write("## [FILE] New Files / Features Since Last Report\n\n")
        if last_ts:
            rpt.write(f"Comparing against last report from: `{last_ts.strftime('%Y-%m-%d %H:%M:%S')}`\n\n")
        else:
            rpt.write("This is the **first report**. Showing recently modified files.\n\n")
        
        if new_files:
            rpt.write(f"**Total new/modified files**: {len(new_files)}\n\n")
            # Group by directory
            by_dir = defaultdict(list)
            for file_path, mod_time in new_files[:30]:
                dir_name = os.path.dirname(file_path) or '.'
                by_dir[dir_name].append((os.path.basename(file_path), mod_time))
            
            for dir_name in sorted(by_dir.keys()):
                rpt.write(f"### `{dir_name}/`\n\n")
                for file_name, mod_time in by_dir[dir_name]:
                    rpt.write(f"- `{file_name}` ({mod_time.strftime('%Y-%m-%d %H:%M')})\n")
                rpt.write("\n")
            
            if len(new_files) > 30:
                rpt.write(f"_... and {len(new_files) - 30} more files._\n\n")
        else:
            rpt.write("(No new files detected)\n\n")
        
        rpt.write("---\n\n")
        rpt.write(f"**Report Location**: `{report_path}`\n")
        rpt.write(f"**Next Report**: Will compare against `{timestamp_str}`\n")
    
    # Update last timestamp file
    with open(LAST_TIMESTAMP_FILE, 'w') as f:
        f.write(timestamp_str)
    
    print(f"[DONE] Coherence report generated: {report_path}")
    print(f"[STATS] Checked {len(guarantees)} guarantees ({len([g for g in guarantees if check_guarantee_evidence(g['name'], g['details'], state_text)[0]])} with evidence)")
    print(f"[GOAL] Tracked {len(realities)} Reality Ladder stages")
    print(f"[FILE] Found {len(new_files)} new/modified files")
    print(f"[NOTE] Analyzed {len(state_transitions)} state transitions")
    
    return 0

if __name__ == "__main__":
    exit(main())
