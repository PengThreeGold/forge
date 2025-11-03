# Forge 软件发布管理平台 - 修复和改进文档

本文档记录了对Forge软件发布管理平台进行的主要修复和改进。

## 后端修复

### 1. 数据库配置优化
- 文件：`backend/app/config.py`
- 修复：添加了PostgreSQL配置支持，允许在开发或生产环境中选择使用SQLite或PostgreSQL
- 改进：根据环境变量自动选择数据库类型和连接参数

### 2. 文件处理优化
- 文件：`backend/app/models/software.py`
- 修复：修复了文件哈希计算中的迭代器问题
- 改进：使用更安全的文件读取方式，避免使用可能出错的iter(lambda:)模式

### 3. 文件存储路径处理
- 文件：`backend/app/utils/file.py`
- 修复：添加了应用上下文检查，防止在非应用上下文中使用current_app
- 改进：增加了文件名安全处理，防止路径注入攻击
- 改进：增强了版本号处理，确保文件名安全

### 4. Webhook签名验证
- 文件：`backend/app/api/webhook.py`
- 修复：修复了签名验证逻辑，正确处理签名前缀
- 改进：增加了payload类型检查，确保签名计算正确

### 5. 数据库初始化简化
- 文件：`backend/app/database.py`
- 修复：移除了重复的数据库初始化逻辑和不必要的SQLAlchemy相关代码
- 改进：简化了代码结构，提高可维护性

### 6. 初始化脚本
- 新增：`scripts/init-db.py`
- 功能：提供独立的数据库初始化脚本，可用于命令行初始化
- 改进：支持环境变量配置，减少手动配置

## 前端修复

### 1. API路径修正
- 文件：`frontend/src/api/software.js`
- 修复：修正了API路径，与后端路由保持一致
- 改进：确保所有API调用都能正确路由到后端

### 2. 开发配置优化
- 文件：`frontend/vue.config.js`
- 修复：移除了无效的开发环境HTTPS配置
- 改进：简化了配置，提高开发环境的稳定性

## 使用说明

### 开发环境设置
1. 后端设置：
   ```bash
   cd backend
   pip install -r requirements.txt
   cp .env.example .env
   # 编辑 .env 文件，设置必要的环境变量
   python run.py init-db
   python run.py init-admin --username admin --password admin123 --email admin@example.com
   python run.py run
   ```

2. 前端设置：
   ```bash
   cd frontend
   npm install
   cp .env.example .env
   # 编辑 .env 文件，设置API URL
   npm run serve
   ```

3. 访问应用：
   - 前端应用：http://localhost:8080
   - 后端API：http://localhost:5000/api

### 环境变量配置

#### 后端环境变量 (.env)
```
# Flask配置
FLASK_CONFIG=development  # 或 production
FLASK_DEBUG=true
SECRET_KEY=your-secret-key-change-in-production
JWT_SECRET_KEY=your-jwt-secret-key-change-in-production

# 数据库配置
USE_POSTGRES=false  # 设置为true使用PostgreSQL
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=forge
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# 文件上传配置
UPLOAD_FOLDER=./storage/uploads
SOFTWARE_STORAGE=./storage/software
MAX_CONTENT_LENGTH=524288000  # 500MB

# 管理员账户
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123
ADMIN_EMAIL=admin@example.com
```

#### 前端环境变量 (.env)
```
# API配置
VUE_APP_API_URL=http://localhost:5000

# 应用配置
VUE_APP_TITLE=Forge 软件发布管理平台
VUE_APP_DEBUG=true
```

## 注意事项

1. 首次运行时，需要初始化数据库并创建管理员账户
2. 如需使用PostgreSQL，请确保数据库服务已启动并设置正确的连接参数
3. 上传文件默认存储在`./storage/software`目录中，请确保有足够的空间
4. 开发环境默认使用SQLite，生产环境建议使用PostgreSQL
5. 前端开发服务器默认运行在8080端口，后端API服务器运行在5000端口

## 后续改进建议

1. 添加更多的单元测试和集成测试
2. 实现日志轮转和监控
3. 添加备份和恢复功能
4. 优化大文件上传处理
5. 实现更细粒度的权限控制
6. 添加前端国际化支持
7. 实现实时通知功能