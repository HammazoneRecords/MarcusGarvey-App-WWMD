#!/usr/bin/env python3
"""
Wrapper to run Full Court Press and save output to file
"""
import subprocess
import sys
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_FILE = BASE_DIR / "full_court_press_latest.txt"

# Run with UTF-8 encoding
result = subprocess.run(
    [sys.executable, str(BASE_DIR / "tools" / "full_court_press.py")],
    cwd=BASE_DIR,
    capture_output=True,
    text=True,
    encoding='utf-8',
    errors='replace'
)

# Write to file
output_text = f"""Full Court Press Run - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'='*70}

STDOUT:
{result.stdout}

STDERR:
{result.stderr if result.stderr else '(none)'}

EXIT CODE: {result.returncode}
"""

OUTPUT_FILE.write_text(output_text, encoding='utf-8')

print(f"Output saved to: {OUTPUT_FILE.name}")
print(f"Exit code: {result.returncode}")

# Show summary
if result.returncode == 0:
    print("[OK] Full Court Press: PASS")
else:
    print("[FAIL] Full Court Press: FAILED (see output file for details)")

sys.exit(result.returncode)
