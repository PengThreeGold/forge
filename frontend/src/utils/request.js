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

// 基础 API 实例，用于普通请求
const api = axios.create({
  baseURL: '/api',
  timeout: 30000 // 30秒超时
})

// 为文件上传创建一个专用的 axios 实例，使用更长的超时时间
const uploadApi = axios.create({
  baseURL: '/api',
  timeout: 300000 // 5分钟超时，适合大文件上传
})

// 为基础 API 添加请求拦截器
api.interceptors.request.use(
  config => {
    // 从 localStorage 获取 token
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 为基础 API 添加响应拦截器
api.interceptors.response.use(
  response => {
    const data = response.data
    
    // 处理 Blob 类型响应（文件下载）
    if (response.config.responseType === 'blob') {
      return response
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
    if (import.meta.env.DEV) {
      console.error('[Response Error]', error)
    }

    if (error.response) {
      const { status, data } = error.response
      
      if (status === 401) {
        const authStore = useAuthStore()
        authStore.logout()
        router.push({ name: 'Login' })
        ElMessage.error('登录已过期，请重新登录')
      } else if (status === 403) {
        ElMessage.error(data?.detail || '权限不足')
      } else if (status === 404) {
        ElMessage.error(data?.detail || '请求的资源不存在')
      } else if (status === 422) {
        // 处理验证错误
        if (data?.detail && Array.isArray(data.detail)) {
          const messages = data.detail.map(err => err.msg || err.message).join(', ')
          ElMessage.error('参数错误: ' + messages)
        } else {
          ElMessage.error(data?.detail || '参数验证失败')
        }
      } else if (status === 500) {
        ElMessage.error(data?.detail || '服务器错误，请稍后重试')
      } else {
        ElMessage.error(data?.detail || data?.message || '请求失败')
      }
    } else if (error.request) {
      ElMessage.error('网络错误，请检查网络连接')
    } else {
      ElMessage.error('请求配置错误')
    }
    return Promise.reject(error)
  }
)

// 为 uploadApi 添加相同的请求拦截器
uploadApi.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 为 uploadApi 添加相同的响应拦截器
uploadApi.interceptors.response.use(
  response => {
    const data = response.data
    
    // 处理标准响应格式
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
    if (import.meta.env.DEV) {
      console.error('[Upload Error]', error)
    }

    if (error.response) {
      const { status, data } = error.response
      
      if (status === 401) {
        const authStore = useAuthStore()
        authStore.logout()
        router.push({ name: 'Login' })
        ElMessage.error('登录已过期，请重新登录')
      } else if (status === 403) {
        ElMessage.error(data?.detail || '权限不足')
      } else if (status === 404) {
        ElMessage.error(data?.detail || '请求的资源不存在')
      } else if (status === 422) {
        // 处理验证错误
        if (data?.detail && Array.isArray(data.detail)) {
          const messages = data.detail.map(err => err.msg || err.message).join(', ')
          ElMessage.error('参数错误: ' + messages)
        } else {
          ElMessage.error(data?.detail || '参数验证失败')
        }
      } else if (status === 500) {
        ElMessage.error(data?.detail || '服务器错误，请稍后重试')
      } else {
        ElMessage.error(data?.detail || data?.message || '请求失败')
      }
    } else if (error.request) {
      ElMessage.error('网络错误，请检查网络连接')
    } else {
      ElMessage.error('请求配置错误')
    }
    return Promise.reject(error)
  }
)

export default api
export { uploadApi }
