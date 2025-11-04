import request from '@/utils/request'

// 获取软件空间列表
export function getSpaces() {
  return request({
    url: '/api/software',
    method: 'get',
  })
}

// 创建软件空间
export function createSpace(data) {
  return request({
    url: '/api/software',
    method: 'post',
    data,
  })
}

// 获取软件空间详情
export function getSpace(id) {
  return request({
    url: `/api/software/${id}`,
    method: 'get',
  })
}

// 更新软件空间
export function updateSpace(id, data) {
  return request({
    url: `/api/software/${id}`,
    method: 'put',
    data,
  })
}

// 删除软件空间
export function deleteSpace(id) {
  return request({
    url: `/api/software/${id}`,
    method: 'delete',
  })
}

// 重新生成API密钥
export function regenerateApiKey(id) {
  return request({
    url: `/api/software/${id}/regenerate-api-key`,
    method: 'post',
  })
}

// 获取软件版本列表
export function getVersions(spaceId) {
  return request({
    url: `/api/software/${spaceId}/versions`,
    method: 'get',
  })
}

// 创建软件版本
export function createVersion(spaceId, data) {
  return request({
    url: `/api/software/${spaceId}/versions`,
    method: 'post',
    data,
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
}

// 获取软件版本详情
export function getVersion(id) {
  return request({
    url: `/api/software/versions/${id}`,
    method: 'get',
  })
}

// 更新软件版本
export function updateVersion(id, data) {
  return request({
    url: `/api/software/versions/${id}`,
    method: 'put',
    data,
  })
}

// 删除软件版本
export function deleteVersion(id) {
  return request({
    url: `/api/software/versions/${id}`,
    method: 'delete',
  })
}

// 发布/下架软件版本
export function publishVersion(id, data) {
  return request({
    url: `/api/software/versions/${id}/publish`,
    method: 'put',
    data,
  })
}

// 设为最新版本
export function setAsLatest(id) {
  return request({
    url: `/api/software/versions/${id}/set-latest`,
    method: 'put',
  })
}

// 下载软件版本
export function downloadVersion(id) {
  return request({
    url: `/api/download/${id}`,
    method: 'get',
    responseType: 'blob', // 返回二进制数据
  })
}

// 获取所有软件空间信息（公开API）
export function getPublicSpaces() {
  return request({
    url: `/api/public/spaces`,
    method: 'get',
  })
}

// 获取软件空间信息（公开API）
export function getSpaceInfo(apiKey) {
  return request({
    url: `/api/public/${apiKey}`,
    method: 'get',
  })
}

// 通过ID获取软件空间信息（公开API）
export function getSpaceInfoById(id) {
  return request({
    url: `/api/public/space/${id}`,
    method: 'get',
  })
}

// 获取软件版本列表（公开API）
export function getVersionsInfo(apiKey) {
  return request({
    url: `/api/public/${apiKey}/versions`,
    method: 'get',
  })
}

// 下载软件版本（公开API）
export function downloadVersionPublic(apiKey, version) {
  return request({
    url: `/api/public/${apiKey}/download/${version}`,
    method: 'get',
    responseType: 'blob', // 返回二进制数据
  })
}

// 获取版本下载统计
export function getVersionDownloadStats(id) {
  return request({
    url: `/api/software/versions/${id}/stats`,
    method: 'get',
  })
}

// 获取软件空间下载统计
export function getSpaceDownloadStats(id) {
  return request({
    url: `/api/software/${id}/stats`,
    method: 'get',
  })
}
