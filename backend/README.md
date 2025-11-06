# Forge 软件发布管理平台 - 后端

这是 Forge 软件发布管理平台的后端服务，基于 FastAPI 框架开发。

## 功能特性

- 🔐 **JWT 认证系统**：基于 JWT 的安全认证机制，支持访问令牌和刷新令牌
- 👥 **用户管理**：完整的用户管理功能，包括创建、编辑、删除用户
- 📦 **软件空间管理**：支持创建、编辑、删除软件空间，每个空间有独立的 API 密钥
- 🏷️ **版本管理**：支持多版本软件管理，包括版本发布、文件上传、版本信息管理
- 📊 **统计分析**：提供详细的下载统计、版本统计和系统整体统计
- 🔗 **Webhook 集成**：支持 Webhook 配置，实现事件通知和自动化集成
- 🌐 **公共 API**：提供无需认证的公共下载接口，支持 API 密钥验证
- 🛡️ **安全可靠**：文件完整性校验、密码加密存储、输入验证等多重安全保障

## 技术栈

- **框架**：FastAPI
- **数据库**：SQLite (通过 SQLAlchemy ORM)
- **认证**：JWT (JSON Web Tokens)
- **文件处理**：Python 标准库 + 自定义工具
- **Webhook**：httpx (异步 HTTP 客户端)

## 快速开始

### 1. 环境准备

确保已安装 Python 3.8+：

```bash
python --version
```

### 2. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

### 3. 配置环境变量

复制并编辑环境配置文件：

```bash
cp .env.example .env
```

编辑 `.env` 文件，设置必要的配置：

```env
# FastAPI 配置
PORT=1110
HOST=0.0.0.0
DEBUG=True

# 数据库配置
SQLITE_DB_PATH=forge.db

# CORS配置
CORS_ORIGINS=*

# JWT配置
SECRET_KEY=your-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_MINUTES=10080

# HTTPS配置
HTTPS_ENABLED=False
SSL_CERT_PATH=certs/localhost.crt
SSL_KEY_PATH=certs/localhost.key

# 文件存储配置
UPLOAD_DIR=storage/uploads
MAX_FILE_SIZE=1073741824  # 1GB
```

### 4. 初始化数据库

```bash
python run.py create-tables
python run.py init-data
```

### 5. 初始化管理员账户

```bash
python run.py init-admin
```

按照提示输入管理员账户信息：

- 用户名
- 邮箱（可选）
- 密码
- 确认密码

### 6. 启动服务器

```bash
python run.py run
```

服务器启动后，可以通过以下地址访问：

- API 服务：`http://localhost:1110`
- API 文档：`http://localhost:1110/api/docs`
- 健康检查：`http://localhost:1110/health`

## 基本测试

运行基本功能测试：

```bash
python test_basic.py
```

## API 文档

启动服务器后，可以通过 `http://localhost:1110/api/docs` 访问交互式 API 文档。

## 开发说明

### 数据库迁移

项目使用 SQLAlchemy 进行数据库操作。如需修改数据库结构，请：

1. 更新 `app/models/` 中的模型定义
2. 删除现有数据库文件（开发环境）
3. 运行 `python run.py create-tables` 重新创建表结构

生产环境建议使用 Alembic 进行数据库迁移。

### 添加新的 API 端点

1. 在 `app/schemas/` 中定义请求和响应模式
2. 在 `app/crud/` 中实现数据库操作
3. 在 `app/api/` 中创建路由处理函数
4. 在 `app/main.py` 中注册新路由

## 部署建议

### 生产环境配置

1. 设置强密码的 `SECRET_KEY`
2. 配置 HTTPS 证书
3. 设置适当的 `CORS_ORIGINS`
4. 使用生产级数据库（如 PostgreSQL）
5. 配置反向代理（如 Nginx）

### 性能优化

1. 使用连接池
2. 启用响应压缩
3. 配置缓存
4. 使用 CDN 分发文件

## 许可证

本项目采用 MIT 许可证。详情请参阅 [LICENSE](../LICENSE) 文件。
