@echo off
cd /d "E:\dev\onmyoji-sa"
if exist "venv\Scripts\python.exe" (
    "venv\Scripts\python.exe" -m config_editor.osa_editor
) else (
    python -m config_editor.osa_editor
) 