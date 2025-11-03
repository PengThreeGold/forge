@echo off
REM Forge 软件发布管理平台 - Docker 开发环境启动脚本 (Windows版)

echo 正在启动Forge软件发布管理平台开发环境 (Docker)...

REM 检查Docker是否可用
docker --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo 错误: 未找到Docker。请确保已安装Docker Desktop并已启动。
    pause
    exit /b 1
)

REM 检查Docker Compose是否可用
docker-compose --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo 错误: 未找到Docker Compose。请确保已安装Docker Compose。
    pause
    exit /b 1
)

REM 构建并启动开发环境服务
echo 正在构建开发环境Docker镜像...
docker-compose -f docker-compose.dev.yml build

if %ERRORLEVEL% neq 0 (
    echo 错误: 构建Docker镜像失败。
    pause
    exit /b 1
)

echo 正在启动开发环境服务...
docker-compose -f docker-compose.dev.yml up -d

if %ERRORLEVEL% neq 0 (
    echo 错误: 启动Docker服务失败。
    pause
    exit /b 1
)

REM 等待服务启动
echo 等待服务启动...
timeout /t 10 /nobreak >nul

REM 初始化数据库（如果是第一次运行）
echo 检查是否需要初始化数据库...
docker-compose -f docker-compose.dev.yml exec backend python run.py init-db

REM 检查是否需要创建管理员账户
docker-compose -f docker-compose.dev.yml exec backend python -c "from app.models.user import User; admin=User.query.filter_by(role='admin').first(); print(1 if admin else 0)" > admin_check.txt
set /p admin_exists=<admin_check.txt
del admin_check.txt

if "%admin_exists%"=="0" (
    echo 正在创建管理员账户...
    docker-compose -f docker-compose.dev.yml exec backend python run.py init-admin --username admin --password admin123 --email admin@example.com
)

echo.
echo Forge软件发布管理平台开发环境已启动!
echo.
echo 前端开发服务器地址: http://localhost:8080
echo 后端API地址: http://localhost:5000/api
echo.
echo 数据库连接信息:
echo 主机: localhost
echo 端口: 5432
echo 用户名: postgres
echo 密码: postgres
echo 数据库: forge_dev
echo.
echo Redis连接信息:
echo 主机: localhost
echo 端口: 6379
echo.
echo 注意: 
echo 1. 要停止服务，请运行 docker-stop-dev.bat 脚本或使用命令: docker-compose -f docker-compose.dev.yml down
echo 2. 要查看服务日志，请使用命令: docker-compose -f docker-compose.dev.yml logs -f
echo 3. 前端代码已挂载到容器中，修改后自动热重载
echo 4. 后端代码已挂载到容器中，修改后需要重启后端服务

pause