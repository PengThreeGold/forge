@echo off
REM Forge 软件发布管理平台 - 全项目启动脚本 (Windows版)

echo 正在启动Forge软件发布管理平台...

REM 检查Python是否可用
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo 错误: 未找到Python。请确保已安装Python 3.7或更高版本并添加到PATH环境变量中。
    pause
    exit /b 1
)

REM 检查Node.js是否可用
node --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo 错误: 未找到Node.js。请确保已安装Node.js 14或更高版本并添加到PATH环境变量中。
    pause
    exit /b 1
)

REM 检查Nginx是否可用
nginx -v >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo 警告: 未找到Nginx。请确保已安装Nginx并添加到PATH环境变量中。
    echo 您可以从 https://nginx.org/en/download.html 下载安装。
    echo.
    set /p continue_without_nginx=是否继续启动后端和前端服务?(y/n): 
    if /i not "%continue_without_nginx%"=="y" (
        pause
        exit /b 1
    )
    set START_NGINX=false
) else (
    set START_NGINX=true
)

REM 检查是否已经安装了Python依赖
if not exist "backend\venv\Scripts\activate.bat" (
    echo 正在创建Python虚拟环境...
    cd backend
    python -m venv venv
    if %ERRORLEVEL% neq 0 (
        echo 错误: 创建Python虚拟环境失败。
        pause
        exit /b 1
    )
    
    echo 正在激活虚拟环境并安装依赖...
    call venv\Scripts\activate.bat
    pip install -r requirements.txt
    if %ERRORLEVEL% neq 0 (
        echo 错误: 安装Python依赖失败。
        pause
        exit /b 1
    )
    cd ..
)

REM 检查是否已经安装了前端依赖
if not exist "frontend\node_modules" (
    echo 正在安装前端依赖...
    cd frontend
    npm install
    if %ERRORLEVEL% neq 0 (
        echo 错误: 安装前端依赖失败。
        pause
        exit /b 1
    )
    cd ..
)

REM 检查是否已初始化数据库
if not exist "backend\forge.db" (
    echo 正在初始化数据库...
    cd backend
    call venv\Scripts\activate.bat
    python run.py init-db
    if %ERRORLEVEL% neq 0 (
        echo 错误: 初始化数据库失败。
        pause
        exit /b 1
    )
    cd ..
)

REM 检查是否已创建管理员账户
cd backend
call venv\Scripts\activate.bat
python -c "from app.models.user import User; admin=User.query.filter_by(role='admin').first(); print(1 if admin else 0)" > admin_check.txt
set /p admin_exists=<admin_check.txt
del admin_check.txt
cd ..

if "%admin_exists%"=="0" (
    echo 警告: 未找到管理员账户。
    set /p create_admin=是否现在创建管理员账户?(y/n): 
    if /i "%create_admin%"=="y" (
        cd backend
        call venv\Scripts\activate.bat
        python run.py init-admin
        if %ERRORLEVEL% neq 0 (
            echo 错误: 创建管理员账户失败。
            pause
            exit /b 1
        )
        cd ..
    )
)

REM 检查SSL证书是否存在
if not exist "nginx\certs\localhost.crt" (
    echo 警告: 未找到SSL证书。
    set /p generate_cert=是否现在生成自签名证书?(y/n): 
    if /i "%generate_cert%"=="y" (
        call scripts\generate-cert.bat
        if %ERRORLEVEL% neq 0 (
            echo 生成证书失败。
            pause
            exit /b 1
        )
    )
)

REM 启动后端服务
echo 正在启动后端服务...
start "Forge Backend" cmd /k "cd /d %CD%\backend && venv\Scripts\activate.bat && python run.py"

REM 等待几秒钟让后端服务启动
timeout /t 3 /nobreak >nul

REM 构建前端项目
echo 正在构建前端项目...
cd frontend
npm run build
if %ERRORLEVEL% neq 0 (
    echo 错误: 构建前端项目失败。
    pause
    exit /b 1
)
cd ..

REM 启动Nginx
if "%START_NGINX%"=="true" (
    echo 正在启动Nginx服务器...
    call scripts\start-nginx.bat
)

echo.
echo Forge软件发布管理平台已启动!
echo.
echo 如果已配置HTTPS:
echo 前端访问地址: https://localhost
echo 后端API地址: https://localhost/api
echo.
echo 如果未配置HTTPS:
echo 前端访问地址: http://localhost
echo 后端API地址: http://localhost/api
echo.
echo 注意: 
echo 1. 如果使用自签名证书，浏览器可能会显示安全警告。您可以点击"高级"并继续访问。
echo 2. 后端服务运行在命令行窗口中，请勿关闭该窗口。
echo 3. 如果需要停止服务，请运行stop-all.bat脚本或手动关闭所有窗口。

pause