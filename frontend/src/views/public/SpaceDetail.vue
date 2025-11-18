<template>
  <div v-loading="loading" class="space-detail">
    <el-page-header @back="$router.back()" />
    
    <el-card v-if="space" class="space-info">
      <template #header>
        <div class="card-header">
          <h2>{{ space.name }}</h2>
          <el-tag v-if="space.latest_version" type="success" size="large">
            最新版本: {{ space.latest_version }}
          </el-tag>
        </div>
      </template>
      
      <el-descriptions :column="2" border>
        <el-descriptions-item label="作者">{{ space.author || '未知' }}</el-descriptions-item>
        <el-descriptions-item label="创建时间">
          {{ new Date(space.created_at).toLocaleString() }}
        </el-descriptions-item>
        <el-descriptions-item label="版本数量">{{ space.versions_count }}</el-descriptions-item>
        <el-descriptions-item label="总下载量">{{ space.total_downloads }}</el-descriptions-item>
        <el-descriptions-item label="描述" :span="2">
          {{ space.description || '暂无描述' }}
        </el-descriptions-item>
      </el-descriptions>
    </el-card>

    <el-card class="versions-card">
      <template #header>
        <h3>版本列表</h3>
      </template>
      
      <el-table :data="versions" stripe>
        <el-table-column prop="version" label="版本号" />
        <el-table-column label="更新说明">
          <template #default="{ row }">
            {{ row.release_note || '暂无说明' }}
          </template>
        </el-table-column>
        <el-table-column label="架构">
          <template #default="{ row }">
            <el-tag
              v-for="file in row.architecture_files || []"
              :key="file.id"
              size="small"
              style="margin-right: 5px"
            >
              {{ file.architecture }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="发布时间">
          <template #default="{ row }">
            {{ row.publish_date ? new Date(row.publish_date).toLocaleString() : '未发布' }}
          </template>
        </el-table-column>
        <el-table-column label="下载" width="120">
          <template #default="{ row }">
            <el-dropdown @command="(arch) => handleDownload(row, arch)">
              <el-button type="primary" size="small">
                下载<el-icon class="el-icon--right"><ArrowDown /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item
                    v-for="file in row.architecture_files || []"
                    :key="file.id"
                    :command="file.architecture"
                  >
                    {{ file.architecture }}
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
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
    const res = await api.getPublicSpace(route.params.id)
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
    const res = await api.getPublicVersions(route.params.id, {
      skip: 0,
      limit: 100
    })
    if (res.success) {
      // 处理分页响应数据
      const data = res.data || res
      versions.value = data.items || []
    }
  } catch (error) {
    console.error('获取版本列表失败:', error)
  }
}

function handleDownload(version, arch) {
  if (!arch) {
    ElMessage.error('请选择要下载的架构')
    return
  }

  const spaceId = encodeURIComponent(route.params.id)
  const versionTag = encodeURIComponent(version.version)
  const downloadUrl = `/api/public/download/${spaceId}/${versionTag}?architecture=${encodeURIComponent(arch)}`
  window.open(downloadUrl, '_blank')
  ElMessage.success('开始下载')
}

onMounted(() => {
  fetchSpace()
  fetchVersions()
})
</script>

<style scoped>
.space-detail {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
  min-height: 100vh;
  background: #f5f7fa;
}

.el-page-header {
  margin-bottom: 20px;
  padding: 12px 0;
  background: white;
  border-radius: 8px;
  padding: 16px 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.space-info {
  margin-bottom: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
}

.card-header h2 {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
  color: #303133;
}

.versions-card {
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.versions-card h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

:deep(.el-table) {
  font-size: 14px;
}

:deep(.el-table th) {
  background-color: #fafafa;
  color: #606266;
  font-weight: 600;
}

:deep(.el-descriptions__label) {
  font-weight: 600;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .space-detail {
    padding: 10px;
  }

  .card-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .card-header h2 {
    font-size: 20px;
  }

  :deep(.el-table) {
    font-size: 12px;
  }

  :deep(.el-button--small) {
    padding: 5px 10px;
    font-size: 12px;
  }

  :deep(.el-descriptions) {
    font-size: 13px;
  }
}
</style>
