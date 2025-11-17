@echo off
REM Forge 一键启动脚本 (Windows)

setlocal enabledelayedexpansion

echo =====================================
echo Forge 软件发布管理平台 - 启动脚本
echo =====================================

REM 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误：未找到 Python
    exit /b 1
)

REM 检查 Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo 错误：未找到 Node.js
    exit /b 1
)

REM 进入后端目录
cd backend

REM 检查并安装后端依赖
if not exist ".venv" (
    echo 创建 Python 虚拟环境...
    python -m venv .venv
)

echo 激活虚拟环境...
call .venv\Scripts\activate.bat

echo 安装后端依赖...
pip install -q -r requirements.txt

REM 初始化数据库（如果需要）
if not exist "forge.db" (
    echo 初始化数据库...
    python run.py init
    echo.
    echo 请创建管理员账户：
    python run.py init-admin
)

REM 返回项目根目录
cd ..

REM 构建前端
cd frontend

REM 检查并安装前端依赖
if not exist "node_modules" (
    echo 安装前端依赖...
    call npm install
)

echo 构建前端...
call npm run build

REM 复制前端构建产物到后端静态目录
echo 部署前端...
if exist "..\backend\static" rmdir /s /q "..\backend\static"
xcopy /E /I /Q dist "..\backend\static"

cd ..

REM 启动服务器
echo.
echo =====================================
echo 启动服务器...
echo =====================================
cd backend
call .venv\Scripts\activate.bat
python run.py run
