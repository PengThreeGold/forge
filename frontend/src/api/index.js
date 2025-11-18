import api from '@/utils/request'

export default {
  // 认证相关
  login(data) {
    return api.post('/auth/login', data)
  },

  refreshToken(data) {
    return api.post('/auth/refresh', data)
  },

  getProfile() {
    return api.get('/auth/profile')
  },

  changePassword(data) {
    return api.put('/auth/admin/password', data)
  },

  initAdmin(data) {
    return api.post('/auth/admin/init', data)
  },

  // 公共API
  getPublicSpaces(params) {
    return api.get('/public/spaces', { params })
  },
  
  getPublicSpace(id) {
    return api.get(`/public/spaces/${id}`)
  },
  
  getPublicVersions(spaceId, params) {
    return api.get(`/public/spaces/${spaceId}/versions`, { params })
  },
  
  downloadFile(spaceId, versionOrLatest = 'latest', architecture, apiKey) {
    const params = { architecture }
    if (apiKey) {
      params.api_key = apiKey
    }

    return api.get(`/public/download/${spaceId}/${versionOrLatest}`, {
      params,
      responseType: 'blob'
    })
  },
  
  // 管理API - 空间
  getSpaces(params) {
    return api.get('/spaces/', { params })
  },
  
  getSpace(id) {
    return api.get(`/spaces/${id}`)
  },
  
  createSpace(data) {
    return api.post('/spaces/', data)
  },
  
  updateSpace(id, data) {
    return api.put(`/spaces/${id}`, data)
  },
  
  deleteSpace(id) {
    return api.delete(`/spaces/${id}`)
  },

  getSpaceStats(spaceId) {
    return api.get(`/spaces/${spaceId}/stats`)
  },
  
  // 管理API - 版本
  getVersions(spaceId, params) {
    return api.get(`/spaces/${spaceId}/versions`, { params })
  },
  
  createVersion(spaceId, formData) {
    return api.post(`/spaces/${spaceId}/versions`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },
  
  updateVersion(spaceId, version, formData) {
    return api.put(`/spaces/${spaceId}/versions/${version}`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },
  
  deleteVersion(spaceId, version) {
    return api.delete(`/spaces/${spaceId}/versions/${version}`)
  },

  publishVersion(spaceId, version) {
    return api.post(`/spaces/${spaceId}/versions/${version}/publish`)
  },

  unpublishVersion(spaceId, version) {
    return api.post(`/spaces/${spaceId}/versions/${version}/unpublish`)
  },
  
  // 管理API - 用户
  getUsers(params) {
    return api.get('/users/', { params })
  },
  
  getUser(id) {
    return api.get(`/users/${id}`)
  },
  
  createUser(data) {
    return api.post('/users/', data)
  },
  
  updateUser(id, data) {
    return api.put(`/users/${id}`, data)
  },
  
  deleteUser(id) {
    return api.delete(`/users/${id}`)
  },
  
  // 统计分析
  getSystemStats() {
    return api.get('/stats/system')
  },

  getSpaceStatsDetail(spaceId) {
    return api.get(`/stats/spaces/${spaceId}`)
  },
  
  getDailyDownloadStats(spaceId, params) {
    return api.get(`/stats/spaces/${spaceId}/downloads/daily`, { params })
  },
  
  getVersionDownloadStats(spaceId) {
    return api.get(`/stats/spaces/${spaceId}/downloads/versions`)
  },
  
  // Webhook相关
  getWebhookConfig(spaceId) {
    return api.get(`/spaces/${spaceId}/config`)
  },
  
  updateWebhookConfig(spaceId, data) {
    return api.put(`/spaces/${spaceId}/config`, data)
  },
  
  regenerateWebhookSecret(spaceId) {
    return api.post(`/spaces/${spaceId}/regenerate-secret`)
  },
  
  getWebhookLogs(spaceId, params) {
    return api.get(`/spaces/${spaceId}/logs`, { params })
  },
  
  getFailedWebhookLogs(spaceId, params) {
    return api.get(`/spaces/${spaceId}/logs/failed`, { params })
  },
  
  getWebhookLogsByEvent(spaceId, eventType, params) {
    return api.get(`/spaces/${spaceId}/logs/events/${eventType}`, { params })
  },

  // 权限管理
  getPermissions() {
    return api.get('/permissions/')
  }
}
