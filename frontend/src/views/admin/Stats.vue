<template>
  <div class="admin-stats">
    <el-card>
      <template #header>
        <h2>统计分析</h2>
      </template>
      
      <!-- 系统概览 -->
      <el-row :gutter="20" class="stats-overview">
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon">
                <el-icon size="40" color="#409EFF"><Box /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-number">{{ systemStats.total_spaces || 0 }}</div>
                <div class="stat-label">软件空间</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon">
                <el-icon size="40" color="#67C23A"><Document /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-number">{{ systemStats.total_versions || 0 }}</div>
                <div class="stat-label">版本数量</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon">
                <el-icon size="40" color="#E6A23C"><Download /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-number">{{ formatNumber(systemStats.total_downloads || 0) }}</div>
                <div class="stat-label">总下载量</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon">
                <el-icon size="40" color="#F56C6C"><User /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-number">{{ systemStats.active_users || 0 }}</div>
                <div class="stat-label">活跃用户</div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 图表区域 -->
      <el-row :gutter="20" class="chart-section">
        <el-col :span="12">
          <el-card>
            <template #header>
              <h3>每日下载趋势</h3>
            </template>
            <div v-loading="dailyLoading" class="chart-container">
              <div v-if="dailyDownloads.length > 0" ref="dailyChart" class="chart"></div>
              <el-empty v-else description="暂无数据" />
            </div>
          </el-card>
        </el-col>
        <el-col :span="12">
          <el-card>
            <template #header>
              <h3>热门软件空间</h3>
            </template>
            <div v-loading="spacesLoading" class="chart-container">
              <el-table v-if="recentSpaces.length > 0" :data="recentSpaces" stripe>
                <el-table-column prop="space_name" label="软件名称" show-overflow-tooltip />
                <el-table-column prop="total_downloads" label="下载量" width="100" align="center">
                  <template #default="{ row }">
                    {{ formatNumber(row.total_downloads) }}
                  </template>
                </el-table-column>
                <el-table-column prop="versions_count" label="版本数" width="80" align="center" />
                <el-table-column prop="latest_version" label="最新版本" width="120" align="center" />
              </el-table>
              <el-empty v-else description="暂无数据" />
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 下载记录 -->
      <el-card class="download-records">
        <template #header>
          <div class="card-header">
            <h3>下载记录</h3>
            <div class="header-actions">
              <el-date-picker
                v-model="dateRange"
                type="daterange"
                range-separator="至"
                start-placeholder="开始日期"
                end-placeholder="结束日期"
                format="YYYY-MM-DD"
                value-format="YYYY-MM-DD"
                @change="handleDateChange"
              />
              <el-button @click="handleRefreshDownloads">
                <el-icon><Refresh /></el-icon>
                刷新
              </el-button>
            </div>
          </div>
        </template>
        
        <el-table v-loading="downloadsLoading" :data="downloadRecords" stripe>
          <el-table-column prop="space_name" label="软件名称" show-overflow-tooltip />
          <el-table-column prop="version" label="版本号" width="100" />
          <el-table-column prop="architecture" label="架构" width="80" />
          <el-table-column prop="download_count" label="下载次数" width="100" align="center">
            <template #default="{ row }">
              {{ formatNumber(row.download_count) }}
            </template>
          </el-table-column>
          <el-table-column prop="download_date" label="下载日期" width="120" align="center">
            <template #default="{ row }">
              {{ formatDate(row.download_date) }}
            </template>
          </el-table-column>
        </el-table>
        
        <el-pagination
          v-if="downloadTotal > 0"
          class="pagination"
          :current-page="downloadPage"
          :page-size="downloadPageSize"
          :total="downloadTotal"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleDownloadSizeChange"
          @current-change="handleDownloadPageChange"
        />
      </el-card>
    </el-card>
  </div>
</template>

<script>
export default {
  name: 'AdminStats'
}
</script>

<script setup>
import { ref, reactive, onMounted, onUnmounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { Box, Document, Download, User, Refresh } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import api from '@/api'

// 响应式数据
const systemStats = reactive({
  total_spaces: 0,
  total_versions: 0,
  total_downloads: 0,
  active_users: 0,
  recent_spaces: [],
  daily_downloads: []
})

const dailyDownloads = ref([])
const recentSpaces = ref([])
const downloadRecords = ref([])
const downloadTotal = ref(0)

const dailyLoading = ref(false)
const spacesLoading = ref(false)
const downloadsLoading = ref(false)

const downloadPage = ref(1)
const downloadPageSize = ref(20)
const dateRange = ref([])

let dailyChartInstance = null

// 工具函数
const formatNumber = (num) => {
  if (num >= 10000) {
    return (num / 10000).toFixed(1) + '万'
  }
  return num.toString()
}

const formatDate = (dateString) => {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleDateString('zh-CN')
}

// 获取系统统计
const fetchSystemStats = async () => {
  try {
    dailyLoading.value = true
    spacesLoading.value = true
    
    const res = await api.getSystemStats()
    if (res.success) {
      const data = res.data || res
      Object.assign(systemStats, data)
      dailyDownloads.value = data.daily_downloads || []
      recentSpaces.value = data.recent_spaces || []
      
      // 初始化图表
      nextTick(() => {
        initDailyChart()
      })
    }
  } catch (error) {
    console.error('获取系统统计失败:', error)
    ElMessage.error('获取系统统计失败')
  } finally {
    dailyLoading.value = false
    spacesLoading.value = false
  }
}

// 获取下载记录
const fetchDownloadRecords = async () => {
  try {
    downloadsLoading.value = true
    
    const params = {
      skip: (downloadPage.value - 1) * downloadPageSize.value,
      limit: downloadPageSize.value
    }
    
    if (dateRange.value && dateRange.value.length === 2) {
      params.start_date = dateRange.value[0]
      params.end_date = dateRange.value[1]
    }
    
    const res = await api.getDownloadRecords(params)
    if (res.success) {
      const data = res.data || res
      downloadRecords.value = data.items || []
      downloadTotal.value = data.total || 0
    }
  } catch (error) {
    console.error('获取下载记录失败:', error)
    ElMessage.error('获取下载记录失败')
  } finally {
    downloadsLoading.value = false
  }
}

// 初始化每日下载图表
const initDailyChart = () => {
  if (!dailyDownloads.value.length) return
  
  const chartDom = document.querySelector('.chart')
  if (!chartDom) return
  
  dailyChartInstance = echarts.init(chartDom)
  
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: dailyDownloads.value.map(item => item.date),
      axisLabel: {
        rotate: 45
      }
    },
    yAxis: {
      type: 'value',
      name: '下载次数'
    },
    series: [{
      name: '下载次数',
      type: 'line',
      smooth: true,
      data: dailyDownloads.value.map(item => item.downloads),
      itemStyle: {
        color: '#409EFF'
      },
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: 'rgba(64, 158, 255, 0.3)' },
          { offset: 1, color: 'rgba(64, 158, 255, 0.1)' }
        ])
      }
    }]
  }
  
  dailyChartInstance.setOption(option)
}

// 事件处理
const handleDateChange = () => {
  downloadPage.value = 1
  fetchDownloadRecords()
}

const handleRefreshDownloads = () => {
  fetchDownloadRecords()
}

const handleDownloadSizeChange = (newSize) => {
  downloadPageSize.value = newSize
  downloadPage.value = 1
  fetchDownloadRecords()
}

const handleDownloadPageChange = (newPage) => {
  downloadPage.value = newPage
  fetchDownloadRecords()
}

// 生命周期
let resizeHandler = null

onMounted(() => {
  fetchSystemStats()
  fetchDownloadRecords()
  
  // 响应式图表
  resizeHandler = () => {
    dailyChartInstance?.resize()
  }
  window.addEventListener('resize', resizeHandler)
})

onUnmounted(() => {
  // 清理事件监听器
  if (resizeHandler) {
    window.removeEventListener('resize', resizeHandler)
  }
  // 销毁图表实例
  if (dailyChartInstance) {
    dailyChartInstance.dispose()
    dailyChartInstance = null
  }
})
</script>

<style scoped>
.admin-stats {
  max-width: 1400px;
  margin: 0 auto;
}

.stats-overview {
  margin-bottom: 20px;
}

.stat-card {
  text-align: center;
}

.stat-content {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 20px;
  padding: 20px;
}

.stat-icon {
  flex-shrink: 0;
}

.stat-info {
  text-align: left;
}

.stat-number {
  font-size: 32px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}

.chart-section {
  margin-bottom: 20px;
}

.chart-container {
  height: 300px;
}

.chart {
  width: 100%;
  height: 100%;
}

.download-records {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  gap: 16px;
  align-items: center;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .stats-overview {
    flex-direction: column;
  }
  
  .chart-section {
    flex-direction: column;
  }
  
  .card-header {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }
  
  .header-actions {
    flex-direction: column;
    align-items: stretch;
  }
}
</style>
