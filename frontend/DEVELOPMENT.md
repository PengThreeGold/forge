# Forge 软件发布管理平台 - 开发指南

本文档提供了 Forge 软件发布管理平台的详细开发指南，包括开发环境搭建、代码规范、测试指南等内容。

## 目录

- [开发环境搭建](#开发环境搭建)
- [代码结构说明](#代码结构说明)
- [开发流程](#开发流程)
- [代码规范](#代码规范)
- [API 设计规范](#api-设计规范)
- [前端开发指南](#前端开发指南)
- [后端开发指南)
- [数据库开发指南](#数据库开发指南)
- [测试指南](#测试指南)
- [调试指南](#调试指南)
- [贡献指南](#贡献指南)

## 开发环境搭建

### 系统要求

- **操作系统**: Windows 10, macOS 10.15+, Linux (Ubuntu 20.04+)
- **Python**: 3.8+
- **Node.js**: 16+
- **Git**: 最新版本
- **IDE**: VS Code (推荐) 或其他支持 Python 和 JavaScript 的编辑器

### 安装开发工具

1. **安装 VS Code**

   从 [VS Code 官网](https://code.visualstudio.com/) 下载并安装 VS Code。

2. **安装 VS Code 插件**

   - Python
   - Pylance
   - ESLint
   - Vetur
   - Docker
   - GitLens
   - Auto Rename Tag
   - Path Intellisense

3. **安装 Python**

   从 [Python 官网](https://www.python.org/downloads/) 下载并安装 Python 3.8+。

4. **安装 Node.js**

   从 [Node.js 官网](https://nodejs.org/en/download/) 下载并安装 Node.js 16+。

### 项目初始化

1. **克隆项目**

```bash
git clone https://github.com/your-username/forge.git
cd forge
```

2. **安装后端依赖**

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate  # Windows

pip install -r requirements.txt
```

3. **安装前端依赖**

```bash
cd ../frontend
npm install
```

4. **配置环境变量**

```bash
# 后端环境变量
cd ../backend
cp .env.example .env
# 编辑 .env 文件，填入您的配置信息

# 前端环境变量
cd ../frontend
cp .env.example .env
# 编辑 .env 文件，填入您的配置信息
```

5. **初始化数据库**

```bash
cd ../backend
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate  # Windows

python run.py db-init
```

6. **创建管理员账户**

```bash
python run.py create-admin
```

### 启动开发服务器

1. **启动后端服务器**

```bash
cd backend
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate  # Windows

python run.py run
```

2. **启动前端服务器**

```bash
cd frontend
npm run serve
```

3. **访问应用**

   - 前端应用: http://localhost:8080
   - 后端 API: http://localhost:5000

## 代码结构说明

### 后端代码结构

```
backend/
├── app/
│   ├── __init__.py       # 应用工厂
│   ├── config.py         # 配置文件
│   ├── models/           # 数据模型
│   │   ├── __init__.py
│   │   ├── user.py       # 用户模型
│   │   ├── software.py   # 软件模型
│   │   └── statistics.py # 统计模型
│   ├── api/              # API 路由
│   │   ├── __init__.py
│   │   ├── auth.py       # 认证 API
│   │   ├── software.py   # 软件 API
│   │   ├── statistics.py # 统计 API
│   │   └── webhook.py    # Webhook API
│   ├── services/         # 业务逻辑
│   │   ├── __init__.py
│   │   ├── auth_service.py    # 认证服务
│   │   ├── software_service.py # 软件服务
│   │   └── statistics_service.py # 统计服务
│   └── utils/            # 工具函数
│       ├── __init__.py
│       ├── response.py   # 响应工具
│       ├── file.py       # 文件工具
│       └── auth.py       # 认证工具
├── run.py                # 启动脚本
├── requirements.txt      # Python 依赖
└── Dockerfile            # Docker 配置
```

### 前端代码结构

```
frontend/
├── public/               # 静态资源
├── src/
│   ├── main.js           # 应用入口
│   ├── App.vue           # 根组件
│   ├── router/           # 路由配置
│   │   └── index.js
│   ├── store/            # 状态管理
│   │   ├── index.js
│   │   ├── modules/
│   │   │   ├── auth.js   # 认证状态
│   │   │   ├── software.js # 软件状态
│   │   │   └── statistics.js # 统计状态
│   ├── api/              # API 封装
│   │   ├── index.js
│   │   ├── auth.js       # 认证 API
│   │   ├── software.js   # 软件 API
│   │   ├── statistics.js # 统计 API
│   │   └── webhook.js    # Webhook API
│   ├── utils/            # 工具函数
│   │   ├── index.js
│   │   ├── auth.js       # 认证工具
│   │   ├── request.js    # 请求工具
│   │   └── common.js     # 通用工具
│   ├── components/       # 公共组件
│   │   ├── Header.vue    # 页头组件
│   │   ├── Sidebar.vue   # 侧边栏组件
│   │   ├── DataTable.vue # 数据表格组件
│   │   ├── FileUpload.vue # 文件上传组件
│   │   └── Pagination.vue # 分页组件
│   └── views/            # 页面组件
│       ├── Login.vue     # 登录页面
│       ├── Dashboard.vue # 仪表板
│       ├── SoftwareList.vue # 软件列表
│       ├── SoftwareDetail.vue # 软件详情
│       ├── SoftwareEdit.vue # 软件编辑
│       ├── Statistics.vue # 统计页面
│       ├── Settings.vue  # 设置页面
│       └── NotFound.vue  # 404 页面
├── package.json          # Node.js 依赖
├── vite.config.js        # Vite 配置
└── .env                  # 环境变量
```

## 开发流程

### Git 工作流

1. **分支策略**

   - `main`: 主分支，用于生产环境
   - `develop`: 开发分支，用于集成功能
   - `feature/*`: 功能分支，用于开发新功能
   - `hotfix/*`: 修复分支，用于紧急修复生产环境的问题

2. **开发步骤**

   ```bash
   # 1. 切换到 develop 分支并更新
   git checkout develop
   git pull upstream develop

   # 2. 创建功能分支
   git checkout -b feature/your-feature-name

   # 3. 开发并提交代码
   git add .
   git commit -m "feat: 添加新功能"

   # 4. 推送分支
   git push origin feature/your-feature-name

   # 5. 创建 Pull Request
   # 在 GitHub 上创建从 feature/your-feature-name 到 develop 的 Pull Request

   # 6. 代码审查和合并
   # 等待代码审查，根据反馈修改代码，最终合并到 develop 分支
   ```

### 提交信息规范

我们使用 [Conventional Commits](https://www.conventionalcommits.org/) 规范：

- **feat**: 新功能
- **fix**: 修复 bug
- **docs**: 文档更改
- **style**: 代码格式（不影响代码运行的变动）
- **refactor**: 重构（既不是新增功能，也不是修改 bug 的代码变动）
- **perf**: 性能优化
- **test**: 增加测试
- **chore**: 构建过程或辅助工具的变动

提交信息格式：

```
<type>(<scope>): <subject>

<body>

<footer>
```

示例：

```
feat(auth): 添加用户登录功能

添加用户登录功能，包括用户名密码验证和JWT令牌生成。

Closes #123
```

### 代码审查指南

1. **审查检查清单**

   - [ ] 代码符合项目编码规范
   - [ ] 功能实现符合需求
   - [ ] 添加了适当的测试
   - [ ] 更新了相关文档
   - [ ] 没有引入安全漏洞
   - [ ] 没有引入性能问题
   - [ ] 提交信息符合规范

2. **审查流程**

   - 开发者完成功能开发并提交 Pull Request
   - 指定至少一名审查者进行代码审查
   - 审查者提出修改建议
   - 开发者根据反馈修改代码
   - 审查者确认修改后批准 Pull Request
   - 项目维护者合并代码到 develop 分支

## 代码规范

### Python 代码规范

1. **基本规范**

   - 遵循 [PEP 8](https://www.python.org/dev/peps/pep-0008/) 代码风格
   - 使用 4 个空格缩进
   - 行长度限制为 120 字符
   - 使用双引号作为字符串引号
   - 使用下划线命名法命名变量和函数

2. **导入规范**

   ```python
   # 标准库导入
   import os
   import sys
   from datetime import datetime

   # 第三方库导入
   import flask
   from flask_sqlalchemy import SQLAlchemy

   # 本地应用导入
   from app import create_app
   from app.models import User
   ```

3. **函数和类规范**

   ```python
   # 函数命名和文档字符串
   def get_user_by_id(user_id):
       """根据用户ID获取用户信息。

       Args:
           user_id (int): 用户ID

       Returns:
           User: 用户对象，如果不存在则返回None
       """
       return User.query.get(user_id)

   # 类命名和文档字符串
   class UserService:
       """用户服务类，提供用户相关的业务逻辑。"""

       def __init__(self, db):
           """初始化用户服务。

           Args:
               db (SQLAlchemy): 数据库实例
           """
           self.db = db

       def create_user(self, username, email, password):
           """创建新用户。

           Args:
               username (str): 用户名
               email (str): 邮箱
               password (str): 密码

           Returns:
               User: 创建的用户对象
           """
           # 实现代码
           pass
   ```

4. **异常处理规范**

   ```python
   try:
       user = User.query.get(user_id)
       if not user:
           raise ValueError("用户不存在")
       return user.to_dict()
   except ValueError as e:
       current_app.logger.error(f"获取用户信息失败: {str(e)}")
       return None, str(e)
   except Exception as e:
       current_app.logger.error(f"获取用户信息失败: {str(e)}")
       return None, "服务器内部错误"
   ```

### JavaScript/TypeScript 代码规范

1. **基本规范**

   - 遵循 [Standard JS](https://standardjs.com/) 代码风格
   - 使用 2 个空格缩进
   - 行长度限制为 100 字符
   - 使用单引号作为字符串引号
   - 使用驼峰命名法命名变量和函数

2. **导入规范**

   ```javascript
   // Vue 相关
   import { ref, reactive, onMounted } from 'vue'
   import { useRouter } from 'vue-router'
   import { useStore } from 'vuex'

   // 第三方库
   import axios from 'axios'
   import { ElMessage } from 'element-plus'

   // 本地组件和工具
   import DataTable from '@/components/DataTable.vue'
   import { formatDate } from '@/utils/common'
   ```

3. **组件规范**

   ```javascript
   <template>
     <div class="user-list">
       <el-table :data="users" style="width: 100%">
         <el-table-column prop="username" label="用户名" />
         <el-table-column prop="email" label="邮箱" />
         <el-table-column label="操作">
           <template #default="{ row }">
             <el-button type="primary" @click="editUser(row)">编辑</el-button>
           </template>
         </el-table-column>
       </el-table>
     </div>
   </template>

   <script>
   import { ref, onMounted } from 'vue'
   import { ElMessage } from 'element-plus'
   import { getUserList } from '@/api/auth'

   export default {
     name: 'UserList',
     setup() {
       const users = ref([])

       const fetchUsers = async () => {
         try {
           const response = await getUserList()
           users.value = response.data
         } catch (error) {
           ElMessage.error('获取用户列表失败')
         }
       }

       onMounted(() => {
         fetchUsers()
       })

       return {
         users
       }
     }
   }
   </script>

   <style scoped>
   .user-list {
     padding: 20px;
   }
   </style>
   ```

4. **API 调用规范**

   ```javascript
   // API 封装
   import request from '@/utils/request'

   export function getUserList(params) {
     return request({
       url: '/api/users',
       method: 'get',
       params
     })
   }

   export function createUser(data) {
     return request({
       url: '/api/users',
       method: 'post',
       data
     })
   }

   // 组件中使用
   import { getUserList, createUser } from '@/api/auth'

   const fetchUsers = async () => {
     try {
       const response = await getUserList({ page: 1, pageSize: 10 })
       users.value = response.data.items
     } catch (error) {
       ElMessage.error('获取用户列表失败')
     }
   }

   const handleCreate = async (userData) => {
     try {
       await createUser(userData)
       ElMessage.success('用户创建成功')
       fetchUsers()
     } catch (error) {
       ElMessage.error('用户创建失败')
     }
   }
   ```

## API 设计规范

### RESTful API 设计

1. **URL 设计**

   - 使用名词复数形式表示资源集合
   - 使用层级结构表示资源之间的关系
   - 使用查询参数进行过滤、排序、分页

   示例：

   ```
   GET /api/software          # 获取软件列表
   POST /api/software         # 创建软件
   GET /api/software/{id}     # 获取特定软件
   PUT /api/software/{id}     # 更新特定软件
   DELETE /api/software/{id}  # 删除特定软件

   GET /api/software/{id}/versions         # 获取软件版本列表
   POST /api/software/{id}/versions        # 上传软件版本
   GET /api/software/{id}/versions/{vid}   # 获取特定版本
   PUT /api/software/{id}/versions/{vid}   # 更新特定版本
   DELETE /api/software/{id}/versions/{vid} # 删除特定版本
   ```

2. **HTTP 方法**

   - GET: 获取资源
   - POST: 创建资源
   - PUT: 更新资源（全量更新）
   - PATCH: 更新资源（部分更新）
   - DELETE: 删除资源

3. **响应格式**

   统一使用 JSON 格式，遵循以下结构：

   ```json
   {
     "success": true,
     "data": {},
     "message": "操作成功"
   }
   ```

   或错误响应：

   ```json
   {
     "success": false,
     "error": {
       "code": "ERROR_CODE",
       "message": "错误描述"
     },
     "message": "操作失败"
   }
   ```

4. **状态码**

   - 200 OK: 请求成功
   - 201 Created: 资源创建成功
   - 400 Bad Request: 请求参数错误
   - 401 Unauthorized: 未授权
   - 403 Forbidden: 权限不足
   - 404 Not Found: 资源不存在
   - 500 Internal Server Error: 服务器内部错误

### 版本控制

API 版本通过 URL 路径控制，例如：

```
/api/v1/software
```

当前版本为 v1，未来升级时将引入新版本，同时保持旧版本兼容性。

### 认证与授权

使用 JWT (JSON Web Token) 进行认证和授权：

1. **认证流程**

   - 用户登录获取访问令牌
   - 在请求头中包含访问令牌：`Authorization: Bearer <access_token>`
   - 令牌过期后使用刷新令牌获取新的访问令牌

2. **权限控制**

   - 基于角色的访问控制（RBAC）
   - 支持管理员和普通用户角色
   - 特定 API 接口需要特定角色才能访问

### 错误处理

1. **错误码定义**

   | 错误码 | 描述 |
   |--------|------|
   | INVALID_PARAMETER | 请求参数无效 |
   | MISSING_PARAMETER | 缺少必需参数 |
   | INVALID_CREDENTIALS | 用户名或密码错误 |
   | UNAUTHORIZED | 未授权访问 |
   | FORBIDDEN | 权限不足 |
   | RESOURCE_NOT_FOUND | 资源不存在 |
   | RESOURCE_ALREADY_EXISTS | 资源已存在 |
   | FILE_UPLOAD_FAILED | 文件上传失败 |
   | INVALID_FILE_TYPE | 无效的文件类型 |
   | FILE_TOO_LARGE | 文件过大 |
   | WEBHOOK_FAILED | Webhook 调用失败 |
   | INTERNAL_ERROR | 服务器内部错误 |

2. **错误响应示例**

   ```json
   {
     "success": false,
     "error": {
       "code": "INVALID_PARAMETER",
       "message": "请求参数无效"
     },
     "message": "操作失败"
   }
   ```

## 前端开发指南

### Vue 3 开发

1. **Composition API**

   使用 Vue 3 的 Composition API 进行组件开发：

   ```javascript
   import { ref, reactive, computed, onMounted, watch } from 'vue'
   import { useStore } from 'vuex'
   import { useRouter, useRoute } from 'vue-router'

   export default {
     name: 'SoftwareList',
     setup() {
       const store = useStore()
       const router = useRouter()
       const route = useRoute()

       // 响应式状态
       const loading = ref(false)
       const search = ref('')
       const softwareList = ref([])

       // 计算属性
       const filteredSoftwareList = computed(() => {
         return softwareList.value.filter(software => 
           software.name.toLowerCase().includes(search.value.toLowerCase())
         )
       })

       // 方法
       const fetchSoftwareList = async () => {
         loading.value = true
         try {
           const response = await store.dispatch('software/fetchSoftwareList')
           softwareList.value = response.data.items
         } catch (error) {
           ElMessage.error('获取软件列表失败')
         } finally {
           loading.value = false
         }
       }

       const handleEdit = (software) => {
         router.push(`/software/edit/${software.id}`)
       }

       // 生命周期
       onMounted(() => {
         fetchSoftwareList()
       })

       // 监听器
       watch(search, (newVal) => {
         // 搜索逻辑
       })

       return {
         loading,
         search,
         softwareList,
         filteredSoftwareList,
         handleEdit
       }
     }
   }
   ```

2. **组件通信**

   使用 props 和 emit 进行父子组件通信：

   ```javascript
   // 父组件
   <template>
     <div>
       <child-component :message="message" @update-message="handleUpdateMessage" />
     </div>
   </template>

   <script>
   import { ref } from 'vue'
   import ChildComponent from './ChildComponent.vue'

   export default {
     components: { ChildComponent },
     setup() {
       const message = ref('Hello from parent')

       const handleUpdateMessage = (newMessage) => {
         message.value = newMessage
       }

       return {
         message,
         handleUpdateMessage
       }
     }
   }
   </script>

   // 子组件
   <template>
     <div>
       <p>{{ message }}</p>
       <button @click="updateMessage">Update Message</button>
     </div>
   </template>

   <script>
   export default {
     props: {
       message: {
         type: String,
         required: true
       }
     },
     emits: ['update-message'],
     setup(props, { emit }) {
       const updateMessage = () => {
         emit('update-message', 'Hello from child')
       }

       return {
         updateMessage
       }
     }
   }
   </script>
   ```

3. **状态管理**

   使用 Vuex 进行状态管理：

   ```javascript
   // store/modules/software.js
   import { getSoftwareList, createSoftware, updateSoftware, deleteSoftware } from '@/api/software'

   const state = {
     softwareList: [],
     currentSoftware: null,
     loading: false
   }

   const mutations = {
     SET_SOFTWARE_LIST(state, list) {
       state.softwareList = list
     },
     SET_CURRENT_SOFTWARE(state, software) {
       state.currentSoftware = software
     },
     SET_LOADING(state, loading) {
       state.loading = loading
     },
     ADD_SOFTWARE(state, software) {
       state.softwareList.push(software)
     },
     UPDATE_SOFTWARE(state, updatedSoftware) {
       const index = state.softwareList.findIndex(s => s.id === updatedSoftware.id)
       if (index !== -1) {
         state.softwareList.splice(index, 1, updatedSoftware)
       }
     },
     DELETE_SOFTWARE(state, id) {
       state.softwareList = state.softwareList.filter(s => s.id !== id)
     }
   }

   const actions = {
     async fetchSoftwareList({ commit }) {
       commit('SET_LOADING', true)
       try {
         const response = await getSoftwareList()
         commit('SET_SOFTWARE_LIST', response.data.items)
         return response
       } finally {
         commit('SET_LOADING', false)
       }
     },
     async createSoftware({ commit }, softwareData) {
       const response = await createSoftware(softwareData)
       commit('ADD_SOFTWARE', response.data)
       return response
     },
     async updateSoftware({ commit }, { id, data }) {
       const response = await updateSoftware(id, data)
       commit('UPDATE_SOFTWARE', response.data)
       return response
     },
     async deleteSoftware({ commit }, id) {
       await deleteSoftware(id)
       commit('DELETE_SOFTWARE', id)
     }
   }

   const getters = {
     softwareList: state => state.softwareList,
     currentSoftware: state => state.currentSoftware,
     loading: state => state.loading
   }

   export default {
     namespaced: true,
     state,
     mutations,
     actions,
     getters
   }
   ```

### 路由管理

使用 Vue Router 进行路由管理：

```javascript
// router/index.js
import { createRouter, createWebHistory } from 'vue-router'
import store from '@/store'

const routes = [
  {
    path: '/',
    redirect: '/dashboard'
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('@/views/Dashboard.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/software',
    name: 'SoftwareList',
    component: () => import('@/views/SoftwareList.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/software/:id',
    name: 'SoftwareDetail',
    component: () => import('@/views/SoftwareDetail.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/software/:id/edit',
    name: 'SoftwareEdit',
    component: () => import('@/views/SoftwareEdit.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/statistics',
    name: 'Statistics',
    component: () => import('@/views/Statistics.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('@/views/Settings.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/NotFound.vue')
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth)
  const isAuthenticated = store.getters['auth/isAuthenticated']

  if (requiresAuth && !isAuthenticated) {
    next('/login')
  } else {
    next()
  }
})

export default router
```

### UI 组件使用

使用 Element Plus 组件库：

```javascript
<template>
  <div class="software-form">
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="120px"
    >
      <el-form-item label="软件名称" prop="name">
        <el-input v-model="form.name" placeholder="请输入软件名称" />
      </el-form-item>
      
      <el-form-item label="软件描述" prop="description">
        <el-input
          v-model="form.description"
          type="textarea"
          :rows="4"
          placeholder="请输入软件描述"
        />
      </el-form-item>
      
      <el-form-item label="状态" prop="status">
        <el-select v-model="form.status" placeholder="请选择状态">
          <el-option label="激活" value="active" />
          <el-option label="停用" value="inactive" />
        </el-select>
      </el-form-item>
      
      <el-form-item>
        <el-button type="primary" @click="handleSubmit">提交</el-button>
        <el-button @click="handleReset">重置</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script>
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'

export default {
  name: 'SoftwareForm',
  setup() {
    const formRef = ref(null)
    
    const form = reactive({
      name: '',
      description: '',
      status: 'active'
    })
    
    const rules = {
      name: [
        { required: true, message: '请输入软件名称', trigger: 'blur' },
        { min: 2, max: 50, message: '长度在 2 到 50 个字符', trigger: 'blur' }
      ],
      description: [
        { max: 500, message: '最多 500 个字符', trigger: 'blur' }
      ],
      status: [
        { required: true, message: '请选择状态', trigger: 'change' }
      ]
    }
    
    const handleSubmit = () => {
      formRef.value.validate((valid) => {
        if (valid) {
          ElMessage.success('提交成功')
          // 提交逻辑
        } else {
          ElMessage.error('请正确填写表单')
          return false
        }
      })
    }
    
    const handleReset = () => {
      formRef.value.resetFields()
    }
    
    return {
      formRef,
      form,
      rules,
      handleSubmit,
      handleReset
    }
  }
}
</script>

<style scoped>
.software-form {
  max-width: 600px;
  margin: 0 auto;
  padding: 20px;
}
</style>
```

## 后端开发指南

### Flask 应用结构

1. **应用工厂模式**

   ```python
   # app/__init__.py
   from flask import Flask
   from flask_sqlalchemy import SQLAlchemy
   from flask_jwt_extended import JWTManager
   from flask_cors import CORS
   from flask_migrate import Migrate
   from app.config import Config

   db = SQLAlchemy()
   jwt = JWTManager()
   migrate = Migrate()

   def create_app(config_class=Config):
       app = Flask(__name__)
       app.config.from_object(config_class)

       # 初始化扩展
       db.init_app(app)
       jwt.init_app(app)
       migrate.init_app(app, db)
       CORS(app)

       # 注册蓝图
       from app.api.auth import bp as auth_bp
       app.register_blueprint(auth_bp, url_prefix='/api/auth')

       from app.api.software import bp as software_bp
       app.register_blueprint(software_bp, url_prefix='/api/software')

       from app.api.statistics import bp as statistics_bp
       app.register_blueprint(statistics_bp, url_prefix='/api/statistics')

       from app.api.webhook import bp as webhook_bp
       app.register_blueprint(webhook_bp, url_prefix='/api/webhook')

       return app
   ```

2. **配置管理**

   ```python
   # app/config.py
   import os
   from dotenv import load_dotenv

   basedir = os.path.abspath(os.path.dirname(__file__))
   load_dotenv(os.path.join(basedir, '.env'))

   class Config:
       SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
       JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key'
       JWT_ACCESS_TOKEN_EXPIRES = int(os.environ.get('JWT_ACCESS_TOKEN_EXPIRES', 7200))
       JWT_REFRESH_TOKEN_EXPIRES = int(os.environ.get('JWT_REFRESH_TOKEN_EXPIRES', 604800))
       SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
           'sqlite:///' + os.path.join(basedir, 'forge.db')
       SQLALCHEMY_TRACK_MODIFICATIONS = False
       UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or os.path.join(basedir, 'uploads')
       MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 1073741824))  # 1GB

   class DevelopmentConfig(Config):
       DEBUG = True

   class ProductionConfig(Config):
       DEBUG = False

   class TestingConfig(Config):
       TESTING = True
       SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

   config = {
       'development': DevelopmentConfig,
       'production': ProductionConfig,
       'testing': TestingConfig,
       'default': DevelopmentConfig
   }
   ```

3. **蓝图注册**

   ```python
   # app/api/auth.py
   from flask import Blueprint

   bp = Blueprint('auth', __name__)

   from app.api.auth import routes
   ```

   ```python
   # app/api/auth/routes.py
   from flask import request, jsonify
   from app.api.auth import bp
   from app.utils.response import success_response, error_response
   from app.services.auth_service import AuthService

   @bp.route('/login', methods=['POST'])
   def login():
       """用户登录"""
       data = request.get_json()
       
       if not data or not data.get('username') or not data.get('password'):
           return error_response('MISSING_PARAMETER', '缺少用户名或密码'), 400
       
       auth_service = AuthService()
       result = auth_service.login(data['username'], data['password'])
       
       if result['success']:
           return success_response(result['data'], '登录成功')
       else:
           return error_response('INVALID_CREDENTIALS', result['message']), 401
   ```

### 数据模型设计

1. **基类模型**

   ```python
   # app/models/__init__.py
   from datetime import datetime
   from app import db

   class BaseModel(db.Model):
       """基类模型，提供通用字段"""
       __abstract__ = True

       id = db.Column(db.Integer, primary_key=True)
       created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
       updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

       def to_dict(self):
           """将模型转换为字典"""
           result = {}
           for column in self.__table__.columns:
               value = getattr(self, column.name)
               if isinstance(value, datetime):
                   value = value.isoformat()
               result[column.name] = value
           return result
   ```

2. **用户模型**

   ```python
   # app/models/user.py
   from werkzeug.security import generate_password_hash, check_password_hash
   from app import db
   from app.models import BaseModel

   class User(BaseModel):
       __tablename__ = 'users'

       username = db.Column(db.String(80), unique=True, nullable=False)
       email = db.Column(db.String(120), unique=True, nullable=False)
       password_hash = db.Column(db.String(128), nullable=False)
       role = db.Column(db.String(20), nullable=False, default='user')

       def set_password(self, password):
           """设置密码"""
           self.password_hash = generate_password_hash(password)

       def check_password(self, password):
           """验证密码"""
           return check_password_hash(self.password_hash, password)

       def to_dict(self):
           """将用户转换为字典，排除敏感信息"""
           data = super().to_dict()
           data.pop('password_hash', None)
           return data

       def __repr__(self):
           return f'<User {self.username}>'
   ```

3. **软件模型**

   ```python
   # app/models/software.py
   from app import db
   from app.models import BaseModel

   class SoftwareSpace(BaseModel):
       __tablename__ = 'software_spaces'

       name = db.Column(db.String(100), nullable=False)
       description = db.Column(db.Text)
       status = db.Column(db.String(20), nullable=False, default='active')
       owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

       owner = db.relationship('User', backref=db.backref('software_spaces', lazy='dynamic'))
       versions = db.relationship('SoftwareVersion', backref='software', lazy='dynamic', cascade='all, delete-orphan')

       def to_dict(self):
           data = super().to_dict()
           data['versions_count'] = self.versions.count()
           return data

       def __repr__(self):
           return f'<SoftwareSpace {self.name}>'

   class SoftwareVersion(BaseModel):
       __tablename__ = 'software_versions'

       version_number = db.Column(db.String(50), nullable=False)
       release_notes = db.Column(db.Text)
       file_size = db.Column(db.BigInteger, nullable=False)
       file_hash = db.Column(db.String(64), nullable=False)
       software_id = db.Column(db.Integer, db.ForeignKey('software_spaces.id'), nullable=False)
       uploader_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
       status = db.Column(db.String(20), nullable=False, default='active')
       download_count = db.Column(db.Integer, nullable=False, default=0)

       software = db.relationship('SoftwareSpace', backref=db.backref('versions', lazy='dynamic'))
       uploader = db.relationship('User', backref=db.backref('uploaded_versions', lazy='dynamic'))
       download_records = db.relationship('DownloadRecord', backref='version', lazy='dynamic', cascade='all, delete-orphan')

       def to_dict(self):
           data = super().to_dict()
           data['software'] = self.software.to_dict() if self.software else None
           data['uploader'] = self.uploader.to_dict() if self.uploader else None
           return data

       def __repr__(self):
           return f'<SoftwareVersion {self.version_number}>'
   ```

### API 路由实现

1. **认证 API**

   ```python
   # app/api/auth/routes.py
   from flask import request, jsonify, current_app
   from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, jwt_required
   from app.api.auth import bp
   from app.utils.response import success_response, error_response
   from app.services.auth_service import AuthService
   from app.utils.auth import token_required

   @bp.route('/login', methods=['POST'])
   def login():
       """用户登录"""
       data = request.get_json()
       
       if not data or not data.get('username') or not data.get('password'):
           return error_response('MISSING_PARAMETER', '缺少用户名或密码'), 400
       
       auth_service = AuthService()
       result = auth_service.login(data['username'], data['password'])
       
       if result['success']:
           return success_response(result['data'], '登录成功')
       else:
           return error_response('INVALID_CREDENTIALS', result['message']), 401

   @bp.route('/refresh', methods=['POST'])
   @jwt_required(refresh=True)
   def refresh():
       """刷新令牌"""
       current_user_id = get_jwt_identity()
       auth_service = AuthService()
       result = auth_service.refresh_token(current_user_id)
       
       if result['success']:
           return success_response(result['data'], '令牌刷新成功')
       else:
           return error_response('UNAUTHORIZED', result['message']), 401

   @bp.route('/profile', methods=['GET'])
   @token_required
   def profile():
       """获取用户信息"""
       current_user_id = get_jwt_identity()
       auth_service = AuthService()
       result = auth_service.get_user_profile(current_user_id)
       
       if result['success']:
           return success_response(result['data'], '获取用户信息成功')
       else:
           return error_response('RESOURCE_NOT_FOUND', result['message']), 404

   @bp.route('/change-password', methods=['POST'])
   @token_required
   def change_password():
       """修改密码"""
       current_user_id = get_jwt_identity()
       data = request.get_json()
       
       if not data or not data.get('old_password') or not data.get('new_password'):
           return error_response('MISSING_PARAMETER', '缺少密码参数'), 400
       
       auth_service = AuthService()
       result = auth_service.change_password(current_user_id, data['old_password'], data['new_password'])
       
       if result['success']:
           return success_response(None, '密码修改成功')
       else:
           return error_response('INVALID_CREDENTIALS', result['message']), 400

   @bp.route('/init-admin', methods=['POST'])
   def init_admin():
       """初始化管理员账户"""
       data = request.get_json()
       
       if not data or not data.get('username') or not data.get('password') or not data.get('email'):
           return error_response('MISSING_PARAMETER', '缺少必要参数'), 400
       
       auth_service = AuthService()
       result = auth_service.init_admin(data['username'], data['password'], data['email'])
       
       if result['success']:
           return success_response(result['data'], '管理员创建成功')
       else:
           return error_response('RESOURCE_ALREADY_EXISTS', result['message']), 409
   ```

2. **软件管理 API**

   ```python
   # app/api/software/routes.py
   from flask import request, jsonify, current_app, send_file
   from flask_jwt_extended import get_jwt_identity, jwt_required
   from app.api.software import bp
   from app.utils.response import success_response, error_response
   from app.services.software_service import SoftwareService
   from app.utils.auth import token_required, admin_required
   from werkzeug.utils import secure_filename
   import os
   import uuid

   @bp.route('', methods=['GET'])
   @token_required
   def get_software_list():
       """获取软件列表"""
       page = request.args.get('page', 1, type=int)
       page_size = request.args.get('pageSize', 20, type=int)
       search = request.args.get('search', '')
       sort_by = request.args.get('sortBy', 'created_at')
       order = request.args.get('order', 'desc')
       
       software_service = SoftwareService()
       result = software_service.get_software_list(page, page_size, search, sort_by, order)
       
       if result['success']:
           return success_response(result['data'], '获取软件列表成功')
       else:
           return error_response('INTERNAL_ERROR', result['message']), 500

   @bp.route('', methods=['POST'])
   @token_required
   def create_software():
       """创建软件"""
       current_user_id = get_jwt_identity()
       data = request.get_json()
       
       if not data or not data.get('name') or not data.get('description'):
           return error_response('MISSING_PARAMETER', '缺少必要参数'), 400
       
       software_service = SoftwareService()
       result = software_service.create_software(current_user_id, data)
       
       if result['success']:
           return success_response(result['data'], '软件创建成功'), 201
       else:
           return error_response('INTERNAL_ERROR', result['message']), 500

   @bp.route('/<int:id>', methods=['GET'])
   @token_required
   def get_software(id):
       """获取软件详情"""
       software_service = SoftwareService()
       result = software_service.get_software(id)
       
       if result['success']:
           return success_response(result['data'], '获取软件详情成功')
       else:
           return error_response('RESOURCE_NOT_FOUND', result['message']), 404

   @bp.route('/<int:id>', methods=['PUT'])
   @token_required
   def update_software(id):
       """更新软件"""
       current_user_id = get_jwt_identity()
       data = request.get_json()
       
       software_service = SoftwareService()
       result = software_service.update_software(current_user_id, id, data)
       
       if result['success']:
           return success_response(result['data'], '软件更新成功')
       else:
           if 'not found' in result['message'].lower():
               return error_response('RESOURCE_NOT_FOUND', result['message']), 404
           elif 'permission' in result['message'].lower():
               return error_response('FORBIDDEN', result['message']), 403
           else:
               return error_response('INTERNAL_ERROR', result['message']), 500

   @bp.route('/<int:id>', methods=['DELETE'])
   @token_required
   def delete_software(id):
       """删除软件"""
       current_user_id = get_jwt_identity()
       
       software_service = SoftwareService()
       result = software_service.delete_software(current_user_id, id)
       
       if result['success']:
           return success_response(None, '软件删除成功')
       else:
           if 'not found' in result['message'].lower():
               return error_response('RESOURCE_NOT_FOUND', result['message']), 404
           elif 'permission' in result['message'].lower():
               return error_response('FORBIDDEN', result['message']), 403
           else:
               return error_response('INTERNAL_ERROR', result['message']), 500

   @bp.route('/<int:id>/versions', methods=['GET'])
   @token_required
   def get_software_versions(id):
       """获取软件版本列表"""
       software_service = SoftwareService()
       result = software_service.get_software_versions(id)
       
       if result['success']:
           return success_response(result['data'], '获取软件版本列表成功')
       else:
           return error_response('RESOURCE_NOT_FOUND', result['message']), 404

   @bp.route('/<int:id>/versions', methods=['POST'])
   @token_required
   def upload_software_version(id):
       """上传软件版本"""
       current_user_id = get_jwt_identity()
       
       if 'file' not in request.files:
           return error_response('MISSING_PARAMETER', '缺少文件参数'), 400
       
       file = request.files['file']
       if file.filename == '':
           return error_response('MISSING_PARAMETER', '未选择文件'), 400
       
       version_number = request.form.get('version_number')
       release_notes = request.form.get('release_notes', '')
       
       if not version_number:
           return error_response('MISSING_PARAMETER', '缺少版本号'), 400
       
       # 生成安全的文件名
       filename = secure_filename(file.filename)
       file_ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
       safe_filename = f"{uuid.uuid4()}.{file_ext}"
       
       software_service = SoftwareService()
       result = software_service.upload_software_version(
           current_user_id, id, file, safe_filename, version_number, release_notes
       )
       
       if result['success']:
           return success_response(result['data'], '版本上传成功'), 201
       else:
           if 'not found' in result['message'].lower():
               return error_response('RESOURCE_NOT_FOUND', result['message']), 404
           elif 'permission' in result['message'].lower():
               return error_response('FORBIDDEN', result['message']), 403
           else:
               return error_response('INTERNAL_ERROR', result['message']), 500

   @bp.route('/<int:id>/versions/<int:version_id>/download', methods=['GET'])
   @token_required
   def download_software_version(id, version_id):
       """下载软件版本"""
       current_user_id = get_jwt_identity()
       ip_address = request.remote_addr
       user_agent = request.headers.get('User-Agent', '')
       
       software_service = SoftwareService()
       result = software_service.download_software_version(
           current_user_id, id, version_id, ip_address, user_agent
       )
       
       if result['success']:
           return send_file(result['data']['file_path'], as_attachment=True, download_name=result['data']['filename'])
       else:
           if 'not found' in result['message'].lower():
               return error_response('RESOURCE_NOT_FOUND', result['message']), 404
           elif 'permission' in result['message'].lower():
               return error_response('FORBIDDEN', result['message']), 403
           else:
               return error_response('INTERNAL_ERROR', result['message']), 500

   # 公开下载接口，无需认证
   @bp.route('/public/<int:id>/versions/<int:version_id>/download', methods=['GET'])
   def public_download_software_version(id, version_id):
       """公开下载软件版本"""
       ip_address = request.remote_addr
       user_agent = request.headers.get('User-Agent', '')
       
       software_service = SoftwareService()
       result = software_service.public_download_software_version(
           id, version_id, ip_address, user_agent
       )
       
       if result['success']:
           return send_file(result['data']['file_path'], as_attachment=True, download_name=result['data']['filename'])
       else:
           if 'not found' in result['message'].lower():
               return error_response('RESOURCE_NOT_FOUND', result['message']), 404
           elif 'inactive' in result['message'].lower():
               return error_response('FORBIDDEN', result['message']), 403
           else:
               return error_response('INTERNAL_ERROR', result['message']), 500
   ```

### 服务层实现

1. **认证服务**

   ```python
   # app/services/auth_service.py
   from werkzeug.security import check_password_hash
   from flask_jwt_extended import create_access_token, create_refresh_token
   from app import db
   from app.models.user import User
   from app.utils.response import success_response, error_response
   import hashlib

   class AuthService:
       def __init__(self):
           pass

       def login(self, username, password):
           """用户登录"""
           user = User.query.filter_by(username=username).first()
           
           if user and user.check_password(password):
               access_token = create_access_token(identity=user.id)
               refresh_token = create_refresh_token(identity=user.id)
               
               return success_response({
                   'access_token': access_token,
                   'refresh_token': refresh_token,
                   'user': user.to_dict()
               }, '登录成功')
           else:
               return error_response(None, '用户名或密码错误')

       def refresh_token(self, user_id):
           """刷新令牌"""
           user = User.query.get(user_id)
           
           if user:
               access_token = create_access_token(identity=user.id)
               return success_response({
                   'access_token': access_token
               }, '令牌刷新成功')
           else:
               return error_response(None, '用户不存在')

       def get_user_profile(self, user_id):
           """获取用户信息"""
           user = User.query.get(user_id)
           
           if user:
               return success_response(user.to_dict(), '获取用户信息成功')
           else:
               return error_response(None, '用户不存在')

       def change_password(self, user_id, old_password, new_password):
           """修改密码"""
           user = User.query.get(user_id)
           
           if not user:
               return error_response(None, '用户不存在')
           
           if not user.check_password(old_password):
               return error_response(None, '原密码错误')
           
           user.set_password(new_password)
           db.session.commit()
           
           return success_response(None, '密码修改成功')

       def init_admin(self, username, password, email):
           """初始化管理员账户"""
           # 检查是否已存在管理员
           admin_user = User.query.filter_by(role='admin').first()
           if admin_user:
               return error_response(None, '管理员已存在')
           
           # 创建新管理员
           admin = User(username=username, email=email, role='admin')
           admin.set_password(password)
           
           db.session.add(admin)
           db.session.commit()
           
           return success_response(admin.to_dict(), '管理员创建成功')
   ```

2. **软件服务**

   ```python
   # app/services/software_service.py
   from app import db
   from app.models.user import User
   from app.models.software import SoftwareSpace, SoftwareVersion, DownloadRecord
   from app.utils.response import success_response, error_response
   from werkzeug.utils import secure_filename
   import os
   import uuid
   import hashlib
   from datetime import datetime

   class SoftwareService:
       def __init__(self):
           pass

       def get_software_list(self, page, page_size, search, sort_by, order):
           """获取软件列表"""
           query = SoftwareSpace.query
           
           # 搜索过滤
           if search:
               query = query.filter(SoftwareSpace.name.contains(search))
           
           # 排序
           if order == 'asc':
               query = query.order_by(getattr(SoftwareSpace, sort_by).asc())
           else:
               query = query.order_by(getattr(SoftwareSpace, sort_by).desc())
           
           # 分页
           pagination = query.paginate(page=page, per_page=page_size, error_out=False)
           
           return success_response({
               'items': [software.to_dict() for software in pagination.items],
               'total': pagination.total,
               'page': page,
               'pageSize': page_size
           }, '获取软件列表成功')

       def get_software(self, software_id):
           """获取软件详情"""
           software = SoftwareSpace.query.get(software_id)
           
           if software:
               return success_response(software.to_dict(), '获取软件详情成功')
           else:
               return error_response(None, '软件不存在')

       def create_software(self, user_id, data):
           """创建软件"""
           user = User.query.get(user_id)
           if not user:
               return error_response(None, '用户不存在')
           
           software = SoftwareSpace(
               name=data['name'],
               description=data['description'],
               status=data.get('status', 'active'),
               owner_id=user_id
           )
           
           db.session.add(software)
           db.session.commit()
           
           return success_response(software.to_dict(), '软件创建成功')

       def update_software(self, user_id, software_id, data):
           """更新软件"""
           software = SoftwareSpace.query.get(software_id)
           
           if not software:
               return error_response(None, '软件不存在')
           
           # 检查权限
           if software.owner_id != user_id:
               return error_response(None, '无权限修改此软件')
           
           # 更新字段
           if 'name' in data:
               software.name = data['name']
           if 'description' in data:
               software.description = data['description']
           if 'status' in data:
               software.status = data['status']
           
           software.updated_at = datetime.utcnow()
           db.session.commit()
           
           return success_response(software.to_dict(), '软件更新成功')

       def delete_software(self, user_id, software_id):
           """删除软件"""
           software = SoftwareSpace.query.get(software_id)
           
           if not software:
               return error_response(None, '软件不存在')
           
           # 检查权限
           if software.owner_id != user_id:
               return error_response(None, '无权限删除此软件')
           
           # 删除软件及其所有版本和文件
           db.session.delete(software)
           db.session.commit()
           
           return success_response(None, '软件删除成功')

       def get_software_versions(self, software_id):
           """获取软件版本列表"""
           software = SoftwareSpace.query.get(software_id)
           
           if not software:
               return error_response(None, '软件不存在')
           
           versions = software.versions.all()
           return success_response([version.to_dict() for version in versions], '获取软件版本列表成功')

       def upload_software_version(self, user_id, software_id, file, filename, version_number, release_notes):
           """上传软件版本"""
           software = SoftwareSpace.query.get(software_id)
           
           if not software:
               return error_response(None, '软件不存在')
           
           # 检查权限
           if software.owner_id != user_id:
               return error_response(None, '无权限上传此软件的版本')
           
           # 检查版本号是否已存在
           existing_version = SoftwareVersion.query.filter_by(
               software_id=software_id,
               version_number=version_number
           ).first()
           
           if existing_version:
               return error_response(None, '版本号已存在')
           
           # 确保上传目录存在
           upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], str(software_id))
           os.makedirs(upload_folder, exist_ok=True)
           
           # 保存文件
           file_path = os.path.join(upload_folder, filename)
           file.save(file_path)
           
           # 计算文件大小和哈希
           file_size = os.path.getsize(file_path)
           file_hash = self._calculate_file_hash(file_path)
           
           # 创建版本记录
           version = SoftwareVersion(
               version_number=version_number,
               release_notes=release_notes,
               file_size=file_size,
               file_hash=file_hash,
               software_id=software_id,
               uploader_id=user_id,
               status='active'
           )
           
           db.session.add(version)
           db.session.commit()
           
           return success_response(version.to_dict(), '版本上传成功')

       def download_software_version(self, user_id, software_id, version_id, ip_address, user_agent):
           """下载软件版本"""
           software = SoftwareSpace.query.get(software_id)
           version = SoftwareVersion.query.get(version_id)
           
           if not software or not version:
               return error_response(None, '软件或版本不存在')
           
           if version.software_id != software_id:
               return error_response(None, '版本不属于此软件')
           
           # 检查软件状态
           if software.status != 'active' or version.status != 'active':
               return error_response(None, '软件或版本已停用')
           
           # 构建文件路径
           file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], str(software_id), 
                                   os.path.basename(version.file_path))
           
           if not os.path.exists(file_path):
               return error_response(None, '文件不存在')
           
           # 记录下载
           download_record = DownloadRecord(
               ip_address=ip_address,
               user_agent=user_agent,
               version_id=version_id
           )
           
           db.session.add(download_record)
           
           # 更新下载计数
           version.download_count += 1
           
           db.session.commit()
           
           # 构造下载文件名
           file_ext = os.path.splitext(file_path)[1]
           download_filename = f"{software.name}-{version.version_number}{file_ext}"
           
           return success_response({
               'file_path': file_path,
               'filename': download_filename
           }, '下载成功')

       def public_download_software_version(self, software_id, version_id, ip_address, user_agent):
           """公开下载软件版本"""
           software = SoftwareSpace.query.get(software_id)
           version = SoftwareVersion.query.get(version_id)
           
           if not software or not version:
               return error_response(None, '软件或版本不存在')
           
           if version.software_id != software_id:
               return error_response(None, '版本不属于此软件')
           
           # 检查软件状态
           if software.status != 'active' or version.status != 'active':
               return error_response(None, '软件或版本已停用')
           
           # 构建文件路径
           file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], str(software_id), 
                                   os.path.basename(version.file_path))
           
           if not os.path.exists(file_path):
               return error_response(None, '文件不存在')
           
           # 记录下载
           download_record = DownloadRecord(
               ip_address=ip_address,
               user_agent=user_agent,
               version_id=version_id
           )
           
           db.session.add(download_record)
           
           # 更新下载计数
           version.download_count += 1
           
           db.session.commit()
           
           # 构造下载文件名
           file_ext = os.path.splitext(file_path)[1]
           download_filename = f"{software.name}-{version.version_number}{file_ext}"
           
           return success_response({
               'file_path': file_path,
               'filename': download_filename
           }, '下载成功')

       def _calculate_file_hash(self, file_path):
           """计算文件SHA256哈希值"""
           sha256_hash = hashlib.sha256()
           with open(file_path, 'rb') as f:
               # 分块读取文件，避免大文件内存问题
               for byte_block in iter(lambda: f.read(4096), b""):
                   sha256_hash.update(byte_block)
           return sha256_hash.hexdigest()
   ```

### 工具函数

1. **响应工具**

   ```python
   # app/utils/response.py
   def success_response(data=None, message='操作成功'):
       """成功响应"""
       return {
           'success': True,
           'data': data,
           'message': message
       }

   def error_response(code, message='操作失败'):
       """错误响应"""
       return {
           'success': False,
           'error': {
               'code': code,
               'message': message
           },
           'message': message
       }
   ```

2. **认证工具**

   ```python
   # app/utils/auth.py
   from functools import wraps
   from flask_jwt_extended import get_jwt_identity, get_jwt
   from flask import jsonify
   from app.models.user import User

   def token_required(f):
       """JWT令牌验证装饰器"""
       @wraps(f)
       def decorated(*args, **kwargs):
           current_user_id = get_jwt_identity()
           if not current_user_id:
               return jsonify(success_response(None, '未授权')), 401
           
           user = User.query.get(current_user_id)
           if not user:
               return jsonify(success_response(None, '用户不存在')), 401
           
           return f(current_user_id, *args, **kwargs)
       return decorated

   def admin_required(f):
       """管理员权限验证装饰器"""
       @wraps(f)
       def decorated(*args, **kwargs):
           current_user_id = get_jwt_identity()
           if not current_user_id:
               return jsonify(success_response(None, '未授权')), 401
           
           user = User.query.get(current_user_id)
           if not user or user.role != 'admin':
               return jsonify(success_response(None, '权限不足')), 403
           
           return f(current_user_id, *args, **kwargs)
       return decorated
   ```

3. **文件工具**

   ```python
   # app/utils/file.py
   import os
   import uuid
   from werkzeug.utils import secure_filename

   def ensure_directory_exists(directory):
       """确保目录存在，如果不存在则创建"""
       if not os.path.exists(directory):
           os.makedirs(directory)

   def generate_safe_filename(filename):
       """生成安全的文件名"""
       # 获取文件扩展名
       _, ext = os.path.splitext(filename)
       ext = ext.lower()
       
       # 使用UUID生成文件名
       safe_filename = f"{uuid.uuid4()}{ext}"
       return safe_filename

   def get_file_size(file_path):
       """获取文件大小（字节）"""
       return os.path.getsize(file_path)

   def calculate_file_hash(file_path, algorithm='sha256'):
       """计算文件哈希值"""
       import hashlib
       
       hash_func = getattr(hashlib, algorithm)()
       with open(file_path, 'rb') as f:
           # 分块读取文件，避免大文件内存问题
           for byte_block in iter(lambda: f.read(4096), b""):
               hash_func.update(byte_block)
       return hash_func.hexdigest()
   ```

## 数据库开发指南

### 数据库迁移

1. **初始化迁移**

   ```bash
   cd backend
   source venv/bin/activate  # Linux/macOS
   # 或
   venv\Scripts\activate  # Windows

   flask db init
   ```

2. **创建迁移**

   ```bash
   flask db migrate -m "初始化数据库"
   ```

3. **应用迁移**

   ```bash
   flask db upgrade
   ```

4. **回滚迁移**

   ```bash
   flask db downgrade
   ```

### 数据库操作

1. **查询操作**

   ```python
   # 获取所有用户
   users = User.query.all()

   # 根据ID获取用户
   user = User.query.get(user_id)

   # 根据条件过滤
   active_users = User.query.filter_by(status='active').all()

   # 复杂查询
   users = User.query.filter(
       User.username.contains('admin') | User.email.contains('admin')
   ).order_by(User.created_at.desc()).limit(10).all()

   # 分页查询
   pagination = User.query.paginate(page=1, per_page=10, error_out=False)
   users = pagination.items
   total = pagination.total
   ```

2. **创建操作**

   ```python
   # 创建新用户
   user = User(username='test', email='test@example.com')
   user.set_password('password')
   db.session.add(user)
   db.session.commit()
   ```

3. **更新操作**

   ```python
   # 更新用户
   user = User.query.get(user_id)
   if user:
       user.email = 'new_email@example.com'
       db.session.commit()
   ```

4. **删除操作**

   ```python
   # 删除用户
   user = User.query.get(user_id)
   if user:
       db.session.delete(user)
       db.session.commit()
   ```

5. **关系查询**

   ```python
   # 获取用户的所有软件
   user = User.query.get(user_id)
   software_spaces = user.software_spaces.all()

   # 获取软件的所有版本
   software = SoftwareSpace.query.get(software_id)
   versions = software.versions.all()

   # 预加载关联数据
   software = SoftwareSpace.query.options(
       db.joinedload(SoftwareSpace.versions)
   ).get(software_id)
   ```

### 数据库优化

1. **索引优化**

   ```python
   # 在模型中添加索引
   class User(BaseModel):
       __tablename__ = 'users'
       
       username = db.Column(db.String(80), unique=True, nullable=False, index=True)
       email = db.Column(db.String(120), unique=True, nullable=False, index=True)
       # 其他字段...
   ```

2. **查询优化**

   ```python
   # 使用 select_from 优化复杂查询
   from sqlalchemy.orm import lazyload, joinedload, subqueryload

   # 预加载关联数据，避免N+1查询问题
   software_spaces = SoftwareSpace.query.options(
       joinedload(SoftwareSpace.owner),
       subqueryload(SoftwareSpace.versions).joinedload(SoftwareVersion.uploader)
   ).all()

   # 使用过滤条件优化查询
   active_software = SoftwareSpace.query.filter(
       SoftwareSpace.status == 'active',
       SoftwareSpace.versions.any(SoftwareVersion.status == 'active')
   ).all()
   ```

3. **批量操作**

   ```python
   # 批量插入
   users = [
       User(username=f'user{i}', email=f'user{i}@example.com') 
       for i in range(100)
   ]
   db.session.bulk_save_objects(users)
   db.session.commit()

   # 批量更新
   db.session.query(User).filter(
       User.status == 'inactive'
   ).update({'status': 'active'}, synchronize_session=False)
   db.session.commit()
   ```

## 测试指南

### 单元测试

1. **后端测试**

   ```python
   # tests/test_auth.py
   import pytest
   import json
   from app import create_app, db
   from app.models.user import User

   @pytest.fixture
   def app():
       app = create_app('testing')
       with app.app_context():
           db.create_all()
           yield app
           db.drop_all()

   @pytest.fixture
   def client(app):
       return app.test_client()

   @pytest.fixture
   def runner(app):
       return app.test_cli_runner()

   @pytest.fixture
   def auth_headers(client):
       # 创建测试用户
       user = User(username='test', email='test@example.com')
       user.set_password('password')
       db.session.add(user)
       db.session.commit()
       
       # 登录获取令牌
       response = client.post('/api/auth/login', 
                             data=json.dumps({
                                 'username': 'test',
                                 'password': 'password'
                             }),
                             content_type='application/json')
       
       data = json.loads(response.data)
       token = data['data']['access_token']
       
       return {'Authorization': f'Bearer {token}'}

   def test_login_success(client):
       # 创建测试用户
       user = User(username='test', email='test@example.com')
       user.set_password('password')
       db.session.add(user)
       db.session.commit()
       
       # 测试登录
       response = client.post('/api/auth/login', 
                             data=json.dumps({
                                 'username': 'test',
                                 'password': 'password'
                             }),
                             content_type='application/json')
       
       assert response.status_code == 200
       data = json.loads(response.data)
       assert data['success'] is True
       assert 'access_token' in data['data']
       assert 'refresh_token' in data['data']

   def test_login_failure(client):
       response = client.post('/api/auth/login', 
                             data=json.dumps({
                                 'username': 'nonexistent',
                                 'password': 'wrong'
                             }),
                             content_type='application/json')
       
       assert response.status_code == 401
       data = json.loads(response.data)
       assert data['success'] is False

   def test_get_profile(client, auth_headers):
       response = client.get('/api/auth/profile', headers=auth_headers)
       
       assert response.status_code == 200
       data = json.loads(response.data)
       assert data['success'] is True
       assert data['data']['username'] == 'test'

   def test_unauthorized_access(client):
       response = client.get('/api/auth/profile')
       
       assert response.status_code == 401
       data = json.loads(response.data)
       assert data['success'] is False
   ```

2. **前端测试**

   ```javascript
   // tests/unit/auth.spec.js
   import { mount } from '@vue/test-utils'
   import { createPinia, setActivePinia } from 'pinia'
   import LoginForm from '@/views/Login.vue'
   import ElementPlus from 'element-plus'
   import axios from 'axios'

   jest.mock('axios')

   describe('LoginForm.vue', () => {
     beforeEach(() => {
       setActivePinia(createPinia())
     })

     it('renders correctly', () => {
       const wrapper = mount(LoginForm, {
         global: {
           plugins: [ElementPlus]
         }
       })
       expect(wrapper.find('.login-form').exists()).toBe(true)
     })

     it('submits form with valid data', async () => {
       const mockResponse = {
         data: {
           success: true,
           data: {
             access_token: 'fake-token',
             refresh_token: 'fake-refresh-token',
             user: {
               id: 1,
               username: 'test',
               email: 'test@example.com'
             }
           },
           message: '登录成功'
         }
       }

       axios.post.mockResolvedValue(mockResponse)

       const wrapper = mount(LoginForm, {
         global: {
           plugins: [ElementPlus]
         }
       })

       await wrapper.find('[data-testid="username"]').setValue('test')
       await wrapper.find('[data-testid="password"]').setValue('password')
       await wrapper.find('[data-testid="submit-button"]').trigger('click')

       expect(axios.post).toHaveBeenCalledWith('/api/auth/login', {
         username: 'test',
         password: 'password'
       })
     })

     it('shows error message for invalid credentials', async () => {
       const mockResponse = {
         response: {
           data: {
             success: false,
             error: {
               code: 'INVALID_CREDENTIALS',
               message: '用户名或密码错误'
             },
             message: '操作失败'
           }
         }
       }

       axios.post.mockRejectedValue(mockResponse)

       const wrapper = mount(LoginForm, {
         global: {
           plugins: [ElementPlus]
         }
       })

       await wrapper.find('[data-testid="username"]').setValue('test')
       await wrapper.find('[data-testid="password"]').setValue('wrong')
       await wrapper.find('[data-testid="submit-button"]').trigger('click')

       expect(wrapper.find('.el-message--error').exists()).toBe(true)
     })
   })
   ```

### 集成测试

1. **API 集成测试**

   ```python
   # tests/test_api_integration.py
   import pytest
   import json
   from app import create_app, db
   from app.models.user import User
   from app.models.software import SoftwareSpace, SoftwareVersion

   @pytest.fixture
   def app():
       app = create_app('testing')
       with app.app_context():
           db.create_all()
           yield app
           db.drop_all()

   @pytest.fixture
   def client(app):
       return app.test_client()

   @pytest.fixture
   def runner(app):
       return app.test_cli_runner()

   @pytest.fixture
   def test_user(app):
       user = User(username='test', email='test@example.com', role='admin')
       user.set_password('password')
       db.session.add(user)
       db.session.commit()
       return user

   @pytest.fixture
   def auth_headers(client, test_user):
       response = client.post('/api/auth/login', 
                             data=json.dumps({
                                 'username': 'test',
                                 'password': 'password'
                             }),
                             content_type='application/json')
       
       data = json.loads(response.data)
       token = data['data']['access_token']
       
       return {'Authorization': f'Bearer {token}'}

   def test_software_crud(client, auth_headers):
       # 创建软件
       software_data = {
           'name': 'Test Software',
           'description': 'Test Description'
       }
       
       response = client.post('/api/software', 
                             data=json.dumps(software_data),
                             content_type='application/json',
                             headers=auth_headers)
       
       assert response.status_code == 201
       data = json.loads(response.data)
       software_id = data['data']['id']
       
       # 获取软件详情
       response = client.get(f'/api/software/{software_id}', headers=auth_headers)
       assert response.status_code == 200
       
       # 更新软件
       update_data = {
           'name': 'Updated Software',
           'description': 'Updated Description'
       }
       
       response = client.put(f'/api/software/{software_id}', 
                            data=json.dumps(update_data),
                            content_type='application/json',
                            headers=auth_headers)
       
       assert response.status_code == 200
       
       # 删除软件
       response = client.delete(f'/api/software/{software_id}', headers=auth_headers)
       assert response.status_code == 200
       
       # 验证软件已删除
       response = client.get(f'/api/software/{software_id}', headers=auth_headers)
       assert response.status_code == 404

   def test_software_version_upload(client, auth_headers, test_user):
       # 创建软件
       software_data = {
           'name': 'Test Software',
           'description': 'Test Description'
       }
       
       response = client.post('/api/software', 
                             data=json.dumps(software_data),
                             content_type='application/json',
                             headers=auth_headers)
       
       assert response.status_code == 201
       data = json.loads(response.data)
       software_id = data['data']['id']
       
       # 上传版本
       with open('tests/fixtures/test_file.exe', 'rb') as f:
           response = client.post(f'/api/software/{software_id}/versions',
                                 data={
                                     'file': f,
                                     'version_number': '1.0.0',
                                     'release_notes': 'Initial release'
                                 },
                                 headers=auth_headers)
       
       assert response.status_code == 201
       data = json.loads(response.data)
       version_id = data['data']['id']
       
       # 获取版本列表
       response = client.get(f'/api/software/{software_id}/versions', headers=auth_headers)
       assert response.status_code == 200
       data = json.loads(response.data)
       assert len(data['data']) == 1
       assert data['data'][0]['version_number'] == '1.0.0'
       
       # 删除版本
       response = client.delete(f'/api/software/{software_id}/versions/{version_id}', headers=auth_headers)
       assert response.status_code == 200
   ```

2. **端到端测试**

   ```javascript
   // tests/e2e/login.spec.js
   const { test, expect } = require('@playwright/test');

   test('successful login', async ({ page }) => {
     await page.goto('http://localhost:8080/login');
     
     // 填写登录表单
     await page.fill('[data-testid="username"]', 'admin');
     await page.fill('[data-testid="password"]', 'admin123');
     
     // 点击登录按钮
     await page.click('[data-testid="submit-button"]');
     
     // 验证导航到仪表板
     await expect(page).toHaveURL('http://localhost:8080/dashboard');
     await expect(page.locator('.dashboard')).toBeVisible();
   });

   test('failed login', async ({ page }) => {
     await page.goto('http://localhost:8080/login');
     
     // 填写登录表单
     await page.fill('[data-testid="username"]', 'wrong');
     await page.fill('[data-testid="password"]', 'wrong');
     
     // 点击登录按钮
     await page.click('[data-testid="submit-button"]');
     
     // 验证错误消息
     await expect(page.locator('.el-message--error')).toBeVisible();
     await expect(page.locator('.el-message--error')).toHaveText('用户名或密码错误');
   });

   test('create software', async ({ page }) => {
     // 登录
     await page.goto('http://localhost:8080/login');
     await page.fill('[data-testid="username"]', 'admin');
     await page.fill('[data-testid="password"]', 'admin123');
     await page.click('[data-testid="submit-button"]');
     
     // 导航到软件列表
     await page.click('[data-testid="software-menu"]');
     await expect(page).toHaveURL('http://localhost:8080/software');
     
     // 点击创建按钮
     await page.click('[data-testid="create-button"]');
     
     // 填写软件信息
     await page.fill('[data-testid="name"]', 'Test Software');
     await page.fill('[data-testid="description"]', 'Test Description');
     
     // 提交表单
     await page.click('[data-testid="submit-button"]');
     
     // 验证创建成功
     await expect(page.locator('.el-message--success')).toBeVisible();
     await expect(page.locator('.el-message--success')).toHaveText('软件创建成功');
   });
   ```

### 测试覆盖率

1. **后端测试覆盖率**

   ```bash
   # 安装 coverage
   pip install coverage

   # 运行测试并生成覆盖率报告
   coverage run -m pytest
   coverage report
   coverage html
   ```

2. **前端测试覆盖率**

   ```json
   // package.json
   {
     "scripts": {
       "test:unit": "jest --coverage",
       "test:e2e": "playwright test"
     }
   }
   ```

   ```bash
   # 运行单元测试并生成覆盖率报告
   npm run test:unit

   # 运行端到端测试
   npm run test:e2e
   ```

## 调试指南

### 后端调试

1. **使用 VS Code 调试**

   创建 `.vscode/launch.json` 文件：

   ```json
   {
     "version": "0.2.0",
     "configurations": [
       {
         "name": "Python: Flask",
         "type": "python",
         "request": "launch",
         "module": "flask",
         "env": {
           "FLASK_APP": "run.py",
           "FLASK_ENV": "development"
         },
         "args": [
           "run",
           "--no-debugger",
           "--no-reload"
         ],
         "jinja": true,
         "justMyCode": true
       }
     ]
   }
   ```

2. **使用日志调试**

   ```python
   import logging
   from flask import current_app

   # 配置日志
   logging.basicConfig(
       level=logging.DEBUG,
       format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
   )

   # 在代码中添加日志
   current_app.logger.debug('Debug message')
   current_app.logger.info('Info message')
   current_app.logger.warning('Warning message')
   current_app.logger.error('Error message')
   ```

3. **使用 pdb 调试**

   ```python
   # 在代码中添加断点
   import pdb; pdb.set_trace()
   ```

### 前端调试

1. **使用 Vue Devtools**

   安装 Vue Devtools 浏览器扩展，用于调试 Vue 组件状态和 Vuex 状态。

2. **使用浏览器开发者工具**

   - 使用 Console 面板查看日志和错误
   - 使用 Network 面板检查 API 请求
   - 使用 Sources 面板设置断点调试

3. **使用 VS Code 调试**

   创建 `.vscode/launch.json` 文件：

   ```json
   {
     "version": "0.2.0",
     "configurations": [
       {
         "type": "chrome",
         "request": "launch",
         "name": "vuejs: chrome",
         "url": "http://localhost:8080",
         "webRoot": "${workspaceFolder}/frontend/src",
         "breakOnLoad": true,
         "sourceMapPathOverrides": {
           "webpack:///src/*": "${webRoot}/*"
         }
       }
     ]
   }
   ```

### 数据库调试

1. **SQL 日志**

   ```python
   # 在配置中启用 SQL 日志
   import logging
   from flask_sqlalchemy import get_debug_queries

   # 配置 SQL 日志
   logging.basicConfig()
   logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

   # 在请求后记录查询
   @app.after_request
   def after_request(response):
       for query in get_debug_queries():
           if query.duration >= 0.1:  # 记录执行时间超过 100ms 的查询
               current_app.logger.warning(
                   f"Slow query: {query.statement}\nParameters: {query.parameters}\nDuration: {query.duration}"
               )
       return response
   ```

2. **使用 Flask-DebugToolbar**

   ```bash
   pip install flask-debugtoolbar
   ```

   ```python
   # app/__init__.py
   from flask_debugtoolbar import DebugToolbarExtension

   def create_app(config_class=Config):
       app = Flask(__name__)
       app.config.from_object(config_class)

       # 初始化扩展
       # ...
       
       # 仅在开发环境启用 DebugToolbar
       if app.debug:
           app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
           toolbar = DebugToolbarExtension(app)

       return app
   ```

## 贡献指南

### 代码贡献流程

1. **Fork 项目**

   在 GitHub 上 fork [Forge](https://github.com/your-username/forge) 项目。

2. **克隆项目**

   ```bash
   git clone https://github.com/your-username/forge.git
   cd forge
   ```

3. **创建功能分支**

   ```bash
   git checkout -b feature/your-feature-name
   ```

4. **开发并提交代码**

   ```bash
   git add .
   git commit -m "feat: 添加新功能"
   ```

5. **推送分支**

   ```bash
   git push origin feature/your-feature-name
   ```

6. **创建 Pull Request**

   在 GitHub 上创建一个从您的功能分支到 `develop` 分支的 Pull Request。

### 文档贡献

1. **更新文档**

   如果您修改了功能或添加了新功能，请更新相关文档。

2. **文档格式**

   使用 Markdown 格式编写文档，遵循项目中的文档风格。

3. **提交文档**

   将文档更改与代码更改一起提交，或单独创建一个文档更新 Pull Request。

### 问题报告

1. **报告 Bug**

   如果您发现了 bug，请创建一个 Issue 并包含以下信息：

   - 标题：简明扼要地描述 bug
   - 环境：操作系统、浏览器版本、Node.js 版本等
   - 复现步骤：详细描述如何复现 bug
   - 期望行为：描述您期望发生什么
   - 实际行为：描述实际发生了什么
   - 错误信息：如果有错误信息，请包含完整的错误堆栈
   - 截图：如果适用，请添加截图

2. **请求新功能**

   如果您有新功能的想法，请创建一个 Issue 并包含以下信息：

   - 标题：简明扼要地描述功能
   - 功能描述：详细描述功能的目的和用途
   - 使用场景：描述功能的使用场景
   - 实现建议：如果有，请提供实现建议
   - 替代方案：如果有，请提供替代方案
   - 相关链接：如果有，请提供相关链接

### 代码审查

1. **审查标准**

   - 代码符合项目编码规范
   - 功能实现符合需求
   - 添加了适当的测试
   - 更新了相关文档
   - 没有引入安全漏洞
   - 没有引入性能问题
   - 提交信息符合规范

2. **审查流程**

   - 开发者完成功能开发并提交 Pull Request
   - 指定至少一名审查者进行代码审查
   - 审查者提出修改建议
   - 开发者根据反馈修改代码
   - 审查者确认修改后批准 Pull Request
   - 项目维护者合并代码到 develop 分支

通过以上开发指南，您应该能够了解如何参与 Forge 软件发布管理平台的开发。如果您有任何问题，请参考相关文档或联系开发团队。