@echo off
REM Forge 软件发布管理平台 - Docker 开发环境停止脚本 (Windows版)

echo 正在停止Forge软件发布管理平台开发环境 (Docker)...

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

REM 询问是否保留数据卷
set /p preserve_volumes=是否保留开发环境数据卷?(y/n): 
if /i "%preserve_volumes%"=="y" (
    set VOLUMES_FLAG=
) else (
    set VOLUMES_FLAG=--volumes
)

REM 停止并删除容器、网络和可选的数据卷
echo 正在停止并删除开发环境容器...
docker-compose -f docker-compose.dev.yml down %VOLUMES_FLAG%

if %ERRORLEVEL% neq 0 (
    echo 警告: 停止Docker开发环境服务时出现错误。
) else (
    echo Docker开发环境服务已成功停止。
)

REM 询问是否删除Docker镜像
set /p remove_images=是否删除开发环境Docker镜像?(y/n): 
if /i "%remove_images%"=="y" (
    echo 正在删除开发环境Docker镜像...
    docker-compose -f docker-compose.dev.yml down --rmi all
    if %ERRORLEVEL% neq 0 (
        echo 警告: 删除Docker镜像时出现错误。
    ) else (
        echo Docker镜像已成功删除。
    )
)

echo.
echo Forge软件发布管理平台开发环境已停止。
pause