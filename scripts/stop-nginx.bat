@echo off
REM Forge 软件发布管理平台 - Nginx 停止脚本 (Windows版)

echo 正在停止Nginx服务器...

REM 检查Nginx是否正在运行
tasklist /FI "IMAGENAME eq nginx.exe" 2>NUL | find /I "nginx.exe" >NUL
if %ERRORLEVEL% neq 0 (
    echo Nginx未运行。
    pause
    exit /b 0
)

REM 尝试优雅地停止Nginx
cd ..\nginx
nginx -s quit

REM 等待几秒钟让Nginx优雅关闭
timeout /t 5 /nobreak >nul

REM 检查Nginx是否已停止
tasklist /FI "IMAGENAME eq nginx.exe" 2>NUL | find /I "nginx.exe" >NUL
if %ERRORLEVEL% neq 0 (
    echo Nginx已成功停止。
) else (
    echo 警告: 优雅停止失败，尝试强制停止...
    
    REM 强制停止Nginx进程
    taskkill /F /IM nginx.exe
    
    REM 再次检查
    timeout /t 2 /nobreak >nul
    tasklist /FI "IMAGENAME eq nginx.exe" 2>NUL | find /I "nginx.exe" >NUL
    if %ERRORLEVEL% neq 0 (
        echo Nginx已强制停止。
    ) else (
        echo 错误: 无法停止Nginx进程。
        echo 请手动结束nginx.exe进程。
    )
)

pause