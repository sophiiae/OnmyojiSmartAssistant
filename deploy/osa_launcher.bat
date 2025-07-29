@echo off
set "SCRIPT_DIR=%~dp0"
set "PROJECT_ROOT=%SCRIPT_DIR%.."

cd /d "%PROJECT_ROOT%"
if exist "venv\Scripts\python.exe" (
    "venv\Scripts\python.exe" -m config_editor.main
) else (
    python -m config_editor.main
) 