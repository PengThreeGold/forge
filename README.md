# Forge 软件发布管理平台

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.121+-green.svg)](https://fastapi.tiangolo.com)
[![Vue.js](https://img.shields.io/badge/vue-3.4+-brightgreen.svg)](https://vuejs.org)

Forge 是一个现代化的软件发布管理平台，旨在帮助开发团队更高效地管理和发布软件版本。它提供了完整的软件版本管理、发布管理、存储管理、下载管理和统计功能，**采用单进程架构，无需反向代理，一键启动**。

## ✨ 特性

- 🚀 **单进程架构**：后端集成前端静态文件服务，无需 Nginx 等反向代理
- 🔐 **安全认证**：基于 JWT 的认证系统，支持安全的用户登录和权限管理
- 📦 **软件版本管理**：支持多版本软件管理，包括版本号、发布说明、文件上传等
- 📊 **统计分析**：提供详细的下载统计、版本统计和系统整体统计
- 🔔 **Webhook 集成**：支持 Webhook 配置，实现事件通知和自动化集成
- 🌐 **公共 API**：提供无需认证的公共下载接口，支持 API 密钥验证
- 📱 **响应式设计**：基于 Element Plus 的现代化 UI，支持多种设备访问
- 🛡️ **安全可靠**：文件完整性校验、密码加密存储、输入验证等多重安全保障
- ⚡ **一键启动**：提供自动化脚本，一条命令完成所有配置和启动

## 📋 系统要求

- **Python 3.8+**
- **Node.js 16+**（仅构建时需要，运行时不需要）
- **SQLite**（内置，无需额外安装）

## 🚀 快速开始

### 方式一：一键启动（推荐）

#### Linux/macOS

```bash
# 克隆仓库
git clone https://github.com/PengThreeGold/forge.git
cd forge

# 赋予执行权限
chmod +x start.sh

# 一键启动
./start.sh
```

#### Windows

```batch
# 克隆仓库
git clone https://github.com/PengThreeGold/forge.git
cd forge

# 一键启动
start.bat
```

启动脚本会自动：
1. 创建 Python 虚拟环境并安装后端依赖
2. 初始化数据库和基础数据
3. 安装前端依赖并构建生产版本
4. 将前端文件部署到后端静态目录
5. 启动服务器

首次启动会提示创建管理员账户，按提示输入即可。

### 方式二：手动启动

#### 1. 后端设置

```bash
cd backend

# 创建虚拟环境（可选但推荐）
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# 或
.venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt

# 初始化数据库
python run.py init

# 创建管理员账户
python run.py init-admin

# 启动后端（仅后端，用于开发）
python run.py run
```

#### 2. 前端设置（开发模式）

```bash
cd frontend

# 安装依赖
npm install

# 开发模式（带热重载）
npm run dev

# 或构建生产版本
npm run build
```

## 📖 使用说明

### 访问应用

启动后访问：
- **主页**：http://localhost:1110
- **管理后台**：http://localhost:1110/login
- **API 文档**：http://localhost:1110/api/docs

### 默认端口

- 后端 API：1110
- 前端开发服务器（如果分离运行）：3000

### 目录结构

```
forge/
├── backend/              # 后端代码
│   ├── app/             # 应用代码
│   │   ├── api/         # API 路由
│   │   ├── core/        # 核心配置
│   │   ├── crud/        # 数据库操作
│   │   ├── db/          # 数据库配置
│   │   ├── models/      # 数据模型
│   │   ├── schemas/     # Pydantic 模式
│   │   └── utils/       # 工具函数
│   ├── storage/         # 文件存储
│   ├── static/          # 前端静态文件（自动生成）
│   ├── run.py           # 启动脚本
│   ├── requirements.txt # Python 依赖
│   └── .env            # 环境配置
├── frontend/            # 前端代码
│   ├── src/
│   │   ├── api/         # API 接口
│   │   ├── layouts/     # 布局组件
│   │   ├── views/       # 页面组件
│   │   ├── stores/      # 状态管理
│   │   ├── router/      # 路由配置
│   │   └── utils/       # 工具函数
│   ├── package.json     # Node 依赖
│   └── vite.config.js   # Vite 配置
├── start.sh             # Linux/macOS 启动脚本
├── start.bat            # Windows 启动脚本
└── README.md            # 本文件
```

## 🔧 配置说明

### 后端配置

编辑 `backend/.env` 文件：

```env
# 服务器配置
HOST=0.0.0.0
PORT=1110
DEBUG=True

# JWT 配置（生产环境务必修改）
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_MINUTES=10080

# 数据库配置
SQLITE_DB_PATH=forge.db

# CORS 配置
CORS_ORIGINS=*

# 文件存储配置
UPLOAD_DIR=storage/uploads
MAX_FILE_SIZE=1073741824

# Webhook 配置
WEBHOOK_TIMEOUT=10
WEBHOOK_MAX_RETRIES=3
```

### 前端配置

编辑 `frontend/vite.config.js` 修改开发服务器配置。

## 🔐 安全建议

1. **生产环境必须修改 SECRET_KEY**：
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

2. **限制 CORS 来源**：将 `CORS_ORIGINS` 设置为具体域名

3. **使用 HTTPS**：生产环境建议配置 SSL 证书

4. **定期备份数据库**：SQLite 数据库文件位于 `backend/forge.db`

## 📝 API 使用示例

### 获取公共软件列表

```bash
curl http://localhost:1110/api/public/spaces
```

### 下载软件

```bash
curl -O "http://localhost:1110/api/public/spaces/{space_id}/download?version=1.0.0&arch=x86_64&api_key=your_api_key"
```

### 管理 API（需要认证）

```bash
# 登录获取 token
curl -X POST http://localhost:1110/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"your_password"}'

# 使用 token 访问管理接口
curl http://localhost:1110/api/spaces \
  -H "Authorization: Bearer your_access_token"
```

## 🛠️ 开发指南

### 后端开发

```bash
cd backend
python run.py run  # 启动后端，支持热重载
```

### 前端开发

```bash
cd frontend
npm run dev  # 启动前端开发服务器，自动代理 API 到后端
```

### 运行测试

```bash
# 后端测试
cd backend
pytest

# 前端测试
cd frontend
npm run test
```

## 🐛 故障排除

### 问题：启动失败

- 检查 Python 和 Node.js 版本是否符合要求
- 确保端口 1110 未被占用
- 查看错误日志定位问题

### 问题：前端页面空白

- 检查前端是否已构建：`ls backend/static`
- 重新运行启动脚本

### 问题：数据库错误

- 删除 `backend/forge.db` 后重新运行 `python run.py init`

## 📄 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📞 联系方式

- 作者：PengThreeGold
- 仓库：https://github.com/PengThreeGold/forge

---

**注意**：本项目处于活跃开发中，API 可能会有变化。生产环境使用前请充分测试。
    pip install -r requirements.txt
    cp .env.example .env
    # 编辑 .env 文件，填入您的配置信息
    python run.py init-admin
    python run.py run
    ```

3. **前端设置**

    ```bash
    cd frontend
    npm install
    cp .env.example .env
    # 编辑 .env 文件，填入您的配置信息
    npm run serve
    ```

4. **访问应用**

    - 前端应用：<http://localhost:8080>
    - 后端 API：<http://localhost:5000>

## 文档

- [架构设计](ARCHITECTURE.md)
- [API 文档](backend\openapi.yaml)
- [贡献指南](CONTRIBUTING.md)
- [更新日志](CHANGELOG.md)

## 功能模块

### 用户管理

- 用户注册和登录
- JWT 令牌认证
- 密码修改
- 权限管理

### 软件管理

- 软件空间创建、编辑、删除
- 软件空间状态管理（激活/停用）
- 软件版本管理
- 软件文件上传
- 软件版本状态管理

### 下载管理

- 软件下载功能
- 下载记录统计
- 公开下载接口（无需认证）

### 统计分析

- 软件下载统计
- 版本下载统计
- 日下载量统计
- 系统整体统计

### Webhook 集成

- Webhook 配置管理
- 事件通知（下载、创建、更新、删除）
- Webhook 密钥验证

## 开发指南

请参考 [开发指南](DEVELOPMENT.md) 了解如何参与项目开发。

## 部署指南

请参考 [部署指南](DEPLOYMENT.md) 了解如何部署应用到生产环境。

## API 文档

请参考 [API 文档](backend\openapi.yaml) 了解详细的 API 接口说明。

## 贡献

我们欢迎任何形式的贡献，包括但不限于：

- 报告 Bug
- 提出新功能建议
- 改进文档
- 提交代码

## 许可证

本项目采用 MIT 许可证。详情请参阅 [LICENSE](LICENSE) 文件。

## 致谢

感谢以下开源项目：

- [Vue.js](https://vuejs.org/)
- [Element Plus](https://element-plus.org/)
- [Docker](https://www.docker.com/)
- [Nginx](https://nginx.org/)
