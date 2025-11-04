@echo off
echo ==========================================
echo CORS 快速测试脚本
echo ==========================================
echo.
echo 此脚本将快速测试 CORS 配置是否正确
echo.

REM 检查 curl 是否可用
where curl >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: curl 命令不可用，请先安装 curl 或使用 Git Bash
    pause
    exit /b 1
)

set BACKEND_URL=http://localhost:5000
set FRONTEND_URL=http://localhost:8080

echo [1/3] 检查后端服务...
curl -s --output nul --connect-timeout 3 "%BACKEND_URL%/api/auth/login"
if %errorlevel% equ 0 (
    echo ✓ 后端服务正在运行
) else (
    echo ✗ 后端服务未运行，请先启动:
    echo   cd backend ^&^& python run.py
    pause
    exit /b 1
)

echo [2/3] 检查前端服务...
curl -s --output nul --connect-timeout 3 "%FRONTEND_URL%"
if %errorlevel% equ 0 (
    echo ✓ 前端服务正在运行
) else (
    echo ✗ 前端服务未运行，请先启动:
    echo   cd frontend ^&^& npm run serve
    pause
    exit /b 1
)

echo [3/3] 测试 CORS 预检请求...
curl -s -i -X OPTIONS -H "Origin: %FRONTEND_URL%" -H "Access-Control-Request-Method: POST" "%BACKEND_URL%/api/auth/login" | findstr /i "Access-Control-Allow-Origin" >nul
if %errorlevel% equ 0 (
    echo ✓ CORS 预检请求成功
    echo.
    echo ==========================================
    echo 恭喜！CORS 配置正常
    echo ==========================================
    echo.
    echo 现在可以在浏览器中访问 %FRONTEND_URL% 测试应用功能
) else (
    echo ✗ CORS 预检请求失败
    echo.
    echo 可能的解决方案:
    echo 1. 检查后端环境变量配置 (.env 文件中的 CORS_ORIGINS)
    echo 2. 重启后端服务
    echo 3. 清除浏览器缓存
    echo.
    echo 详细修复指南请参考: CORS-修复指南.md
)

echo.
pause