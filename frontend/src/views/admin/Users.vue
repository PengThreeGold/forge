<template>
  <div class="admin-users">
    <el-card>
      <template #header>
        <div class="card-header">
          <h2>用户管理</h2>
          <div class="header-actions">
            <el-input
              v-model="searchText"
              placeholder="搜索用户名或邮箱..."
              clearable
              style="width: 250px"
              @input="debouncedSearch"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
            <el-button type="primary" @click="handleRefresh">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
          </div>
        </div>
      </template>
      
      <!-- 优化后的用户表格 -->
      <el-table 
        v-loading="loading" 
        :data="displayUsers" 
        stripe
        :max-height="tableHeight"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column 
          prop="username" 
          label="用户名" 
          min-width="120"
          show-overflow-tooltip
        />
        <el-table-column 
          prop="email" 
          label="邮箱" 
          min-width="180"
          show-overflow-tooltip
        />
        <el-table-column label="角色" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.role === 'admin' ? 'danger' : 'primary'" size="small">
              {{ row.role === 'admin' ? '管理员' : '用户' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'info'" size="small">
              {{ row.is_active ? '激活' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="创建时间" width="180" align="center">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right" align="center">
          <template #default="{ row }">
            <el-button size="small" @click="handleEdit(row)">编辑</el-button>
            <el-button 
              size="small" 
              :type="row.is_active ? 'danger' : 'success'"
              @click="handleToggleStatus(row)"
            >
              {{ row.is_active ? '禁用' : '启用' }}
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
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

      <!-- 空状态 -->
      <el-empty v-if="!loading && displayUsers.length === 0" description="暂无用户数据" />
    </el-card>

    <!-- 编辑用户对话框 -->
    <el-dialog
      v-model="dialogVisible"
      title="编辑用户"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
        <el-form-item label="用户名">
          <el-input v-model="form.username" disabled />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="form.email" disabled />
        </el-form-item>
        <el-form-item label="角色" prop="role">
          <el-radio-group v-model="form.role">
            <el-radio value="user">用户</el-radio>
            <el-radio value="admin">管理员</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="状态" prop="is_active">
          <el-switch
            v-model="form.is_active"
            active-text="激活"
            inactive-text="禁用"
          />
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
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Refresh } from '@element-plus/icons-vue'
import api from '@/api'
import { useCacheStore } from '@/stores/cache'

const cacheStore = useCacheStore()

// 响应式数据
const loading = ref(false)
const users = ref([])
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const searchText = ref('')
const selectedUsers = ref([])

const dialogVisible = ref(false)
const submitting = ref(false)
const formRef = ref(null)
const form = ref({
  id: '',
  username: '',
  email: '',
  role: 'user',
  is_active: true
})

const tableHeight = ref(400)

// 防抖搜索
let searchTimer = null
const debouncedSearch = () => {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    page.value = 1
    fetchUsers()
  }, 300)
}

// 计算属性：过滤后的用户数据
const displayUsers = computed(() => {
  if (!searchText.value) return users.value
  
  const search = searchText.value.toLowerCase()
  return users.value.filter(user => 
    user.username.toLowerCase().includes(search) || 
    user.email.toLowerCase().includes(search)
  )
})

// 表单验证规则
const rules = {
  role: [{ required: true, message: '请选择用户角色', trigger: 'change' }]
}

// 工具函数
const formatDate = (dateString) => {
  return new Date(dateString).toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 获取用户列表
async function fetchUsers() {
  try {
    loading.value = true
    
    // 构建缓存key
    const cacheKey = `users_${page.value}_${pageSize.value}_${searchText.value}`
    
    // 检查缓存
    const cached = cacheStore.getUsersCache(cacheKey)
    if (cached) {
      users.value = cached.items
      total.value = cached.total
      return
    }
    
    const params = {
      skip: (page.value - 1) * pageSize.value,
      limit: pageSize.value,
      search: searchText.value || undefined
    }
    
    const res = await api.getUsers(params)
    
    if (res.success) {
      const data = res.data || res
      users.value = data.items || []
      total.value = data.total || 0
      
      // 缓存数据
      cacheStore.setUsersCache(cacheKey, {
        items: users.value,
        total: total.value,
        timestamp: Date.now()
      })
    }
  } catch (error) {
    console.error('获取用户列表失败:', error)
    ElMessage.error('获取用户列表失败')
  } finally {
    loading.value = false
  }
}

// 处理多选
function handleSelectionChange(selection) {
  selectedUsers.value = selection
}

// 分页处理
function handleSizeChange(newSize) {
  pageSize.value = newSize
  page.value = 1
  fetchUsers()
}

function handlePageChange(newPage) {
  page.value = newPage
  fetchUsers()
}

// 刷新数据
function handleRefresh() {
  // 清除缓存
  cacheStore.clearUsersCache()
  fetchUsers()
}

// 编辑用户
function handleEdit(row) {
  form.value = {
    id: row.id,
    username: row.username,
    email: row.email,
    role: row.role,
    is_active: row.is_active
  }
  dialogVisible.value = true
}

// 切换用户状态
async function handleToggleStatus(row) {
  try {
    const action = row.is_active ? '禁用' : '启用'
    await ElMessageBox.confirm(
      `确定要${action}用户 "${row.username}" 吗？`,
      '确认',
      {
        type: 'warning',
        confirmButtonText: '确定',
        cancelButtonText: '取消'
      }
    )
    
    const res = await api.updateUser(row.id, { is_active: !row.is_active })
    if (res.success) {
      ElMessage.success(`${action}成功`)
      // 清除缓存并刷新
      cacheStore.clearUsersCache()
      fetchUsers()
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('操作失败:', error)
      ElMessage.error('操作失败')
    }
  }
}

// 提交编辑
async function handleSubmit() {
  try {
    await formRef.value.validate()
    submitting.value = true
    
    const res = await api.updateUser(form.value.id, {
      role: form.value.role,
      is_active: form.value.is_active
    })
    
    if (res.success) {
      ElMessage.success('更新成功')
      dialogVisible.value = false
      // 清除缓存并刷新
      cacheStore.clearUsersCache()
      fetchUsers()
    }
  } catch (error) {
    console.error('提交失败:', error)
    ElMessage.error('提交失败')
  } finally {
    submitting.value = false
  }
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
  fetchUsers()
  calculateTableHeight()
  window.addEventListener('resize', calculateTableHeight)
})

onUnmounted(() => {
  clearTimeout(searchTimer)
  window.removeEventListener('resize', calculateTableHeight)
})
</script>

<style scoped>
.admin-users {
  max-width: 1200px;
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
  .card-header {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }
  
  .header-actions {
    flex-direction: column;
    align-items: stretch;
  }
  
  .header-actions .el-input {
    width: 100% !important;
  }
}
</style>
