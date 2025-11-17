<template>
  <div class="admin-space-detail">
    <el-page-header @back="$router.back()" />
    <el-card v-loading="loading" class="space-info">
      <template #header>
        <h2>{{ space?.name }}</h2>
      </template>
      <el-descriptions v-if="space" :column="2" border>
        <el-descriptions-item label="ID">{{ space.id }}</el-descriptions-item>
        <el-descriptions-item label="API Key">
          <el-input v-model="space.api_key" readonly>
            <template #append>
              <el-button @click="handleCopy(space.api_key)">复制</el-button>
            </template>
          </el-input>
        </el-descriptions-item>
        <el-descriptions-item label="作者">{{ space.author }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="space.status === 'active' ? 'success' : 'info'">
            {{ space.status === 'active' ? '激活' : '停用' }}
          </el-tag>
        </el-descriptions-item>
      </el-descriptions>
    </el-card>

    <el-card class="versions-card">
      <template #header>
        <div class="card-header">
          <h3>版本管理</h3>
          <el-button type="primary" @click="handleCreateVersion">
            <el-icon><Plus /></el-icon>
            新建版本
          </el-button>
        </div>
      </template>
      <el-table :data="versions" stripe>
        <el-table-column prop="version" label="版本号" />
        <el-table-column label="更新说明">
          <template #default="{ row }">
            {{ row.release_note || '暂无说明' }}
          </template>
        </el-table-column>
        <el-table-column label="发布状态">
          <template #default="{ row }">
            <el-tag :type="row.is_published ? 'success' : 'info'">
              {{ row.is_published ? '已发布' : '草稿' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button size="small" @click="handleEditVersion(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="handleDeleteVersion(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import api from '@/api'

const route = useRoute()
const loading = ref(false)
const space = ref(null)
const versions = ref([])

async function fetchSpace() {
  try {
    loading.value = true
    const res = await api.getSpace(route.params.id)
    if (res.success) {
      space.value = res.data || res
    }
  } catch (error) {
    console.error('获取空间信息失败:', error)
  } finally {
    loading.value = false
  }
}

async function fetchVersions() {
  try {
    const res = await api.getVersions(route.params.id, { skip: 0, limit: 100 })
    if (res.success) {
      // 处理分页响应数据
      const data = res.data || res
      versions.value = data.items || []
    }
  } catch (error) {
    console.error('获取版本列表失败:', error)
  }
}

function handleCopy(text) {
  navigator.clipboard.writeText(text)
  ElMessage.success('已复制到剪贴板')
}

function handleCreateVersion() {
  ElMessage.info('版本创建功能待实现')
}

function handleEditVersion(row) {
  ElMessage.info('版本编辑功能待实现')
}

function handleDeleteVersion(row) {
  ElMessage.info('版本删除功能待实现')
}

onMounted(() => {
  fetchSpace()
  fetchVersions()
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

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h3 {
  margin: 0;
}
</style>
