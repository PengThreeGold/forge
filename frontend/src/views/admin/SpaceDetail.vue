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
        <el-descriptions-item label="版本数量">{{ space.versions_count }}</el-descriptions-item>
        <el-descriptions-item label="总下载量">{{ formatNumber(space.total_downloads) }}</el-descriptions-item>
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
              @input="debouncedVersionSearch"
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
        <el-table-column label="操作" width="200" fixed="right" align="center">
          <template #default="{ row }">
            <el-button size="small" @click="handleViewVersion(row)">查看</el-button>
            <el-button size="small" type="primary" @click="handleEditVersion(row)">编辑</el-button>
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
          <el-input v-model="versionForm.version" placeholder="例如: 1.0.0" />
        </el-form-item>
        <el-form-item label="更新说明" prop="release_note">
          <el-input
            v-model="versionForm.release_note"
            type="textarea"
            :rows="4"
            placeholder="请输入更新说明"
          />
        </el-form-item>
        <el-form-item label="发布状态" prop="is_published">
          <el-radio-group v-model="versionForm.is_published">
            <el-radio :value="false">草稿</el-radio>
            <el-radio :value="true">发布</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="发布时间" v-if="versionForm.is_published">
          <el-date-picker
            v-model="versionForm.publish_date"
            type="datetime"
            placeholder="选择发布时间"
            format="YYYY-MM-DD HH:mm"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="versionDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="versionSubmitting" @click="handleVersionSubmit">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Plus, CopyDocument } from '@element-plus/icons-vue'
import api from '@/api'
import { useCacheStore } from '@/stores/cache'

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
  release_note: '',
  is_published: false,
  publish_date: null
})

const tableHeight = ref(400)

// 防抖搜索
let versionSearchTimer = null
const debouncedVersionSearch = () => {
  clearTimeout(versionSearchTimer)
  versionSearchTimer = setTimeout(() => {
    versionPage.value = 1
    fetchVersions()
  }, 300)
}

// 计算属性：过滤后的版本数据
const displayVersions = computed(() => {
  if (!versionSearch.value) return versions.value
  
  const search = versionSearch.value.toLowerCase()
  return versions.value.filter(version => 
    version.version.toLowerCase().includes(search)
  )
})

// 表单验证规则
const versionRules = {
  version: [
    { required: true, message: '请输入版本号', trigger: 'blur' },
    { pattern: /^\d+\.\d+\.\d+$/, message: '版本号格式不正确，例如: 1.0.0', trigger: 'blur' }
  ],
  release_note: [{ required: false }],
  is_published: [{ required: true }]
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
    
    // 检查缓存
    const cached = cacheStore.getSpacesCache(`space_${route.params.id}`)
    if (cached) {
      space.value = cached
      return
    }
    
    const res = await api.getSpace(route.params.id)
    if (res.success) {
      space.value = res.data || res
      // 缓存空间信息
      cacheStore.setSpacesCache(`space_${route.params.id}`, space.value)
    }
  } catch (error) {
    console.error('获取空间信息失败:', error)
    ElMessage.error('获取空间信息失败')
  } finally {
    loading.value = false
  }
}

// 获取版本列表
async function fetchVersions() {
  try {
    versionsLoading.value = true
    
    // 构建缓存key
    const cacheKey = `versions_${route.params.id}_${versionPage.value}_${versionPageSize.value}_${versionSearch.value}`
    
    // 检查缓存
    const cached = cacheStore.getVersionsCache(cacheKey)
    if (cached) {
      versions.value = cached.items
      versionTotal.value = cached.total
      return
    }
    
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
      
      // 缓存版本数据
      cacheStore.setVersionsCache(cacheKey, {
        items: versions.value,
        total: versionTotal.value,
        timestamp: Date.now()
      })
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
    release_note: '',
    is_published: false,
    publish_date: null
  }
  versionDialogVisible.value = true
}

function handleViewVersion(row) {
  // 跳转到版本详情页面（待实现）
  ElMessage.info('版本详情功能开发中')
}

function handleEditVersion(row) {
  versionDialogMode.value = 'edit'
  editingVersionId.value = row.id
  versionForm.value = {
    version: row.version,
    release_note: row.release_note || '',
    is_published: row.is_published,
    publish_date: row.publish_date ? new Date(row.publish_date) : null
  }
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
    
    const res = await api.deleteVersion(route.params.id, row.id)
    if (res.success) {
      ElMessage.success('删除成功')
      // 清除相关缓存
      cacheStore.clearVersionsCache()
      fetchVersions()
      // 同时刷新空间信息
      fetchSpace()
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

async function handleVersionSubmit() {
  try {
    await versionFormRef.value.validate()
    versionSubmitting.value = true
    
    let res
    const versionData = {
      version: versionForm.value.version,
      release_note: versionForm.value.release_note,
      is_published: versionForm.value.is_published,
      publish_date: versionForm.value.publish_date
    }
    
    if (versionDialogMode.value === 'create') {
      res = await api.createVersion(route.params.id, versionData)
    } else {
      res = await api.updateVersion(route.params.id, editingVersionId.value, versionData)
    }
    
    if (res.success) {
      ElMessage.success(versionDialogMode.value === 'create' ? '创建成功' : '更新成功')
      versionDialogVisible.value = false
      // 清除相关缓存
      cacheStore.clearVersionsCache()
      fetchVersions()
      // 同时刷新空间信息
      fetchSpace()
    }
  } catch (error) {
    console.error('提交失败:', error)
    ElMessage.error('提交失败')
  } finally {
    versionSubmitting.value = false
  }
}

// 计算表格高度
function calculateTableHeight() {
  nextTick(() => {
    const windowHeight = window.innerHeight
    const tableTop = 400 // 估算表格顶部位置
    tableHeight.value = Math.max(300, windowHeight - tableTop - 100)
  })
}

// 生命周期
onMounted(() => {
  fetchSpace()
  fetchVersions()
  calculateTableHeight()
  window.addEventListener('resize', calculateTableHeight)
})

onUnmounted(() => {
  clearTimeout(versionSearchTimer)
  window.removeEventListener('resize', calculateTableHeight)
})
</script>

<style scoped>
.admin-space-detail {
  max-width: 1200px;
  margin: 0 auto;
}

.el-page-header {
  margin-bottom: 20px;
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
}

.card-header h2,
.card-header h3 {
  margin: 0;
}

.header-actions,
.version-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.api-key-container {
  display: flex;
  align-items: center;
  gap: 12px;
}

.api-key {
  font-family: monospace;
  font-size: 14px;
  background: #f5f7fa;
  padding: 4px 8px;
  border-radius: 4px;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .card-header {
    flex-direction: column;
    gap: 16px;
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
}
</style>
