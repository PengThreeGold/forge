@echo off
REM Forge 软件发布管理平台 - Nginx 配置测试脚本 (Windows版)

echo 正在测试Nginx配置...

REM 检查Nginx配置文件是否存在
if not exist "..\nginx\nginx.conf" (
    echo 错误: 未找到Nginx配置文件。
    echo 请确保nginx.conf文件存在于nginx目录中。
    pause
    exit /b 1
)

REM 测试Nginx配置
cd ..\nginx
nginx -t

if %ERRORLEVEL% equ 0 (
    echo.
    echo Nginx配置测试通过!
) else (
    echo.
    echo 错误: Nginx配置测试失败。
    echo 请检查nginx.conf配置文件是否有误。
)

pause