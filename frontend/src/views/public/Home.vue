<template>
  <div class="public-home">
    <div class="hero">
      <h1>欢迎使用 Forge</h1>
      <p>现代化的软件发布管理平台</p>
    </div>
    
    <div class="container">
      <el-card class="search-card">
        <el-input
          v-model="searchText"
          placeholder="搜索软件..."
          clearable
          @keyup.enter="handleSearch"
        >
          <template #append>
            <el-button :icon="Search" @click="handleSearch" />
          </template>
        </el-input>
      </el-card>

      <div v-loading="loading" class="spaces-grid">
        <el-card
          v-for="space in spaces"
          :key="space.id"
          class="space-card"
          shadow="hover"
          @click="goToSpace(space.id)"
        >
          <template #header>
            <div class="space-header">
              <h3>{{ space.name }}</h3>
              <el-tag v-if="space.latest_version" type="success">
                {{ space.latest_version }}
              </el-tag>
            </div>
          </template>
          <p class="description">{{ space.description || '暂无描述' }}</p>
          <div class="space-info">
            <div class="info-item">
              <el-icon><User /></el-icon>
              <span>{{ space.author || '未知' }}</span>
            </div>
            <div class="info-item">
              <el-icon><Download /></el-icon>
              <span>{{ space.total_downloads || 0 }} 次下载</span>
            </div>
            <div class="info-item">
              <el-icon><Files /></el-icon>
              <span>{{ space.versions_count || 0 }} 个版本</span>
            </div>
          </div>
        </el-card>
      </div>

      <el-pagination
        v-if="total > 0"
        class="pagination"
        :current-page="page"
        :page-size="pageSize"
        :total="total"
        layout="prev, pager, next, total"
        @current-change="handlePageChange"
      />

      <el-empty v-if="!loading && spaces.length === 0" description="暂无软件" />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Search } from '@element-plus/icons-vue'
import api from '@/api'

const router = useRouter()

const loading = ref(false)
const spaces = ref([])
const searchText = ref('')
const page = ref(1)
const pageSize = ref(12)
const total = ref(0)

async function fetchSpaces() {
  try {
    loading.value = true
    const res = await api.getPublicSpaces({
      skip: (page.value - 1) * pageSize.value,
      limit: pageSize.value,
      search: searchText.value || undefined
    })
    
    if (res.success) {
      // 处理分页响应数据
      const data = res.data || res
      spaces.value = data.items || []
      total.value = data.total || 0
    }
  } catch (error) {
    console.error('获取软件列表失败:', error)
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  page.value = 1
  fetchSpaces()
}

function handlePageChange(newPage) {
  page.value = newPage
  fetchSpaces()
}

function goToSpace(id) {
  router.push(`/public/spaces/${id}`)
}

onMounted(() => {
  fetchSpaces()
})
</script>

<style scoped>
.public-home {
  min-height: 100vh;
  background: #f5f7fa;
}

.hero {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  text-align: center;
  padding: 80px 20px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.hero h1 {
  font-size: 48px;
  margin: 0 0 20px 0;
  font-weight: 700;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
}

.hero p {
  font-size: 20px;
  opacity: 0.95;
  font-weight: 300;
}

.container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 40px 20px;
}

.search-card {
  margin-bottom: 40px;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.spaces-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 24px;
  margin-bottom: 40px;
}

.space-card {
  cursor: pointer;
  transition: all 0.3s ease;
  border-radius: 8px;
  overflow: hidden;
}

.space-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.space-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.space-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.description {
  color: #606266;
  margin: 16px 0;
  min-height: 48px;
  line-height: 1.6;
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
  overflow: hidden;
}

.space-info {
  display: flex;
  flex-direction: column;
  gap: 10px;
  font-size: 14px;
  color: #909399;
  padding-top: 12px;
  border-top: 1px solid #ebeef5;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.info-item .el-icon {
  font-size: 16px;
}

.pagination {
  display: flex;
  justify-content: center;
  padding: 20px 0;
}

:deep(.el-empty) {
  padding: 60px 0;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .spaces-grid {
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 20px;
  }
}

@media (max-width: 768px) {
  .hero {
    padding: 60px 20px;
  }

  .hero h1 {
    font-size: 36px;
  }

  .hero p {
    font-size: 18px;
  }

  .container {
    padding: 30px 15px;
  }

  .spaces-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }
}

@media (max-width: 480px) {
  .hero h1 {
    font-size: 28px;
  }

  .hero p {
    font-size: 16px;
  }
}
</style>
