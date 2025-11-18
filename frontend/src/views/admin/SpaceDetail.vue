<template>
  <div class="admin-space-detail">
    <el-page-header @back="$router.back()" />
    
    <!-- 空间信息卡片 -->
    <el-card v-loading="loading" class="space-info">
      <template #header>
        <div class="card-header">
          <h2>{{ space?.name }}</h2>
          <div class="header-actions">
            <el-button @click="handleCopyApiKey" :icon="CopyDocument">
              复制API Key
            </el-button>
            <el-button type="primary" @click="handleRegenerateKey">
              重新生成Key
            </el-button>
          </div>
        </div>
      </template>
      
      <el-descriptions v-if="space" :column="2" border>
        <el-descriptions-item label="ID">{{ space.id }}</el-descriptions-item>
        <el-descriptions-item label="API Key">
          <div class="api-key-container">
            <span class="api-key">{{ maskApiKey(space.api_key) }}</span>
            <el-button size="small" @click="showFullKey = !showFullKey">
              {{ showFullKey ? '隐藏' : '显示' }}
            </el-button>
          </div>
        </el-descriptions-item>
        <el-descriptions-item label="作者">{{ space.author }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="space.status === 'active' ? 'success' : 'info'">
            {{ space.status === 'active' ? '激活' : '停用' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="版本数量">{{ space.versions_count || 0 }}</el-descriptions-item>
        <el-descriptions-item label="总下载量">{{ formatNumber(space.downloads_count || 0) }}</el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ formatDate(space.created_at) }}</el-descriptions-item>
        <el-descriptions-item label="更新时间">{{ formatDate(space.updated_at) }}</el-descriptions-item>
        <el-descriptions-item label="描述" :span="2">
          {{ space.description || '暂无描述' }}
        </el-descriptions-item>
      </el-descriptions>
    </el-card>

    <!-- 版本管理卡片 -->
    <el-card class="versions-card">
      <template #header>
        <div class="card-header">
          <h3>版本管理</h3>
          <div class="version-actions">
            <el-input
              v-model="versionSearch"
              placeholder="搜索版本号..."
              clearable
              style="width: 200px"
              @change="handleVersionSearch"
              @keyup.enter="handleVersionSearch"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
            <el-button type="primary" @click="handleCreateVersion">
              <el-icon><Plus /></el-icon>
              新建版本
            </el-button>
          </div>
        </div>
      </template>
      
      <!-- 版本表格 -->
      <el-table 
        v-loading="versionsLoading" 
        :data="displayVersions" 
        stripe
        :max-height="tableHeight"
        :height="tableHeight"
        style="width: 100%"
      >
        <el-table-column prop="version" label="版本号" min-width="120" />
        <el-table-column label="更新说明" min-width="200" show-overflow-tooltip>
          <template #default="{ row }">
            {{ row.release_note || '暂无说明' }}
          </template>
        </el-table-column>
        <el-table-column label="架构文件" min-width="150">
          <template #default="{ row }">
            <div v-if="row.architecture_files && row.architecture_files.length > 0">
              <el-tag
                v-for="file in row.architecture_files"
                :key="file.id"
                size="small"
                style="margin-right: 5px; margin-bottom: 3px"
              >
                {{ file.architecture }}
              </el-tag>
            </div>
            <span v-else style="color: #909399;">暂无文件</span>
          </template>
        </el-table-column>
        <el-table-column label="发布状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.is_published ? 'success' : 'info'" size="small">
              {{ row.is_published ? '已发布' : '草稿' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="文件大小" width="120" align="center">
          <template #default="{ row }">
            {{ formatFileSize(row.total_size) }}
          </template>
        </el-table-column>
        <el-table-column label="发布时间" width="180" align="center">
          <template #default="{ row }">
            {{ row.publish_date ? formatDate(row.publish_date) : '未发布' }}
          </template>
        </el-table-column>
        <el-table-column label="创建时间" width="180" align="center">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="280" fixed="right" align="center">
          <template #default="{ row }">
            <el-button size="small" @click="handleViewVersion(row)">查看</el-button>
            <el-button size="small" type="primary" @click="handleEditVersion(row)">编辑</el-button>
            <el-button 
              v-if="!row.is_published" 
              size="small" 
              type="success" 
              @click="handlePublishVersion(row)"
            >
              发布
            </el-button>
            <el-button 
              v-else 
              size="small" 
              type="warning" 
              @click="handleUnpublishVersion(row)"
            >
              取消发布
            </el-button>
            <el-button size="small" type="danger" @click="handleDeleteVersion(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 版本分页 -->
      <el-pagination
        v-if="versionTotal > 0"
        class="pagination"
        :current-page="versionPage"
        :page-size="versionPageSize"
        :total="versionTotal"
        :page-sizes="[10, 20, 50]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleVersionSizeChange"
        @current-change="handleVersionPageChange"
      />

      <!-- 空状态 -->
      <el-empty v-if="!versionsLoading && displayVersions.length === 0" description="暂无版本数据" />
    </el-card>

    <!-- 版本编辑对话框 -->
    <el-dialog
      v-model="versionDialogVisible"
      :title="versionDialogMode === 'create' ? '新建版本' : '编辑版本'"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form ref="versionFormRef" :model="versionForm" :rules="versionRules" label-width="100px">
        <el-form-item label="版本号" prop="version">
          <el-input 
            v-model="versionForm.version" 
            placeholder="例如: 1.0.0"
            :disabled="versionDialogMode === 'edit'"
          />
        </el-form-item>
        
        <el-form-item v-if="versionDialogMode === 'create'" label="架构类型" prop="architecture">
          <el-select v-model="versionForm.architecture" placeholder="请选择架构类型">
            <el-option label="x86_64" value="x86_64" />
            <el-option label="aarch64" value="aarch64" />
          </el-select>
        </el-form-item>
        
        <el-form-item v-if="versionDialogMode === 'create'" label="上传文件" prop="file">
          <el-upload
            ref="uploadRef"
            :auto-upload="false"
            :limit="1"
            :on-change="handleFileChange"
            :file-list="fileList"
            drag
          >
            <el-icon class="el-icon--upload"><upload-filled /></el-icon>
            <div class="el-upload__text">
              将文件拖到此处，或<em>点击上传</em>
            </div>
            <template #tip>
              <div class="el-upload__tip">
                支持各类安装包文件
              </div>
            </template>
          </el-upload>
        </el-form-item>
        
        <el-form-item label="更新说明" prop="release_note">
          <el-input
            v-model="versionForm.release_note"
            type="textarea"
            :rows="4"
            placeholder="请输入更新说明"
          />
        </el-form-item>
        
        <el-form-item label="文档链接" prop="documentation_url">
          <el-input
            v-model="versionForm.documentation_url"
            placeholder="https://docs.example.com"
          />
        </el-form-item>
        
        <el-form-item label="发布状态" prop="is_published">
          <el-switch
            v-model="versionForm.is_published"
            active-text="发布"
            inactive-text="草稿"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="versionDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="versionSubmitting" @click="handleVersionSubmit">
          {{ versionDialogMode === 'create' ? '创建并上传' : '更新' }}
        </el-button>
      </template>
    </el-dialog>
    
    <!-- Webhook 配置 -->
    <webhook-config :space-id="route.params.id" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Plus, CopyDocument, UploadFilled } from '@element-plus/icons-vue'
import api from '@/api'
import { useCacheStore } from '@/stores/cache'
import WebhookConfig from './WebhookConfig.vue'

const route = useRoute()
const cacheStore = useCacheStore()

// 响应式数据
const loading = ref(false)
const space = ref(null)
const showFullKey = ref(false)

// 版本相关数据
const versions = ref([])
const versionsLoading = ref(false)
const versionPage = ref(1)
const versionPageSize = ref(10)
const versionTotal = ref(0)
const versionSearch = ref('')

const versionDialogVisible = ref(false)
const versionDialogMode = ref('create')
const versionSubmitting = ref(false)
const versionFormRef = ref(null)
const editingVersionId = ref(null)

const versionForm = ref({
  version: '',
  architecture: '',
  file: null,
  release_note: '',
  documentation_url: '',
  is_published: false
})

const uploadRef = ref(null)
const fileList = ref([])

const tableHeight = ref(500)

// 版本搜索处理
function handleVersionSearch() {
  versionPage.value = 1
  fetchVersions()
}

// 直接使用后端返回的数据
const displayVersions = computed(() => versions.value)

// 表单验证规则
const versionRules = {
  version: [
    { required: true, message: '请输入版本号', trigger: 'blur' },
    { pattern: /^\d+\.\d+\.\d+$/, message: '版本号格式不正确，例如: 1.0.0', trigger: 'blur' }
  ],
  architecture: [
    { required: true, message: '请选择架构类型', trigger: 'change' }
  ],
  file: [
    { 
      required: true, 
      validator: (rule, value, callback) => {
        if (versionDialogMode.value === 'create' && !versionForm.value.file) {
          callback(new Error('请上传文件'))
        } else {
          callback()
        }
      },
      trigger: 'change'
    }
  ]
}

// 工具函数
const formatNumber = (num) => {
  if (!num) return '0'
  if (num >= 10000) {
    return (num / 10000).toFixed(1) + '万'
  }
  return num.toString()
}

const formatDate = (dateString) => {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const formatFileSize = (bytes) => {
  if (!bytes) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
}

const maskApiKey = (key) => {
  if (!key) return ''
  if (showFullKey.value) return key
  return key.substring(0, 8) + '****' + key.substring(key.length - 4)
}

// 获取空间信息
async function fetchSpace() {
  try {
    loading.value = true
    
    const res = await api.getSpace(route.params.id)
    if (res.success) {
      space.value = res.data || res
      
      // 同时获取统计信息
      fetchSpaceStats()
    }
  } catch (error) {
    console.error('获取空间信息失败:', error)
    ElMessage.error('获取空间信息失败')
  } finally {
    loading.value = false
  }
}

// 获取空间统计信息
async function fetchSpaceStats() {
  try {
    const res = await api.getSpaceStats(route.params.id)
    if (res.success && space.value) {
      // 更新统计数据
      const stats = res.data
      space.value.versions_count = stats.versions_count || 0
      space.value.downloads_count = stats.downloads_count || 0
    }
  } catch (error) {
    console.error('获取空间统计失败:', error)
  }
}

// 获取版本列表
async function fetchVersions() {
  try {
    versionsLoading.value = true
    
    const params = {
      skip: (versionPage.value - 1) * versionPageSize.value,
      limit: versionPageSize.value,
      search: versionSearch.value || undefined
    }
    
    const res = await api.getVersions(route.params.id, params)
    
    if (res.success) {
      const data = res.data || res
      versions.value = data.items || []
      versionTotal.value = data.total || 0
    }
  } catch (error) {
    console.error('获取版本列表失败:', error)
    ElMessage.error('获取版本列表失败')
  } finally {
    versionsLoading.value = false
  }
}

// 复制API Key
function handleCopyApiKey() {
  if (space.value?.api_key) {
    navigator.clipboard.writeText(space.value.api_key)
    ElMessage.success('API Key已复制到剪贴板')
  }
}

// 重新生成API Key
async function handleRegenerateKey() {
  try {
    await ElMessageBox.confirm(
      '确定要重新生成API Key吗？旧的Key将立即失效。',
      '警告',
      {
        type: 'warning',
        confirmButtonText: '确定',
        cancelButtonText: '取消'
      }
    )
    
    const res = await api.regenerateApiKey(route.params.id)
    if (res.success) {
      ElMessage.success('API Key重新生成成功')
      // 刷新空间信息
      fetchSpace()
      // 清除缓存
      cacheStore.clearSpacesCache()
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('重新生成Key失败:', error)
      ElMessage.error('重新生成Key失败')
    }
  }
}

// 版本分页处理
function handleVersionSizeChange(newSize) {
  versionPageSize.value = newSize
  versionPage.value = 1
  fetchVersions()
}

function handleVersionPageChange(newPage) {
  versionPage.value = newPage
  fetchVersions()
}

// 版本操作函数
function handleCreateVersion() {
  versionDialogMode.value = 'create'
  versionForm.value = {
    version: '',
    architecture: '',
    file: null,
    release_note: '',
    documentation_url: '',
    is_published: false
  }
  fileList.value = []
  versionDialogVisible.value = true
}

function handleFileChange(file, files) {
  versionForm.value.file = file.raw
  fileList.value = files
}

function handleViewVersion(row) {
  // 跳转到版本详情页面（待实现）
  ElMessage.info('版本详情功能开发中')
}

function handleEditVersion(row) {
  versionDialogMode.value = 'edit'
  editingVersionId.value = row.version
  versionForm.value = {
    version: row.version,
    architecture: '',
    file: null,
    release_note: row.release_note || '',
    documentation_url: row.documentation_url || '',
    is_published: row.is_published
  }
  fileList.value = []
  versionDialogVisible.value = true
}

async function handleDeleteVersion(row) {
  try {
    await ElMessageBox.confirm(
      `确定要删除版本 "${row.version}" 吗？此操作不可恢复。`,
      '警告',
      {
        type: 'warning',
        confirmButtonText: '确定',
        cancelButtonText: '取消'
      }
    )
    
    const res = await api.deleteVersion(route.params.id, row.version)
    if (res.success) {
      ElMessage.success('删除成功')
      fetchVersions()
      fetchSpace()
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

async function handlePublishVersion(row) {
  try {
    await ElMessageBox.confirm(
      `确定要发布版本 "${row.version}" 吗？发布后用户可以下载此版本。`,
      '提示',
      {
        type: 'info',
        confirmButtonText: '确定',
        cancelButtonText: '取消'
      }
    )
    
    const res = await api.publishVersion(route.params.id, row.version)
    if (res.success) {
      ElMessage.success('发布成功')
      fetchVersions()
      fetchSpace()
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('发布失败:', error)
      ElMessage.error('发布失败')
    }
  }
}

async function handleUnpublishVersion(row) {
  try {
    await ElMessageBox.confirm(
      `确定要取消发布版本 "${row.version}" 吗？取消后用户将无法下载此版本。`,
      '提示',
      {
        type: 'warning',
        confirmButtonText: '确定',
        cancelButtonText: '取消'
      }
    )
    
    const res = await api.unpublishVersion(route.params.id, row.version)
    if (res.success) {
      ElMessage.success('已取消发布')
      fetchVersions()
      fetchSpace()
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('操作失败:', error)
      ElMessage.error('操作失败')
    }
  }
}

async function handleVersionSubmit() {
  try {
    await versionFormRef.value.validate()
    versionSubmitting.value = true
    
    if (versionDialogMode.value === 'create') {
      // 创建版本并上传文件
      const formData = new FormData()
      formData.append('version', versionForm.value.version)
      formData.append('architecture', versionForm.value.architecture)
      formData.append('file', versionForm.value.file)
      formData.append('release_note', versionForm.value.release_note || '')
      formData.append('documentation_url', versionForm.value.documentation_url || '')
      formData.append('is_published', versionForm.value.is_published)
      
      const res = await api.createVersion(route.params.id, formData)
      if (res.success) {
        ElMessage.success('版本创建成功')
        versionDialogVisible.value = false
        fetchVersions()
        fetchSpace()
      }
    } else {
      // 更新版本
      const formData = new FormData()
      formData.append('release_note', versionForm.value.release_note || '')
      formData.append('documentation_url', versionForm.value.documentation_url || '')
      formData.append('is_published', versionForm.value.is_published)
      
      const res = await api.updateVersion(route.params.id, editingVersionId.value, formData)
      if (res.success) {
        ElMessage.success('版本更新成功')
        versionDialogVisible.value = false
        fetchVersions()
        fetchSpace()
      }
    }
  } catch (error) {
    console.error('提交失败:', error)
    ElMessage.error(error.message || '提交失败')
  } finally {
    versionSubmitting.value = false
  }
}

// 计算表格高度
function calculateTableHeight() {
  // 使用固定高度，保证所有表格高度一致
  tableHeight.value = 500
}

// 生命周期
onMounted(() => {
  fetchSpace()
  fetchVersions()
  calculateTableHeight()
})

onUnmounted(() => {
  // 清理资源
})
</script>

<style scoped>
.admin-space-detail {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
}

.el-page-header {
  margin-bottom: 20px;
  padding: 12px 0;
}

.space-info {
  margin-bottom: 20px;
}

.versions-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
}

.card-header h2,
.card-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.header-actions,
.version-actions {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}

.api-key-container {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.api-key {
  font-family: 'Courier New', Courier, monospace;
  font-size: 13px;
  background: #f5f7fa;
  padding: 6px 12px;
  border-radius: 4px;
  color: #606266;
  border: 1px solid #dcdfe6;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

:deep(.el-table) {
  font-size: 14px;
  /* 性能优化 */
  will-change: scroll-position;
  transform: translateZ(0);
}

:deep(.el-table__body-wrapper) {
  /* 优化滚动性能 */
  overflow-y: auto;
  overflow-x: hidden;
  -webkit-overflow-scrolling: touch;
}

:deep(.el-table__body-wrapper::-webkit-scrollbar) {
  width: 8px;
  height: 8px;
}

:deep(.el-table__body-wrapper::-webkit-scrollbar-track) {
  background: #f5f7fa;
  border-radius: 4px;
}

:deep(.el-table__body-wrapper::-webkit-scrollbar-thumb) {
  background: #c1c1c1;
  border-radius: 4px;
  transition: background 0.2s ease;
}

:deep(.el-table__body-wrapper::-webkit-scrollbar-thumb:hover) {
  background: #a8a8a8;
}

:deep(.el-table th) {
  background-color: #fafafa;
  color: #606266;
  font-weight: 600;
}

:deep(.el-descriptions__label) {
  font-weight: 600;
}

:deep(.el-upload-dragger) {
  padding: 30px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .admin-space-detail {
    padding: 10px;
  }

  .card-header {
    flex-direction: column;
    align-items: stretch;
  }
  
  .header-actions,
  .version-actions {
    flex-direction: column;
    align-items: stretch;
  }
  
  .version-actions .el-input {
    width: 100% !important;
  }
  
  :deep(.el-table) {
    font-size: 12px;
  }
  
  :deep(.el-button--small) {
    padding: 5px 10px;
    font-size: 12px;
  }
}

@media (max-width: 480px) {
  .api-key {
    font-size: 11px;
    word-break: break-all;
  }
}
</style>
