# Forge 前端开发文档

本文档提供了 Forge 软件发布管理平台前端的详细说明，包括开发环境搭建、部署指南等内容。

## 环境要求

- **Node.js**: 16+
- **npm**: 8+

## 开发环境搭建

### 1. 安装依赖

```bash
cd frontend
npm install
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件，填入您的配置信息
```

`.env` 文件示例：

```
VUE_APP_API_BASE_URL=http://localhost:5000/api
VUE_APP_TITLE=Forge 软件发布管理平台
VUE_APP_VERSION=1.0.0
```

### 3. 启动开发服务器

```bash
npm run serve
```

访问 http://localhost:8080 查看前端应用。

## 项目结构

```
frontend/
├── public/                 # 静态资源
├── src/
│   ├── main.js            # 应用入口
│   ├── App.vue            # 根组件
│   ├── router/            # 路由配置
│   ├── store/             # 状态管理
│   ├── api/               # API 封装
│   ├── utils/             # 工具函数
│   ├── components/        # 公共组件
│   └── views/             # 页面组件
├── package.json           # Node.js 依赖
├── vue.config.js          # Vue 配置
└── Dockerfile             # Docker 配置
```

## 构建与部署

### 生产环境构建

```bash
npm run build
```

构建后的文件将位于 `dist` 目录。

### Docker 部署

```bash
# 构建镜像
docker build -t forge-frontend .

# 运行容器
docker run -d -p 8080:80 forge-frontend
```

### Nginx 部署

将 `dist` 目录下的文件复制到 Nginx 的网站根目录，并配置 Nginx：

```nginx
server {
    listen 80;
    server_name your-domain.com;
    root /var/www/forge;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://backend:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 组件开发

### 创建新组件

1. 在 `src/components` 目录下创建组件文件
2. 在组件中实现所需功能
3. 在需要使用组件的页面中导入并注册

### 页面开发

1. 在 `src/views` 目录下创建页面文件
2. 在 `src/router/index.js` 中添加路由配置
3. 在菜单中添加导航链接

## API 调用

### 使用封装的 API 方法

```javascript
import { getSoftwareList, createSoftware } from '@/api/software'

// 获取软件列表
async function fetchSoftware() {
  try {
    const response = await getSoftwareList()
    console.log(response.data)
  } catch (error) {
    console.error('获取软件列表失败:', error)
  }
}

// 创建软件
async function addSoftware(data) {
  try {
    const response = await createSoftware(data)
    console.log('软件创建成功:', response.data)
  } catch (error) {
    console.error('软件创建失败:', error)
  }
}
```

### 直接使用 Axios

```javascript
import axios from '@/utils/request'

// 发起 GET 请求
axios.get('/api/software')
  .then(response => {
    console.log(response.data)
  })
  .catch(error => {
    console.error('请求失败:', error)
  })

// 发起 POST 请求
axios.post('/api/software', {
    name: 'Test Software',
    description: 'Test Description'
  })
  .then(response => {
    console.log(response.data)
  })
  .catch(error => {
    console.error('请求失败:', error)
  })
```

## 状态管理

### 使用 Vuex 状态

```javascript
import { useStore } from 'vuex'

export default {
  setup() {
    const store = useStore()
    
    // 获取状态
    const user = computed(() => store.state.auth.user)
    
    // 提交 mutation
    const login = (userData) => {
      store.commit('auth/SET_USER', userData)
    }
    
    // 分发 action
    const fetchUser = () => {
      store.dispatch('auth/fetchUser')
    }
    
    return {
      user,
      login,
      fetchUser
    }
  }
}
```

## 样式开发

### 使用全局样式

在 `src/assets/css/global.css` 中定义全局样式，这些样式将在整个应用中生效。

### 使用变量

在 `src/assets/css/variables.scss` 中定义 CSS 变量，如颜色、字体大小等。

## 常见问题

### 1. 前端无法访问后端 API

**解决方案**：

1. 检查 `.env` 文件中的 `VUE_APP_API_BASE_URL` 配置是否正确
2. 确保后端服务正在运行
3. 检查浏览器控制台是否有 CORS 错误

### 2. 构建失败

**解决方案**：

1. 检查 Node.js 和 npm 版本是否符合要求
2. 删除 `node_modules` 目录并重新运行 `npm install`
3. 检查代码语法错误

### 3. 样式不生效

**解决方案**：

1. 检查样式文件是否正确导入
2. 确保选择器优先级足够高
3. 检查是否有其他样式覆盖

## 更多资源

- [Vue.js 官方文档](https://vuejs.org/)
- [Element Plus 官方文档](https://element-plus.org/)
- [Vue Router 官方文档](https://router.vuejs.org/)
- [Vuex 官方文档](https://vuex.vuejs.org/)