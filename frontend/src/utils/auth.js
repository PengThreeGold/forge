import store from '@/store'

// 检查用户是否已认证
export function isAuthenticated() {
  return store.getters.isAuthenticated
}

// 获取当前用户
export function getCurrentUser() {
  return store.getters.currentUser
}

// 获取用户token
export function getToken() {
  return store.getters.token
}

// 检查用户是否有特定角色
export function hasRole(role) {
  const user = getCurrentUser()
  return user && user.role === role
}

// 检查用户是否为管理员
export function isAdmin() {
  return hasRole('admin')
}

// 保存认证信息到本地存储
export function saveAuthInfo(token, refreshToken, user) {
  localStorage.setItem('token', token)
  localStorage.setItem('refreshToken', refreshToken)
  localStorage.setItem('user', JSON.stringify(user))
}

// 从本地存储清除认证信息
export function clearAuthInfo() {
  localStorage.removeItem('token')
  localStorage.removeItem('refreshToken')
  localStorage.removeItem('user')
}

// 检查token是否即将过期（提前5分钟）
export function isTokenExpiringSoon() {
  const token = getToken()
  if (!token) return true

  try {
    // 解析JWT token获取过期时间
    const base64Url = token.split('.')[1]
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/')
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split('')
        .map(function (c) {
          return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2)
        })
        .join('')
    )

    const payload = JSON.parse(jsonPayload)
    const expirationTime = payload.exp * 1000 // 转换为毫秒
    const currentTime = new Date().getTime()
    const fiveMinutes = 5 * 60 * 1000

    return expirationTime - currentTime < fiveMinutes
  } catch (e) {
    console.error('解析token失败:', e)
    return true
  }
}

// 处理401错误（未授权）
export function handleUnauthorizedError() {
  // 清除本地存储的认证信息
  clearAuthInfo()

  // 跳转到登录页
  if (window.location.pathname !== '/login') {
    window.location.href = `/login?redirect=${encodeURIComponent(window.location.pathname + window.location.search)}`
  }
}

// 添加请求拦截器，自动处理token刷新
export function setupAxiosInterceptors(axios) {
  axios.interceptors.request.use(
    config => {
      // 添加token到请求头
      const token = getToken()
      if (token) {
        config.headers.Authorization = `Bearer ${token}`
      }
      return config
    },
    error => {
      return Promise.reject(error)
    }
  )

  axios.interceptors.response.use(
    response => {
      return response
    },
    async error => {
      const originalRequest = error.config

      // 如果是401错误且不是刷新token的请求
      if (error.response && error.response.status === 401 && !originalRequest._retry) {
        originalRequest._retry = true

        try {
          // 尝试刷新token
          const response = await store.dispatch('auth/refreshToken')

          // 更新请求头中的token
          originalRequest.headers.Authorization = `Bearer ${response}`

          // 重新发送原始请求
          return axios(originalRequest)
        } catch (refreshError) {
          // 刷新token失败，跳转到登录页
          handleUnauthorizedError()
          return Promise.reject(refreshError)
        }
      }

      return Promise.reject(error)
    }
  )
}
