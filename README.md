# Forge 软件发布管理平台

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![Node.js Version](https://img.shields.io/badge/node-16+-green.svg)](https://nodejs.org)
[![Vue.js](https://img.shields.io/badge/vue-3.0+-brightgreen.svg)](https://vuejs.org)

Forge 是一个现代化的软件发布管理平台，旨在帮助开发团队更高效地管理和发布软件版本。它提供了完整的软件版本管理、发布管理、存储管理、下载管理和统计功能，支持前后端完全分离的架构，并支持 HTTPS 配置。

## 特性

- 🚀 **前后端分离架构**：使用 Vue 3.0+ 和 fastapi 构建，实现完全的前后端分离
- 🔐 **安全认证**：基于 JWT 的认证系统，支持安全的用户登录和权限管理
- 📦 **软件版本管理**：支持多版本软件管理，包括版本号、发布说明、文件上传等
- 📊 **统计分析**：提供详细的下载统计、版本统计和系统整体统计
- 🔔 **Webhook 集成**：支持 Webhook 配置，实现事件通知和自动化集成
- 🌐 **HTTPS 支持**：支持 HTTPS 配置，确保数据传输安全
- 📱 **响应式设计**：基于 Element Plus 的现代化 UI，支持多种设备访问
- 🛡️ **安全可靠**：文件完整性校验、密码加密存储、输入验证等多重安全保障

## 系统要求

- **后端**：
  - Python
  - FastAPI
  - SQLAlchemy
  - SQLite

- **前端**：
  - Node.js 16+
  - Vue 3.0+
  - Element Plus
  - Axios

- **其他**：
  - Nginx (可选，用于生产环境部署)

## 快速开始

1. **克隆仓库**

    ```bash
    git clone https://github.com/your-username/forge.git
    cd forge
    ```

2. **后端设置**

    ```bash
    cd backend
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
