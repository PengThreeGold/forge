# Forge 软件发布管理平台 - 前端

这是 Forge 软件发布管理平台的前端项目，基于 Vue 3、Element Plus 和 Axios 构建。

## 功能特性

- 🚀 **基于 Vue 3.0+**：使用最新的 Vue 3 Composition API
- 🎨 **Element Plus UI**：美观现代的 UI 组件库
- 🔐 **安全认证**：基于 JWT 的认证系统，支持令牌自动刷新
- 📱 **响应式设计**：支持桌面、平板和手机端
- 📊 **数据可视化**：使用 ECharts 实现的统计图表
- 🌐 **国际化支持**：支持多语言切换
- 🗂️ **文件上传**：支持多种文件格式的上传
- 🔗 **Webhook 管理**：完整的事件通知系统

## 项目结构

```
frontend
├── public/                 # 静态资源
│   └── index.html        # HTML模板
├── src/                   # 源代码
│   ├── api/             # API请求
│   │   ├── auth.js      # 认证相关API
│   │   ├── space.js     # 软件空间API
│   │   ├── user.js      # 用户管理API
│   │   ├── version.js   # 版本管理API
│   │   ├── statistics.js # 统计API
│   │   └── webhook.js   # Webhook API
│   ├── assets/           # 资源文件
│   ├── components/       # 公共组件
│   ├── layout/          # 布局组件
│   │   ├── components/   # 布局子组件
│   │   │   ├── Navbar.vue
│   │   │   ├── Sidebar.vue
│   │   │   └── SidebarItem.vue
│   │   └── index.vue    # 主布局
│   ├── router/          # 路由配置
│   │   └── index.js
│   ├── store/           # Vuex状态管理
│   │   ├── modules/     # Vuex模块
│   │   │   ├── auth.js
│   │   │   ├── user.js
│   │   │   ├── space.js
│   │   │   ├── version.js
│   │   │   └── statistics.js
│   │   └── index.js
│   ├── styles/          # 样式文件
│   │   ├── index.scss    # 全局样式
│   │   ├── variables.scss # SCSS变量
│   │   └── responsive.scss # 响应式样式
│   ├── utils/           # 工具函数
│   │   └── validate.js  # 表单验证函数
│   ├── views/           # 页面组件
│   │   ├── Login.vue    # 登录页
│   │   ├── Dashboard.vue # 仪表板
│   │   ├── Profile.vue  # 个人资料
│   │   ├── PublicDownload.vue # 公共下载页
│   │   ├── space/      # 软件空间相关页面
│   │   ├── user/       # 用户管理页面
│   │   ├── version/    # 版本管理页面
│   │   ├── webhook/    # Webhook管理页面
│   │   └── statistics/ # 统计页面
│   ├── App.vue          # 根组件
│   └── main.js          # 入口文件
├── .env                 # 环境变量
├── .env.example          # 环境变量示例
├── package.json          # 项目依赖
└── vue.config.js         # Vue CLI配置
```

## 技术栈

- **Vue 3.0+**：前端框架
- **Vue Router 4**：路由管理
- **Vuex 4**：状态管理
- **Element Plus**：UI 组件库
- **Axios**：HTTP 客户端
- **ECharts**：图表库
- **Sass**：CSS 预处理器

## 安装和运行

### 环境要求

- Node.js 16+
- npm 7+

### 安装依赖

```bash
cd frontend
npm install
```

### 环境配置

复制环境变量配置文件：

```bash
cp .env.example .env
```

根据实际情况修改`.env`文件中的配置：

```env
# 端口配置
PORT=8080

# API基础URL
VUE_APP_API_BASE_URL=http://localhost:1110

# 应用标题
VUE_APP_TITLE=Forge 软件发布管理平台
```

### 开发运行

```bash
npm run serve
```

访问 [http://localhost:8080](http://localhost:8080)

### 生产构建

```bash
npm run build
```

构建后的文件将在`dist`目录中。

### 代码检查

```bash
npm run lint
```

## 主要功能

### 用户管理

- 用户列表展示
- 新增用户
- 编辑用户信息
- 删除用户
- 重置用户密码

### 软件空间管理

- 软件空间列表展示
- 创建新的软件空间
- 编辑软件空间信息
- 激活/停用软件空间
- 删除软件空间

### 软件版本管理

- 版本列表展示
- 创建新版本
- 编辑版本信息
- 发布/取消发布版本
- 上传版本文件
- 删除版本

### 统计分析

- 系统总体统计
- 下载趋势图
- 软件空间分布图
- 版本下载统计
- 软件空间排行榜

### Webhook 管理

- 配置 Webhook URL
- 设置 Webhook 密钥
- 选择事件类型
- 测试 Webhook

## 浏览器支持

- Chrome (推荐)
- Firefox
- Safari
- Edge

## 开发说明

### 代码规范

- 使用 ESLint 进行代码检查
- 遵循 Vue 3 Composition API 风格
- 使用 SCSS 编写样式
- 组件命名使用 PascalCase
- 文件命名使用 kebab-case

### 状态管理

使用 Vuex 进行状态管理，按功能模块划分：

- `auth`：用户认证信息
- `user`：用户管理
- `space`：软件空间管理
- `version`：版本管理
- `statistics`：统计数据

### API 请求

使用 Axios 进行 API 请求，统一处理：

- 请求/响应拦截
- 错误处理
- 令牌自动刷新
- 加载状态管理

### 路由守卫

实现路由守卫进行权限控制：

- 检查用户登录状态
- 验证用户角色权限
- 自动重定向到登录页

## 更新日志

### v1.0.0 (2023-12-06)

- 初始版本发布
- 完成所有核心功能
- 支持响应式设计

## 许可证

MIT License
