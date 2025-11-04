import request from '@/utils/request'

// 用户登录
export function login(data) {
  return request({
    url: '/api/auth/login',
    method: 'post',
    data,
  })
}

// 用户登出
export function logout() {
  return request({
    url: '/api/auth/logout',
    method: 'post',
  })
}

// 刷新令牌
export function refreshToken() {
  return request({
    url: '/api/auth/refresh',
    method: 'post',
  })
}

// 获取用户信息
export function getProfile() {
  return request({
    url: '/api/auth/profile',
    method: 'get',
  })
}

// 修改密码
export function changePassword(data) {
  return request({
    url: '/api/auth/change-password',
    method: 'post',
    data,
  })
}

// 初始化管理员账户
export function initAdmin(data) {
  return request({
    url: '/api/auth/init-admin',
    method: 'post',
    data,
  })
}

// 检查是否需要初始化管理员（安全的GET，不会创建用户）
export function checkInitAdmin() {
  return request({
    url: '/api/auth/init-admin',
    method: 'get',
  })
}
