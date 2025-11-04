<template>
  <div v-loading="loading" class="public-software-detail-container">
    <div class="page-header">
      <div class="header-content">
        <el-button icon="ArrowLeft" @click="goBack">返回</el-button>
        <div class="header-title">
          <h1>{{ software.name }}</h1>
          <div class="software-meta">
            <span class="author">作者: {{ software.author || '未知' }}</span>
            <span class="publish-date">{{ formatDate(software.created_at) }}</span>
            <div class="download-stats">
              <el-icon><Download /></el-icon>
              <span>{{ formatNumber(software.downloads_count || 0) }} 次下载</span>
            </div>
          </div>
        </div>
        <div class="header-actions">
          <el-button
            type="primary"
            size="large"
            :loading="downloading"
            @click="downloadLatestVersion"
          >
            <el-icon><Download /></el-icon>
            下载最新版
          </el-button>
        </div>
      </div>
    </div>

    <div class="content-wrapper">
      <el-row :gutter="24">
        <el-col :span="18">
          <!-- 软件描述 -->
          <el-card shadow="never" class="description-card">
            <template #header>
              <span>软件介绍</span>
            </template>
            <div class="software-description">
              <p v-if="software.description">{{ software.description }}</p>
              <p v-else class="no-description">暂无描述</p>
            </div>
          </el-card>

          <!-- 版本历史 -->
          <el-card shadow="never" class="versions-card">
            <template #header>
              <div class="card-header">
                <span>版本历史</span>
                <el-radio-group v-model="versionFilter" size="small">
                  <el-radio-button label="all">全部</el-radio-button>
                  <el-radio-button label="stable">稳定版</el-radio-button>
                  <el-radio-button label="prerelease">预发布</el-radio-button>
                </el-radio-group>
              </div>
            </template>

            <div class="version-list">
              <div
                v-for="version in filteredVersions"
                :key="version.id"
                class="version-item"
                :class="{ 'is-latest': version.is_latest }"
              >
                <div class="version-header">
                  <div class="version-info">
                    <el-tag :type="version.is_latest ? 'danger' : 'primary'" size="large">
                      {{ version.version }}
                    </el-tag>
                    <el-tag v-if="version.is_latest" type="danger" size="small">Latest</el-tag>
                    <el-tag v-if="version.is_prerelease" type="warning" size="small"
                      >Pre-release</el-tag
                    >
                    <span class="publish-date">
                      {{ formatDateTime(version.publish_date || version.created_at) }}
                    </span>
                  </div>
                  <div class="version-actions">
                    <el-button
                      v-if="version.is_published"
                      type="primary"
                      size="small"
                      :loading="downloading === version.id"
                      @click="downloadVersion(version)"
                    >
                      <el-icon><Download /></el-icon>
                      下载
                    </el-button>
                  </div>
                </div>

                <div class="version-content">
                  <div v-if="version.release_note" class="release-note">
                    <div
                      class="note-content"
                      v-html="formatReleaseNote(version.release_note)"
                    ></div>
                    <el-button
                      v-if="version.release_note.length > 300"
                      type="text"
                      @click="toggleReleaseNote(version)"
                    >
                      {{ version.showFull ? '收起' : '展开全部' }}
                    </el-button>
                  </div>
                  <div class="no-release-note" v-else>暂无发布说明</div>
                </div>

                <div class="version-assets" v-if="version.is_published && version.file_size_human">
                  <div class="asset-info">
                    <el-icon class="asset-icon"><Document /></el-icon>
                    <span class="asset-name">{{ version.version }} 安装包</span>
                    <span class="asset-size">{{ version.file_size_human }}</span>
                  </div>
                </div>
              </div>

              <el-empty v-if="filteredVersions.length === 0" description="暂无版本" />
            </div>
          </el-card>
        </el-col>

        <el-col :span="6">
          <!-- 软件信息 -->
          <el-card shadow="never" class="info-card">
            <template #header>
              <span>软件信息</span>
            </template>

            <div class="info-item">
              <span class="info-label">作者:</span>
              <span class="info-value">{{ software.author || '未知' }}</span>
            </div>

            <div class="info-item">
              <span class="info-label">创建时间:</span>
              <span class="info-value">{{ formatDate(software.created_at) }}</span>
            </div>

            <div class="info-item">
              <span class="info-label">版本数:</span>
              <span class="info-value">{{ versions.length }}</span>
            </div>

            <div class="info-item">
              <span class="info-label">总下载量:</span>
              <span class="info-value">{{ formatNumber(software.downloads_count || 0) }}</span>
            </div>

            <div class="info-item">
              <span class="info-label">最新版本:</span>
              <el-tag type="primary" size="small">{{ getLatestVersion() }}</el-tag>
            </div>
          </el-card>

          <!-- 下载统计 -->
          <el-card shadow="never" class="stats-card">
            <template #header>
              <span>下载统计</span>
            </template>

            <div class="stats-item">
              <div class="stats-value">
                {{ formatNumber(software.downloads_count || 0) }}
              </div>
              <div class="stats-label">总下载量</div>
            </div>

            <div class="stats-item">
              <div class="stats-value">{{ getVersionDownloads() }}</div>
              <div class="stats-label">最新版本下载</div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script>
import { defineComponent, ref, reactive, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Download, Document, ArrowLeft } from '@element-plus/icons-vue'
import { getSpaceInfo, getVersionsInfo, downloadVersionPublic } from '@/api/software'
import { formatDateTime } from '@/utils/common'

export default defineComponent({
  name: 'PublicSoftwareDetail',
  setup() {
    const router = useRouter()
    const route = useRoute()

    // 数据
    const software = ref({})
    const versions = ref([])
    const loading = ref(false)
    const downloading = ref(null)
    const versionFilter = ref('all')

    // 计算属性
    const softwareId = computed(() => route.params.id)

    const filteredVersions = computed(() => {
      let result = [...versions.value]

      // 过滤版本
      switch (versionFilter.value) {
        case 'stable':
          result = result.filter(v => v.is_published && !v.is_prerelease)
          break
        case 'prerelease':
          result = result.filter(v => v.is_published && v.is_prerelease)
          break
        default:
          result = result.filter(v => v.is_published)
      }

      // 按创建时间降序排序
      result.sort((a, b) => new Date(b.created_at) - new Date(a.created_at))

      return result
    })

    // 获取软件信息
    const getSoftwareInfo = async () => {
      try {
        loading.value = true

        // 这里需要根据软件ID获取软件信息
        // 由于当前API设计，我们需要通过API密钥获取信息
        // 在实际应用中，应该有专门的公共API通过软件ID获取信息
        // 这里使用模拟数据
        const mockSoftware = {
          id: softwareId.value,
          name: '示例软件',
          author: '示例作者',
          description:
            '这是一个示例软件的描述，用于展示软件详情页面的功能。软件具有强大的功能和友好的用户界面。',
          created_at: '2023-01-15T10:30:00Z',
          downloads_count: 1250,
          api_key: 'demo-api-key',
        }

        software.value = mockSoftware

        // 获取版本列表
        if (mockSoftware.api_key) {
          await getVersions(mockSoftware.api_key)
        }
      } catch (error) {
        console.error('获取软件信息失败:', error)
        ElMessage.error('获取软件信息失败')
      } finally {
        loading.value = false
      }
    }

    // 获取版本列表
    const getVersions = async apiKey => {
      try {
        const response = await getVersionsInfo(apiKey)
        if (response && response.data) {
          versions.value = Array.isArray(response.data)
            ? response.data.map(v => ({
                ...v,
                showFull: false,
              }))
            : []
        } else {
          versions.value = []
        }
      } catch (error) {
        console.error('获取版本列表失败:', error)
        // 使用模拟数据
        versions.value = [
          {
            id: '1',
            version: 'v1.2.0',
            release_note:
              '这是v1.2.0版本的发布说明。\n\n主要更新：\n- 修复了一些已知问题\n- 提升了性能\n- 改进了用户界面\n\n感谢所有用户的反馈和支持！',
            is_published: true,
            is_prerelease: false,
            is_latest: true,
            publish_date: '2023-05-15T10:30:00Z',
            created_at: '2023-05-15T10:30:00Z',
            file_size_human: '25.3 MB',
            download_count: 450,
          },
          {
            id: '2',
            version: 'v1.1.0',
            release_note:
              '这是v1.1.0版本的发布说明。\n\n主要更新：\n- 新增了一些功能\n- 修复了一些bug',
            is_published: true,
            is_prerelease: false,
            is_latest: false,
            publish_date: '2023-04-10T10:30:00Z',
            created_at: '2023-04-10T10:30:00Z',
            file_size_human: '24.8 MB',
            download_count: 300,
          },
          {
            id: '3',
            version: 'v1.1.1-beta',
            release_note: '这是一个预发布版本，用于测试新功能。',
            is_published: true,
            is_prerelease: true,
            is_latest: false,
            publish_date: '2023-05-10T10:30:00Z',
            created_at: '2023-05-10T10:30:00Z',
            file_size_human: '25.1 MB',
            download_count: 50,
          },
        ]
      }
    }

    // 下载最新版本
    const downloadLatestVersion = () => {
      const latestVersion = versions.value.find(v => v.is_latest)
      if (latestVersion) {
        downloadVersion(latestVersion)
      } else if (filteredVersions.value.length > 0) {
        downloadVersion(filteredVersions.value[0])
      } else {
        ElMessage.error('暂无可下载的版本')
      }
    }

    // 下载指定版本
    const downloadVersion = async version => {
      try {
        downloading.value = version.id

        const apiKey = software.value.api_key
        if (!apiKey) {
          ElMessage.error('无法获取下载链接')
          return
        }

        const response = await downloadVersionPublic(apiKey, version.version)

        // 创建下载链接
        const url = window.URL.createObjectURL(new Blob([response.data]))
        const link = document.createElement('a')
        link.href = url

        // 获取文件名
        let filename = `${version.version}`
        const contentDisposition = response.headers['content-disposition']
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
        ElMessage.error('下载失败')
      } finally {
        downloading.value = null
      }
    }

    // 切换发布说明展开/收起
    const toggleReleaseNote = version => {
      version.showFull = !version.showFull
    }

    // 格式化发布说明
    const formatReleaseNote = note => {
      if (!note) return ''

      // 简单的Markdown转HTML
      return note
        .replace(/\n/g, '<br>')
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/`(.*?)`/g, '<code>$1</code>')
        .replace(/(https?:\/\/[^\s]+)/g, '<a href="$1" target="_blank">$1</a>')
    }

    // 获取最新版本
    const getLatestVersion = () => {
      const latestVersion = versions.value.find(v => v.is_latest)
      return latestVersion
        ? latestVersion.version
        : versions.value.length > 0
          ? versions.value[0].version
          : '无'
    }

    // 获取最新版本的下载量
    const getVersionDownloads = () => {
      const latestVersion = versions.value.find(v => v.is_latest)
      return formatNumber(latestVersion ? latestVersion.download_count || 0 : 0)
    }

    // 格式化数字
    const formatNumber = num => {
      if (num >= 1000000) {
        return (num / 1000000).toFixed(1) + 'M'
      } else if (num >= 1000) {
        return (num / 1000).toFixed(1) + 'K'
      }
      return num.toString()
    }

    // 格式化日期
    const formatDate = dateStr => {
      if (!dateStr) return '未知'
      const date = new Date(dateStr)
      return date.toLocaleDateString('zh-CN')
    }

    // 返回上一页
    const goBack = () => {
      router.push('/public')
    }

    onMounted(() => {
      getSoftwareInfo()
    })

    return {
      software,
      versions,
      loading,
      downloading,
      versionFilter,
      filteredVersions,
      downloadLatestVersion,
      downloadVersion,
      toggleReleaseNote,
      formatReleaseNote,
      getLatestVersion,
      getVersionDownloads,
      formatNumber,
      formatDate,
      goBack,
      formatDateTime,
      Download,
      Document,
      ArrowLeft,
    }
  },
})
</script>

<style scoped>
.public-software-detail-container {
  min-height: 100vh;
  background-color: #f5f7fa;
  padding: 0;
}

.page-header {
  background-color: #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 24px 0;
  margin-bottom: 24px;
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 0 20px;
}

.header-title h1 {
  margin: 0 0 12px 0;
  font-size: 32px;
  font-weight: 600;
  color: #303133;
}

.software-meta {
  display: flex;
  align-items: center;
  gap: 16px;
  color: #909399;
  font-size: 14px;
}

.download-stats {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #409eff;
}

.content-wrapper {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.description-card,
.versions-card,
.info-card,
.stats-card {
  margin-bottom: 24px;
  border-radius: 8px;
}

.software-description {
  line-height: 1.6;
  color: #606266;
}

.no-description {
  color: #909399;
  font-style: italic;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.version-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.version-item {
  padding: 20px;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  background-color: #fff;
}

.version-item.is-latest {
  border-color: #f56c6c;
  box-shadow: 0 0 0 1px rgba(245, 108, 108, 0.2);
}

.version-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.version-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.publish-date {
  color: #909399;
  font-size: 14px;
}

.version-actions {
  flex-shrink: 0;
}

.version-content {
  margin-bottom: 16px;
}

.release-note {
  margin-bottom: 8px;
}

.note-content {
  line-height: 1.6;
  color: #606266;
  max-height: 120px;
  overflow: hidden;
}

.no-release-note {
  color: #909399;
  font-style: italic;
}

.version-assets {
  padding-top: 16px;
  border-top: 1px solid #ebeef5;
}

.asset-info {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #606266;
}

.asset-icon {
  color: #409eff;
}

.asset-name {
  font-weight: 500;
}

.asset-size {
  color: #909399;
  font-size: 14px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #ebeef5;
}

.info-item:last-child {
  border-bottom: none;
}

.info-label {
  color: #909399;
}

.info-value {
  color: #303133;
  font-weight: 500;
}

.stats-item {
  text-align: center;
  padding: 16px 0;
}

.stats-value {
  font-size: 24px;
  font-weight: 600;
  color: #409eff;
  margin-bottom: 8px;
}

.stats-label {
  color: #909399;
  font-size: 14px;
}

/* 暗色主题 */
.dark-theme .public-software-detail-container {
  background-color: #141414;
}

.dark-theme .page-header {
  background-color: #1d2935;
}

.dark-theme .header-title h1 {
  color: #e5eaf3;
}

.dark-theme .software-meta {
  color: #a8abb2;
}

.dark-theme .description-card,
.dark-theme .versions-card,
.dark-theme .info-card,
.dark-theme .stats-card {
  background-color: #1d2935;
  border-color: #4c4d4f;
}

.dark-theme .software-description {
  color: #cfd3dc;
}

.dark-theme .version-item {
  background-color: #1d2935;
  border-color: #4c4d4f;
}

.dark-theme .version-item.is-latest {
  border-color: #ef9a9a;
  box-shadow: 0 0 0 1px rgba(239, 154, 154, 0.2);
}

.dark-theme .note-content {
  color: #cfd3dc;
}

.dark-theme .no-release-note,
.dark-theme .no-description {
  color: #7c7e81;
}

.dark-theme .version-assets {
  border-top-color: #4c4d4f;
}

.dark-theme .asset-info {
  color: #cfd3dc;
}

.dark-theme .info-item {
  border-bottom-color: #4c4d4f;
}

.dark-theme .info-value {
  color: #e5eaf3;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .header-content {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }

  .header-title {
    text-align: center;
  }

  .software-meta {
    justify-content: center;
  }
}

@media (max-width: 768px) {
  .header-content {
    padding: 0 16px;
  }

  .content-wrapper {
    padding: 0 16px;
  }

  .header-title h1 {
    font-size: 24px;
  }

  .software-meta {
    flex-wrap: wrap;
    gap: 8px;
  }

  .version-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .version-info {
    flex-wrap: wrap;
    gap: 8px;
  }
}
</style>
