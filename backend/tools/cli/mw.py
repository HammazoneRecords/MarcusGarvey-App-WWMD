#!/usr/bin/env python3
"""
MW CLI - Solob Wrapper Command-Line Interface

Purpose: Unified CLI for audit, lint, and court-sweep operations.
Enforces OBSERVE mode safety, four-strike roadblock protocol, and evidence-only output.

Usage:
    mw audit encoding
    mw audit witness
    mw lint bundles
    mw court-sweep
"""

import os
import sys
import json
import platform
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, List, Tuple

# Roadblock tracking
roadblock_count = 0
roadblock_log = []

def detect_os() -> str:
    """Detect operating system."""
    return platform.system()  # Returns 'Windows', 'Linux', 'Darwin', etc.

def locate_repo_root() -> Optional[Path]:
    """
    Locate repository root by searching upward for marker files.
    Markers: .vscode/, docs/ANTIFRAGILITY_CONTEXT_ACDOC.md
    """
    current = Path.cwd()
    for parent in [current] + list(current.parents):
        if (parent / "docs" / "ANTIFRAGILITY_CONTEXT_ACDOC.md").exists():
            return parent
        if (parent / "STATE_NOTE.cmd").exists(): # Backup marker
            return parent
    return None

def locate_venv_python(repo_root: Path) -> Optional[Path]:
    """
    Locate venv Python executable.
    Windows: .venv\Scripts\python.exe
    Unix: .venv/bin/python
    """
    os_type = detect_os()
    if os_type == "Windows":
        venv_python = repo_root / ".venv" / "Scripts" / "python.exe"
    else:
        venv_python = repo_root / ".venv" / "bin" / "python"
    
    if venv_python.exists():
        return venv_python
    return None

def record_roadblock(error_msg: str):
    """Record a roadblock and check if we've hit the 4-strike limit."""
    global roadblock_count, roadblock_log
    roadblock_count += 1
    roadblock_log.append(f"Roadblock {roadblock_count}: {error_msg}")
    
    # Print error immediately for visibility
    print(f"[ROADBLOCK] {error_msg}", file=sys.stderr)
    
    if roadblock_count >= 4:
        print("\n" + "="*60)
        print("FOUR-STRIKE ROADBLOCK LIMIT REACHED")
        print("="*60)
        print("\nRoadblock History:")
        for entry in roadblock_log:
            print(f"  {entry}")
        print("\nREQUEST FOR USER INPUT:")
        print("Please provide ONE of the following:")
        print("  1) Paste full error output (stdout/stderr)")
        print("  2) Confirm repo root path (current detection)")
        print("  3) Confirm venv exists and location")
        print("  4) Choose action: [retry / skip / manual-fix]")
        print("\nAI MUST NOT GUESS STATE AFTER STRIKE 4.")
        print("="*60)
        sys.exit(1)

def ensure_evidence_dir(repo_root: Path, subdir: str) -> Path:
    """Ensure evidence output directory exists."""
    evidence_dir = repo_root / "evidence" / subdir
    evidence_dir.mkdir(parents=True, exist_ok=True)
    return evidence_dir

def run_script(repo_root: Path, venv_python: Path, script_path: str, args: List[str] = None) -> Tuple[int, str, str]:
    """
    Run a Python script using venv Python.
    Returns: (exit_code, stdout, stderr)
    """
    cmd = [str(venv_python), str(repo_root / script_path)]
    if args:
        cmd.extend(args)
    
    try:
        result = subprocess.run(
            cmd,
            cwd=str(repo_root),
            capture_output=True, # Capture unless we want direct streaming
            text=True,
            timeout=300  # 5 minute timeout
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        record_roadblock(f"Script timeout: {script_path}")
        return 1, "", "Script execution timeout (5 minutes)"
    except Exception as e:
        record_roadblock(f"Script execution failed: {script_path} - {str(e)}")
        return 1, "", str(e)

def run_interactive_script(repo_root: Path, venv_python: Path, script_path: str, args: List[str] = None) -> int:
    """
    Run a Python script interactively (streaming stdout/stderr).
    Used for 'mw run' where we want to see output immediately.
    """
    cmd = [str(venv_python), str(repo_root / script_path)]
    if args:
        cmd.extend(args)
        
    try:
        # Popen to stream output
        process = subprocess.Popen(
            cmd,
            cwd=str(repo_root),
            stdout=sys.stdout,
            stderr=sys.stderr
        )
        process.communicate()
        return process.returncode
    except Exception as e:
        record_roadblock(f"Interactive script failed: {script_path} - {str(e)}")
        return 1

def confirm_latch():
    """Require strict user confirmation."""
    print("Type YES_I_MEAN_IT to confirm")
    try:
        response = input("> ")
    except EOFError:
        response = ""
        
    if response.strip() != "YES_I_MEAN_IT":
        print("Blocked: confirmation latch not satisfied.")
        sys.exit(1)

def require_note(note: Optional[str]) -> str:
    """Require a non-empty note."""
    if note and note.strip():
        return note.strip()
    
    print("Enter STATE_HISTORY note (required, cannot be blank)")
    try:
        user_note = input("> ")
    except EOFError:
        user_note = ""
        
    if not user_note.strip():
        print("Blocked: Note is required.")
        sys.exit(1)
    return user_note.strip()

def get_current_state(repo_root: Path) -> dict:
    """Read current state from STATE.json."""
    state_path = repo_root / "docs" / "STATE.json"
    if not state_path.exists():
        record_roadblock(f"Missing: {state_path}")
        sys.exit(1)
        
    try:
        with open(state_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        record_roadblock(f"Failed to read STATE.json: {e}")
        sys.exit(1)

def cmd_state(repo_root: Path):
    """Print current state."""
    state_data = get_current_state(repo_root)
    print(f"STATE: {state_data.get('state', 'UNKNOWN')}")
    print(f"active_session_id: {state_data.get('active_session_id', '(none)')}")

def cmd_observe(repo_root: Path, venv_python: Path, note: Optional[str]):
    """Transition to OBSERVE state."""
    note = require_note(note)
    
    state_data = get_current_state(repo_root)
    current_state = state_data.get('state', '').upper()
    
    if current_state == 'OBSERVE':
        print("Blocked: already in OBSERVE (no-op transition).")
        return

    # Append SID if present
    sid = state_data.get('active_session_id')
    if sid and f"sid={sid}" not in note:
        note = f"{note} (sid={sid})"

    print(f"Current STATE: {current_state}")
    print("Target  STATE: OBSERVE")
    print(f"Note: {note}")
    confirm_latch()
    
    # Run transition
    script_path = "scripts/state_transition.py"
    args = ["--to", "OBSERVE", "--note", note, "--confirm", "YES_I_MEAN_IT"]
    
    code = run_interactive_script(repo_root, venv_python, script_path, args)
    if code != 0:
        sys.exit(code)

def generate_sid() -> str:
    """Generate a new Session ID."""
    # Format: S_YYYYMMDDTHHMMSSZ_ARKV0
    utc_str = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"S_{utc_str}_ARKV0"

def cmd_record(repo_root: Path, venv_python: Path, note: Optional[str]):
    """Transition to RECORD state."""
    note = require_note(note)
    
    state_data = get_current_state(repo_root)
    current_state = state_data.get('state', '').upper()
    
    if current_state == 'RECORD':
        print("Blocked: already in RECORD (no-op transition).")
        return

    # Generate/Propagate SID
    sid = state_data.get('active_session_id')
    if not sid:
        sid = generate_sid()
        # Update STATE.json immediately with new SID so state_transition.py picks it up?
        # Actually state_transition.py usually just reads the file. 
        # solob.ps1 updated the file manually before calling the script.
        # process: read -> updated in memory -> write -> call script.
        state_data['active_session_id'] = sid
        with open(repo_root / "docs" / "STATE.json", 'w', encoding='utf-8') as f:
            json.dump(state_data, f, indent=2, sort_keys=True)
            f.write('\n') # trailing newline
            
    if f"sid={sid}" not in note:
        note = f"{note} (sid={sid})"

    print(f"Current STATE: {current_state}")
    print("Target  STATE: RECORD")
    print(f"Note: {note}")
    confirm_latch()
    
    # Run transition
    script_path = "scripts/state_transition.py"
    args = ["--to", "RECORD", "--note", note, "--confirm", "YES_I_MEAN_IT"]
    
    code = run_interactive_script(repo_root, venv_python, script_path, args)
    if code != 0:
        sys.exit(code)

def cmd_run(repo_root: Path, venv_python: Path, intent: Optional[str], script: Optional[str], script_args: List[str]):
    """Run a recorded script."""
    
    # Check state first (fast fail)
    state_data = get_current_state(repo_root)
    if state_data.get('state', '').upper() != 'RECORD':
        print(f"Blocked: Current state={state_data.get('state')}. Action='run' requires RECORD.")
        sys.exit(1)

    if not intent or not intent.strip():
        print("Blocked: --intent is required and cannot be blank.")
        sys.exit(1)
        
    if not script or not script.strip():
        print("Blocked: --script is required.")
        sys.exit(1)
        
    full_script_path = repo_root / script
    if not full_script_path.exists():
        print(f"Blocked: script not found: {script}")
        sys.exit(1)
        
    # Construct command
    # python scripts/run_recorded.py --intent "..." script.py -- [args...]
    runner_path = "scripts/run_recorded.py"
    
    run_args = ["--intent", intent, script, "--"]
    if script_args:
        run_args.extend(script_args)
        
    print(f"RUN: mw run {script} {run_args}")
    
    code = run_interactive_script(repo_root, venv_python, runner_path, run_args)
    if code != 0:
        sys.exit(code)

def cmd_audit_encoding(repo_root: Path, venv_python: Path):
    """Run encoding audit and save to evidence/audits/"""
    print("Running encoding audit...")
    
    # Check if encoding_report.ps1 exists
    ps_script = repo_root / "tools" / "encoding_report.ps1"
    if not ps_script.exists():
        record_roadblock(f"Encoding audit script not found: {ps_script}")
        return
    
    # Run PowerShell script
    try:
        result = subprocess.run(
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(ps_script)],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            timeout=60
        )
        
        # Save output to evidence/audits/
        output_dir = ensure_evidence_dir(repo_root, "audits")
        output_file = output_dir / "encoding_audit_latest.txt"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("=== ENCODING AUDIT OUTPUT ===\n")
            f.write(f"Exit Code: {result.returncode}\n\n")
            f.write("STDOUT:\n")
            f.write(result.stdout)
            f.write("\n\nSTDERR:\n")
            f.write(result.stderr)
        
        print(f"[DONE] Encoding audit complete: {output_file}")
        print(f"  Exit code: {result.returncode}")
        
    except Exception as e:
        record_roadblock(f"Encoding audit failed: {str(e)}")

def cmd_audit_witness(repo_root: Path, venv_python: Path):
    """Run witness epoch audit and save to evidence/audits/"""
    print("Running witness epoch audit...")
    
    # Check if verify_witness_epoch.ps1 exists
    ps_script = repo_root / "tools" / "verify_witness_epoch.ps1"
    if not ps_script.exists():
        record_roadblock(f"Witness audit script not found: {ps_script}")
        return
    
    # Run PowerShell script
    try:
        result = subprocess.run(
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(ps_script)],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            timeout=60
        )
        
        # Save output to evidence/audits/
        output_dir = ensure_evidence_dir(repo_root, "audits")
        output_file = output_dir / "witness_audit_latest.txt"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("=== WITNESS EPOCH AUDIT OUTPUT ===\n")
            f.write(f"Exit Code: {result.returncode}\n\n")
            f.write("STDOUT:\n")
            f.write(result.stdout)
            f.write("\n\nSTDERR:\n")
            f.write(result.stderr)
        
        print(f"[DONE] Witness audit complete: {output_file}")
        print(f"  Exit code: {result.returncode}")
        
    except Exception as e:
        record_roadblock(f"Witness audit failed: {str(e)}")

def cmd_lint_bundles(repo_root: Path, venv_python: Path):
    """
    Lint bundles: run witness epoch validator + STATE_HISTORY format validator.
    Saves output to evidence/audits/bundle_lint_latest.txt
    """
    print("[MW] Linting bundles...")
    
    # 1. Witness epoch validation
    py_script = repo_root / "tools" / "verify_witness_epoch.py"
    if not py_script.exists():
        print(f"[ERROR] Script not found: {py_script}", file=sys.stderr)
        return 1
    
    result_epoch = subprocess.run(
        [str(venv_python), str(py_script), "--state-history", "docs/STATE_HISTORY.md"],
        cwd=str(repo_root),
        capture_output=True,
        text=True,
        timeout=60
    )
    
    # 2. Format validation
    format_script = repo_root / "tools" / "validate_state_history_format.py"
    format_output = ""
    format_exit = 0
    
    if format_script.exists():
        result_format = subprocess.run(
            [str(venv_python), str(format_script), "--state-history", "docs/STATE_HISTORY.md"],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            timeout=60
        )
        format_output = result_format.stdout
        format_exit = result_format.returncode
    
    # Combine outputs
    combined_output = f"""=== Witness Epoch Validation ===
{result_epoch.stdout}
{result_epoch.stderr}

=== Format Validation ===
{format_output}
"""
    
    # Save to evidence/audits/
    audits_dir = repo_root / "evidence" / "audits"
    audits_dir.mkdir(parents=True, exist_ok=True)
    output_file = audits_dir / "bundle_lint_latest.txt"
    output_file.write_text(combined_output, encoding="utf-8")
    
    # Report
    print(combined_output)
    print(f"[OK] Saved to: {output_file.relative_to(repo_root)}")
    
    # Exit code: fail if either check fails
    if result_epoch.returncode != 0 or format_exit != 0:
        print(f"[FAIL] Exit codes: witness_epoch={result_epoch.returncode}, format={format_exit}")
        return max(result_epoch.returncode, format_exit)
    
    print("[PASS] All bundle checks passed")
    return 0


def cmd_lint_scripts(repo_root: Path, venv_python: Path):
    """Run script state scan and save to evidence/audits/"""
    print("Running script state scan...")
    
    ps_script = repo_root / "tools" / "script_state_scan.ps1"
    if not ps_script.exists():
        record_roadblock(f"Script state scan not found: {ps_script}")
        return
    
    # Run PowerShell script
    try:
        result = subprocess.run(
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(ps_script)],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            timeout=30
        )
        
        print(f"[DONE] Script state scan complete")
        print(f"  Exit code: {result.returncode}")
        print(f"  Output: evidence/audits/script_state_scan_latest.txt")
        
    except Exception as e:
        record_roadblock(f"Script state scan failed: {str(e)}")

def cmd_court_sweep(repo_root: Path, venv_python: Path):
    """Run court sweep (comprehensive system health check)"""
    print("Running court sweep...")
    
    # Check if preflight_balance_check.py exists
    script_path = "scripts/preflight_balance_check.py"
    if not (repo_root / script_path).exists():
        record_roadblock(f"Court sweep script not found: {script_path}")
        return
    
    # Run the script
    exit_code, stdout, stderr = run_script(repo_root, venv_python, script_path)
    
    # Save output to evidence/audits/
    output_dir = ensure_evidence_dir(repo_root, "audits")
    output_file = output_dir / "court_sweep_latest.txt"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("=== COURT SWEEP OUTPUT ===\n")
        f.write(f"Exit Code: {exit_code}\n\n")
        f.write("STDOUT:\n")
        f.write(stdout)
        f.write("\n\nSTDERR:\n")
        f.write(stderr)
    
    print(f"[DONE] Court sweep complete: {output_file}")
    print(f"  Exit code: {exit_code}")
    
    if exit_code == 0:
        print("  Verdict: GO")
    else:
        print("  Verdict: NO-GO")


def cmd_ritual_run(repo_root: Path, venv_python: Path, config_path: str, dry_run: bool):
    """
    Execute a ritual via the ritual engine.
    Routes through run_recorded.py for proper front-door execution.
    """
    print(f"[MW] Running ritual: {config_path}")
    print(f"[MW] Dry-run: {dry_run}")
    
    # Resolve config path
    config_full = Path(config_path)
    if not config_full.is_absolute():
        config_full = (repo_root / config_path).resolve()
    
    if not config_full.exists():
        record_roadblock(f"Ritual config not found: {config_full}")
        return
    
    # Load config to get intent
    try:
        config_data = json.loads(config_full.read_text(encoding="utf-8"))
        intent = config_data.get("intent", "RITUAL_EXECUTION")
        ritual_name = config_data.get("ritual_name", "unknown")
    except Exception as e:
        record_roadblock(f"Failed to read ritual config: {e}")
        return
    
    # Build script args
    script_args = ["--config", str(config_full)]
    if dry_run:
        script_args.append("--dry-run")
    
    # Route through run_recorded.py for proper front-door
    full_intent = f"RITUAL: {ritual_name} - {intent}"
    cmd_run(repo_root, venv_python, full_intent, "scripts/ritual_engine.py", script_args)


def cmd_ritual_list(repo_root: Path):
    """List available ritual configs."""
    print("[MW] Available ritual configs:")
    print()
    
    rituals_dir = repo_root / "config" / "rituals"
    if not rituals_dir.exists():
        print(f"No rituals directory found: {rituals_dir}")
        return
    
    configs = list(rituals_dir.glob("*.json"))
    if not configs:
        print("No ritual configs found.")
        return
    
    for config_path in sorted(configs):
        if config_path.name.startswith("test"):
            continue  # Skip test files
        try:
            data = json.loads(config_path.read_text(encoding="utf-8"))
            name = data.get("ritual_name", "unknown")
            intent = data.get("intent", "")
            anchor = data.get("anchor_id", "")
            print(f"  {config_path.name}")
            print(f"    Name: {name}")
            print(f"    Intent: {intent}")
            print(f"    Anchor: {anchor}")
            print()
        except Exception:
            print(f"  {config_path.name} (invalid JSON)")


def cmd_ritual_validate(repo_root: Path, venv_python: Path, config_path: str):
    """Validate a ritual config without executing (dry-run mode)."""
    print(f"[MW] Validating ritual config: {config_path}")
    cmd_ritual_run(repo_root, venv_python, config_path, dry_run=True)


def parse_args():
    """Simple manual arg parsing (avoiding argparse for custom structure if needed)"""
    # mw <command> [subcommand/flags]
    if len(sys.argv) < 2:
        return None, None
    
    command = sys.argv[1]
    
    # Extract flags manually for specific commands to keep simple
    # Using argparse would be cleaner but this works for the rigid structure
    return command, sys.argv[2:]

def main():
    """Main CLI entry point."""
    print("MW CLI - Solob Wrapper Command-Line Interface")
    print("=" * 60)
    
    # Detect OS
    os_type = detect_os()
    print(f"OS: {os_type}")
    
    # Locate repo root
    repo_root = locate_repo_root()
    if not repo_root:
        record_roadblock("Could not locate repository root (no docs/ANTIFRAGILITY_CONTEXT_ACDOC.md found)")
        return
    # print(f"Repo Root: {repo_root}") # Less noise
    
    # Locate venv Python
    venv_python = locate_venv_python(repo_root)
    if not venv_python:
        record_roadblock(f"Could not locate venv Python (expected at {repo_root / '.venv'})")
        return
    # print(f"Venv Python: {venv_python}")
    
    if len(sys.argv) < 2:
        print("\nUsage:")
        print("  mw state")
        print("  mw observe --note \"...\"")
        print("  mw record --note \"...\"")
        print("  mw run --intent \"...\" --script <path> -- [args]")
        print("  mw audit encoding")
        print("  mw audit witness")
        print("  mw lint bundles")
        print("  mw court-sweep")
        sys.exit(1)
    
    command = sys.argv[1]
    
    # Route main commands
    if command == "state":
        cmd_state(repo_root)
        
    elif command == "observe":
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument("command") # 'observe'
        parser.add_argument("--note", type=str, help="Note for state history")
        args, unknown = parser.parse_known_args()
        cmd_observe(repo_root, venv_python, args.note)
        
    elif command == "record":
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument("command") # 'record'
        parser.add_argument("--note", type=str, help="Note for state history")
        args, unknown = parser.parse_known_args()
        cmd_record(repo_root, venv_python, args.note)
        
    elif command == "run":
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument("command") # 'run'
        parser.add_argument("--intent", type=str, required=True, help="Intent for recorded run")
        parser.add_argument("--script", type=str, required=True, help="Script path to run")
        
        # mw run --intent "i" --script s.py -- arg1 arg2
        # argparse puts arg1 arg2 into unknown if they follow --
        
        args, unknown = parser.parse_known_args()
        
        # Cleanup unknown: remove '--' if present
        script_args = [u for u in unknown if u != "--"]
        
        cmd_run(repo_root, venv_python, args.intent, args.script, script_args)
        
    elif command == "audit":
        subcommand = sys.argv[2] if len(sys.argv) > 2 else None
        if subcommand == "encoding":
            cmd_audit_encoding(repo_root, venv_python)
        elif subcommand == "witness":
            cmd_audit_witness(repo_root, venv_python)
        else:
            print(f"Unknown audit subcommand: {subcommand}")
            sys.exit(1)
            
    elif command == "lint":
        subcommand = sys.argv[2] if len(sys.argv) > 2 else None
        if subcommand == "bundles":
            cmd_lint_bundles(repo_root, venv_python)
        elif subcommand == "scripts":
            cmd_lint_scripts(repo_root, venv_python)
        else:
            print(f"Unknown lint subcommand: {subcommand}")
            sys.exit(1)
            
    elif command == "court-sweep":
        cmd_court_sweep(repo_root, venv_python)
        
    elif command == "ritual":
        subcommand = sys.argv[2] if len(sys.argv) > 2 else None
        if subcommand == "run":
            import argparse
            parser = argparse.ArgumentParser()
            parser.add_argument("command")  # 'ritual'
            parser.add_argument("subcommand")  # 'run'
            parser.add_argument("--config", type=str, required=True, help="Path to ritual config JSON")
            parser.add_argument("--dry-run", action="store_true", help="Validate without executing")
            args, unknown = parser.parse_known_args()
            cmd_ritual_run(repo_root, venv_python, args.config, args.dry_run)
        elif subcommand == "list":
            cmd_ritual_list(repo_root)
        elif subcommand == "validate":
            import argparse
            parser = argparse.ArgumentParser()
            parser.add_argument("command")  # 'ritual'
            parser.add_argument("subcommand")  # 'validate'
            parser.add_argument("--config", type=str, required=True, help="Path to ritual config JSON")
            args, unknown = parser.parse_known_args()
            cmd_ritual_validate(repo_root, venv_python, args.config)
        else:
            print(f"Unknown ritual subcommand: {subcommand}")
            print("Available: run, list, validate")
            sys.exit(1)
        
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("MW CLI execution complete")

if __name__ == "__main__":
    main()
