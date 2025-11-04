<template>
  <div class="dashboard-container">
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card shadow="hover" class="dashboard-card">
          <template #header>
            <div class="card-header">
              <span>软件空间</span>
              <el-tag type="primary" size="small">{{ overview.spaces_count || 0 }}</el-tag>
            </div>
          </template>
          <div class="card-content">
            <div class="card-icon">
              <el-icon><FolderOpened /></el-icon>
            </div>
            <div class="card-value">{{ overview.spaces_count || 0 }}</div>
            <div class="card-desc">已创建的软件空间总数</div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card shadow="hover" class="dashboard-card">
          <template #header>
            <div class="card-header">
              <span>软件版本</span>
              <el-tag type="success" size="small">{{ overview.versions_count || 0 }}</el-tag>
            </div>
          </template>
          <div class="card-content">
            <div class="card-icon">
              <el-icon><Document /></el-icon>
            </div>
            <div class="card-value">{{ overview.versions_count || 0 }}</div>
            <div class="card-desc">已发布的软件版本总数</div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card shadow="hover" class="dashboard-card">
          <template #header>
            <div class="card-header">
              <span>下载总量</span>
              <el-tag type="warning" size="small">{{ overview.total_downloads || 0 }}</el-tag>
            </div>
          </template>
          <div class="card-content">
            <div class="card-icon">
              <el-icon><Download /></el-icon>
            </div>
            <div class="card-value">{{ overview.total_downloads || 0 }}</div>
            <div class="card-desc">软件下载总次数</div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card shadow="hover" class="dashboard-card">
          <template #header>
            <div class="card-header">
              <span>独立用户</span>
              <el-tag type="info" size="small">{{ overview.unique_ips || 0 }}</el-tag>
            </div>
          </template>
          <div class="card-content">
            <div class="card-icon">
              <el-icon><User /></el-icon>
            </div>
            <div class="card-value">{{ overview.unique_ips || 0 }}</div>
            <div class="card-desc">独立IP下载用户数</div>
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
              <el-button type="text" @click="router.push('/statistics')">查看更多</el-button>
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
              <span>最新下载记录</span>
              <el-button type="text" @click="router.push('/statistics')">查看更多</el-button>
            </div>
          </template>
          <el-table :data="overview.recent_downloads || []" style="width: 100%" max-height="300">
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
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card shadow="hover" class="data-card">
          <template #header>
            <div class="card-header">
              <span>热门版本</span>
              <el-button type="text" @click="router.push('/statistics')">查看更多</el-button>
            </div>
          </template>
          <el-table :data="overview.versions_downloads || []" style="width: 100%" max-height="300">
            <el-table-column
              prop="space_name"
              label="软件名称"
              min-width="120"
              show-overflow-tooltip
            />
            <el-table-column prop="version" label="版本" width="100" />
            <el-table-column prop="downloads" label="下载次数" width="100" />
            <el-table-column label="操作" width="100">
              <template #default="scope">
                <el-button type="text" @click="viewSoftware(scope.row.space_name)">查看</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import { defineComponent, ref, reactive, onMounted, nextTick } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'
import * as echarts from 'echarts'
import { formatDateTime } from '@/utils/common'

export default defineComponent({
  name: 'Dashboard',
  setup() {
    const store = useStore()
    const router = useRouter()

    // 数据
    const overview = reactive({})
    const timeline = ref([])
    const timelineDays = ref(30)

    // 图表引用
    const downloadTimelineChart = ref(null)
    const popularSoftwareChart = ref(null)

    // 图表实例
    let downloadTimelineChartInstance = null
    let popularSoftwareChartInstance = null

    // 获取概览数据
    const getOverviewData = async () => {
      try {
        store.dispatch('setLoading', true)

        const response = await store.dispatch('statistics/getOverview')
        Object.assign(overview, response.data)
      } catch (error) {
        console.error('获取概览数据失败:', error)
      } finally {
        store.dispatch('setLoading', false)
      }
    }

    // 获取下载时间线数据
    const getTimelineData = async () => {
      try {
        store.dispatch('setLoading', true)

        const response = await store.dispatch('statistics/getDownloadsTimeline', {
          days: timelineDays.value,
        })

        timeline.value = response.data.timeline
        renderDownloadTimelineChart()
      } catch (error) {
        console.error('获取下载时间线数据失败:', error)
      } finally {
        store.dispatch('setLoading', false)
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

    // 处理时间线天数变化
    const handleTimelineDaysChange = () => {
      getTimelineData()
    }

    // 查看软件详情
    const viewSoftware = softwareName => {
      // 跳转到软件列表页并搜索该软件
      store.dispatch('software/getSpaces').then(() => {
        const space = store.getters['software/spaces'].find(s => s.name === softwareName)
        if (space) {
          // 跳转到软件详情页
          // 这里需要先获取软件空间ID，然后跳转到详情页
          // 由于前端架构限制，这里先跳转到软件列表页
          // 在实际应用中，可以直接跳转到软件详情页
          // 例如：router.push(`/software/${space.id}`)
          router.push('/software')
        }
      })
    }

    onMounted(async () => {
      // 获取数据
      await getOverviewData()
      await getTimelineData()

      // 等待DOM更新后渲染图表
      await nextTick()
      renderDownloadTimelineChart()
      renderPopularSoftwareChart()
    })

    return {
      overview,
      timeline,
      timelineDays,
      downloadTimelineChart,
      popularSoftwareChart,
      handleTimelineDaysChange,
      viewSoftware,
      formatDateTime,
    }
  },
})
</script>

<style scoped>
.dashboard-container {
  padding: 20px;
}

.dashboard-card {
  height: 180px;
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
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

.card-desc {
  font-size: 14px;
  color: #909399;
}

.chart-row,
.data-row {
  margin-top: 20px;
}

.chart-card {
  height: 400px;
}

.chart-content {
  height: 320px;
}

.data-card {
  height: 400px;
}

.dark-theme .card-icon {
  color: #79bbff;
}

.dark-theme .card-desc {
  color: #a8abb2;
}

@media (max-width: 768px) {
  .dashboard-container {
    padding: 10px;
  }

  .el-col {
    margin-bottom: 10px;
  }

  .chart-row .el-col,
  .data-row .el-col {
    margin-bottom: 0;
  }

  .chart-content {
    height: 250px;
  }
}
</style>
