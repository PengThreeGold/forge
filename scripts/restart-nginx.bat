@echo off
REM Forge 软件发布管理平台 - Nginx 重启脚本 (Windows版)

echo 正在重启Nginx服务器...

REM 停止Nginx
call stop-nginx.bat

REM 等待一秒钟
timeout /t 1 /nobreak >nul

REM 启动Nginx
call start-nginx.bat

pause