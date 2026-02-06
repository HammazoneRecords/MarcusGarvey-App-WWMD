@echo off
REM Load API key from .env and run wwmd_ask_hybrid.py
for /f "tokens=2 delims==" %%a in ('type .env ^| findstr GEMINI_API_KEY') do set GEMINI_API_KEY=%%a
set GEMINI_API_KEY=%GEMINI_API_KEY:"=%
cd "backend"
python scripts/wwmd_ask_hybrid.py %*
cd ".."
