/**
 * API配置模块
 * 用于配置API请求的基础URL和其他设置
 */

// 获取当前协议
const protocol = window.location.protocol

// 获取当前主机名
const hostname = window.location.hostname

// 获取当前端口
const port = window.location.port

// 构建API基础URL
const getApiBaseUrl = () => {
  // 如果是生产环境或者已经配置了环境变量，则使用环境变量中的API_URL
  if (process.env.VUE_APP_API_URL) {
    return process.env.VUE_APP_API_URL
  }

  // 否则根据当前URL动态构建API URL
  let apiUrl = `${protocol}//${hostname}`

  // 如果端口不是默认端口，则添加端口
  if (port && port !== '80' && port !== '443') {
    apiUrl += `:${port}`
  }

  return apiUrl
}

// API基础URL
export const API_BASE_URL = getApiBaseUrl()

// 上传URL
export const UPLOAD_URL = `${API_BASE_URL}/api/software/upload`

// 文件下载URL
export const FILE_DOWNLOAD_URL = `${API_BASE_URL}/api/software/download`

// 超时设置
export const TIMEOUT = 30000 // 30秒

// 重试设置
export const MAX_RETRIES = 3 // 最大重试次数

// 是否启用HTTPS
export const HTTPS_ENABLED = protocol === 'https:'

// 请求重试延迟
export const RETRY_DELAY = 1000 // 1秒

// 请求头设置
export const DEFAULT_HEADERS = {
  'Content-Type': 'application/json',
  'X-Requested-With': 'XMLHttpRequest',
}

// 文件上传相关配置
export const UPLOAD_CONFIG = {
  // 上传文件大小限制，单位为字节，默认为500MB
  maxFileSize: 500 * 1024 * 1024,
  // 允许的文件类型
  allowedFileTypes: [
    '.exe',
    '.msi',
    '.dmg',
    '.pkg',
    '.deb',
    '.rpm',
    '.zip',
    '.tar.gz',
    '.tar.bz2',
    '.rar',
    '.7z',
    '.jar',
    '.war',
    '.ear',
  ],
  // 分片上传大小，单位为字节，默认为5MB
  chunkSize: 5 * 1024 * 1024,
  // 并发上传数量
  concurrentUploads: 3,
  // 重试次数
  maxRetries: 3,
}

// WebSocket配置
export const WEBSOCKET_CONFIG = {
  // WebSocket URL
  url: `${HTTPS_ENABLED ? 'wss' : 'ws'}://${hostname}${port ? `:${port}` : ''}/ws`,
  // 重连间隔，单位为毫秒
  reconnectInterval: 3000,
  // 最大重连次数
  maxReconnectAttempts: 5,
}

// 默认导出所有配置
export default {
  API_BASE_URL,
  UPLOAD_URL,
  FILE_DOWNLOAD_URL,
  TIMEOUT,
  MAX_RETRIES,
  HTTPS_ENABLED,
  RETRY_DELAY,
  DEFAULT_HEADERS,
  UPLOAD_CONFIG,
  WEBSOCKET_CONFIG,
}
