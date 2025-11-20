#!/bin/bash

# Forge 一键启动脚本 (Linux/macOS)

set -e

# 设置日志文件路径
LOG_FILE="forge.log"

echo "====================================="
echo "Forge 软件发布管理平台 - 启动脚本"
echo "====================================="

# 将日志输出到文件和终端
exec > >(tee -a "$LOG_FILE")
exec 2>&1

echo "$(date '+%Y-%m-%d %H:%M:%S') - 开始启动Forge平台"

# 检查 Python
if ! command -v python &> /dev/null; then
    if ! command -v python3 &> /dev/null; then
        echo "错误：未找到 Python"
        exit 1
    fi
    alias python=python3
fi

# 检查 Node.js
if ! command -v node &> /dev/null; then
    echo "错误：未找到 Node.js"
    exit 1
fi

# 进入后端目录
cd backend

# 检查虚拟环境是否已存在
if [ ! -d ".venv" ]; then
    echo "创建 Python 虚拟环境..."
    python3 -m venv .venv
else
    echo "检测到虚拟环境已存在，跳过创建步骤"
fi

echo "激活虚拟环境..."
source .venv/bin/activate

echo "安装/更新后端依赖..."
pip install -q -r requirements.txt

# 初始化数据库（如果需要）
if [ ! -f "forge.db" ]; then
    echo "初始化数据库..."
    python run.py init
    echo ""
    echo "请创建管理员账户："
    python run.py init-admin
fi

# 返回项目根目录
cd ..

# 构建前端
cd frontend

# 检查并安装前端依赖
if [ ! -d "node_modules" ]; then
    echo "安装前端依赖..."
    npm install
else
    echo "检测到前端依赖已存在，跳过安装步骤"
fi

echo "构建前端..."
npm run build

# 复制前端构建产物到后端静态目录
echo "部署前端..."
rm -rf ../backend/static
cp -r dist ../backend/static

cd ..

# 启动服务器
echo ""
echo "====================================="
echo "启动服务器..."
echo "====================================="
cd backend
source .venv/bin/activate
echo "$(date '+%Y-%m-%d %H:%M:%S') - 服务器启动中..."
nohup python run.py run > ../forge.log 2>&1 &
SERVER_PID=$!
echo "服务器已启动，PID: $SERVER_PID"
echo "日志文件: forge.log"
echo "请访问: http://localhost:1110"
echo "如需停止服务器，请执行: kill $SERVER_PID"
