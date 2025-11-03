import request from '@/utils/request'

// 获取统计概览
export function getOverview() {
  return request({
    url: '/api/statistics/overview',
    method: 'get'
  })
}

// 获取下载统计
export function getDownloads(params = {}) {
  return request({
    url: '/api/statistics/downloads',
    method: 'get',
    params
  })
}

// 获取下载时间线
export function getDownloadsTimeline(params = {}) {
  return request({
    url: '/api/statistics/downloads/timeline',
    method: 'get',
    params
  })
}

// 获取软件空间统计
export function getSpaceStatistics(spaceId) {
  return request({
    url: `/api/statistics/spaces/${spaceId}`,
    method: 'get'
  })
}

// 获取Webhook日志
export function getWebhooks(params = {}) {
  return request({
    url: '/api/webhooks',
    method: 'get',
    params
  })
}

// 获取Webhook日志详情
export function getWebhook(logId) {
  return request({
    url: `/api/webhooks/${logId}`,
    method: 'get'
  })
}

// 重试Webhook
export function retryWebhook(logId) {
  return request({
    url: `/api/webhooks/retry/${logId}`,
    method: 'post'
  })
}

// 测试Webhook
export function testWebhook(spaceId) {
  return request({
    url: `/api/webhooks/test/${spaceId}`,
    method: 'post'
  })
}