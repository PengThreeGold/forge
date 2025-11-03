@echo off
REM Forge 软件发布管理平台 - Docker 启动脚本 (Windows版)

echo 正在启动Forge软件发布管理平台 (Docker)...

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

REM 检查环境变量文件是否存在
if not exist ".env" (
    echo 警告: 未找到.env环境变量文件。
    set /p create_env=是否从.env.example复制创建环境变量文件?(y/n): 
    if /i "%create_env%"=="y" (
        copy .env.example .env
        echo 已创建.env文件，请根据实际情况修改其中的配置。
        echo 按任意键继续...
        pause >nul
    ) else (
        echo 请手动创建.env文件。
        pause
        exit /b 1
    )
)

REM 检查SSL证书目录是否存在
if not exist "nginx\certs" (
    mkdir nginx\certs
)

REM 检查SSL证书是否存在
if not exist "nginx\certs\localhost.crt" (
    echo 警告: 未找到SSL证书。
    echo 在Docker环境中，您可以使用Let's Encrypt获取免费证书，或者使用自签名证书。
    echo 如果是开发环境，可以使用以下命令生成自签名证书:
    echo openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout nginx/certs/localhost.key -out nginx/certs/localhost.crt -subj "/CN=localhost"
    set /p generate_cert=是否现在生成自签名证书?(y/n): 
    if /i "%generate_cert%"=="y" (
        openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout nginx/certs/localhost.key -out nginx/certs/localhost.crt -subj "/CN=localhost"
        if %ERRORLEVEL% neq 0 (
            echo 生成证书失败，请确保已安装OpenSSL。
            pause
            exit /b 1
        )
    )
)

REM 询问使用哪个配置文件启动
echo 请选择启动模式:
echo 1. 开发模式 (仅后端和前端)
echo 2. 生产模式 (包括Nginx反向代理)
set /p mode=请输入选项(1/2): 

if "%mode%"=="1" (
    set COMPOSE_PROFILES=
    echo 正在启动开发模式...
) else if "%mode%"=="2" (
    set COMPOSE_PROFILES=--profile production
    echo 正在启动生产模式...
) else (
    echo 无效的选项，将使用开发模式启动。
    set COMPOSE_PROFILES=
)

REM 构建并启动服务
echo 正在构建Docker镜像...
docker-compose build

if %ERRORLEVEL% neq 0 (
    echo 错误: 构建Docker镜像失败。
    pause
    exit /b 1
)

echo 正在启动服务...
docker-compose %COMPOSE_PROFILES% up -d

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
docker-compose exec backend python run.py init-db

REM 检查是否需要创建管理员账户
docker-compose exec backend python -c "from app.models.user import User; admin=User.query.filter_by(role='admin').first(); print(1 if admin else 0)" > admin_check.txt
set /p admin_exists=<admin_check.txt
del admin_check.txt

if "%admin_exists%"=="0" (
    echo 正在创建管理员账户...
    docker-compose exec backend python run.py init-admin --username admin --password admin123 --email admin@example.com
)

echo.
echo Forge软件发布管理平台已启动!
echo.
echo 如果使用开发模式:
echo 前端访问地址: http://localhost
echo 后端API地址: http://localhost/api
echo.
echo 如果使用生产模式:
echo 前端访问地址: http://localhost:8080
echo 后端API地址: http://localhost:8080/api
echo.
echo HTTPS访问:
echo 前端HTTPS访问地址: https://localhost:8443
echo 后端HTTPS API地址: https://localhost:8443/api
echo.
echo 注意: 
echo 1. 如果使用自签名证书，浏览器可能会显示安全警告。您可以点击"高级"并继续访问。
echo 2. 要停止服务，请运行 docker-stop.bat 脚本或使用命令: docker-compose down
echo 3. 要查看服务日志，请使用命令: docker-compose logs -f

pause