import api from '@/utils/request'

export default {
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
    return api.get('/spaces', { params })
  },
  
  getSpace(id) {
    return api.get(`/spaces/${id}`)
  },
  
  createSpace(data) {
    return api.post('/spaces', data)
  },
  
  updateSpace(id, data) {
    return api.put(`/spaces/${id}`, data)
  },
  
  deleteSpace(id) {
    return api.delete(`/spaces/${id}`)
  },
  
  regenerateApiKey(id) {
    return api.post(`/spaces/${id}/regenerate-key`)
  },
  
  // 管理API - 版本
  getVersions(spaceId, params) {
    return api.get(`/spaces/${spaceId}/versions`, { params })
  },
  
  getVersion(spaceId, versionId) {
    return api.get(`/spaces/${spaceId}/versions/${versionId}`)
  },
  
  createVersion(spaceId, data) {
    return api.post(`/spaces/${spaceId}/versions`, data)
  },
  
  updateVersion(spaceId, versionId, data) {
    return api.put(`/spaces/${spaceId}/versions/${versionId}`, data)
  },
  
  deleteVersion(spaceId, version) {
    return api.delete(`/spaces/${spaceId}/versions/${version}`)
  },
  
  uploadFile(spaceId, versionId, arch, file, onProgress) {
    const formData = new FormData()
    formData.append('file', file)
    
    return api.post(
      `/spaces/${spaceId}/versions/${versionId}/upload/${arch}`,
      formData,
      {
        headers: { 'Content-Type': 'multipart/form-data' },
        onUploadProgress: onProgress
      }
    )
  },
  
  deleteFile(spaceId, versionId, fileId) {
    return api.delete(`/spaces/${spaceId}/versions/${versionId}/files/${fileId}`)
  },
  
  // 管理API - 用户
  getUsers(params) {
    return api.get('/users', { params })
  },
  
  getUser(id) {
    return api.get(`/users/${id}`)
  },
  
  createUser(data) {
    return api.post('/users', data)
  },
  
  updateUser(id, data) {
    return api.put(`/users/${id}`, data)
  },
  
  deleteUser(id) {
    return api.delete(`/users/${id}`)
  },
  
  // 管理API - 统计
  getStats() {
    return api.get('/stats')
  },
  
  getSpaceStats(spaceId) {
    return api.get(`/stats/spaces/${spaceId}`)
  },
  
  getVersionStats(spaceId, versionId) {
    return api.get(`/stats/spaces/${spaceId}/versions/${versionId}`)
  },
  
  getDownloadRecords(params) {
    return api.get('/stats/downloads', { params })
  },
  
  // 管理员认证相关
  changePassword(data) {
    return api.put('/auth/admin/password', data)
  },
  
  initAdmin(data) {
    return api.post('/auth/admin/init', data)
  },
  
  // 系统统计相关
  getSystemStats() {
    return api.get('/stats/system')
  },
  
  getDailyDownloadStats(spaceId) {
    return api.get(`/stats/spaces/${spaceId}/downloads/daily`)
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
  }
}
