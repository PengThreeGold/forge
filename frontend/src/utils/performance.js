// 性能监控工具类

class PerformanceMonitor {
  constructor() {
    this.metrics = new Map()
    this.thresholds = {
      api: 1000, // API响应时间阈值(ms)
      render: 100, // 渲染时间阈值(ms)
      load: 2000 // 页面加载时间阈值(ms)
    }
    this.enabled = import.meta.env.DEV // 只在开发环境启用
  }

  // 开始计时
  startTimer(name) {
    if (!this.enabled) return
    this.metrics.set(name, {
      startTime: performance.now(),
      status: 'running'
    })
  }

  // 结束计时
  endTimer(name) {
    if (!this.enabled) return
    const metric = this.metrics.get(name)
    if (metric && metric.status === 'running') {
      const endTime = performance.now()
      const duration = endTime - metric.startTime
      metric.endTime = endTime
      metric.duration = duration
      metric.status = 'completed'
      
      // 检查是否超过阈值
      this.checkThreshold(name, duration)
      
      // 输出性能信息
      console.log(`[Performance] ${name}: ${duration.toFixed(2)}ms`)
    }
  }

  // 检查阈值
  checkThreshold(name, duration) {
    let threshold = this.thresholds.api
    if (name.includes('render')) threshold = this.thresholds.render
    if (name.includes('load')) threshold = this.thresholds.load
    
    if (duration > threshold) {
      console.warn(`[Performance Warning] ${name} took ${duration.toFixed(2)}ms, exceeds threshold ${threshold}ms`)
    }
  }

  // 获取性能指标
  getMetric(name) {
    return this.metrics.get(name)
  }

  // 获取所有指标
  getAllMetrics() {
    return Array.from(this.metrics.entries()).map(([name, data]) => ({
      name,
      duration: data.duration || 0,
      status: data.status
    }))
  }

  // 清除指标
  clearMetric(name) {
    this.metrics.delete(name)
  }

  // 清除所有指标
  clearAllMetrics() {
    this.metrics.clear()
  }

  // 生成性能报告
  generateReport() {
    if (!this.enabled) return
    
    const metrics = this.getAllMetrics()
    const report = {
      timestamp: new Date().toISOString(),
      totalMetrics: metrics.length,
      slowMetrics: metrics.filter(m => {
        let threshold = this.thresholds.api
        if (m.name.includes('render')) threshold = this.thresholds.render
        if (m.name.includes('load')) threshold = this.thresholds.load
        return m.duration > threshold
      }),
      metrics: metrics.sort((a, b) => b.duration - a.duration)
    }
    
    console.log('[Performance Report]', report)
    return report
  }
}

// 创建全局性能监控实例
export const performanceMonitor = new PerformanceMonitor()

// Vue组件性能监控混入
export const performanceMixin = {
  mounted() {
    if (import.meta.env.DEV) {
      const componentName = this.$options.name || this.$options.__file || 'Unknown'
      performanceMonitor.startTimer(`component_render_${componentName}`)
    }
  },
  updated() {
    if (import.meta.env.DEV) {
      const componentName = this.$options.name || this.$options.__file || 'Unknown'
      performanceMonitor.endTimer(`component_render_${componentName}`)
    }
  }
}

// API性能监控
export function monitorAPI(apiCall, name) {
  if (!import.meta.env.DEV) return apiCall
  
  return async (...args) => {
    performanceMonitor.startTimer(`api_${name}`)
    try {
      const result = await apiCall(...args)
      performanceMonitor.endTimer(`api_${name}`)
      return result
    } catch (error) {
      performanceMonitor.endTimer(`api_${name}`)
      throw error
    }
  }
}

// 页面加载性能监控
export function monitorPageLoad(pageName) {
  if (!import.meta.env.DEV) return
  
  performanceMonitor.startTimer(`page_load_${pageName}`)
  
  // 在页面加载完成后结束计时
  window.addEventListener('load', () => {
    performanceMonitor.endTimer(`page_load_${pageName}`)
  })
}

// 内存使用监控
export function monitorMemory() {
  if (!import.meta.env.DEV || !performance.memory) return
  
  const memory = performance.memory
  console.log('[Memory Usage]', {
    used: (memory.usedJSHeapSize / 1024 / 1024).toFixed(2) + ' MB',
    total: (memory.totalJSHeapSize / 1024 / 1024).toFixed(2) + ' MB',
    limit: (memory.jsHeapSizeLimit / 1024 / 1024).toFixed(2) + ' MB'
  })
}

// 长任务监控
export function monitorLongTasks() {
  if (!import.meta.env.DEV || !PerformanceObserver) return
  
  try {
    const observer = new PerformanceObserver((list) => {
      for (const entry of list.getEntries()) {
        if (entry.duration > 50) { // 长任务定义为超过50ms的任务
          console.warn(`[Long Task] ${entry.name}: ${entry.duration.toFixed(2)}ms`)
        }
      }
    })
    
    observer.observe({ entryTypes: ['longtask'] })
  } catch (error) {
    console.log('Long task monitoring not supported')
  }
}

// 资源加载监控
export function monitorResourceLoad() {
  if (!import.meta.env.DEV || !PerformanceObserver) return
  
  try {
    const observer = new PerformanceObserver((list) => {
      for (const entry of list.getEntries()) {
        if (entry.duration > 1000) { // 加载时间超过1秒的资源
          console.warn(`[Slow Resource] ${entry.name}: ${entry.duration.toFixed(2)}ms`)
        }
      }
    })
    
    observer.observe({ entryTypes: ['resource'] })
  } catch (error) {
    console.log('Resource load monitoring not supported')
  }
}

// 初始化性能监控
export function initPerformanceMonitoring() {
  if (!import.meta.env.DEV) return
  
  // 监控长任务
  monitorLongTasks()
  
  // 监控资源加载
  monitorResourceLoad()
  
  // 定期输出内存使用情况
  setInterval(monitorMemory, 30000) // 每30秒检查一次内存
  
  // 定期生成性能报告
  setInterval(() => {
    performanceMonitor.generateReport()
  }, 60000) // 每分钟生成一次报告
  
  console.log('[Performance] Monitoring initialized')
}

export default {
  performanceMonitor,
  performanceMixin,
  monitorAPI,
  monitorPageLoad,
  monitorMemory,
  monitorLongTasks,
  monitorResourceLoad,
  initPerformanceMonitoring
}