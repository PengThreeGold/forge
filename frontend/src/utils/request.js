import axios from 'axios'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import router from '@/router'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000
})

// 请求拦截器
api.interceptors.request.use(
  config => {
    // 从 localStorage 直接获取 token，避免 Pinia 初始化时序问题
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    
    // 添加调试日志
    console.log(`[Request] ${config.method?.toUpperCase()} ${config.url}`)
    console.log(`[Request] Headers:`, config.headers)
    
    return config
  },
  error => {
    console.error('[Request Error]', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  response => {
    const data = response.data

    // 处理分页响应格式
    if (data && (data.items !== undefined || data.total !== undefined || data.page !== undefined)) {
      return {
        success: true,
        message: '请求成功',
        data: data
      }
    }
    
    // 处理标准响应格式
    if (data && typeof data.success === 'boolean') {
      return data
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

export default api
