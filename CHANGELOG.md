# Changelog

All notable changes to the Forge project will be documented in this file.

## [1.1.0] - 2025-11-17

### 🎉 重大更新

- **单进程架构**：后端现在可以直接服务前端静态文件，无需 Nginx 等反向代理
- **一键启动**：添加自动化启动脚本 (start.sh / start.bat)，自动完成环境配置和部署
- **完整前端**：使用 Vue 3 + Element Plus 构建现代化 Web 界面

### ✨ 新增功能

#### 前端
- 公共页面：软件浏览和下载
- 管理后台：用户认证、空间管理、版本管理
- 响应式设计：支持桌面和移动设备
- 状态管理：使用 Pinia 进行全局状态管理
- 路由守卫：基于角色的访问控制

#### 后端优化
- 静态文件服务：集成 FastAPI StaticFiles
- SPA 路由支持：正确处理前端路由刷新
- 配置改进：优化数据库路径处理
- 初始化命令：添加 `init` 命令一键初始化

### 🔧 修复

- **安全性**：补充 SECRET_KEY 配置示例和警告
- **环境变量**：完善 .env 和 .env.example 配置
- **数据库路径**：修复相对路径可能导致的问题
- **命令行参数**：改进 run.py 参数处理，支持默认命令

### 📝 文档

- 重写 README.md，添加详细的快速开始指南
- 添加架构说明和目录结构
- 添加故障排除部分
- 添加 API 使用示例

### 🛠️ 技术栈

#### 后端
- FastAPI 0.121+
- SQLAlchemy 2.0+
- Pydantic 2.0+
- Python-JOSE (JWT)
- Bcrypt (密码加密)

#### 前端
- Vue 3.4+
- Vite 5.0+
- Element Plus 2.5+
- Pinia 2.1+
- Axios 1.6+
- Vue Router 4.2+

### 📦 部署改进

- 前端构建产物自动部署到后端 static 目录
- 单个端口（1110）服务整个应用
- 无需复杂的 Nginx 配置
- 适合容器化部署

### 🔒 安全增强

- SECRET_KEY 使用随机生成的强密钥
- 完善的 CORS 配置
- JWT token 过期时间合理设置
- 密码使用 bcrypt 加密

### 🚀 性能优化

- 前端代码分割和懒加载
- 静态资源缓存优化
- API 响应拦截和错误处理

## [1.0.0] - 2025-11-01

### 初始版本

- 基础后端 API 实现
- SQLite 数据库支持
- JWT 认证系统
- 软件空间管理
- 版本管理
- 文件上传下载
- Webhook 集成
- 统计分析功能

---

**注意事项：**

1. 从 1.0.0 升级到 1.1.0：
   - 需要重新构建前端：`npm run build`
   - 更新 .env 文件，添加 SECRET_KEY
   - 建议备份数据库后重新初始化

2. 生产环境部署：
   - 务必修改 SECRET_KEY 为强随机密钥
   - 设置 DEBUG=False
   - 配置具体的 CORS_ORIGINS
   - 考虑使用 HTTPS

3. 数据迁移：
   - 本次更新不影响数据库结构
   - 可直接使用现有数据库文件

---

**维护者：** PengThreeGold  
**最后更新：** 2025-11-17
