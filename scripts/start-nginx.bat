@echo off
REM Forge 软件发布管理平台 - Nginx 启动脚本 (Windows版)

echo 正在启动Nginx服务器...

REM 检查Nginx配置文件是否存在
if not exist "..\nginx\nginx.conf" (
    echo 错误: 未找到Nginx配置文件。
    echo 请确保nginx.conf文件存在于nginx目录中。
    pause
    exit /b 1
)

REM 检查SSL证书是否存在
if not exist "..\nginx\certs\localhost.crt" (
    echo 警告: 未找到SSL证书。
    echo 请先运行generate-cert.bat生成自签名证书。
    echo.
    set /p generate_cert=是否现在生成证书?(y/n): 
    if /i "%generate_cert%"=="y" (
        call generate-cert.bat
        if %ERRORLEVEL% neq 0 (
            echo 生成证书失败。
            pause
            exit /b 1
        )
    ) else (
        echo 将在没有SSL证书的情况下启动Nginx。HTTPS将无法正常工作。
        echo.
    )
)

REM 检查Nginx是否已经运行
tasklist /FI "IMAGENAME eq nginx.exe" 2>NUL | find /I "nginx.exe" >NUL
if %ERRORLEVEL% equ 0 (
    echo 警告: Nginx已经在运行。
    set /p restart=是否重启Nginx?(y/n): 
    if /i "%restart%"=="y" (
        echo 正在停止Nginx...
        cd ..\nginx
        nginx -s quit
        timeout /t 2 /nobreak >nul
    ) else (
        echo Nginx保持运行状态。
        pause
        exit /b 0
    )
)

REM 启动Nginx
echo 正在启动Nginx...
cd ..\nginx
start nginx

REM 检查Nginx是否启动成功
timeout /t 2 /nobreak >nul
tasklist /FI "IMAGENAME eq nginx.exe" 2>NUL | find /I "nginx.exe" >NUL
if %ERRORLEVEL% equ 0 (
    echo Nginx启动成功!
    echo.
    echo 前端访问地址: http://localhost:80
    echo 后端API地址: http://localhost/api
    echo.
    echo 如果已配置HTTPS:
    echo 前端HTTPS访问地址: https://localhost:443
    echo 后端HTTPS API地址: https://localhost/api
    echo.
    echo 注意: 如果使用自签名证书，浏览器可能会显示安全警告。
    echo 您可以点击"高级"并继续访问。
) else (
    echo 错误: Nginx启动失败。
    echo 请检查nginx.conf配置文件是否有误。
)

pause