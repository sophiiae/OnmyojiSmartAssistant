@echo off
chcp 65001
echo OSA项目exe构建工具
echo ================================================
echo.

echo 正在检查Python环境...
python --version
if errorlevel 1 (
    echo 错误：未找到Python环境，请先安装Python
    pause
    exit /b 1
)

echo.
echo 正在安装PyInstaller...
pip install pyinstaller

echo.
echo 开始构建OSA.exe程序...
python build_exe.py

echo.
echo 构建完成！请查看上级目录下的OSA.exe文件
pause 