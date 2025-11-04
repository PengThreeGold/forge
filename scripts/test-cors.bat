@echo off
setlocal enabledelayedexpansion

echo ==========================================
echo CORS 配置测试脚本 (Windows)
echo ==========================================

REM 检查后端服务是否运行
echo 1. 检查后端服务状态...
set BACKEND_URL=http://localhost:5000
curl -s --output nul --connect-timeout 5 "%BACKEND_URL%/api/auth/login"
if !errorlevel! equ 0 (
    echo ✓ 后端服务正在运行
) else (
    echo ✗ 后端服务未运行或无法访问
    echo 请先启动后端服务: cd backend ^&^& python run.py
    pause
    exit /b 1
)

REM 检查前端服务是否运行
echo 2. 检查前端服务状态...
set FRONTEND_URL=http://localhost:8080
curl -s --output nul --connect-timeout 5 "%FRONTEND_URL%"
if !errorlevel! equ 0 (
    echo ✓ 前端服务正在运行
) else (
    echo ✗ 前端服务未运行或无法访问
    echo 请先启动前端服务: cd frontend ^&^& npm run serve
    pause
    exit /b 1
)

REM 测试 CORS 预检请求
echo 3. 测试 CORS 预检请求 (OPTIONS)...
set ORIGIN=http://localhost:8080
set METHOD=POST
set HEADERS=Content-Type, Authorization

curl -s -i -X OPTIONS ^
    -H "Origin: %ORIGIN%" ^
    -H "Access-Control-Request-Method: %METHOD%" ^
    -H "Access-Control-Request-Headers: %HEADERS%" ^
    "%BACKEND_URL%/api/auth/login" > temp_response.txt

findstr /i "Access-Control-Allow-Origin" temp_response.txt >nul
if !errorlevel! equ 0 (
    echo ✓ CORS 预检请求成功，服务器返回了必要的头部
) else (
    echo ✗ CORS 预检请求失败，服务器未返回必要的头部
    echo 响应内容:
    type temp_response.txt
)

REM 测试简单的跨域 GET 请求
echo 4. 测试跨域 GET 请求...
curl -s -i -X GET ^
    -H "Origin: %ORIGIN%" ^
    -H "Accept: application/json" ^
    "%BACKEND_URL%/api/auth/init-admin" > temp_response2.txt

findstr /i "Access-Control-Allow-Origin" temp_response2.txt >nul
if !errorlevel! equ 0 (
    echo ✓ 跨域 GET 请求成功，服务器返回了必要的头部
) else (
    echo ✗ 跨域 GET 请求失败，服务器未返回必要的头部
    echo 响应内容:
    type temp_response2.txt
)

REM 清理临时文件
if exist temp_response.txt del temp_response.txt
if exist temp_response2.txt del temp_response2.txt

echo ==========================================
echo 测试完成
echo ==========================================

REM 浏览器测试建议
echo 6. 浏览器端跨域测试建议:
echo - 打开浏览器访问 %FRONTEND_URL%
echo - 打开浏览器开发者工具 (F12)
echo - 尝试登录或其他需要API交互的操作
echo - 检查 Network 标签中是否有 CORS 错误
echo - 检查 Console 标签中是否有跨域相关错误
echo.
echo 如果仍有问题，请检查:
echo - 前端环境变量配置 (.env.development)
echo - 后端环境变量配置 (.env)
echo - 浏览器缓存和扩展程序
echo ==========================================

pause