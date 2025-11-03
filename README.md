# Forge 软件发布管理平台

Forge 是一个现代化的软件发布管理平台，旨在帮助开发团队更高效地管理和发布软件版本。

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
    python run.py init-db
    python run.py init-admin --username admin --password admin123 --email admin@example.com
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
    - 后端 API：<http://localhost:5000/api>

## 项目结构

```text
forge/
├── backend/                 # 后端 Flask 应用
├── frontend/                # 前端 Vue 应用
├── scripts/                 # 脚本文件
└── README.md               # 项目说明
```

## 更多文档

- [前端文档](frontend/README.md)
- [后端文档](backend/README.md)

## 许可证

本项目采用 MIT 许可证。详情请参阅 [LICENSE](LICENSE) 文件。
