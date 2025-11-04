import { createStore } from 'vuex'
import auth from './modules/auth'
import software from './modules/software'
import statistics from './modules/statistics'

export default createStore({
  state: {
    // 全局状态
    loading: false,
    error: null,
    sidebarCollapsed: false,
    theme: 'light', // light 或 dark
  },

  getters: {
    // 全局getters
    loading: state => state.loading,
    error: state => state.error,
    sidebarCollapsed: state => state.sidebarCollapsed,
    theme: state => state.theme,
    isAuthenticated: (state, getters) => getters['auth/isAuthenticated'],
    currentUser: (state, getters) => getters['auth/currentUser'],
    token: (state, getters) => getters['auth/token'],
  },

  mutations: {
    // 全局mutations
    SET_LOADING(state, loading) {
      state.loading = loading
    },

    SET_ERROR(state, error) {
      state.error = error
    },

    CLEAR_ERROR(state) {
      state.error = null
    },

    TOGGLE_SIDEBAR(state) {
      state.sidebarCollapsed = !state.sidebarCollapsed
    },

    SET_THEME(state, theme) {
      state.theme = theme
    },
  },

  actions: {
    // 全局actions
    setLoading({ commit }, loading) {
      commit('SET_LOADING', loading)
    },

    setError({ commit }, error) {
      commit('SET_ERROR', error)
    },

    clearError({ commit }) {
      commit('CLEAR_ERROR')
    },

    toggleSidebar({ commit }) {
      commit('TOGGLE_SIDEBAR')
    },

    setTheme({ commit }, theme) {
      commit('SET_THEME', theme)
      // 应用主题到body
      if (theme === 'dark') {
        document.body.classList.add('dark-theme')
      } else {
        document.body.classList.remove('dark-theme')
      }
    },

    // 初始化应用
    async initApp({ dispatch, commit }) {
      try {
        // 设置加载状态
        dispatch('setLoading', true)

        // 检查本地存储的token
        const token = localStorage.getItem('token')
        if (token) {
          // 设置token到auth模块
          commit('auth/SET_TOKEN', token, { root: true })

          // 获取用户信息
          await dispatch('auth/getUserProfile', null, { root: true })
        }

        // 设置主题
        const savedTheme = localStorage.getItem('theme') || 'light'
        dispatch('setTheme', savedTheme)

        // 设置侧边栏状态
        const sidebarCollapsed = localStorage.getItem('sidebarCollapsed') === 'true'
        if (sidebarCollapsed) {
          commit('TOGGLE_SIDEBAR')
        }

        dispatch('setLoading', false)
      } catch (error) {
        dispatch('setLoading', false)
        dispatch('setError', error.message || '应用初始化失败')

        // 如果是认证错误，清除token并重定向到登录页
        if (error.response && error.response.status === 401) {
          dispatch('auth/logout', null, { root: true })
        }
      }
    },
  },

  modules: {
    auth,
    software,
    statistics,
  },
})
