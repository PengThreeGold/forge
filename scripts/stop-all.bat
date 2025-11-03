@echo off
REM Forge 软件发布管理平台 - 全项目停止脚本 (Windows版)

echo 正在停止Forge软件发布管理平台...

REM 停止Nginx
call scripts\stop-nginx.bat

REM 停止后端服务
echo 正在停止后端服务...
tasklist /FI "IMAGENAME eq python.exe" /FO CSV | find /I "run.py" >NUL
if %ERRORLEVEL% equ 0 (
    echo 正在关闭Python后端进程...
    taskkill /F /FI "WINDOWTITLE eq Forge Backend*"
    timeout /t 2 /nobreak >nul
) else (
    echo 后端服务未运行。
)

REM 检查是否还有Python进程在运行
tasklist /FI "IMAGENAME eq python.exe" /FO CSV >NUL
if %ERRORLEVEL% equ 0 (
    echo 警告: 仍有Python进程在运行。
    set /p stop_all_python=是否停止所有Python进程?(y/n): 
    if /i "%stop_all_python%"=="y" (
        echo 正在停止所有Python进程...
        taskkill /F /IM python.exe
    )
)

echo.
echo Forge软件发布管理平台已停止。
pause