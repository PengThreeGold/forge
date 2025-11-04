// 格式化文件大小
export function formatFileSize(bytes) {
  if (bytes === 0) return '0 B'

  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))

  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// 格式化日期时间
export function formatDateTime(date, format = 'YYYY-MM-DD HH:mm:ss') {
  if (!date) return ''

  const d = new Date(date)
  const year = d.getFullYear()
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  const hours = String(d.getHours()).padStart(2, '0')
  const minutes = String(d.getMinutes()).padStart(2, '0')
  const seconds = String(d.getSeconds()).padStart(2, '0')

  return format
    .replace('YYYY', year)
    .replace('MM', month)
    .replace('DD', day)
    .replace('HH', hours)
    .replace('mm', minutes)
    .replace('ss', seconds)
}

// 格式化相对时间
export function formatRelativeTime(date) {
  if (!date) return ''

  const now = new Date()
  const d = new Date(date)
  const diff = now - d

  // 如果是未来的时间
  if (diff < 0) {
    const futureDiff = Math.abs(diff)
    if (futureDiff < 60000) return '刚刚'
    if (futureDiff < 3600000) return Math.floor(futureDiff / 60000) + '分钟后'
    if (futureDiff < 86400000) return Math.floor(futureDiff / 3600000) + '小时后'
    if (futureDiff < 2592000000) return Math.floor(futureDiff / 86400000) + '天后'
    return formatDateTime(date)
  }

  // 如果是过去的时间
  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return Math.floor(diff / 60000) + '分钟前'
  if (diff < 86400000) return Math.floor(diff / 3600000) + '小时前'
  if (diff < 2592000000) return Math.floor(diff / 86400000) + '天前'

  return formatDateTime(date)
}

// 防抖函数
export function debounce(func, wait, immediate) {
  let timeout

  return function executedFunction(...args) {
    const later = () => {
      timeout = null
      if (!immediate) func(...args)
    }

    const callNow = immediate && !timeout

    clearTimeout(timeout)
    timeout = setTimeout(later, wait)

    if (callNow) func(...args)
  }
}

// 节流函数
export function throttle(func, limit) {
  let inThrottle

  return function () {
    const args = arguments
    const context = this

    if (!inThrottle) {
      func.apply(context, args)
      inThrottle = true
      setTimeout(() => (inThrottle = false), limit)
    }
  }
}

// 深拷贝
export function deepClone(obj) {
  if (obj === null || typeof obj !== 'object') return obj

  if (obj instanceof Date) return new Date(obj.getTime())

  if (obj instanceof Array) {
    return obj.map(item => deepClone(item))
  }

  if (typeof obj === 'object') {
    const clonedObj = {}
    for (const key in obj) {
      if (Object.prototype.hasOwnProperty.call(obj, key)) {
        clonedObj[key] = deepClone(obj[key])
      }
    }
    return clonedObj
  }
}

// 生成随机字符串
export function generateRandomString(length = 8) {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
  let result = ''

  for (let i = 0; i < length; i++) {
    result += chars.charAt(Math.floor(Math.random() * chars.length))
  }

  return result
}

// 复制文本到剪贴板
export function copyToClipboard(text) {
  if (navigator.clipboard) {
    return navigator.clipboard.writeText(text)
  } else {
    // 兼容旧浏览器
    const textarea = document.createElement('textarea')
    textarea.value = text
    textarea.style.position = 'fixed'
    textarea.style.opacity = '0'
    document.body.appendChild(textarea)
    textarea.select()

    try {
      const successful = document.execCommand('copy')
      document.body.removeChild(textarea)
      return Promise.resolve(successful)
    } catch (err) {
      document.body.removeChild(textarea)
      return Promise.reject(err)
    }
  }
}

// 下载文件
export function downloadFile(url, filename) {
  const link = document.createElement('a')
  link.href = url
  link.download = filename || 'download'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

// 验证邮箱格式
export function isValidEmail(email) {
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return re.test(email)
}

// 验证URL格式
export function isValidUrl(url) {
  try {
    new URL(url)
    return true
  } catch (e) {
    return false
  }
}

// 验证版本号格式
export function isValidVersion(version) {
  const re = /^(\d+)\.(\d+)\.(\d+)(?:-([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?(?:\+[0-9A-Za-z-]+)?$/
  return re.test(version)
}

// 比较版本号
export function compareVersions(version1, version2) {
  if (!isValidVersion(version1) || !isValidVersion(version2)) {
    throw new Error('Invalid version format')
  }

  // 移除预发布标识和构建元数据
  const v1 = version1.split('-')[0]
  const v2 = version2.split('-')[0]

  const v1Parts = v1.split('.').map(Number)
  const v2Parts = v2.split('.').map(Number)

  for (let i = 0; i < Math.max(v1Parts.length, v2Parts.length); i++) {
    const v1Part = v1Parts[i] || 0
    const v2Part = v2Parts[i] || 0

    if (v1Part > v2Part) return 1
    if (v1Part < v2Part) return -1
  }

  return 0
}

// 获取浏览器信息
export function getBrowserInfo() {
  const ua = navigator.userAgent
  let browserName = ''
  let browserVersion = ''

  // 检测浏览器名称
  if (ua.indexOf('Chrome') > -1) {
    browserName = 'Chrome'
  } else if (ua.indexOf('Safari') > -1) {
    browserName = 'Safari'
  } else if (ua.indexOf('Firefox') > -1) {
    browserName = 'Firefox'
  } else if (ua.indexOf('MSIE') > -1 || ua.indexOf('Trident') > -1) {
    browserName = 'Internet Explorer'
  } else if (ua.indexOf('Edge') > -1) {
    browserName = 'Microsoft Edge'
  } else {
    browserName = 'Unknown'
  }

  // 获取浏览器版本
  const versionMatch = ua.match(new RegExp(browserName + '/([0-9.]+)'))
  if (versionMatch && versionMatch[1]) {
    browserVersion = versionMatch[1]
  }

  return {
    name: browserName,
    version: browserVersion,
    userAgent: ua,
  }
}

// 获取操作系统信息
export function getOSInfo() {
  const ua = navigator.userAgent
  let os = 'Unknown'

  if (ua.indexOf('Windows') > -1) {
    os = 'Windows'
  } else if (ua.indexOf('Mac') > -1) {
    os = 'macOS'
  } else if (ua.indexOf('X11') > -1 || ua.indexOf('Linux') > -1) {
    os = 'Linux'
  } else if (ua.indexOf('Android') > -1) {
    os = 'Android'
  } else if (ua.indexOf('iOS') > -1 || /iPad|iPhone|iPod/.test(ua)) {
    os = 'iOS'
  }

  return os
}

// 检查是否为移动设备
export function isMobileDevice() {
  return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent)
}

// 检查是否为触摸设备
export function isTouchDevice() {
  return 'ontouchstart' in window || navigator.maxTouchPoints > 0 || navigator.msMaxTouchPoints > 0
}
