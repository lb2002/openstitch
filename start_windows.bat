@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
    echo Erstelle virtuelle Python-Umgebung ...
    python -m venv .venv
    .venv\Scripts\python.exe -m pip install -e .
)
start "" ".venv\Scripts\pythonw.exe" -m openstitch
