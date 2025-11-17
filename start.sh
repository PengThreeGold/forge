#!/bin/bash

# Forge 一键启动脚本 (Linux/macOS)

set -e

echo "====================================="
echo "Forge 软件发布管理平台 - 启动脚本"
echo "====================================="

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "错误：未找到 Python 3"
    exit 1
fi

# 检查 Node.js
if ! command -v node &> /dev/null; then
    echo "错误：未找到 Node.js"
    exit 1
fi

# 进入后端目录
cd backend

# 检查并安装后端依赖
if [ ! -d ".venv" ]; then
    echo "创建 Python 虚拟环境..."
    python3 -m venv .venv
fi

echo "激活虚拟环境..."
source .venv/bin/activate

echo "安装后端依赖..."
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
python run.py run
