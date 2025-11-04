import axios from 'axios'
import store from '@/store'
import { ElMessage, ElMessageBox } from 'element-plus'
import { API_BASE_URL, TIMEOUT } from '@/api/config'

// 创建axios实例
const service = axios.create({
  baseURL: process.env.VUE_APP_API_URL || API_BASE_URL, // API基础URL
  timeout: process.env.VUE_APP_TIMEOUT || TIMEOUT, // 请求超时时间
  // 设置跨域请求是否需要凭证（cookies）
  withCredentials: true,
  // 设置请求头
  headers: {
    'Cache-Control': 'no-cache',
    Pragma: 'no-cache',
  },
})

// 请求拦截器
service.interceptors.request.use(
  config => {
    // 在发送请求之前做些什么

    // 如果是刷新令牌的请求，使用刷新令牌
    if (config.url === '/api/auth/refresh') {
      const refreshToken = store.getters.refreshToken
      if (refreshToken) {
        config.headers['Authorization'] = `Bearer ${refreshToken}`
      }
    } else {
      // 其他请求使用访问令牌
      const token = store.getters.token
      if (token) {
        config.headers['Authorization'] = `Bearer ${token}`
      }
    }

    // 如果是HTTPS请求，添加安全相关请求头
    if (window.location.protocol === 'https:') {
      config.headers['X-Content-Type-Options'] = 'nosniff'
      config.headers['X-Frame-Options'] = 'DENY'
      config.headers['X-XSS-Protection'] = '1; mode=block'
    }

    // 设置Loading状态
    if (config.showLoading !== false) {
      store.dispatch('setLoading', true)
    }

    return config
  },
  error => {
    // 对请求错误做些什么
    console.error('请求错误:', error)
    store.dispatch('setLoading', false)
    return Promise.reject(error)
  }
)

// 响应拦截器
service.interceptors.response.use(
  response => {
    // 对响应数据做点什么

    // 关闭Loading状态
    if (response.config.showLoading !== false) {
      store.dispatch('setLoading', false)
    }

    // 如果是二进制数据（文件下载），直接返回
    if (response.config.responseType === 'blob') {
      return response
    }

    // 获取响应数据
    const res = response.data

    // 如果返回的是二进制数据（文件下载），直接返回
    if (
      response.headers['content-type'] &&
      response.headers['content-type'].includes('application/octet-stream')
    ) {
      return response
    }

    // 根据自定义状态码处理响应
    if (res.success !== undefined) {
      if (res.success) {
        return res
      } else {
        // 处理业务错误
        ElMessage({
          message: res.message || '操作失败',
          type: 'error',
          duration: 5 * 1000,
        })
        return Promise.reject(new Error(res.message || '操作失败'))
      }
    } else {
      // 如果没有success字段，直接返回响应数据
      return res
    }
  },
  error => {
    // 对响应错误做点什么

    // 关闭Loading状态
    if (error.config && error.config.showLoading !== false) {
      store.dispatch('setLoading', false)
    }

    // 获取错误响应
    const response = error.response

    // 处理不同的HTTP状态码
    if (response) {
      switch (response.status) {
        case 400:
          ElMessage({
            message: response.data?.message || '请求参数错误',
            type: 'error',
            duration: 5 * 1000,
          })
          break
        case 401:
          // 401错误：未授权，可能是token过期或无效
          ElMessageBox.confirm('登录状态已过期，请重新登录', '系统提示', {
            confirmButtonText: '重新登录',
            cancelButtonText: '取消',
            type: 'warning',
          }).then(() => {
            // 清除token并跳转到登录页
            store.dispatch('auth/logout').then(() => {
              location.reload()
            })
          })
          break
        case 403:
          ElMessage({
            message: response.data?.message || '权限不足，无法访问',
            type: 'error',
            duration: 5 * 1000,
          })
          break
        case 404:
          ElMessage({
            message: response.data?.message || '请求的资源不存在',
            type: 'error',
            duration: 5 * 1000,
          })
          break
        case 500:
          ElMessage({
            message: response.data?.message || '服务器内部错误',
            type: 'error',
            duration: 5 * 1000,
          })
          break
        default:
          ElMessage({
            message: response.data?.message || `未知错误: ${response.status}`,
            type: 'error',
            duration: 5 * 1000,
          })
      }
    } else {
      // 网络错误或请求超时
      ElMessage({
        message: error.message || '网络错误，请检查您的网络连接',
        type: 'error',
        duration: 5 * 1000,
      })
    }

    return Promise.reject(error)
  }
)

// 封装GET请求
export function get(url, params = {}, config = {}) {
  return service({
    url,
    method: 'get',
    params,
    ...config,
  })
}

// 封装POST请求
export function post(url, data = {}, config = {}) {
  return service({
    url,
    method: 'post',
    data,
    ...config,
  })
}

// 封装PUT请求
export function put(url, data = {}, config = {}) {
  return service({
    url,
    method: 'put',
    data,
    ...config,
  })
}

// 封装DELETE请求
export function del(url, config = {}) {
  return service({
    url,
    method: 'delete',
    ...config,
  })
}

// 封装文件上传请求
export function upload(url, file, onUploadProgress, config = {}) {
  const formData = new FormData()
  formData.append('file', file)

  return service({
    url,
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data',
    },
    onUploadProgress,
    ...config,
  })
}

// 封装文件下载请求
export function download(url, filename, config = {}) {
  return service({
    url,
    method: 'get',
    responseType: 'blob',
    ...config,
  }).then(response => {
    // 从响应头获取文件名
    const contentDisposition = response.headers['content-disposition']
    let downloadFilename = filename || 'download'

    if (contentDisposition) {
      const filenameRegex = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/
      const matches = filenameRegex.exec(contentDisposition)
      if (matches != null && matches[1]) {
        downloadFilename = matches[1].replace(/['"]/g, '')
      }
    }

    // 创建下载链接
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', downloadFilename)
    document.body.appendChild(link)
    link.click()

    // 清理
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)

    return response
  })
}

export default service
