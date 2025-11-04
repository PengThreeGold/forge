import * as authApi from '@/api/auth'

const state = {
  token: localStorage.getItem('token') || null,
  refreshToken: localStorage.getItem('refreshToken') || null,
  user: JSON.parse(localStorage.getItem('user')) || null,
}

const getters = {
  isAuthenticated: state => !!state.token,
  currentUser: state => state.user,
  token: state => state.token,
  refreshToken: state => state.refreshToken,
  userRole: state => (state.user ? state.user.role : null),
}

const mutations = {
  SET_TOKEN(state, token) {
    state.token = token
    if (token) {
      localStorage.setItem('token', token)
    } else {
      localStorage.removeItem('token')
    }
  },

  SET_REFRESH_TOKEN(state, refreshToken) {
    state.refreshToken = refreshToken
    if (refreshToken) {
      localStorage.setItem('refreshToken', refreshToken)
    } else {
      localStorage.removeItem('refreshToken')
    }
  },

  SET_USER(state, user) {
    state.user = user
    if (user) {
      localStorage.setItem('user', JSON.stringify(user))
    } else {
      localStorage.removeItem('user')
    }
  },

  CLEAR_AUTH(state) {
    state.token = null
    state.refreshToken = null
    state.user = null
    localStorage.removeItem('token')
    localStorage.removeItem('refreshToken')
    localStorage.removeItem('user')
  },
}

const actions = {
  // 登录
  async login({ commit, dispatch }, credentials) {
    try {
      const response = await authApi.login(credentials)

      // 保存token和用户信息，处理后端返回的结构化响应
      if (response.success && response.data) {
        commit('SET_TOKEN', response.data.access_token)
        commit('SET_REFRESH_TOKEN', response.data.refresh_token)
        commit('SET_USER', response.data.user)
      } else {
        throw new Error(response.message || '登录失败')
      }

      return response
    } catch (error) {
      dispatch('setError', error.response?.data?.message || error.message || '登录失败', {
        root: true,
      })
      throw error
    }
  },

  // 登出
  async logout({ commit, dispatch }) {
    try {
      // 如果有token，调用登出API
      if (state.token) {
        await authApi.logout()
      }
    } catch (error) {
      console.error('登出API调用失败:', error)
    } finally {
      // 无论API调用成功与否，都清除本地认证信息
      commit('CLEAR_AUTH')
      dispatch('setError', null, { root: true })
    }
  },

  // 刷新令牌
  async refreshToken({ commit, dispatch }) {
    try {
      const response = await authApi.refreshToken()

      // 更新token，处理后端返回的结构化响应
      if (response.success && response.data) {
        commit('SET_TOKEN', response.data.access_token)
        return response.data.access_token
      } else {
        throw new Error(response.message || '令牌刷新失败')
      }
    } catch (error) {
      // 刷新失败，清除认证信息并跳转到登录页
      dispatch('logout')
      dispatch(
        'setError',
        error.response?.data?.message || error.message || '会话已过期，请重新登录',
        {
          root: true,
        }
      )
      throw error
    }
  },

  // 获取用户信息
  async getUserProfile({ commit, dispatch }) {
    try {
      const response = await authApi.getProfile()

      // 更新用户信息，处理后端返回的结构化响应
      if (response.success && response.data) {
        commit('SET_USER', response.data)
      } else {
        throw new Error(response.message || '获取用户信息失败')
      }

      return response
    } catch (error) {
      dispatch('setError', error.response?.data?.message || error.message || '获取用户信息失败', {
        root: true,
      })

      // 如果是401错误，可能是token过期，尝试刷新
      if (error.response && error.response.status === 401) {
        // 避免无限循环的token刷新
        if (!this.refreshing) {
          this.refreshing = true
          try {
            await dispatch('refreshToken')
            this.refreshing = false
            return await dispatch('getUserProfile')
          } catch (refreshError) {
            this.refreshing = false
            throw refreshError
          }
        } else {
          throw error
        }
      }

      throw error
    }
  },

  // 修改密码
  async changePassword({ dispatch }, passwords) {
    try {
      const response = await authApi.changePassword(passwords)
      return response.data
    } catch (error) {
      dispatch('setError', error.response?.data?.message || '修改密码失败', { root: true })
      throw error
    }
  },

  // 初始化管理员账户
  async initAdmin({ dispatch }, adminData) {
    try {
      const response = await authApi.initAdmin(adminData)

      // 处理后端返回的结构化响应
      if (response.success && response.data) {
        return response.data
      } else {
        throw new Error(response.message || '初始化管理员账户失败')
      }
    } catch (error) {
      dispatch(
        'setError',
        error.response?.data?.message || error.message || '初始化管理员账户失败',
        {
          root: true,
        }
      )
      throw error
    }
  },
}

export default {
  namespaced: true,
  state,
  getters,
  mutations,
  actions,
}
