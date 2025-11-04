# CORS 修复指南

## 问题描述

前端使用时会遇到 CORS (跨域资源共享) 错误，导致无法正常访问后端 API。这是因为浏览器出于安全考虑，会阻止从一个域名的网页去请求另一个域名的资源，除非服务器明确允许这种跨域请求。

## 修复方案

### 1. 后端修复

#### 1.1 更新 CORS 配置

在 `backend/app/__init__.py` 中更新了 CORS 初始化配置，使其更加灵活和安全：

```python
# 配置CORS以允许前端访问
# 支持从配置中获取允许的源，如果未配置则允许所有源
allowed_origins = app.config.get('CORS_ORIGINS', ["*"])

cors.init_app(app, resources={
    r"/api/*": {
        "origins": allowed_origins,
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": [
            "Content-Type", 
            "Authorization", 
            "X-Requested-With",
            "X-CSRF-Token",
            "X-Content-Type-Options",
            "X-Frame-Options",
            "X-XSS-Protection"
        ],
        "supports_credentials": True,
        "expose_headers": ["Content-Range", "X-Content-Range"]
    }
})
```

#### 1.2 更新配置文件

在 `backend/app/config.py` 中添加了 CORS 相关配置：

```python
# CORS配置
CORS_ORIGINS = os.environ.get('CORS_ORIGINS', "*").split(",") if os.environ.get('CORS_ORIGINS') else ["*"]
```

生产环境配置更严格：

```python
# 生产环境CORS配置
CORS_ORIGINS = os.environ.get('CORS_ORIGINS', "*").split(",") if os.environ.get('CORS_ORIGINS') else ["https://localhost:8080", "https://localhost:3000"]
```

#### 1.3 增强响应处理

在 `backend/app/utils/response.py` 中添加了 CORS 头处理函数和预检请求处理：

```python
def add_cors_headers(response):
    """添加CORS头到响应"""
    # 获取允许的源
    from flask import current_app
    allowed_origins = current_app.config.get('CORS_ORIGINS', ["*"])
    
    # 处理请求源
    origin = request.headers.get('Origin', '')
    
    if "*" in allowed_origins:
        # 如果允许所有源，则设置 *
        response.headers.add('Access-Control-Allow-Origin', '*')
    elif origin in allowed_origins:
        # 如果请求的源在允许列表中，则设置该源
        response.headers.add('Access-Control-Allow-Origin', origin)
    
    # 添加其他CORS头
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
    response.headers.add('Access-Control-Allow-Headers', 
                         'Content-Type, Authorization, X-Requested-With, X-CSRF-Token, X-Content-Type-Options, X-Frame-Options, X-XSS-Protection')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    response.headers.add('Access-Control-Max-Age', '86400')  # 24小时
    response.headers.add('Vary', 'Origin')
```

#### 1.4 更新 OpenAPI 规范

在 `backend/openapi.yaml` 中添加了 CORS 相关的扩展配置：

```yaml
# CORS 配置
x-cors:
  origins: "*"
  methods: ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
  headers: ["Content-Type", "Authorization", "X-Requested-With", "X-CSRF-Token", "X-Content-Type-Options", "X-Frame-Options", "X-XSS-Protection"]
  credentials: true
  maxAge: 86400
  exposedHeaders: ["Content-Range", "X-Content-Range"]
```

#### 1.5 环境变量配置

创建了 `backend/.env.example` 文件，包含 CORS 相关的环境变量：

```bash
# CORS配置
# 开发环境可以设置为 "*", 生产环境应设置具体的域名
CORS_ORIGINS=http://localhost:8080,http://localhost:3000
```

### 2. 前端修复

#### 2.1 更新请求配置

在 `frontend/src/utils/request.js` 中更新了 axios 实例配置：

```javascript
// 创建axios实例
const service = axios.create({
  baseURL: process.env.VUE_APP_API_URL || API_BASE_URL, // API基础URL
  timeout: process.env.VUE_APP_TIMEOUT || TIMEOUT, // 请求超时时间
  // 设置跨域请求是否需要凭证（cookies）
  // 注意：当CORS配置为 "*" 时，withCredentials 必须为 false
  withCredentials: process.env.NODE_ENV === 'production' ? true : false,
  // 设置请求头
  headers: {
    'Cache-Control': 'no-cache',
    Pragma: 'no-cache',
    'Content-Type': 'application/json',
  },
})
```

#### 2.2 确保请求包含必要的头部

在请求拦截器中添加了必要的头部：

```javascript
// 确保所有请求都包含必要的 CORS 头
config.headers['X-Requested-With'] = 'XMLHttpRequest'
```

#### 2.3 更新环境配置

创建了 `frontend/.env.development` 和 `frontend/.env.production` 文件，包含 CORS 相关配置：

开发环境：
```bash
# CORS 配置
VUE_APP_CORS_ORIGIN=http://localhost:8080
VUE_APP_CORS_CREDENTIALS=false
```

生产环境：
```bash
# CORS 配置
VUE_APP_CORS_ORIGIN=https://forge.com
VUE_APP_CORS_CREDENTIALS=true
```

#### 2.4 更新 Vue 配置

在 `frontend/vue.config.js` 中更新了开发服务器配置：

```javascript
devServer: {
  port: 8080,
  proxy: {
    '/api': {
      target: 'http://localhost:5000',
      changeOrigin: true,
      secure: false,
      pathRewrite: {
        '^/api': '/api',
      },
      onProxyReq: function(proxyReq, req, res) {
        // 添加必要的请求头
        proxyReq.setHeader('X-Requested-With', 'XMLHttpRequest');
      },
      onError: function(err, req, res) {
        // 代理错误处理
        console.error('代理错误:', err);
      }
    },
  },
  // 添加 CORS 配置
  headers: {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Requested-With',
  }
},
```

### 3. 测试方案

#### 3.1 自动化测试

创建了两个测试脚本：
- `scripts/test-cors.sh` - Linux/Mac 系统
- `scripts/test-cors.bat` - Windows 系统

这些脚本会自动测试以下内容：
1. 后端服务状态
2. 前端服务状态
3. CORS 预检请求 (OPTIONS)
4. 简单的跨域 GET 请求
5. 带有凭证的跨域请求

#### 3.2 手动测试

1. 启动后端服务：
   ```bash
   cd backend
   python run.py
   ```

2. 启动前端服务：
   ```bash
   cd frontend
   npm run serve
   ```

3. 运行测试脚本：
   ```bash
   # Linux/Mac
   ./scripts/test-cors.sh
   
   # Windows
   scripts\test-cors.bat
   ```

4. 浏览器测试：
   - 打开浏览器访问 http://localhost:8080
   - 打开浏览器开发者工具 (F12)
   - 尝试登录或其他需要 API 交互的操作
   - 检查 Network 标签中是否有 CORS 错误
   - 检查 Console 标签中是否有跨域相关错误

## 常见问题与解决方案

### 1. 预检请求失败

问题：OPTIONS 请求返回 404 或 405 错误。

解决方案：
- 确保后端正确处理 OPTIONS 请求
- 检查 CORS 中间件是否正确配置
- 确认请求头是否在允许列表中

### 2. 凭证问题

问题：前端无法发送带有凭证的请求。

解决方案：
- 检查后端 CORS 配置中的 `supports_credentials` 是否为 true
- 检查前端 `withCredentials` 设置是否与后端匹配
- 如果后端允许所有源 (*)，则前端不能设置 `withCredentials: true`

### 3. 环境变量不生效

问题：环境变量配置后不生效。

解决方案：
- 重启后端服务
- 检查环境变量文件名是否正确
- 确认环境变量语法是否正确

### 4. 浏览器缓存

问题：修改配置后仍然报错。

解决方案：
- 清除浏览器缓存
- 禁用浏览器缓存（开发者工具中）
- 尝试无痕模式

## 安全注意事项

1. 生产环境应设置具体的允许源，而不是使用 "*"
2. 定期检查和更新 CORS 配置
3. 注意敏感信息不要暴露在 CORS 头中
4. 结合其他安全措施，如 CSRF 防护

## 总结

通过以上修复，前后端之间的 CORS 问题应该已经解决。修复的关键点包括：

1. 后端正确配置 CORS 中间件和响应头
2. 前端正确配置请求头和凭证设置
3. 环境变量正确配置
4. 提供了完整的测试方案验证修复效果

如果仍有问题，请检查日志文件和浏览器开发者工具中的错误信息，以便进一步排查。