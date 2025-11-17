import { ref, computed } from 'vue'
import { defineStore } from 'pinia'

// 缓存管理store
export const useCacheStore = defineStore('cache', () => {
  // 空间数据缓存
  const spacesCache = ref(new Map())
  const usersCache = ref(new Map())
  const versionsCache = ref(new Map())
  
  // 缓存配置
  const CACHE_TTL = 5 * 60 * 1000 // 5分钟
  const MAX_CACHE_SIZE = 100 // 最大缓存条目数

  // 获取缓存
  function getCache(cache, key) {
    const item = cache.get(key)
    if (item && Date.now() - item.timestamp < CACHE_TTL) {
      return item.data
    }
    cache.delete(key)
    return null
  }

  // 设置缓存
  function setCache(cache, key, data) {
    // 清理过期缓存
    cleanupCache(cache)
    
    // 如果缓存已满，删除最旧的条目
    if (cache.size >= MAX_CACHE_SIZE) {
      const oldestKey = cache.keys().next().value
      cache.delete(oldestKey)
    }
    
    cache.set(key, {
      data,
      timestamp: Date.now()
    })
  }

  // 清理过期缓存
  function cleanupCache(cache) {
    const now = Date.now()
    for (const [key, item] of cache.entries()) {
      if (now - item.timestamp > CACHE_TTL) {
        cache.delete(key)
      }
    }
  }

  // 空间缓存操作
  function getSpacesCache(key) {
    return getCache(spacesCache.value, key)
  }

  function setSpacesCache(key, data) {
    setCache(spacesCache.value, key, data)
  }

  function clearSpacesCache() {
    spacesCache.value.clear()
  }

  // 用户缓存操作
  function getUsersCache(key) {
    return getCache(usersCache.value, key)
  }

  function setUsersCache(key, data) {
    setCache(usersCache.value, key, data)
  }

  function clearUsersCache() {
    usersCache.value.clear()
  }

  // 版本缓存操作
  function getVersionsCache(key) {
    return getCache(versionsCache.value, key)
  }

  function setVersionsCache(key, data) {
    setCache(versionsCache.value, key, data)
  }

  function clearVersionsCache() {
    versionsCache.value.clear()
  }

  // 清理所有缓存
  function clearAllCache() {
    spacesCache.value.clear()
    usersCache.value.clear()
    versionsCache.value.clear()
  }

  // 定期清理缓存
  setInterval(() => {
    cleanupCache(spacesCache.value)
    cleanupCache(usersCache.value)
    cleanupCache(versionsCache.value)
  }, 60000) // 每分钟清理一次

  return {
    // 空间缓存
    getSpacesCache,
    setSpacesCache,
    clearSpacesCache,
    
    // 用户缓存
    getUsersCache,
    setUsersCache,
    clearUsersCache,
    
    // 版本缓存
    getVersionsCache,
    setVersionsCache,
    clearVersionsCache,
    
    // 通用操作
    clearAllCache,
    
    // 缓存统计
    cacheStats: computed(() => ({
      spaces: spacesCache.value.size,
      users: usersCache.value.size,
      versions: versionsCache.value.size,
      total: spacesCache.value.size + usersCache.value.size + versionsCache.value.size
    }))
  }
})