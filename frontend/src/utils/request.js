import axios from 'axios'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import router from '@/router'

// 创建请求队列管理器
class RequestQueue {
  constructor() {
    this.queue = new Map()
    this.maxConcurrent = 5
    this.activeRequests = 0
  }

  add(key, request) {
    if (this.activeRequests >= this.maxConcurrent) {
      return new Promise((resolve) => {
        this.queue.set(key, { request, resolve })
      })
    }
    
    this.activeRequests++
    return request().finally(() => {
      this.activeRequests--
      this.processQueue()
    })
  }

  processQueue() {
    if (this.queue.size > 0 && this.activeRequests < this.maxConcurrent) {
      const [key, { request, resolve }] = this.queue.entries().next().value
      this.queue.delete(key)
      
      this.activeRequests++
      request().then(resolve).finally(() => {
        this.activeRequests--
        this.processQueue()
      })
    }
  }
}

const requestQueue = new RequestQueue()

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
  // 启用请求缓存
  headers: {
    'Cache-Control': 'no-cache'
  }
})

// 简单的内存缓存
const cache = new Map()
const CACHE_TTL = 5 * 60 * 1000 // 5分钟

function getCacheKey(config) {
  return `${config.method}:${config.url}:${JSON.stringify(config.params || {})}`
}

function isCacheable(config) {
  return config.method === 'get' && !config.url.includes('stats') && !config.url.includes('download')
}

// 请求拦截器
api.interceptors.request.use(
  config => {
    // 检查缓存
    if (isCacheable(config)) {
      const cacheKey = getCacheKey(config)
      const cached = cache.get(cacheKey)
      if (cached && Date.now() - cached.timestamp < CACHE_TTL) {
        config.adapter = () => Promise.resolve(cached.data)
        return config
      }
    }

    // 从 localStorage 获取 token
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    
    // 只在开发环境打印调试日志
    if (import.meta.env.DEV) {
      console.log(`[Request] ${config.method?.toUpperCase()} ${config.url}`)
    }
    
    return config
  },
  error => {
    if (import.meta.env.DEV) {
      console.error('[Request Error]', error)
    }
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  response => {
    const data = response.data

    // 缓存响应数据
    if (isCacheable(response.config)) {
      const cacheKey = getCacheKey(response.config)
      cache.set(cacheKey, {
        data: response,
        timestamp: Date.now()
      })
    }
    
    // 处理标准响应格式（优先检查）
    if (data && typeof data.success === 'boolean') {
      return data
    }
    
    // 处理分页响应格式
    if (data && (data.items !== undefined || data.total !== undefined || data.page !== undefined)) {
      return {
        success: true,
        message: '请求成功',
        data: data
      }
    }

    // 处理其他响应格式
    return {
      success: true,
      message: '请求成功',
      data: data ?? null
    }
  },
  async error => {
    if (error.response) {
      const { status, data } = error.response
      
      if (status === 401) {
        const authStore = useAuthStore()
        authStore.logout()
        router.push({ name: 'Login' })
        ElMessage.error('登录已过期，请重新登录')
      } else if (status === 403) {
        ElMessage.error('权限不足')
      } else if (status === 404) {
        ElMessage.error('请求的资源不存在')
      } else if (status === 500) {
        ElMessage.error('服务器错误，请稍后重试')
      } else {
        ElMessage.error(data?.message || '请求失败')
      }
    } else {
      ElMessage.error('网络错误，请检查网络连接')
    }
    return Promise.reject(error)
  }
)

// 清理过期缓存
setInterval(() => {
  const now = Date.now()
  for (const [key, value] of cache.entries()) {
    if (now - value.timestamp > CACHE_TTL) {
      cache.delete(key)
    }
  }
}, 60000) // 每分钟清理一次

export default api
