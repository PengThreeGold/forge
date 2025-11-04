<template>
  <div v-loading="loading" class="software-detail-container">
    <div class="page-header">
      <div class="page-title">
        <el-button icon="ArrowLeft" circle @click="goBack" />
        <h2>{{ space.name }}</h2>
      </div>
      <div class="page-actions">
        <el-button type="primary" @click="editSpace">
          <el-icon><Edit /></el-icon>
          编辑
        </el-button>
        <el-button type="warning" @click="showApiKey">
          <el-icon><Key /></el-icon>
          API密钥
        </el-button>
        <el-button type="success" @click="showCreateVersionDialog">
          <el-icon><Plus /></el-icon>
          上传版本
        </el-button>
      </div>
    </div>

    <el-row :gutter="20">
      <el-col :span="8">
        <el-card shadow="hover" class="info-card">
          <template #header>
            <span>基本信息</span>
          </template>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="软件名称">{{ space.name }}</el-descriptions-item>
            <el-descriptions-item label="作者">{{ space.author || '未设置' }}</el-descriptions-item>
            <el-descriptions-item label="创建时间">{{
              formatDateTime(space.created_at)
            }}</el-descriptions-item>
            <el-descriptions-item label="版本数">{{ versions.length }}</el-descriptions-item>
            <el-descriptions-item label="下载次数">{{
              space.downloads_count || 0
            }}</el-descriptions-item>
          </el-descriptions>

          <div class="description-box">
            <h3>描述</h3>
            <p>{{ space.description || '暂无描述' }}</p>
          </div>
        </el-card>
      </el-col>

      <el-col :span="16">
        <el-card shadow="hover" class="versions-card">
          <template #header>
            <div class="card-header">
              <span>版本列表</span>
              <el-radio-group v-model="versionFilter" size="small">
                <el-radio-button label="all">全部</el-radio-button>
                <el-radio-button label="published">已发布</el-radio-button>
                <el-radio-button label="unpublished">未发布</el-radio-button>
              </el-radio-group>
            </div>
          </template>

          <el-table :data="filteredVersions" style="width: 100%">
            <el-table-column prop="version" label="版本" width="120" />
            <el-table-column prop="file_size_human" label="文件大小" width="120" />
            <el-table-column prop="publish_date" label="发布时间" width="180">
              <template #default="scope">
                {{ scope.row.publish_date ? formatDateTime(scope.row.publish_date) : '未发布' }}
              </template>
            </el-table-column>
            <el-table-column prop="is_published" label="状态" width="100">
              <template #default="scope">
                <el-tag :type="scope.row.is_published ? 'success' : 'info'">
                  {{ scope.row.is_published ? '已发布' : '未发布' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="250">
              <template #default="scope">
                <el-button
                  v-if="scope.row.is_published"
                  type="primary"
                  size="small"
                  @click="downloadVersion(scope.row)"
                >
                  <el-icon><Download /></el-icon>
                  下载
                </el-button>
                <el-button
                  type="warning"
                  size="small"
                  @click="publishVersion(scope.row, !scope.row.is_published)"
                >
                  {{ scope.row.is_published ? '下架' : '发布' }}
                </el-button>
                <el-button type="danger" size="small" @click="confirmDeleteVersion(scope.row)">
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="chart-row">
      <el-col :span="24">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <div class="card-header">
              <span>下载统计</span>
              <el-radio-group v-model="chartDays" size="small" @change="loadTimelineData">
                <el-radio-button :label="7">7天</el-radio-button>
                <el-radio-button :label="30">30天</el-radio-button>
                <el-radio-button :label="90">90天</el-radio-button>
              </el-radio-group>
            </div>
          </template>
          <div ref="downloadChart" class="chart-content"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 创建版本对话框 -->
    <el-dialog
      v-model="versionDialogVisible"
      title="上传软件版本"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form ref="versionFormRef" :model="versionForm" :rules="versionRules" label-width="100px">
        <el-form-item label="版本号" prop="version">
          <el-input v-model="versionForm.version" placeholder="请输入版本号，如：1.0.0" />
        </el-form-item>

        <el-form-item label="选择文件" prop="file">
          <el-upload
            ref="upload"
            class="upload-demo"
            drag
            action="#"
            :auto-upload="false"
            :limit="1"
            :file-list="fileList"
            :on-change="handleFileChange"
            :on-remove="handleFileRemove"
          >
            <el-icon class="el-icon--upload"><upload-filled /></el-icon>
            <div class="el-upload__text">将文件拖到此处，或<em>点击上传</em></div>
            <template #tip>
              <div class="el-upload__tip">
                支持exe、msi、dmg、pkg、deb、rpm、zip、tar、gz、rar、7z等格式，且不超过500MB
              </div>
            </template>
          </el-upload>
        </el-form-item>

        <el-form-item label="发布说明" prop="release_note">
          <el-input
            v-model="versionForm.release_note"
            type="textarea"
            :rows="4"
            placeholder="请输入版本发布说明（可选）"
          />
        </el-form-item>

        <el-form-item label="文档地址" prop="documentation_url">
          <el-input v-model="versionForm.documentation_url" placeholder="请输入文档地址（可选）" />
        </el-form-item>
      </el-form>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="versionDialogVisible = false">取消</el-button>
          <el-button type="primary" :loading="uploadLoading" @click="handleUpload">
            确认上传
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- API密钥对话框 -->
    <el-dialog
      v-model="apiKeyDialogVisible"
      title="API密钥"
      width="600px"
      :close-on-click-modal="false"
    >
      <div class="api-key-container">
        <p class="api-key-desc">API密钥用于外部访问您的软件空间，请妥善保管：</p>
        <div class="api-key-box">
          <el-input v-model="currentApiKey" type="textarea" :rows="3" readonly />
          <el-button type="primary" @click="copyApiKey">
            <el-icon><CopyDocument /></el-icon>
            复制
          </el-button>
        </div>
        <div class="api-key-actions">
          <el-button type="warning" @click="regenerateApiKey">
            <el-icon><RefreshRight /></el-icon>
            重新生成
          </el-button>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { defineComponent, ref, reactive, computed, onMounted, nextTick } from 'vue'
import { useStore } from 'vuex'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import * as echarts from 'echarts'
import { formatDateTime } from '@/utils/common'

export default defineComponent({
  name: 'SoftwareDetail',
  setup() {
    const store = useStore()
    const router = useRouter()
    const route = useRoute()

    // 数据
    const space = ref({})
    const versions = ref([])
    const loading = ref(false)

    // 过滤器
    const versionFilter = ref('all')

    // 图表相关
    const downloadChart = ref(null)
    const chartDays = ref(30)
    const timelineData = ref([])
    let downloadChartInstance = null

    // 对话框相关
    const versionDialogVisible = ref(false)
    const uploadLoading = ref(false)

    // 表单
    const versionForm = reactive({
      version: '',
      file: null,
      release_note: '',
      documentation_url: '',
    })

    const versionRules = {
      version: [
        { required: true, message: '请输入版本号', trigger: 'blur' },
        { pattern: /^\d+\.\d+\.\d+$/, message: '版本号格式应为 x.y.z', trigger: 'blur' },
      ],
      file: [{ required: true, message: '请选择文件', trigger: 'change' }],
    }

    const versionFormRef = ref(null)
    const fileList = ref([])
    const upload = ref(null)

    // API密钥对话框
    const apiKeyDialogVisible = ref(false)
    const currentApiKey = ref('')

    // 计算属性
    const filteredVersions = computed(() => {
      if (versionFilter.value === 'all') {
        return versions.value
      } else if (versionFilter.value === 'published') {
        return versions.value.filter(v => v.is_published)
      } else {
        return versions.value.filter(v => !v.is_published)
      }
    })

    // 获取软件空间详情
    const getSpaceDetail = async () => {
      try {
        loading.value = true

        const spaceId = route.params.id
        const response = await store.dispatch('software/getSpace', spaceId)
        space.value = response.data

        // 获取版本列表
        await getVersions(spaceId)

        // 获取下载时间线数据
        await loadTimelineData()
      } catch (error) {
        console.error('获取软件空间详情失败:', error)
      } finally {
        loading.value = false
      }
    }

    // 获取版本列表
    const getVersions = async spaceId => {
      try {
        const response = await store.dispatch('software/getVersions', spaceId)
        versions.value = response.data
      } catch (error) {
        console.error('获取版本列表失败:', error)
      }
    }

    // 加载时间线数据
    const loadTimelineData = async () => {
      try {
        const response = await store.dispatch('statistics/getDownloadsTimeline', {
          days: chartDays.value,
          spaceId: route.params.id,
        })

        timelineData.value = response.data.timeline
        renderDownloadChart()
      } catch (error) {
        console.error('获取下载时间线数据失败:', error)
      }
    }

    // 渲染下载图表
    const renderDownloadChart = () => {
      if (!downloadChart.value) return

      if (downloadChartInstance) {
        downloadChartInstance.dispose()
      }

      downloadChartInstance = echarts.init(downloadChart.value)

      const dates = timelineData.value.map(item => item.date)
      const downloads = timelineData.value.map(item => item.downloads)

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

      downloadChartInstance.setOption(option)

      // 响应式调整
      window.addEventListener('resize', () => {
        downloadChartInstance && downloadChartInstance.resize()
      })
    }

    // 返回上一页
    const goBack = () => {
      router.push('/software')
    }

    // 编辑软件空间
    const editSpace = () => {
      router.push(`/software/${space.value.id}/edit`)
    }

    // 显示API密钥
    const showApiKey = () => {
      currentApiKey.value = space.value.api_key
      apiKeyDialogVisible.value = true
    }

    // 显示创建版本对话框
    const showCreateVersionDialog = () => {
      versionDialogVisible.value = true
    }

    // 处理文件变化
    const handleFileChange = file => {
      versionForm.file = file.raw
      fileList.value = [file]
    }

    // 处理文件移除
    const handleFileRemove = () => {
      versionForm.file = null
      fileList.value = []
    }

    // 处理上传
    const handleUpload = async () => {
      if (!versionFormRef.value) return

      try {
        await versionFormRef.value.validate()

        uploadLoading.value = true

        const spaceId = route.params.id
        await store.dispatch('software/createVersion', {
          spaceId,
          versionData: versionForm,
        })

        ElMessage.success('版本上传成功')
        versionDialogVisible.value = false
        resetVersionForm()
        getVersions(spaceId)
      } catch (error) {
        console.error('版本上传失败:', error)
      } finally {
        uploadLoading.value = false
      }
    }

    // 重置版本表单
    const resetVersionForm = () => {
      versionForm.version = ''
      versionForm.file = null
      versionForm.release_note = ''
      versionForm.documentation_url = ''
      fileList.value = []

      if (versionFormRef.value) {
        versionFormRef.value.resetFields()
      }

      if (upload.value) {
        upload.value.clearFiles()
      }
    }

    // 下载版本
    const downloadVersion = async version => {
      try {
        const response = await store.dispatch('software/downloadVersion', version.id)

        // 创建下载链接
        const url = window.URL.createObjectURL(new Blob([response.data]))
        const link = document.createElement('a')
        link.href = url

        // 获取文件名
        const contentDisposition = response.headers['content-disposition']
        let filename = `v${version.version}`

        if (contentDisposition) {
          const filenameRegex = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/
          const matches = filenameRegex.exec(contentDisposition)
          if (matches != null && matches[1]) {
            filename = matches[1].replace(/['"]/g, '')
          }
        }

        link.setAttribute('download', filename)
        document.body.appendChild(link)
        link.click()

        // 清理
        document.body.removeChild(link)
        window.URL.revokeObjectURL(url)
      } catch (error) {
        console.error('下载失败:', error)
      }
    }

    // 发布/下架版本
    const publishVersion = async (version, publish) => {
      try {
        await store.dispatch('software/publishVersion', {
          versionId: version.id,
          publish,
        })

        ElMessage.success(publish ? '版本发布成功' : '版本下架成功')
        getVersions(route.params.id)
      } catch (error) {
        console.error('操作失败:', error)
      }
    }

    // 确认删除版本
    const confirmDeleteVersion = version => {
      ElMessageBox.confirm(`确定要删除版本"${version.version}"吗？此操作不可逆。`, '删除确认', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      })
        .then(async () => {
          try {
            await store.dispatch('software/deleteVersion', version.id)
            ElMessage.success('删除成功')
            getVersions(route.params.id)
          } catch (error) {
            console.error('删除版本失败:', error)
          }
        })
        .catch(() => {
          // 用户取消删除
        })
    }

    // 复制API密钥
    const copyApiKey = async () => {
      try {
        await navigator.clipboard.writeText(currentApiKey.value)
        ElMessage.success('API密钥已复制到剪贴板')
      } catch (error) {
        ElMessage.error('复制失败，请手动复制')
      }
    }

    // 重新生成API密钥
    const regenerateApiKey = async () => {
      try {
        ElMessageBox.confirm('确定要重新生成API密钥吗？旧的API密钥将立即失效。', '确认操作', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning',
        })
          .then(async () => {
            const response = await store.dispatch('software/regenerateApiKey', route.params.id)
            currentApiKey.value = response.data.api_key
            ElMessage.success('API密钥已重新生成')
          })
          .catch(() => {
            // 用户取消操作
          })
      } catch (error) {
        console.error('重新生成API密钥失败:', error)
      }
    }

    onMounted(async () => {
      await getSpaceDetail()

      // 等待DOM更新后渲染图表
      await nextTick()
      renderDownloadChart()
    })

    return {
      space,
      versions,
      loading,
      versionFilter,
      filteredVersions,
      downloadChart,
      chartDays,
      versionDialogVisible,
      uploadLoading,
      versionForm,
      versionRules,
      versionFormRef,
      fileList,
      upload,
      apiKeyDialogVisible,
      currentApiKey,
      goBack,
      editSpace,
      showApiKey,
      showCreateVersionDialog,
      handleFileChange,
      handleFileRemove,
      handleUpload,
      downloadVersion,
      publishVersion,
      confirmDeleteVersion,
      copyApiKey,
      regenerateApiKey,
      loadTimelineData,
      formatDateTime,
    }
  },
})
</script>

<style scoped>
.software-detail-container {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-title {
  display: flex;
  align-items: center;
}

.page-title h2 {
  margin: 0 0 0 10px;
  font-size: 24px;
  font-weight: 500;
}

.page-actions {
  display: flex;
  gap: 10px;
}

.info-card,
.versions-card {
  margin-bottom: 20px;
}

.description-box {
  margin-top: 20px;
}

.description-box h3 {
  margin: 0 0 10px;
  font-size: 16px;
  font-weight: 500;
}

.description-box p {
  margin: 0;
  color: #606266;
  line-height: 1.6;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chart-row {
  margin-top: 20px;
}

.chart-card {
  height: 400px;
}

.chart-content {
  height: 320px;
}

.upload-demo {
  width: 100%;
}

.el-upload__tip {
  color: #909399;
  font-size: 12px;
  margin-top: 7px;
}

.api-key-container {
  padding: 10px 0;
}

.api-key-desc {
  margin-bottom: 15px;
  color: #606266;
}

.api-key-box {
  display: flex;
  margin-bottom: 15px;
}

.api-key-box .el-textarea {
  flex: 1;
  margin-right: 10px;
}

.api-key-actions {
  text-align: right;
}

.dark-theme .description-box p {
  color: #cfd3dc;
}

.dark-theme .el-upload__tip {
  color: #a8abb2;
}

.dark-theme .api-key-desc {
  color: #cfd3dc;
}

@media (max-width: 768px) {
  .software-detail-container {
    padding: 10px;
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .page-actions {
    margin-top: 10px;
    width: 100%;
    justify-content: flex-end;
  }

  .page-actions .el-button {
    margin-left: 0;
  }

  .chart-content {
    height: 250px;
  }
}
</style>
