@echo off
setlocal
cd /d "%~dp0"

REM Optional: show current state quickly
for /f "usebackq delims=" %%S in (`python -c "import json;from pathlib import Path;print(json.loads(Path('docs/STATE.json').read_text(encoding='utf-8'))['state'])"`) do set CUR=%%S
echo Current STATE: %CUR%
echo.

set "NOTE=%*"
if "%NOTE%"=="" (
  set /p NOTE=Enter STATE_HISTORY note ^(or leave blank^): 
)

echo.
choice /m "Confirm transition to OBSERVE?"
if errorlevel 2 (
  echo Cancelled.
  exit /b 1
)

python scripts\state_transition.py --to OBSERVE --confirm YES_I_MEAN_IT --note "%NOTE%"
echo.
pause
