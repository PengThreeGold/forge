import * as statisticsApi from '@/api/statistics'

const state = {
  overview: null,
  downloads: [],
  downloadsTotal: 0,
  downloadsPage: 1,
  downloadsPerPage: 20,
  timeline: [],
  spaceStatistics: null,
  webhooks: [],
  webhooksTotal: 0,
  webhooksPage: 1,
  webhooksPerPage: 20,
  loading: false,
  error: null
}

const getters = {
  overview: state => state.overview,
  downloads: state => state.downloads,
  downloadsTotal: state => state.downloadsTotal,
  downloadsPage: state => state.downloadsPage,
  downloadsPerPage: state => state.downloadsPerPage,
  timeline: state => state.timeline,
  spaceStatistics: state => state.spaceStatistics,
  webhooks: state => state.webhooks,
  webhooksTotal: state => state.webhooksTotal,
  webhooksPage: state => state.webhooksPage,
  webhooksPerPage: state => state.webhooksPerPage,
  loading: state => state.loading,
  error: state => state.error,
  
  // 获取下载分页信息
  downloadsPagination: state => ({
    total: state.downloadsTotal,
    page: state.downloadsPage,
    perPage: state.downloadsPerPage,
    pages: Math.ceil(state.downloadsTotal / state.downloadsPerPage)
  }),
  
  // 获取Webhook分页信息
  webhooksPagination: state => ({
    total: state.webhooksTotal,
    page: state.webhooksPage,
    perPage: state.webhooksPerPage,
    pages: Math.ceil(state.webhooksTotal / state.webhooksPerPage)
  })
}

const mutations = {
  SET_OVERVIEW(state, overview) {
    state.overview = overview
  },
  
  SET_DOWNLOADS(state, { downloads, total, page, perPage }) {
    state.downloads = downloads
    state.downloadsTotal = total
    state.downloadsPage = page
    state.downloadsPerPage = perPage
  },
  
  SET_TIMELINE(state, timeline) {
    state.timeline = timeline
  },
  
  SET_SPACE_STATISTICS(state, statistics) {
    state.spaceStatistics = statistics
  },
  
  SET_WEBHOOKS(state, { webhooks, total, page, perPage }) {
    state.webhooks = webhooks
    state.webhooksTotal = total
    state.webhooksPage = page
    state.webhooksPerPage = perPage
  },
  
  SET_LOADING(state, loading) {
    state.loading = loading
  },
  
  SET_ERROR(state, error) {
    state.error = error
  },
  
  CLEAR_ERROR(state) {
    state.error = null
  },
  
  CLEAR_STATE(state) {
    state.overview = null
    state.downloads = []
    state.downloadsTotal = 0
    state.downloadsPage = 1
    state.timeline = []
    state.spaceStatistics = null
    state.webhooks = []
    state.webhooksTotal = 0
    state.webhooksPage = 1
    state.error = null
  }
}

const actions = {
  // 获取统计概览
  async getOverview({ commit }) {
    try {
      commit('SET_LOADING', true)
      commit('CLEAR_ERROR')
      
      const response = await statisticsApi.getOverview()
      commit('SET_OVERVIEW', response.data)
      
      commit('SET_LOADING', false)
      return response
    } catch (error) {
      commit('SET_LOADING', false)
      commit('SET_ERROR', error.response?.data?.message || '获取统计概览失败')
      throw error
    }
  },
  
  // 获取下载统计
  async getDownloads({ commit }, { page = 1, perPage = 20, spaceId, versionId, startDate, endDate } = {}) {
    try {
      commit('SET_LOADING', true)
      commit('CLEAR_ERROR')
      
      const response = await statisticsApi.getDownloads({
        page,
        per_page: perPage,
        space_id: spaceId,
        version_id: versionId,
        start_date: startDate,
        end_date: endDate
      })
      
      commit('SET_DOWNLOADS', {
        downloads: response.data.downloads,
        total: response.data.total,
        page: response.data.current_page,
        perPage: response.data.per_page
      })
      
      commit('SET_LOADING', false)
      return response
    } catch (error) {
      commit('SET_LOADING', false)
      commit('SET_ERROR', error.response?.data?.message || '获取下载统计失败')
      throw error
    }
  },
  
  // 获取下载时间线
  async getDownloadsTimeline({ commit }, { days = 30, spaceId } = {}) {
    try {
      commit('SET_LOADING', true)
      commit('CLEAR_ERROR')
      
      const response = await statisticsApi.getDownloadsTimeline({
        days,
        space_id: spaceId
      })
      
      commit('SET_TIMELINE', response.data.timeline)
      
      commit('SET_LOADING', false)
      return response
    } catch (error) {
      commit('SET_LOADING', false)
      commit('SET_ERROR', error.response?.data?.message || '获取下载时间线失败')
      throw error
    }
  },
  
  // 获取软件空间统计
  async getSpaceStatistics({ commit }, spaceId) {
    try {
      commit('SET_LOADING', true)
      commit('CLEAR_ERROR')
      
      const response = await statisticsApi.getSpaceStatistics(spaceId)
      commit('SET_SPACE_STATISTICS', response.data)
      
      commit('SET_LOADING', false)
      return response
    } catch (error) {
      commit('SET_LOADING', false)
      commit('SET_ERROR', error.response?.data?.message || '获取软件空间统计失败')
      throw error
    }
  },
  
  // 获取Webhook日志
  async getWebhooks({ commit }, { page = 1, perPage = 20, spaceId } = {}) {
    try {
      commit('SET_LOADING', true)
      commit('CLEAR_ERROR')
      
      const response = await statisticsApi.getWebhooks({
        page,
        per_page: perPage,
        space_id: spaceId
      })
      
      commit('SET_WEBHOOKS', {
        webhooks: response.data.webhooks,
        total: response.data.total,
        page: response.data.current_page,
        perPage: response.data.per_page
      })
      
      commit('SET_LOADING', false)
      return response
    } catch (error) {
      commit('SET_LOADING', false)
      commit('SET_ERROR', error.response?.data?.message || '获取Webhook日志失败')
      throw error
    }
  },
  
  // 获取Webhook日志详情
  async getWebhook({ commit }, logId) {
    try {
      commit('SET_LOADING', true)
      commit('CLEAR_ERROR')
      
      const response = await statisticsApi.getWebhook(logId)
      
      commit('SET_LOADING', false)
      return response
    } catch (error) {
      commit('SET_LOADING', false)
      commit('SET_ERROR', error.response?.data?.message || '获取Webhook日志详情失败')
      throw error
    }
  },
  
  // 重试Webhook
  async retryWebhook({ commit }, logId) {
    try {
      commit('SET_LOADING', true)
      commit('CLEAR_ERROR')
      
      const response = await statisticsApi.retryWebhook(logId)
      
      commit('SET_LOADING', false)
      return response
    } catch (error) {
      commit('SET_LOADING', false)
      commit('SET_ERROR', error.response?.data?.message || '重试Webhook失败')
      throw error
    }
  },
  
  // 测试Webhook
  async testWebhook({ commit }, spaceId) {
    try {
      commit('SET_LOADING', true)
      commit('CLEAR_ERROR')
      
      const response = await statisticsApi.testWebhook(spaceId)
      
      commit('SET_LOADING', false)
      return response
    } catch (error) {
      commit('SET_LOADING', false)
      commit('SET_ERROR', error.response?.data?.message || '测试Webhook失败')
      throw error
    }
  },
  
  // 清空状态
  clearState({ commit }) {
    commit('CLEAR_STATE')
  }
}

export default {
  namespaced: true,
  state,
  getters,
  mutations,
  actions
}