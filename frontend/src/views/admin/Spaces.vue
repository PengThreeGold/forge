<template>
  <div class="admin-spaces">
    <el-card>
      <template #header>
        <div class="card-header">
          <h2>软件空间管理</h2>
          <el-button type="primary" @click="handleCreate">
            <el-icon><Plus /></el-icon>
            新建空间
          </el-button>
        </div>
      </template>

      <!-- 搜索和筛选 -->
      <div class="filter-bar">
        <el-input
          v-model="searchText"
          placeholder="搜索空间名称或作者..."
          clearable
          style="width: 300px"
          @input="debouncedSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        
        <el-select v-model="statusFilter" placeholder="状态筛选" clearable style="width: 120px">
          <el-option label="全部" value="" />
          <el-option label="激活" value="active" />
          <el-option label="停用" value="inactive" />
        </el-select>
      </div>

      <!-- 优化后的表格 -->
      <el-table 
        v-loading="loading" 
        :data="displaySpaces" 
        stripe
        :max-height="tableHeight"
        @sort-change="handleSortChange"
      >
        <el-table-column 
          prop="name" 
          label="名称" 
          sortable="custom"
          min-width="150"
          show-overflow-tooltip
        />
        <el-table-column 
          prop="author" 
          label="作者" 
          sortable="custom"
          min-width="120"
          show-overflow-tooltip
        />
        <el-table-column label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'info'" size="small">
              {{ row.status === 'active' ? '激活' : '停用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="versions_count" label="版本数" width="80" align="center" />
        <el-table-column label="下载量" width="100" align="center">
          <template #default="{ row }">
            {{ formatNumber(row.downloads_count ?? 0) }}
          </template>
        </el-table-column>
        <el-table-column label="创建时间" width="180" align="center">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right" align="center">
          <template #default="{ row }">
            <el-button size="small" @click="goToDetail(row.id)">详情</el-button>
            <el-button size="small" type="primary" @click="handleEdit(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-if="total > 0"
        class="pagination"
        :current-page="page"
        :page-size="pageSize"
        :total="total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handlePageChange"
      />
    </el-card>

    <!-- 创建/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogMode === 'create' ? '新建空间' : '编辑空间'"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="软件名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入软件名称" />
        </el-form-item>
        <el-form-item label="作者" prop="author">
          <el-input v-model="form.author" placeholder="请输入作者名称" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="4"
            placeholder="请输入软件描述"
          />
        </el-form-item>
        <el-form-item v-if="dialogMode === 'edit'" label="状态" prop="status">
          <el-radio-group v-model="form.status">
            <el-radio value="active">激活</el-radio>
            <el-radio value="inactive">停用</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Plus } from '@element-plus/icons-vue'
import api from '@/api'
import { useCacheStore } from '@/stores/cache'

const router = useRouter()
const cacheStore = useCacheStore()

// 响应式数据
const loading = ref(false)
const spaces = ref([])
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const searchText = ref('')
const statusFilter = ref('')
const sortProp = ref('')
const sortOrder = ref('')

const dialogVisible = ref(false)
const dialogMode = ref('create')
const submitting = ref(false)
const formRef = ref(null)
const form = ref({
  name: '',
  author: '',
  description: '',
  status: 'active'
})
const editingId = ref(null)

// 表格高度计算
const tableHeight = ref(400)

// 防抖搜索
let searchTimer = null
const debouncedSearch = () => {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    page.value = 1
    fetchSpaces()
  }, 300)
}

// 计算属性：过滤后的数据
const displaySpaces = computed(() => {
  let filtered = spaces.value
  
  // 文本搜索过滤
  if (searchText.value) {
    const search = searchText.value.toLowerCase()
    filtered = filtered.filter(space => 
      space.name.toLowerCase().includes(search) || 
      space.author.toLowerCase().includes(search)
    )
  }
  
  // 状态过滤
  if (statusFilter.value) {
    filtered = filtered.filter(space => space.status === statusFilter.value)
  }
  
  return filtered
})

// 表单验证规则
const rules = {
  name: [{ required: true, message: '请输入软件名称', trigger: 'blur' }]
}

// 工具函数
const formatNumber = (num) => {
  if (num >= 10000) {
    return (num / 10000).toFixed(1) + '万'
  }
  return num.toString()
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 获取空间列表
async function fetchSpaces() {
  try {
    loading.value = true
    
    // 构建缓存key
    const cacheKey = `spaces_${page.value}_${pageSize.value}_${searchText.value}_${statusFilter.value}_${sortProp.value}_${sortOrder.value}`
    
    // 检查缓存
    const cached = cacheStore.getSpacesCache(cacheKey)
    if (cached) {
      spaces.value = cached.items
      total.value = cached.total
      return
    }
    
    const params = {
      skip: (page.value - 1) * pageSize.value,
      limit: pageSize.value,
      search: searchText.value || undefined,
      status: statusFilter.value || undefined,
      sort: sortProp.value || undefined,
      order: sortOrder.value || undefined
    }
    
    const res = await api.getSpaces(params)
    
    if (res.success) {
      const data = res.data || res
      spaces.value = data.items || []
      total.value = data.total || 0
      
      // 缓存数据
      cacheStore.setSpacesCache(cacheKey, {
        items: spaces.value,
        total: total.value,
        timestamp: Date.now()
      })
    }
  } catch (error) {
    console.error('获取空间列表失败:', error)
    ElMessage.error('获取空间列表失败')
  } finally {
    loading.value = false
  }
}

// 排序处理
function handleSortChange({ prop, order }) {
  sortProp.value = prop
  sortOrder.value = order === 'ascending' ? 'asc' : order === 'descending' ? 'desc' : ''
  page.value = 1
  fetchSpaces()
}

// 分页处理
function handleSizeChange(newSize) {
  pageSize.value = newSize
  page.value = 1
  fetchSpaces()
}

function handlePageChange(newPage) {
  page.value = newPage
  fetchSpaces()
}

// 其他操作函数
function handleCreate() {
  dialogMode.value = 'create'
  form.value = {
    name: '',
    author: '',
    description: '',
    status: 'active'
  }
  dialogVisible.value = true
}

function handleEdit(row) {
  dialogMode.value = 'edit'
  editingId.value = row.id
  form.value = {
    name: row.name,
    author: row.author || '',
    description: row.description || '',
    status: row.status
  }
  dialogVisible.value = true
}

async function handleSubmit() {
  try {
    await formRef.value.validate()
    submitting.value = true
    
    let res
    if (dialogMode.value === 'create') {
      res = await api.createSpace(form.value)
    } else {
      res = await api.updateSpace(editingId.value, form.value)
    }
    
    if (res.success) {
      ElMessage.success(dialogMode.value === 'create' ? '创建成功' : '更新成功')
      dialogVisible.value = false
      // 清除相关缓存
      cacheStore.clearSpacesCache()
      fetchSpaces()
    }
  } catch (error) {
    console.error('提交失败:', error)
    ElMessage.error('提交失败')
  } finally {
    submitting.value = false
  }
}

async function handleDelete(row) {
  try {
    await ElMessageBox.confirm('确定要删除此空间吗？删除后无法恢复。', '警告', {
      type: 'warning',
      confirmButtonText: '确定',
      cancelButtonText: '取消'
    })
    
    const res = await api.deleteSpace(row.id)
    if (res.success) {
      ElMessage.success('删除成功')
      // 清除相关缓存
      cacheStore.clearSpacesCache()
      fetchSpaces()
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

function goToDetail(id) {
  router.push(`/admin/spaces/${id}`)
}

// 计算表格高度
function calculateTableHeight() {
  nextTick(() => {
    const windowHeight = window.innerHeight
    const tableTop = 200 // 估算表格顶部位置
    tableHeight.value = Math.max(300, windowHeight - tableTop - 100)
  })
}

// 生命周期
onMounted(() => {
  fetchSpaces()
  calculateTableHeight()
  window.addEventListener('resize', calculateTableHeight)
})

onUnmounted(() => {
  clearTimeout(searchTimer)
  window.removeEventListener('resize', calculateTableHeight)
})
</script>

<style scoped>
.admin-spaces {
  max-width: 1400px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h2 {
  margin: 0;
}

.filter-bar {
  display: flex;
  gap: 16px;
  margin-bottom: 16px;
  align-items: center;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .filter-bar {
    flex-direction: column;
    align-items: stretch;
  }
  
  .filter-bar .el-input,
  .filter-bar .el-select {
    width: 100% !important;
  }
}
</style>
