@echo off
chcp 65001
echo 正在启动OSA配置编辑器...
echo.
echo 注意：首次启动可能需要30-60秒，请耐心等待...
echo.

if exist "OSA.exe" (
    echo 正在启动程序，请稍候...
    start "" "OSA.exe"
    echo.
    echo OSA程序已启动！
    echo 如果程序没有立即显示，请检查任务栏或等待几秒钟
) else (
    echo 错误：未找到OSA.exe文件
    echo 请先运行 构建OSA.bat 构建程序
    pause
) 