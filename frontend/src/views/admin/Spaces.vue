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

      <el-table v-loading="loading" :data="spaces" stripe>
        <el-table-column prop="name" label="名称" />
        <el-table-column prop="author" label="作者" />
        <el-table-column label="状态">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'info'">
              {{ row.status === 'active' ? '激活' : '停用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="versions_count" label="版本数" width="100" />
        <el-table-column label="下载量" width="100">
          <template #default="{ row }">
            {{ row.downloads_count ?? 0 }}
          </template>
        </el-table-column>
        <el-table-column label="创建时间" width="180">
          <template #default="{ row }">
            {{ new Date(row.created_at).toLocaleString() }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
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
        layout="prev, pager, next, total"
        @current-change="handlePageChange"
      />
    </el-card>

    <!-- 创建/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogMode === 'create' ? '新建空间' : '编辑空间'"
      width="600px"
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
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '@/api'

const router = useRouter()

const loading = ref(false)
const spaces = ref([])
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)

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

const rules = {
  name: [{ required: true, message: '请输入软件名称', trigger: 'blur' }]
}

async function fetchSpaces() {
  try {
    loading.value = true
    const res = await api.getSpaces({
      skip: (page.value - 1) * pageSize.value,
      limit: pageSize.value
    })
    
    if (res.success) {
      // 处理分页响应数据
      const data = res.data || res
      spaces.value = data.items || []
      total.value = data.total || 0
    }
  } catch (error) {
    console.error('获取空间列表失败:', error)
  } finally {
    loading.value = false
  }
}

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
      fetchSpaces()
    }
  } catch (error) {
    console.error('提交失败:', error)
  } finally {
    submitting.value = false
  }
}

async function handleDelete(row) {
  try {
    await ElMessageBox.confirm('确定要删除此空间吗？删除后无法恢复。', '警告', {
      type: 'warning'
    })
    
    const res = await api.deleteSpace(row.id)
    if (res.success) {
      ElMessage.success('删除成功')
      fetchSpaces()
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
    }
  }
}

function handlePageChange(newPage) {
  page.value = newPage
  fetchSpaces()
}

function goToDetail(id) {
  router.push(`/admin/spaces/${id}`)
}

onMounted(() => {
  fetchSpaces()
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

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}
</style>
