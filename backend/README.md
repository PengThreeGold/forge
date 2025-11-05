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

## 项目结构

```text
backend/
├── app/
│   ├── api/              # API 路由
│   │   ├── auth.py       # 认证相关API
│   │   ├── users.py      # 用户管理API
│   │   ├── spaces.py     # 软件空间管理API
│   │   ├── versions.py   # 版本管理API
│   │   ├── public.py     # 公共API
│   │   ├── stats.py      # 统计API
│   │   ├── webhooks.py   # Webhook管理API
│   │   └── deps.py       # API依赖项
│   ├── core/              # 核心功能
│   │   ├── config.py     # 配置管理
│   │   ├── security.py   # 安全相关功能
│   │   └── deps.py       # 依赖项
│   ├── crud/              # CRUD 操作
│   │   ├── base.py       # 基础CRUD类
│   │   ├── user.py       # 用户CRUD
│   │   ├── software_space.py  # 软件空间CRUD
│   │   ├── software_version.py # 版本CRUD
│   │   ├── download_record.py # 下载记录CRUD
│   │   └── webhook_log.py   # Webhook日志CRUD
│   ├── db/                # 数据库相关
│   │   ├── database.py   # 数据库连接和会话
│   │   └── init_db.py    # 数据库初始化
│   ├── models/             # 数据模型
│   │   ├── user.py       # 用户模型
│   │   ├── software_space.py  # 软件空间模型
│   │   ├── software_version.py # 版本模型
│   │   ├── download_record.py # 下载记录模型
│   │   ├── webhook_log.py   # Webhook日志模型
│   │   ├── role.py       # 角色模型
│   │   └── permission.py # 权限模型
│   ├── schemas/            # Pydantic模式
│   │   ├── user.py       # 用户模式
│   │   ├── software_space.py  # 软件空间模式
│   │   ├── software_version.py # 版本模式
│   │   ├── download_record.py # 下载记录模式
│   │   ├── webhook_log.py   # Webhook日志模式
│   │   ├── webhook.py     # Webhook模式
│   │   ├── stats.py      # 统计模式
│   │   └── common.py     # 通用模式
│   ├── utils/              # 工具函数
│   │   ├── file.py       # 文件处理工具
│   │   ├── webhook.py    # Webhook工具
│   │   └── validation.py # 验证工具
│   ├── storage/            # 文件存储目录
│   ├── main.py             # 主应用入口
│   └── __init__.py
├── storage/                # 文件存储目录
├── run.py                 # 运行脚本
├── test_basic.py           # 基本测试脚本
├── requirements.txt         # Python依赖
├── .env.example          # 环境变量示例
└── README.md             # 项目说明
```

## API 文档

启动服务器后，可以通过 `http://localhost:1110/api/docs` 访问交互式 API 文档。

主要 API 端点：

### 认证

- `POST /api/auth/login` - 用户登录
- `POST /api/auth/refresh` - 刷新令牌
- `GET /api/auth/profile` - 获取用户信息
- `PUT /api/auth/admin/password` - 修改密码
- `POST /api/auth/admin/init` - 初始化管理员

### 用户管理

- `GET /api/users/` - 获取用户列表
- `POST /api/users/` - 创建用户
- `GET /api/users/{user_id}` - 获取用户详情
- `PUT /api/users/{user_id}` - 更新用户信息
- `DELETE /api/users/{user_id}` - 删除用户

### 软件管理

- `GET /api/spaces/` - 获取软件空间列表
- `POST /api/spaces/` - 创建软件空间
- `GET /api/spaces/{space_id}` - 获取软件空间详情
- `PUT /api/spaces/{space_id}` - 更新软件空间
- `DELETE /api/spaces/{space_id}` - 删除软件空间

### 版本管理

- `GET /api/spaces/{space_id}/` - 获取版本列表
- `POST /api/spaces/{space_id}/upload` - 上传版本
- `PUT /api/spaces/{space_id}/{version_id}` - 更新版本
- `DELETE /api/spaces/{space_id}/{version_id}` - 删除版本
- `POST /api/spaces/{space_id}/{version_id}/publish` - 发布版本
- `POST /api/spaces/{space_id}/{version_id}/unpublish` - 取消发布版本

### 公共 API

- `GET /api/public/spaces` - 获取公共软件空间列表
- `GET /api/public/spaces/{space_id}` - 获取公共软件空间详情
- `GET /api/public/spaces/{space_id}/versions` - 获取已发布版本列表
- `GET /api/public/download/{space_id}/{version_id}` - 下载版本

### 统计分析

- `GET /api/stats/system` - 获取系统统计
- `GET /api/stats/spaces/{space_id}` - 获取软件空间统计
- `GET /api/stats/spaces/{space_id}/downloads/daily` - 获取每日下载统计
- `GET /api/stats/spaces/{space_id}/downloads/versions` - 获取版本下载统计

### Webhook 管理

- `GET /api/spaces/{space_id}/webhook/config` - 获取 Webhook 配置
- `PUT /api/spaces/{space_id}/webhook/config` - 更新 Webhook 配置
- `POST /api/spaces/{space_id}/webhook/regenerate-secret` - 重新生成 Webhook 密钥
- `GET /api/spaces/{space_id}/webhook/logs` - 获取 Webhook 日志

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

### 测试

运行基本功能测试：

```bash
python test_basic.py
```

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
