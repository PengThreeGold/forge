import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/utils/request'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || '')
  const refreshToken = ref(localStorage.getItem('refreshToken') || '')
  const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))

  const isAuthenticated = computed(() => !!token.value)
  const isAdmin = computed(() => user.value?.role === 'admin')

  async function login(username, password) {
    try {
      const res = await api.post('/auth/login', { username, password })
      
      if (res.success) {
        token.value = res.data.access_token
        refreshToken.value = res.data.refresh_token
        user.value = res.data.user
        
        localStorage.setItem('token', token.value)
        localStorage.setItem('refreshToken', refreshToken.value)
        localStorage.setItem('user', JSON.stringify(user.value))
        
        return true
      }
      return false
    } catch (error) {
      return false
    }
  }

  function logout() {
    token.value = ''
    refreshToken.value = ''
    user.value = null
    
    localStorage.removeItem('token')
    localStorage.removeItem('refreshToken')
    localStorage.removeItem('user')
  }

  async function refreshAccessToken() {
    try {
      const res = await api.post('/auth/refresh', { 
        refresh_token: refreshToken.value 
      })
      
      if (res.success) {
        token.value = res.data.access_token
        localStorage.setItem('token', token.value)
        return true
      }
      return false
    } catch (error) {
      logout()
      return false
    }
  }

  async function fetchProfile() {
    try {
      const res = await api.get('/auth/profile')
      if (res.success) {
        user.value = res.data
        localStorage.setItem('user', JSON.stringify(user.value))
      }
    } catch (error) {
      console.error('获取用户信息失败:', error)
    }
  }

  return {
    token,
    user,
    isAuthenticated,
    isAdmin,
    login,
    logout,
    refreshAccessToken,
    fetchProfile
  }
})
