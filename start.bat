@echo off
REM 强制设置UTF-8编码，解决中文乱码问题
chcp 65001 > nul
REM Forge 一键启动脚本 (Windows)

setlocal enabledelayedexpansion

REM 设置日志文件路径
set LOG_FILE=forge.log

echo =====================================
echo Forge 软件发布管理平台 - 启动脚本
echo =====================================

REM 记录启动时间
echo %date% %time% - 开始启动Forge平台 >> %LOG_FILE%

REM 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误：未找到 Python
    echo %date% %time% - 错误：未找到 Python >> %LOG_FILE%
    exit /b 1
)

REM 检查 Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo 错误：未找到 Node.js
    echo %date% %time% - 错误：未找到 Node.js >> %LOG_FILE%
    exit /b 1
)

REM 进入后端目录
cd backend

REM 检查虚拟环境是否已存在
if not exist ".venv" (
    echo 创建 Python 虚拟环境...
    echo %date% %time% - 创建 Python 虚拟环境... >> %LOG_FILE%
    python -m venv .venv
) else (
    echo 检测到虚拟环境已存在，跳过创建步骤
    echo %date% %time% - 检测到虚拟环境已存在，跳过创建步骤 >> %LOG_FILE%
)

echo 激活虚拟环境...
call .venv\Scripts\activate.bat

echo 安装/更新后端依赖...
echo %date% %time% - 安装/更新后端依赖... >> %LOG_FILE%
pip install -q -r requirements.txt >> ..\%LOG_FILE% 2>&1

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
    echo %date% %time% - 安装前端依赖... >> ..\%LOG_FILE%
    call npm install >> ..\%LOG_FILE% 2>&1
) else (
    echo 检测到前端依赖已存在，跳过安装步骤
    echo %date% %time% - 检测到前端依赖已存在，跳过安装步骤 >> ..\%LOG_FILE%
)

echo 构建前端...
echo %date% %time% - 构建前端... >> ..\%LOG_FILE%
call npm run build >> ..\%LOG_FILE% 2>&1

REM 复制前端构建产物到后端静态目录
echo 部署前端...
echo %date% %time% - 部署前端... >> ..\%LOG_FILE%
if exist "..\backend\static" rmdir /s /q "..\backend\static"
xcopy /E /I /Q dist "..\backend\static" >> ..\%LOG_FILE% 2>&1

cd ..

REM 启动服务器
echo.
echo =====================================
echo 启动服务器...
echo =====================================
cd backend
call .venv\Scripts\activate.bat
echo %date% %time% - 服务器启动中... >> ..\%LOG_FILE%
start /B python run.py run >> ..\%LOG_FILE% 2>&1

echo 服务器已后台启动
echo 日志文件: forge.log
echo 请访问: http://localhost:1110
echo 如需停止服务器，请关闭对应的命令行窗口或使用任务管理器结束python进程
