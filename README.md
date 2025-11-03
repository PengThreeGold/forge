# Forge 软件发布管理平台

Forge 是一个现代化的软件发布管理平台，旨在帮助开发团队更高效地管理和发布软件版本。

## 快速开始

### 使用 Docker (推荐)

1. **克隆仓库**

```bash
git clone https://github.com/your-username/forge.git
cd forge
```

2. **配置环境变量**

```bash
cp .env.example .env
# 编辑 .env 文件，填入您的配置信息
```

3. **启动服务**

```bash
docker-compose up -d
```

4. **访问应用**

- 前端应用：https://localhost
- 后端 API：https://localhost/api

### 本地开发

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
python run.py db-init
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

- 前端应用：http://localhost:8080
- 后端 API：http://localhost:5000

## 项目结构

```
forge/
├── backend/                 # 后端 Flask 应用
├── frontend/                # 前端 Vue 应用
├── nginx/                   # Nginx 配置
├── scripts/                 # 脚本文件
├── docker-compose.yml       # Docker Compose 配置
└── README.md               # 项目说明
```

## 更多文档

- [前端文档](frontend/README.md)
- [后端文档](backend/README.md)

## 许可证

本项目采用 MIT 许可证。详情请参阅 [LICENSE](LICENSE) 文件。
