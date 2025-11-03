# Forge 后端开发文档

本文档提供了 Forge 软件发布管理平台后端的详细说明，包括开发环境搭建、部署指南等内容。

## 环境要求

- **Python**: 3.8+
- **pip**: 最新版本

## 开发环境搭建

### 1. 创建虚拟环境

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate  # Windows
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件，填入您的配置信息
```

`.env` 文件示例：

```text
FLASK_APP=app
FLASK_ENV=development
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret-key
JWT_ACCESS_TOKEN_EXPIRES=7200
JWT_REFRESH_TOKEN_EXPIRES=604800
DATABASE_URL=sqlite:///forge.db
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=1073741824
```

### 4. 初始化数据库

```bash
python run.py db-init
```

### 5. 创建管理员账户

```bash
python run.py create-admin
```

### 6. 启动开发服务器

```bash
python run.py run
```

访问 [http://localhost:5000/api](http://localhost:5000/api) 查看后端 API。

## 项目结构

```text
backend/
├── app/
│   ├── __init__.py       # 应用工厂
│   ├── config.py         # 配置文件
│   ├── models/           # 数据模型
│   │   ├── user.py       # 用户模型
│   │   ├── software.py   # 软件模型
│   │   └── statistics.py # 统计模型
│   ├── api/              # API 路由
│   │   ├── auth.py       # 认证 API
│   │   ├── software.py   # 软件 API
│   │   ├── statistics.py # 统计 API
│   │   └── webhook.py    # Webhook API
│   ├── services/         # 业务逻辑
│   │   ├── auth_service.py    # 认证服务
│   │   ├── software_service.py # 软件服务
│   │   └── statistics_service.py # 统计服务
│   └── utils/            # 工具函数
│       ├── response.py   # 响应工具
│       ├── file.py       # 文件工具
│       └── auth.py       # 认证工具
├── run.py                # 启动脚本
├── requirements.txt      # Python 依赖
```

## API 接口

### 认证接口

- `POST /api/auth/login` - 用户登录
- `POST /api/auth/refresh` - 刷新令牌
- `GET /api/auth/profile` - 获取用户信息
- `POST /api/auth/change-password` - 修改密码
- `POST /api/auth/init-admin` - 初始化管理员

### 软件管理接口

- `GET /api/software` - 获取软件列表
- `POST /api/software` - 创建软件
- `GET /api/software/{id}` - 获取软件详情
- `PUT /api/software/{id}` - 更新软件
- `DELETE /api/software/{id}` - 删除软件
- `PUT /api/software/{id}/toggle-status` - 切换软件状态

### 软件版本管理接口

- `GET /api/software/{id}/versions` - 获取软件版本列表
- `POST /api/software/{id}/versions` - 上传软件版本
- `GET /api/software/{id}/versions/{version_id}` - 获取软件版本详情
- `PUT /api/software/{id}/versions/{version_id}` - 更新软件版本
- `DELETE /api/software/{id}/versions/{version_id}` - 删除软件版本
- `GET /api/software/{id}/versions/{version_id}/download` - 下载软件

### 统计分析接口

- `GET /api/software/{id}/statistics` - 获取软件统计
- `GET /api/software/{id}/downloads` - 获取下载记录
- `GET /api/statistics/system` - 获取系统统计

### Webhook 接口

- `POST /api/software/{id}/webhook` - 配置 Webhook
- `GET /api/software/{id}/webhook` - 获取 Webhook 配置
- `PUT /api/software/{id}/webhook` - 更新 Webhook 配置
- `DELETE /api/software/{id}/webhook` - 删除 Webhook 配置

## 数据库模型

### User

用户表，存储系统用户信息。

| 字段名 | 类型 | 约束 | 描述 |
|--------|------|------|------|
| id | INTEGER | PRIMARY KEY | 用户ID |
| username | VARCHAR(80) | UNIQUE, NOT NULL | 用户名 |
| email | VARCHAR(120) | UNIQUE, NOT NULL | 邮箱 |
| password_hash | VARCHAR(128) | NOT NULL | 密码哈希 |
| role | VARCHAR(20) | NOT NULL | 角色 |
| created_at | DATETIME | NOT NULL | 创建时间 |
| updated_at | DATETIME | NOT NULL | 更新时间 |

### SoftwareSpace

软件空间表，存储软件项目信息。

| 字段名 | 类型 | 约束 | 描述 |
|--------|------|------|------|
| id | INTEGER | PRIMARY KEY | 软件空间ID |
| name | VARCHAR(100) | NOT NULL | 软件名称 |
| description | TEXT | | 软件描述 |
| status | VARCHAR(20) | NOT NULL | 状态 |
| owner_id | INTEGER | FOREIGN KEY | 所有者ID |
| created_at | DATETIME | NOT NULL | 创建时间 |
| updated_at | DATETIME | NOT NULL | 更新时间 |

### SoftwareVersion

软件版本表，存储软件版本信息。

| 字段名 | 类型 | 约束 | 描述 |
|--------|------|------|------|
| id | INTEGER | PRIMARY KEY | 版本ID |
| version_number | VARCHAR(50) | NOT NULL | 版本号 |
| release_notes | TEXT | | 发布说明 |
| file_size | BIGINT | NOT NULL | 文件大小 |
| file_hash | VARCHAR(64) | NOT NULL | 文件哈希 |
| software_id | INTEGER | FOREIGN KEY | 软件ID |
| uploader_id | INTEGER | FOREIGN KEY | 上传者ID |
| status | VARCHAR(20) | NOT NULL | 状态 |
| created_at | DATETIME | NOT NULL | 创建时间 |
| updated_at | DATETIME | NOT NULL | 更新时间 |
| download_count | INTEGER | NOT NULL | 下载次数 |

### DownloadRecord

下载记录表，存储软件下载记录。

| 字段名 | 类型 | 约束 | 描述 |
|--------|------|------|------|
| id | INTEGER | PRIMARY KEY | 记录ID |
| ip_address | VARCHAR(45) | NOT NULL | IP地址 |
| user_agent | TEXT | | 用户代理 |
| version_id | INTEGER | FOREIGN KEY | 版本ID |
| downloaded_at | DATETIME | NOT NULL | 下载时间 |

### WebhookLog

Webhook 日志表，存储 Webhook 调用记录。

| 字段名 | 类型 | 约束 | 描述 |
|--------|------|------|------|
| id | INTEGER | PRIMARY KEY | 日志ID |
| software_id | INTEGER | FOREIGN KEY | 软件ID |
| event_type | VARCHAR(50) | NOT NULL | 事件类型 |
| payload | TEXT | | 负载数据 |
| response_status | INTEGER | | 响应状态 |
| created_at | DATETIME | NOT NULL | 创建时间 |

## 部署指南

### 生产环境部署

1. **安装 Gunicorn**

    ```bash
    pip install gunicorn
    ```

2. **创建服务文件**

    创建 `/etc/systemd/system/forge.service` 文件：

    ```ini
    [Unit]
    Description=Forge API Server
    After=network.target

    [Service]
    User=www-data
    Group=www-data
    WorkingDirectory=/opt/forge/backend
    Environment=PATH=/opt/forge/backend/venv/bin
    ExecStart=/opt/forge/backend/venv/bin/gunicorn --workers 5 --bind unix:forge.sock -m 007 run:app

    [Install]
    WantedBy=multi-user.target
    ```

3. **启动服务**

    ```bash
    sudo systemctl start forge
    sudo systemctl enable forge
    ```


### 数据库配置

#### PostgreSQL

1. **安装 PostgreSQL**

    ```bash
    sudo apt update
    sudo apt install postgresql postgresql-contrib
    ```

2. **创建数据库和用户**

    ```bash
    sudo -u postgres createuser --interactive
    sudo -u postgres createdb forge_db
    ```

3. **配置连接字符串**

    在 `.env` 文件中设置：

    ```text
    DATABASE_URL=postgresql://user:password@localhost/forge_db
    ```

#### MySQL

1. **安装 MySQL**

    ```bash
    sudo apt update
    sudo apt install mysql-server
    ```

2. **创建数据库和用户**

    ```sql
    CREATE DATABASE forge_db;
    CREATE USER 'forge'@'localhost' IDENTIFIED BY 'forge_password';
    GRANT ALL PRIVILEGES ON forge_db.* TO 'forge'@'localhost';
    FLUSH PRIVILEGES;
    ```

3. **配置连接字符串**

    在 `.env` 文件中设置：

    ```text
    DATABASE_URL=mysql+pymysql://forge:forge_password@localhost:3306/forge_db
    ```

## 安全配置

### 1. 配置 HTTPS

在生产环境中，建议使用 HTTPS 保护数据传输安全。可以通过 Nginx 反向代理配置 SSL。

### 2. 配置密钥

确保在生产环境中使用强密钥：

```python
import secrets

# 生成 SECRET_KEY
print(secrets.token_hex(32))

# 生成 JWT_SECRET_KEY
print(secrets.token_hex(32))
```

### 3. 配置文件上传限制

在 `.env` 文件中设置合适的文件上传限制：

```text
MAX_CONTENT_LENGTH=1073741824  # 1GB
```

## 常见问题

### 1. 数据库连接失败

**解决方案**：

1. 检查数据库服务是否运行
2. 检查数据库连接字符串是否正确
3. 检查数据库用户权限

### 2. 文件上传失败

**解决方案**：

1. 检查上传目录权限
2. 检查文件大小限制
3. 检查磁盘空间

### 3. API 认证失败

**解决方案**：

1. 检查 JWT 密钥配置
2. 检查令牌是否过期
3. 检查请求头中的认证信息

## 更多资源

- [Flask 官方文档](https://flask.palletsprojects.com/)
- [Flask-SQLAlchemy 官方文档](https://flask-sqlalchemy.palletsprojects.com/)
- [Flask-JWT-Extended 官方文档](https://flask-jwt-extended.readthedocs.io/)
- [SQLAlchemy 官方文档](https://www.sqlalchemy.org/)
