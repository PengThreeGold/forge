<template>
  <div class="statistics-container" v-loading="loading">
    <div class="page-header">
      <h2>统计分析</h2>
      <div class="header-actions">
        <el-date-picker
          v-model="dateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          value-format="YYYY-MM-DD"
          @change="handleDateRangeChange"
        />
        <el-button type="primary" @click="refreshData">
          <el-icon><Refresh /></el-icon>
          刷新数据
        </el-button>
      </div>
    </div>

    <el-row :gutter="20" class="overview-row">
      <el-col :span="6">
        <el-card shadow="hover" class="overview-card">
          <div class="card-content">
            <div class="card-icon">
              <el-icon><FolderOpened /></el-icon>
            </div>
            <div class="card-value">{{ overview.spaces_count || 0 }}</div>
            <div class="card-title">软件空间</div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card shadow="hover" class="overview-card">
          <div class="card-content">
            <div class="card-icon">
              <el-icon><Document /></el-icon>
            </div>
            <div class="card-value">{{ overview.versions_count || 0 }}</div>
            <div class="card-title">软件版本</div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card shadow="hover" class="overview-card">
          <div class="card-content">
            <div class="card-icon">
              <el-icon><Download /></el-icon>
            </div>
            <div class="card-value">{{ overview.total_downloads || 0 }}</div>
            <div class="card-title">总下载量</div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card shadow="hover" class="overview-card">
          <div class="card-content">
            <div class="card-icon">
              <el-icon><User /></el-icon>
            </div>
            <div class="card-value">{{ overview.unique_ips || 0 }}</div>
            <div class="card-title">独立用户</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="chart-row">
      <el-col :span="16">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <div class="card-header">
              <span>下载趋势</span>
              <el-radio-group
                v-model="timelineDays"
                size="small"
                @change="handleTimelineDaysChange"
              >
                <el-radio-button :label="7">7天</el-radio-button>
                <el-radio-button :label="30">30天</el-radio-button>
                <el-radio-button :label="90">90天</el-radio-button>
              </el-radio-group>
            </div>
          </template>
          <div class="chart-content" ref="downloadTimelineChart"></div>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <div class="card-header">
              <span>热门软件</span>
            </div>
          </template>
          <div class="chart-content" ref="popularSoftwareChart"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="data-row">
      <el-col :span="12">
        <el-card shadow="hover" class="data-card">
          <template #header>
            <div class="card-header">
              <span>下载记录</span>
              <el-select
                v-model="selectedSpace"
                placeholder="选择软件空间"
                clearable
                @change="handleSpaceChange"
              >
                <el-option
                  v-for="space in spaces"
                  :key="space.id"
                  :label="space.name"
                  :value="space.id"
                />
              </el-select>
            </div>
          </template>

          <el-table
            :data="downloads"
            style="width: 100%"
            max-height="400"
            v-loading="downloadsLoading"
          >
            <el-table-column
              prop="space_name"
              label="软件名称"
              min-width="120"
              show-overflow-tooltip
            />
            <el-table-column prop="version" label="版本" width="100" />
            <el-table-column prop="ip_address" label="IP地址" width="130" />
            <el-table-column prop="download_time" label="下载时间" width="160">
              <template #default="scope">
                {{ formatDateTime(scope.row.download_time) }}
              </template>
            </el-table-column>
          </el-table>

          <div class="pagination-container">
            <el-pagination
              v-model:current-page="downloadsPage"
              v-model:page-size="downloadsPageSize"
              :page-sizes="[10, 20, 50]"
              :total="downloadsTotal"
              small
              layout="total, sizes, prev, pager, next"
              @size-change="handleDownloadsSizeChange"
              @current-change="handleDownloadsCurrentChange"
            />
          </div>
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card shadow="hover" class="data-card">
          <template #header>
            <div class="card-header">
              <span>Webhook日志</span>
              <el-select
                v-model="webhookSpace"
                placeholder="选择软件空间"
                clearable
                @change="handleWebhookSpaceChange"
              >
                <el-option
                  v-for="space in spaces"
                  :key="space.id"
                  :label="space.name"
                  :value="space.id"
                />
              </el-select>
            </div>
          </template>

          <el-table
            :data="webhooks"
            style="width: 100%"
            max-height="400"
            v-loading="webhooksLoading"
          >
            <el-table-column
              prop="space_name"
              label="软件名称"
              min-width="120"
              show-overflow-tooltip
            />
            <el-table-column prop="event_type" label="事件类型" width="120" />
            <el-table-column prop="response_status" label="状态" width="100">
              <template #default="scope">
                <el-tag :type="getWebhookStatusType(scope.row.response_status)">
                  {{ getWebhookStatusText(scope.row.response_status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="attempt_time" label="时间" width="160">
              <template #default="scope">
                {{ formatDateTime(scope.row.attempt_time) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="100">
              <template #default="scope">
                <el-button type="primary" size="small" @click="viewWebhook(scope.row)"
                  >详情</el-button
                >
              </template>
            </el-table-column>
          </el-table>

          <div class="pagination-container">
            <el-pagination
              v-model:current-page="webhooksPage"
              v-model:page-size="webhooksPageSize"
              :page-sizes="[10, 20, 50]"
              :total="webhooksTotal"
              small
              layout="total, sizes, prev, pager, next"
              @size-change="handleWebhooksSizeChange"
              @current-change="handleWebhooksCurrentChange"
            />
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Webhook详情对话框 -->
    <el-dialog
      v-model="webhookDetailVisible"
      title="Webhook详情"
      width="800px"
      :close-on-click-modal="false"
    >
      <div v-if="currentWebhook" class="webhook-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="软件名称">{{
            currentWebhook.space_name
          }}</el-descriptions-item>
          <el-descriptions-item label="事件类型">{{
            currentWebhook.event_type
          }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getWebhookStatusType(currentWebhook.response_status)">
              {{ getWebhookStatusText(currentWebhook.response_status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="时间">{{
            formatDateTime(currentWebhook.attempt_time)
          }}</el-descriptions-item>
          <el-descriptions-item label="请求载荷" :span="2">
            <el-input
              type="textarea"
              :rows="8"
              readonly
              :value="formatJson(currentWebhook.payload)"
            />
          </el-descriptions-item>
          <el-descriptions-item label="响应状态" :span="2">
            {{ currentWebhook.response_status || '无响应' }}
          </el-descriptions-item>
          <el-descriptions-item label="响应内容" :span="2">
            <el-input
              type="textarea"
              :rows="8"
              readonly
              :value="currentWebhook.response_body || '无响应内容'"
            />
          </el-descriptions-item>
        </el-descriptions>

        <div class="webhook-actions">
          <el-button type="primary" @click="retryWebhook(currentWebhook)">
            <el-icon><RefreshRight /></el-icon>
            重试
          </el-button>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { defineComponent, ref, reactive, onMounted, nextTick } from 'vue'
import { useStore } from 'vuex'
import * as echarts from 'echarts'
import { formatDateTime } from '@/utils/common'

export default defineComponent({
  name: 'Statistics',
  setup() {
    const store = useStore()

    // 数据
    const overview = reactive({})
    const spaces = ref([])
    const loading = ref(false)

    // 日期范围
    const dateRange = ref([])

    // 下载记录
    const downloads = ref([])
    const downloadsLoading = ref(false)
    const downloadsPage = ref(1)
    const downloadsPageSize = ref(20)
    const downloadsTotal = ref(0)
    const selectedSpace = ref(null)

    // Webhook日志
    const webhooks = ref([])
    const webhooksLoading = ref(false)
    const webhooksPage = ref(1)
    const webhooksPageSize = ref(20)
    const webhooksTotal = ref(0)
    const webhookSpace = ref(null)

    // 图表相关
    const timelineDays = ref(30)
    const timeline = ref([])

    // 图表引用
    const downloadTimelineChart = ref(null)
    const popularSoftwareChart = ref(null)

    // 图表实例
    let downloadTimelineChartInstance = null
    let popularSoftwareChartInstance = null

    // Webhook详情
    const webhookDetailVisible = ref(false)
    const currentWebhook = ref(null)

    // 获取概览数据
    const getOverviewData = async () => {
      try {
        loading.value = true

        const response = await store.dispatch('statistics/getOverview')
        Object.assign(overview, response.data)
      } catch (error) {
        console.error('获取概览数据失败:', error)
      } finally {
        loading.value = false
      }
    }

    // 获取软件空间列表
    const getSpaces = async () => {
      try {
        const response = await store.dispatch('software/getSpaces')
        spaces.value = response.data
      } catch (error) {
        console.error('获取软件空间列表失败:', error)
      }
    }

    // 获取下载记录
    const getDownloads = async () => {
      try {
        downloadsLoading.value = true

        const params = {
          page: downloadsPage.value,
          per_page: downloadsPageSize.value,
        }

        if (selectedSpace.value) {
          params.space_id = selectedSpace.value
        }

        if (dateRange.value && dateRange.value.length === 2) {
          params.start_date = dateRange.value[0]
          params.end_date = dateRange.value[1]
        }

        const response = await store.dispatch('statistics/getDownloads', params)
        downloads.value = response.data.downloads
        downloadsTotal.value = response.data.total
      } catch (error) {
        console.error('获取下载记录失败:', error)
      } finally {
        downloadsLoading.value = false
      }
    }

    // 获取Webhook日志
    const getWebhooks = async () => {
      try {
        webhooksLoading.value = true

        const params = {
          page: webhooksPage.value,
          per_page: webhooksPageSize.value,
        }

        if (webhookSpace.value) {
          params.space_id = webhookSpace.value
        }

        const response = await store.dispatch('statistics/getWebhooks', params)
        webhooks.value = response.data.webhooks
        webhooksTotal.value = response.data.total
      } catch (error) {
        console.error('获取Webhook日志失败:', error)
      } finally {
        webhooksLoading.value = false
      }
    }

    // 获取下载时间线数据
    const getTimelineData = async () => {
      try {
        const params = {
          days: timelineDays.value,
        }

        if (selectedSpace.value) {
          params.space_id = selectedSpace.value
        }

        const response = await store.dispatch('statistics/getDownloadsTimeline', params)
        timeline.value = response.data.timeline
        renderDownloadTimelineChart()
      } catch (error) {
        console.error('获取下载时间线数据失败:', error)
      }
    }

    // 渲染下载时间线图表
    const renderDownloadTimelineChart = () => {
      if (!downloadTimelineChart.value) return

      if (downloadTimelineChartInstance) {
        downloadTimelineChartInstance.dispose()
      }

      downloadTimelineChartInstance = echarts.init(downloadTimelineChart.value)

      const dates = timeline.value.map(item => item.date)
      const downloads = timeline.value.map(item => item.downloads)

      const option = {
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'cross',
          },
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          containLabel: true,
        },
        xAxis: {
          type: 'category',
          boundaryGap: false,
          data: dates,
          axisLabel: {
            interval: 'auto',
            rotate: 45,
          },
        },
        yAxis: {
          type: 'value',
          name: '下载次数',
        },
        series: [
          {
            name: '下载次数',
            type: 'line',
            stack: 'Total',
            smooth: true,
            areaStyle: {
              opacity: 0.3,
            },
            emphasis: {
              focus: 'series',
            },
            data: downloads,
          },
        ],
      }

      downloadTimelineChartInstance.setOption(option)

      // 响应式调整
      window.addEventListener('resize', () => {
        downloadTimelineChartInstance && downloadTimelineChartInstance.resize()
      })
    }

    // 渲染热门软件图表
    const renderPopularSoftwareChart = () => {
      if (!popularSoftwareChart.value) return

      if (popularSoftwareChartInstance) {
        popularSoftwareChartInstance.dispose()
      }

      popularSoftwareChartInstance = echarts.init(popularSoftwareChart.value)

      // 取前5个热门软件
      const topSoftware = [...(overview.spaces_downloads || [])].slice(0, 5)
      const names = topSoftware.map(item => item.name)
      const downloads = topSoftware.map(item => item.downloads)

      const option = {
        tooltip: {
          trigger: 'item',
          formatter: '{a} <br/>{b}: {c} ({d}%)',
        },
        legend: {
          orient: 'vertical',
          right: 10,
          top: 'center',
        },
        series: [
          {
            name: '下载次数',
            type: 'pie',
            radius: ['40%', '70%'],
            avoidLabelOverlap: false,
            itemStyle: {
              borderRadius: 10,
              borderColor: '#fff',
              borderWidth: 2,
            },
            label: {
              show: false,
              position: 'center',
            },
            emphasis: {
              label: {
                show: true,
                fontSize: '16',
                fontWeight: 'bold',
              },
            },
            labelLine: {
              show: false,
            },
            data: names.map((name, index) => ({
              value: downloads[index],
              name: name,
            })),
          },
        ],
      }

      popularSoftwareChartInstance.setOption(option)

      // 响应式调整
      window.addEventListener('resize', () => {
        popularSoftwareChartInstance && popularSoftwareChartInstance.resize()
      })
    }

    // 刷新数据
    const refreshData = async () => {
      await getOverviewData()
      await getTimelineData()
      await getDownloads()
      await getWebhooks()

      // 等待DOM更新后渲染图表
      await nextTick()
      renderDownloadTimelineChart()
      renderPopularSoftwareChart()
    }

    // 处理日期范围变化
    const handleDateRangeChange = () => {
      downloadsPage.value = 1
      getDownloads()
    }

    // 处理时间线天数变化
    const handleTimelineDaysChange = () => {
      getTimelineData()
    }

    // 处理软件空间变化
    const handleSpaceChange = () => {
      downloadsPage.value = 1
      getDownloads()
      getTimelineData()
    }

    // 处理下载记录分页大小变化
    const handleDownloadsSizeChange = size => {
      downloadsPageSize.value = size
      downloadsPage.value = 1
      getDownloads()
    }

    // 处理下载记录当前页变化
    const handleDownloadsCurrentChange = page => {
      downloadsPage.value = page
      getDownloads()
    }

    // 处理Webhook软件空间变化
    const handleWebhookSpaceChange = () => {
      webhooksPage.value = 1
      getWebhooks()
    }

    // 处理Webhook分页大小变化
    const handleWebhooksSizeChange = size => {
      webhooksPageSize.value = size
      webhooksPage.value = 1
      getWebhooks()
    }

    // 处理Webhook当前页变化
    const handleWebhooksCurrentChange = page => {
      webhooksPage.value = page
      getWebhooks()
    }

    // 查看Webhook详情
    const viewWebhook = webhook => {
      currentWebhook.value = webhook
      webhookDetailVisible.value = true
    }

    // 重试Webhook
    const retryWebhook = async webhook => {
      try {
        await store.dispatch('statistics/retryWebhook', webhook.id)
        getWebhooks()
      } catch (error) {
        console.error('重试Webhook失败:', error)
      }
    }

    // 获取Webhook状态类型
    const getWebhookStatusType = status => {
      if (status >= 200 && status < 300) return 'success'
      if (status >= 400 && status < 500) return 'warning'
      return 'danger'
    }

    // 获取Webhook状态文本
    const getWebhookStatusText = status => {
      if (!status) return '无响应'
      if (status >= 200 && status < 300) return '成功'
      if (status >= 400 && status < 500) return '客户端错误'
      if (status >= 500) return '服务器错误'
      return '未知错误'
    }

    // 格式化JSON
    const formatJson = json => {
      if (!json) return ''
      try {
        return JSON.stringify(JSON.parse(json), null, 2)
      } catch (e) {
        return json
      }
    }

    onMounted(async () => {
      // 获取数据
      await getSpaces()
      await refreshData()
    })

    return {
      overview,
      spaces,
      loading,
      dateRange,
      downloads,
      downloadsLoading,
      downloadsPage,
      downloadsPageSize,
      downloadsTotal,
      selectedSpace,
      webhooks,
      webhooksLoading,
      webhooksPage,
      webhooksPageSize,
      webhooksTotal,
      webhookSpace,
      timelineDays,
      downloadTimelineChart,
      popularSoftwareChart,
      webhookDetailVisible,
      currentWebhook,
      refreshData,
      handleDateRangeChange,
      handleTimelineDaysChange,
      handleSpaceChange,
      handleDownloadsSizeChange,
      handleDownloadsCurrentChange,
      handleWebhookSpaceChange,
      handleWebhooksSizeChange,
      handleWebhooksCurrentChange,
      viewWebhook,
      retryWebhook,
      getWebhookStatusType,
      getWebhookStatusText,
      formatJson,
      formatDateTime,
    }
  },
})
</script>

<style scoped>
.statistics-container {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0;
  font-size: 24px;
  font-weight: 500;
}

.header-actions {
  display: flex;
  gap: 10px;
  align-items: center;
}

.overview-row {
  margin-bottom: 20px;
}

.overview-card {
  height: 150px;
}

.card-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100px;
}

.card-icon {
  font-size: 36px;
  color: #409eff;
  margin-bottom: 10px;
}

.card-value {
  font-size: 28px;
  font-weight: bold;
  margin-bottom: 5px;
}

.card-title {
  font-size: 14px;
  color: #909399;
}

.chart-row {
  margin-bottom: 20px;
}

.chart-card {
  height: 400px;
}

.chart-content {
  height: 320px;
}

.data-card {
  height: 500px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.pagination-container {
  margin-top: 15px;
  text-align: right;
}

.webhook-detail {
  max-height: 60vh;
  overflow-y: auto;
}

.webhook-actions {
  margin-top: 20px;
  text-align: right;
}

.dark-theme .card-icon {
  color: #79bbff;
}

.dark-theme .card-title {
  color: #a8abb2;
}

@media (max-width: 768px) {
  .statistics-container {
    padding: 10px;
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .header-actions {
    margin-top: 10px;
    width: 100%;
    flex-wrap: wrap;
  }

  .header-actions .el-date-picker {
    width: 100%;
    margin-bottom: 10px;
  }

  .chart-content {
    height: 250px;
  }

  .pagination-container {
    text-align: center;
  }
}
</style>
