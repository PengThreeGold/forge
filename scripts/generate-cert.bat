@echo off
REM Forge 软件发布管理平台 - SSL 证书生成脚本 (Windows版)
REM 此脚本用于生成开发环境的自签名SSL证书

echo 正在生成自签名SSL证书...

REM 创建证书目录
if not exist "..\nginx\certs" mkdir "..\nginx\certs"

REM 证书配置
set CERT_COUNTRY=CN
set CERT_STATE=Shanghai
set CERT_LOCALITY=Shanghai
set CERT_ORGANIZATION=Forge Team
set CERT_ORGANIZATIONAL_UNIT=Forge
set CERT_COMMON_NAME=localhost
set CERT_EMAIL=admin@forge.com

REM 私钥文件
set PRIVATE_KEY=..\nginx\certs\localhost.key
REM 证书文件
set CERT_FILE=..\nginx\certs\localhost.crt

REM 检查OpenSSL是否可用
openssl version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo 错误: 未找到OpenSSL。请确保已安装OpenSSL并添加到PATH环境变量中。
    echo 您可以从 https://slproweb.com/products/Win32OpenSSL.html 下载安装。
    exit /b 1
)

REM 生成私钥
openssl genrsa -out %PRIVATE_KEY% 2048
if %ERRORLEVEL% neq 0 (
    echo 错误: 生成私钥失败。
    exit /b 1
)

REM 生成自签名证书
openssl req -new -x509 -key %PRIVATE_KEY% -out %CERT_FILE% -days 3650 -subj "/C=%CERT_COUNTRY%/ST=%CERT_STATE/L=%CERT_LOCALITY/O=%CERT_ORGANIZATION%/OU=%CERT_ORGANIZATIONAL_UNIT%/CN=%CERT_COMMON_NAME%/emailAddress=%CERT_EMAIL%"
if %ERRORLEVEL% neq 0 (
    echo 错误: 生成证书失败。
    exit /b 1
)

REM 设置适当的权限
echo 设置证书文件权限...
icacls %PRIVATE_KEY% /reset
icacls %PRIVATE_KEY% /inheritance:r
icacls %PRIVATE_KEY% /grant:r "SYSTEM:(R)"
icacls %PRIVATE_KEY% /grant:r "Administrators:(R)"

icacls %CERT_FILE% /reset
icacls %CERT_FILE% /inheritance:r
icacls %CERT_FILE% /grant:r "SYSTEM:(R)"
icacls %CERT_FILE% /grant:r "Administrators:(R)"
icacls %CERT_FILE% /grant:r "Users:(R)"

echo SSL证书已生成:
echo 私钥: %PRIVATE_KEY%
echo 证书: %CERT_FILE%
echo.
echo 注意: 这是自签名证书，仅用于开发环境。在生产环境中，请使用受信任的CA签发的证书。