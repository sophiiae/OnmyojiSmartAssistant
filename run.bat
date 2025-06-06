@echo off
REM 自动运行 OSA 配置编辑器（多文件Tab版）
cd /d %~dp0
python -m config_editor.main
pause 