@echo off
chcp 65001
echo OSA项目构建工具
echo ================================================
echo.

echo 正在进入build目录...
cd build

echo.
echo 开始构建OSA.exe程序...
call build.bat

echo.
echo 构建完成！请查看根目录下的OSA.exe文件
pause 