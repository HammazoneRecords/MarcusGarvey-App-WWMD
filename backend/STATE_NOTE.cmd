@echo off
cd /d "%~dp0"
python scripts\state_history_note.py --note "%*"
pause
