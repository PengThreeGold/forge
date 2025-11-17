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
  min-height: 100%;
}

.hero {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  text-align: center;
  padding: 60px 20px;
}

.hero h1 {
  font-size: 48px;
  margin: 0 0 20px 0;
}

.hero p {
  font-size: 20px;
  opacity: 0.9;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 40px 20px;
}

.search-card {
  margin-bottom: 30px;
}

.spaces-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.space-card {
  cursor: pointer;
  transition: transform 0.2s;
}

.space-card:hover {
  transform: translateY(-5px);
}

.space-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.space-header h3 {
  margin: 0;
  font-size: 18px;
}

.description {
  color: #606266;
  margin: 10px 0;
  min-height: 40px;
}

.space-info {
  display: flex;
  flex-direction: column;
  gap: 8px;
  font-size: 14px;
  color: #909399;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 6px;
}

.pagination {
  display: flex;
  justify-content: center;
}
</style>
