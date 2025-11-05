# Forge 后端程序开发说明

## 概述

Forge 是一个现代化的软件发布管理平台后端，基于 Flask 框架构建，提供软件版本管理、发布管理、下载管理、统计分析和 Webhook 集成等功能。

## 技术栈

- **框架**: Flask 2.0+
- **数据库**: SQLite (开发) / PostgreSQL (生产) / MySQL (可选)
- **ORM**: SQLAlchemy
- **认证**: Flask-JWT-Extended
- **API文档**: OpenAPI 3.0
- **限流**: Flask-Limiter
- **跨域**: Flask-CORS

## 核心模块说明

### 1. 应用初始化 (app/**init**.py)

应用使用工厂模式创建，支持不同环境配置：

- `DevelopmentConfig`: 开发环境配置
- `ProductionConfig`: 生产环境配置
- `TestingConfig`: 测试环境配置

主要扩展：

- SQLAlchemy: 数据库ORM
- Migrate: 数据库迁移
- JWT: JWT令牌管理
- CORS: 跨域资源共享
- Limiter: API请求限流

### 2. 数据模型

#### User (用户模型)

- 用户名、密码哈希、邮箱、角色
- 支持管理员和普通用户角色
- 密码使用 Werkzeug 的安全哈希

#### SoftwareSpace (软件空间模型)

- 软件基本信息：名称、描述、作者
- API密钥自动生成和更新
- Webhook配置：URL、密钥、事件订阅
- 状态管理：激活/停用

#### SoftwareVersion (软件版本模型)

- 版本信息：版本号、发布说明、文档链接
- 文件信息：路径、大小、哈希值
- 发布状态：已发布/未发布
- 发布时间管理

#### DownloadRecord (下载记录模型)

- 记录下载时间、IP地址、用户代理
- 关联软件空间和版本

#### WebhookLog (Webhook日志模型)

- 记录Webhook调用情况
- 保存请求载荷和响应状态
- 用于调试和重试机制

### 3. API接口设计

[接口文档](openapi.yaml)

### 4. 业务逻辑层

#### AuthService

处理用户认证相关业务逻辑：

- 用户登录验证
- 令牌生成和验证
- 用户创建和密码修改

#### SoftwareService

处理软件和版本管理业务逻辑：

- 软件空间CRUD操作
- 版本上传和管理
- API密钥生成和更新
- 文件存储和管理

#### StatisticsService

处理统计分析业务逻辑：

- 下载统计和趋势分析
- 软件空间和版本统计
- Webhook日志管理

### 5. 工具函数

#### auth.py

提供认证相关工具函数：

- 用户身份验证
- 密码哈希和验证
- 令牌生成和验证

#### file.py

提供文件处理工具函数：

- 文件上传和保存
- 文件哈希计算
- 文件大小转换
- 文件完整性验证

#### response.py

提供统一响应格式和错误处理：

- 成功响应格式化
- 错误响应格式化
- CORS头添加
- 管理员权限装饰器

## 数据库设计

### 表结构

1. **users** - 用户表
   - id: 主键
   - username: 用户名（唯一）
   - password_hash: 密码哈希
   - email: 邮箱
   - role: 角色
   - created_at: 创建时间
   - updated_at: 更新时间

2. **software_spaces** - 软件空间表
   - id: 主键
   - name: 软件名称
   - description: 描述
   - author: 作者
   - api_key: API密钥（唯一）
   - webhook_url: Webhook URL
   - webhook_secret: Webhook密钥
   - webhook_events: Webhook事件（JSON）
   - is_active: 是否激活
   - created_by: 创建者ID
   - created_at: 创建时间
   - updated_at: 更新时间

3. **software_versions** - 软件版本表
   - id: 主键
   - space_id: 软件空间ID（外键）
   - version: 版本号
   - file_path: 文件路径
   - file_size: 文件大小
   - file_hash: 文件哈希
   - release_note: 发布说明
   - documentation_url: 文档链接
   - is_published: 是否已发布
   - publish_date: 发布日期
   - created_by: 上传者ID（外键）
   - created_at: 创建时间
   - updated_at: 更新时间

4. **download_records** - 下载记录表
   - id: 主键
   - version_id: 版本ID（外键）
   - space_id: 软件空间ID（外键）
   - ip_address: IP地址
   - user_agent: 用户代理
   - download_time: 下载时间

5. **webhook_logs** - Webhook日志表
   - id: 主键
   - space_id: 软件空间ID（外键）
   - event_type: 事件类型
   - payload: 请求载荷
   - response_status: 响应状态码
   - response_body: 响应内容
   - attempt_time: 尝试时间

### 关系设计

- 一个用户可以创建多个软件空间（一对多）
- 一个软件空间可以有多个版本（一对多）
- 一个版本可以有多条下载记录（一对多）
- 一个软件空间可以有多条Webhook日志（一对多）

## 安全考虑

### 1. 认证与授权

- 使用JWT令牌进行API认证
- 支持访问令牌和刷新令牌
- 管理员权限装饰器保护敏感API

### 2. 密码安全

- 使用Werkzeug的安全哈希算法
- 密码强度验证
- 密码修改验证旧密码

### 3. 文件安全

- 文件类型白名单验证
- 安全文件名处理
- 文件哈希验证完整性
- 文件大小限制

### 4. API安全

- 请求限流防止滥用
- CORS配置控制跨域访问
- 输入验证防止注入攻击
- SQL注入防护（ORM自动处理）

## 性能优化

### 1. 数据库优化

- 使用数据库索引提高查询速度
- 分页查询减少数据传输
- 按需加载关联数据

### 2. 文件处理优化

- 文件哈希计算优化
- 文件存储路径合理组织
- 大文件上传处理

### 3. 缓存策略

- 静态资源缓存
- API响应缓存（可选）
- 数据库查询缓存

## 部署配置

### 1. 环境变量配置

```bash
# 基本配置
FLASK_APP=app
FLASK_ENV=production
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret-key

# 数据库配置
USE_POSTGRES=true
POSTGRES_USER=forge
POSTGRES_PASSWORD=forge_password
POSTGRES_DB=forge_db
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# 文件配置
UPLOAD_FOLDER=/app/storage/uploads
SOFTWARE_STORAGE=/app/storage/software
MAX_CONTENT_LENGTH=1073741824

# HTTPS配置
HTTPS_ENABLED=true
SSL_CERT_PATH=/app/certs/forge.crt
SSL_KEY_PATH=/app/certs/forge.key

# CORS配置
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

### 2. 生产环境部署

1. 使用Gunicorn作为WSGI服务器
2. 配置Nginx作为反向代理
3. 设置SSL证书启用HTTPS
4. 配置日志记录
5. 设置系统服务自启动

## 开发指南

### 1. 本地开发环境设置

```bash
# 克隆项目
git clone <repository-url>
cd Forge/backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件

# 初始化数据库
python run.py init-db

# 创建管理员账户
python run.py init-admin

# 启动开发服务器
python run.py
```

### 2. 代码规范

- 遵循PEP 8代码风格
- 使用类型提示提高代码可读性
- 编写文档字符串和注释
- 单元测试覆盖核心功能

### 3. API开发规范

- 使用RESTful API设计原则
- 统一的响应格式
- 适当的HTTP状态码
- 错误信息清晰明确

### 4. 数据库操作规范

- 使用SQLAlchemy ORM进行数据库操作
- 事务处理保证数据一致性
- 避免N+1查询问题
- 使用数据库连接池

## 测试

### 1. 单元测试

```bash
# 运行所有测试
python -m pytest tests/

# 运行特定测试
python -m pytest tests/test_auth.py

# 生成覆盖率报告
python -m pytest --cov=app tests/
```

### 2. API测试

使用提供的测试脚本：

```bash
# 设置环境变量
export API_BASE_URL=http://localhost:5000/api
export API_USERNAME=admin
export API_PASSWORD=admin123

# 运行测试
python tests/test_api.py
```

## 常见问题

### 1. 数据库连接问题

- 检查数据库服务是否运行
- 验证连接字符串是否正确
- 确认数据库用户权限

### 2. 文件上传问题

- 检查上传目录权限
- 验证文件大小限制
- 确认磁盘空间充足

### 3. 令牌过期问题

- 检查JWT配置
- 使用刷新令牌获取新令牌
- 确认系统时间同步

## 版本历史

- v1.0.0: 初始版本，基本功能实现
- v1.1.0: 添加Webhook支持和统计分析
- v1.2.0: 优化公开API和性能改进

## 贡献指南

1. Fork项目仓库
2. 创建功能分支
3. 提交代码更改
4. 编写测试用例
5. 提交Pull Request

## 许可证

本项目采用MIT许可证，详情请参阅LICENSE文件。
