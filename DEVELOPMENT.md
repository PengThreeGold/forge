# Forge 开发指南

## 开发环境设置

### 后端开发

1. **安装依赖**
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# 或
.venv\Scripts\activate     # Windows

pip install -r requirements.txt
```

2. **初始化数据库**
```bash
python run.py init
python run.py init-admin
```

3. **启动开发服务器**
```bash
python run.py run
```

后端将在 http://localhost:1110 启动，支持热重载。

### 前端开发

1. **安装依赖**
```bash
cd frontend
npm install
```

2. **启动开发服务器**
```bash
npm run dev
```

前端将在 http://localhost:3000 启动，API 请求会自动代理到后端。

## 项目架构

### 后端架构

```
backend/
├── app/
│   ├── api/              # API 路由
│   │   ├── auth.py      # 认证相关
│   │   ├── spaces.py    # 空间管理
│   │   ├── versions.py  # 版本管理
│   │   ├── users.py     # 用户管理
│   │   ├── public.py    # 公共 API
│   │   └── stats.py     # 统计
│   ├── core/            # 核心模块
│   │   ├── config.py    # 配置
│   │   ├── security.py  # 安全工具
│   │   └── deps.py      # 依赖注入
│   ├── crud/            # 数据库操作
│   ├── db/              # 数据库配置
│   ├── models/          # ORM 模型
│   ├── schemas/         # Pydantic 模式
│   └── utils/           # 工具函数
├── storage/             # 文件存储
├── static/              # 前端静态文件
└── run.py              # 启动脚本
```

### 前端架构

```
frontend/
├── src/
│   ├── api/            # API 接口封装
│   ├── layouts/        # 布局组件
│   │   ├── PublicLayout.vue   # 公共页面布局
│   │   └── AdminLayout.vue    # 管理后台布局
│   ├── views/          # 页面组件
│   │   ├── auth/       # 认证页面
│   │   ├── public/     # 公共页面
│   │   └── admin/      # 管理页面
│   ├── stores/         # Pinia 状态管理
│   ├── router/         # Vue Router 配置
│   ├── utils/          # 工具函数
│   ├── App.vue         # 根组件
│   └── main.js         # 入口文件
├── index.html
├── package.json
└── vite.config.js
```

## API 设计

### 认证 API

- `POST /api/auth/login` - 用户登录
- `POST /api/auth/refresh` - 刷新令牌
- `GET /api/auth/profile` - 获取当前用户信息

### 空间管理 API

- `GET /api/spaces` - 获取空间列表
- `POST /api/spaces` - 创建空间
- `GET /api/spaces/{id}` - 获取空间详情
- `PUT /api/spaces/{id}` - 更新空间
- `DELETE /api/spaces/{id}` - 删除空间

### 公共 API

- `GET /api/public/spaces` - 获取公共空间列表
- `GET /api/public/spaces/{id}` - 获取空间详情
- `GET /api/public/spaces/{id}/versions` - 获取版本列表
- `GET /api/public/spaces/{id}/download` - 下载文件

## 数据库模型

### User（用户）

```python
- id: int
- username: str
- email: str (可选)
- hashed_password: str
- role: str (admin/user)
- is_active: bool
- created_at: datetime
- updated_at: datetime
```

### SoftwareSpace（软件空间）

```python
- id: str (8位随机字符)
- name: str
- description: str (可选)
- author: str (可选)
- api_key: str (唯一)
- webhook_url: str (可选)
- webhook_secret: str (可选)
- status: str (active/inactive)
- created_by: int (外键)
- created_at: datetime
- updated_at: datetime
```

### SoftwareVersion（软件版本）

```python
- id: int
- space_id: str (外键)
- version: str
- release_notes: str (可选)
- is_published: bool
- published_at: datetime (可选)
- created_by: int (外键)
- created_at: datetime
- updated_at: datetime
```

### SoftwareArchitectureFile（架构文件）

```python
- id: int
- version_id: int (外键)
- architecture: str
- filename: str
- file_path: str
- file_size: int
- md5: str
- created_at: datetime
```

## 开发规范

### 后端

1. **代码风格**：遵循 PEP 8
2. **类型注解**：使用 Python 类型提示
3. **错误处理**：使用 HTTPException
4. **API 响应**：使用统一的 ResponseModel

### 前端

1. **代码风格**：使用 ESLint
2. **组件命名**：PascalCase
3. **文件命名**：PascalCase（组件）、kebab-case（其他）
4. **API 调用**：集中在 api/ 目录

## 测试

### 后端测试

```bash
cd backend
pytest
```

### 前端测试

```bash
cd frontend
npm run test
```

## 部署

### 开发环境

使用 `start.sh` 或 `start.bat` 一键启动。

### 生产环境

1. **构建前端**
```bash
cd frontend
npm run build
```

2. **部署到后端**
```bash
cp -r dist ../backend/static
```

3. **配置生产环境变量**
```bash
# backend/.env
DEBUG=False
SECRET_KEY=<strong-random-key>
CORS_ORIGINS=https://yourdomain.com
```

4. **启动服务**
```bash
cd backend
python run.py run
```

或使用 systemd/supervisor 等进程管理工具。

## 常见问题

### 端口冲突

修改 `backend/.env` 中的 `PORT` 配置。

### 数据库锁定

SQLite 不支持高并发写入，生产环境建议使用 PostgreSQL/MySQL。

### CORS 错误

检查 `backend/.env` 中的 `CORS_ORIGINS` 配置。

## 贡献指南

1. Fork 项目
2. 创建特性分支
3. 提交代码
4. 创建 Pull Request

## 许可证

MIT License
