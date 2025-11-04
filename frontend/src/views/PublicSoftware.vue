<template>
  <div class="public-software-container">
    <div class="page-header">
      <div class="header-content">
        <div class="logo-container">
          <div class="logo">Forge</div>
          <div class="tagline">软件发布管理平台</div>
        </div>
        <div class="header-actions">
          <el-input
            v-model="searchKeyword"
            placeholder="搜索软件..."
            class="search-input"
            @keyup.enter="handleSearch"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
          <el-button type="primary" @click="goToLogin"> 管理员登录 </el-button>
        </div>
      </div>
    </div>

    <div class="content-wrapper">
      <div class="filter-sidebar">
        <el-card class="filter-card" shadow="never">
          <template #header>
            <div class="card-header">
              <el-icon><Filter /></el-icon>
              <span>筛选条件</span>
            </div>
          </template>

          <div class="filter-section">
            <div class="section-title">分类</div>
            <el-radio-group v-model="selectedCategory" @change="handleFilterChange">
              <el-radio label="all" class="filter-radio">全部</el-radio>
              <el-radio label="productivity" class="filter-radio">生产力工具</el-radio>
              <el-radio label="development" class="filter-radio">开发工具</el-radio>
              <el-radio label="utility" class="filter-radio">实用工具</el-radio>
              <el-radio label="multimedia" class="filter-radio">多媒体</el-radio>
            </el-radio-group>
          </div>

          <div class="filter-section">
            <div class="section-title">排序方式</div>
            <el-select v-model="sortBy" class="sort-select" @change="handleFilterChange">
              <el-option label="最新发布" value="latest" />
              <el-option label="下载最多" value="downloads" />
              <el-option label="名称排序" value="name" />
            </el-select>
          </div>
        </el-card>
      </div>

      <div class="software-grid">
        <div v-loading="loading" class="grid-container">
          <el-empty v-if="!loading && filteredSpaces.length === 0" description="暂无软件" />

          <div v-for="space in paginatedSpaces" :key="space.id" class="software-card">
            <el-card shadow="hover" class="card-content" @click="viewSoftware(space)">
              <div class="card-header">
                <div class="software-info">
                  <div class="software-icon">
                    <el-icon :size="32"><FolderOpened /></el-icon>
                  </div>
                  <div class="software-details">
                    <h3 class="software-name">{{ space.name }}</h3>
                    <div class="software-author">作者: {{ space.author || '未知' }}</div>
                  </div>
                </div>
                <div class="download-count">
                  <el-icon><Download /></el-icon>
                  <span>{{ formatNumber(space.downloads_count || 0) }}</span>
                </div>
              </div>

              <div class="software-description">
                {{ space.description || '暂无描述' }}
              </div>

              <div class="software-meta">
                <div class="version-info">
                  <el-tag type="success" size="small">
                    {{ getLatestVersion(space) }}
                  </el-tag>
                  <span class="publish-date">
                    {{ formatDate(space.updated_at || space.created_at) }}
                  </span>
                </div>
                <div class="action-buttons">
                  <el-button type="primary" size="small" @click.stop="downloadLatest(space)">
                    <el-icon><Download /></el-icon>
                    下载
                  </el-button>
                  <el-button size="small" @click.stop="viewSoftware(space)"> 查看详情 </el-button>
                </div>
              </div>
            </el-card>
          </div>
        </div>

        <div class="pagination-container">
          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[12, 24, 48]"
            :total="total"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
          />
        </div>
      </div>
    </div>

    <!-- 软件详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      :title="currentSoftware.name"
      width="800px"
      class="software-detail-dialog"
    >
      <div v-loading="detailLoading" class="detail-content">
        <div class="detail-header">
          <div class="software-icon-large">
            <el-icon :size="64"><FolderOpened /></el-icon>
          </div>
          <div class="software-info-detail">
            <h2>{{ currentSoftware.name }}</h2>
            <p class="author">作者: {{ currentSoftware.author || '未知' }}</p>
            <p class="description">{{ currentSoftware.description || '暂无描述' }}</p>
            <div class="software-stats">
              <div class="stat-item">
                <el-icon><Download /></el-icon>
                <span>下载次数: {{ formatNumber(currentSoftware.downloads_count || 0) }}</span>
              </div>
              <div class="stat-item">
                <el-icon><Document /></el-icon>
                <span>版本数: {{ versions.length }}</span>
              </div>
            </div>
          </div>
        </div>

        <div class="version-list">
          <h3>版本历史</h3>
          <el-table :data="versions" style="width: 100%">
            <el-table-column prop="version" label="版本" width="120" />
            <el-table-column prop="file_size_human" label="文件大小" width="120" />
            <el-table-column prop="publish_date" label="发布时间" width="180">
              <template #default="scope">
                {{ scope.row.publish_date ? formatDate(scope.row.publish_date) : '未发布' }}
              </template>
            </el-table-column>
            <el-table-column prop="is_published" label="状态" width="100">
              <template #default="scope">
                <el-tag :type="scope.row.is_published ? 'success' : 'info'">
                  {{ scope.row.is_published ? '已发布' : '未发布' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="150">
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
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="detailDialogVisible = false">关闭</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { defineComponent, ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { FolderOpened, Download, Document, Filter, Search } from '@element-plus/icons-vue'
import {
  getPublicSpaces,
  getSpaceInfo,
  getVersionsInfo,
  downloadVersionPublic,
} from '@/api/software'

export default defineComponent({
  name: 'PublicSoftware',
  setup() {
    const router = useRouter()

    // 数据
    const spaces = ref([])
    const loading = ref(false)
    const searchKeyword = ref('')
    const selectedCategory = ref('all')
    const sortBy = ref('latest')
    const currentPage = ref(1)
    const pageSize = ref(12)
    const total = ref(0)

    // 对话框相关
    const detailDialogVisible = ref(false)
    const detailLoading = ref(false)
    const currentSoftware = ref({})
    const versions = ref([])

    // 计算属性
    const filteredSpaces = computed(() => {
      if (!spaces.value || !Array.isArray(spaces.value)) {
        return []
      }

      let result = [...spaces.value]

      // 搜索过滤
      if (searchKeyword.value) {
        const keyword = searchKeyword.value.toLowerCase()
        result = result.filter(
          space =>
            (space && space.name && space.name.toLowerCase().includes(keyword)) ||
            (space.author && space.author.toLowerCase().includes(keyword)) ||
            (space.description && space.description.toLowerCase().includes(keyword))
        )
      }

      // 分类过滤 (这里假设后端会提供分类信息，目前只是示例)
      if (selectedCategory.value !== 'all') {
        // result = result.filter(space => space.category === selectedCategory.value)
      }

      // 排序
      switch (sortBy.value) {
        case 'latest':
          result.sort(
            (a, b) =>
              new Date(b.updated_at || b.created_at) - new Date(a.updated_at || a.created_at)
          )
          break
        case 'downloads':
          result.sort((a, b) => (b.downloads_count || 0) - (a.downloads_count || 0))
          break
        case 'name':
          result.sort((a, b) => a.name.localeCompare(b.name))
          break
      }

      return result
    })

    const paginatedSpaces = computed(() => {
      const start = (currentPage.value - 1) * pageSize.value
      const end = start + pageSize.value
      return filteredSpaces.value.slice(start, end)
    })

    // 获取软件列表
    const getSpaces = async () => {
      try {
        loading.value = true
        // 使用公共API获取所有软件空间列表
        const response = await getPublicSpaces()
        if (response && response.data && Array.isArray(response.data)) {
          // 只显示有已发布版本的软件空间
          spaces.value = response.data.filter(space => {
            return space && space.versions_count && space.versions_count > 0
          })
        } else {
          spaces.value = []
        }
      } catch (error) {
        console.error('获取软件列表失败:', error)
        ElMessage.error('获取软件列表失败')
        spaces.value = []
      } finally {
        loading.value = false
      }
    }

    // 获取软件版本列表
    const getVersions = async apiKey => {
      try {
        detailLoading.value = true
        const response = await getVersionsInfo(apiKey)
        if (response && response.data) {
          versions.value = Array.isArray(response.data) ? response.data : []
        } else {
          versions.value = []
        }
      } catch (error) {
        console.error('获取版本列表失败:', error)
        ElMessage.error('获取版本列表失败')
        versions.value = []
      } finally {
        detailLoading.value = false
      }
    }

    // 查看软件详情
    const viewSoftware = async software => {
      currentSoftware.value = software
      detailDialogVisible.value = true

      // 获取版本列表
      if (software.api_key) {
        await getVersions(software.api_key)
      }
    }

    // 获取最新版本
    const getLatestVersion = software => {
      // 这里应该从versions数据中获取最新版本，目前使用占位符
      return 'v1.0.0'
    }

    // 下载最新版本
    const downloadLatest = software => {
      if (software.api_key) {
        const version = getLatestVersion(software)
        downloadVersion({ version, api_key: software.api_key, name: software.name })
      } else {
        ElMessage.error('无法获取下载链接')
      }
    }

    // 下载指定版本
    const downloadVersion = async version => {
      try {
        const apiKey = currentSoftware.value.api_key
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
        let filename = `${version.version || 'download'}`
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
      }
    }

    // 处理搜索
    const handleSearch = () => {
      currentPage.value = 1
    }

    // 处理筛选变化
    const handleFilterChange = () => {
      currentPage.value = 1
    }

    // 处理分页大小变化
    const handleSizeChange = size => {
      pageSize.value = size
      currentPage.value = 1
    }

    // 处理当前页变化
    const handleCurrentChange = page => {
      currentPage.value = page
    }

    // 跳转到登录页
    const goToLogin = () => {
      router.push('/login')
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

    // 监听 filteredSpaces 的变化，更新总数
    watch(filteredSpaces, newValue => {
      total.value = newValue ? newValue.length : 0
    })

    onMounted(() => {
      getSpaces()
    })

    return {
      spaces,
      loading,
      searchKeyword,
      selectedCategory,
      sortBy,
      currentPage,
      pageSize,
      total,
      paginatedSpaces,
      detailDialogVisible,
      detailLoading,
      currentSoftware,
      versions,
      handleSearch,
      handleFilterChange,
      handleSizeChange,
      handleCurrentChange,
      viewSoftware,
      downloadLatest,
      downloadVersion,
      getLatestVersion,
      goToLogin,
      formatNumber,
      formatDate,
      FolderOpened,
      Download,
      Document,
      Filter,
      Search,
    }
  },
})
</script>

<style scoped>
.public-software-container {
  min-height: 100vh;
  background-color: #f5f7fa;
}

.page-header {
  background-color: #fff;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  padding: 16px 0;
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
}

.logo-container {
  display: flex;
  align-items: baseline;
}

.logo {
  font-size: 28px;
  font-weight: bold;
  color: #409eff;
  margin-right: 12px;
}

.tagline {
  font-size: 14px;
  color: #909399;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.search-input {
  width: 300px;
}

.content-wrapper {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  gap: 20px;
  padding: 20px;
}

.filter-sidebar {
  width: 240px;
  flex-shrink: 0;
}

.filter-card {
  border-radius: 8px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
}

.filter-section {
  margin-bottom: 24px;
}

.section-title {
  font-weight: 600;
  margin-bottom: 12px;
  color: #303133;
}

.filter-radio {
  display: block;
  margin-bottom: 8px;
}

.sort-select {
  width: 100%;
}

.software-grid {
  flex: 1;
}

.grid-container {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 20px;
  min-height: 400px;
}

.software-card {
  height: 100%;
}

.card-content {
  height: 100%;
  cursor: pointer;
  transition: all 0.3s;
}

.card-content:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
}

.software-info {
  display: flex;
  align-items: flex-start;
  gap: 12px;
}

.software-icon {
  color: #409eff;
  flex-shrink: 0;
}

.software-details {
  flex: 1;
}

.software-name {
  margin: 0 0 4px 0;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.software-author {
  font-size: 14px;
  color: #909399;
  margin: 0;
}

.download-count {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #409eff;
  font-size: 14px;
}

.software-description {
  color: #606266;
  font-size: 14px;
  line-height: 1.5;
  margin-bottom: 16px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.software-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.version-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.publish-date {
  font-size: 12px;
  color: #909399;
}

.action-buttons {
  display: flex;
  gap: 8px;
}

.pagination-container {
  margin-top: 24px;
  display: flex;
  justify-content: center;
}

/* 软件详情对话框 */
.software-detail-dialog {
  border-radius: 8px;
}

.detail-content {
  padding: 0;
}

.detail-header {
  display: flex;
  gap: 20px;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #ebeef5;
}

.software-icon-large {
  color: #409eff;
  flex-shrink: 0;
}

.software-info-detail {
  flex: 1;
}

.software-info-detail h2 {
  margin: 0 0 8px 0;
  color: #303133;
}

.author,
.description {
  margin: 0 0 12px 0;
  color: #606266;
}

.software-stats {
  display: flex;
  gap: 20px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #606266;
}

.version-list h3 {
  margin: 0 0 16px 0;
  color: #303133;
}

/* 暗色主题 */
.dark-theme .public-software-container {
  background-color: #141414;
}

.dark-theme .page-header {
  background-color: #1d2935;
}

.dark-theme .software-name {
  color: #e5eaf3;
}

.dark-theme .software-description {
  color: #cfd3dc;
}

.dark-theme .detail-header {
  border-bottom-color: #4c4d4f;
}

.dark-theme .software-info-detail h2 {
  color: #e5eaf3;
}

.dark-theme .author,
.dark-theme .description,
.dark-theme .stat-item {
  color: #cfd3dc;
}

.dark-theme .version-list h3 {
  color: #e5eaf3;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .content-wrapper {
    flex-direction: column;
  }

  .filter-sidebar {
    width: 100%;
  }
}

@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    gap: 16px;
    padding: 0 16px;
  }

  .search-input {
    width: 100%;
  }

  .grid-container {
    grid-template-columns: 1fr;
  }

  .detail-header {
    flex-direction: column;
    gap: 16px;
  }

  .software-stats {
    flex-direction: column;
    gap: 8px;
  }
}
</style>
