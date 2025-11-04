<template>
  <div class="software-list-container">
    <div class="page-header">
      <h2>软件空间</h2>
      <el-button type="primary" @click="showCreateDialog">
        <el-icon><Plus /></el-icon>
        创建软件空间
      </el-button>
    </div>

    <div class="search-bar">
      <el-input
        v-model="searchKeyword"
        placeholder="搜索软件名称"
        clearable
        @clear="handleSearch"
        @keyup.enter="handleSearch"
      >
        <template #append>
          <el-button @click="handleSearch">
            <el-icon><Search /></el-icon>
          </el-button>
        </template>
      </el-input>
    </div>

    <el-table
      v-loading="loading"
      :data="filteredSpaces"
      style="width: 100%"
      @sort-change="handleSortChange"
    >
      <el-table-column prop="name" label="软件名称" min-width="150" sortable="custom" />
      <el-table-column prop="author" label="作者" width="120" />
      <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
      <el-table-column prop="versions_count" label="版本数" width="100" sortable="custom" />
      <el-table-column prop="downloads_count" label="下载次数" width="120" sortable="custom" />
      <el-table-column prop="created_at" label="创建时间" width="180" sortable="custom">
        <template #default="scope">
          {{ formatDateTime(scope.row.created_at) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="250" fixed="right">
        <template #default="scope">
          <el-button type="primary" size="small" @click="viewSpace(scope.row)"> 查看 </el-button>
          <el-button type="warning" size="small" @click="editSpace(scope.row)"> 编辑 </el-button>
          <el-button type="danger" size="small" @click="confirmDelete(scope.row)"> 删除 </el-button>
        </template>
      </el-table-column>
    </el-table>

    <div class="pagination-container">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[10, 20, 50, 100]"
        :total="total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>

    <!-- 创建/编辑软件空间对话框 -->
    <el-dialog
      v-model="spaceDialogVisible"
      :title="dialogTitle"
      width="600px"
      :close-on-click-modal="false"
      @close="handleDialogClose"
    >
      <el-form ref="spaceForm" :model="spaceForm" :rules="spaceRules" label-width="100px">
        <el-form-item label="软件名称" prop="name">
          <el-input v-model="spaceForm.name" placeholder="请输入软件名称" />
        </el-form-item>

        <el-form-item label="作者" prop="author">
          <el-input v-model="spaceForm.author" placeholder="请输入作者名称" />
        </el-form-item>

        <el-form-item label="描述" prop="description">
          <el-input
            v-model="spaceForm.description"
            type="textarea"
            :rows="4"
            placeholder="请输入软件描述"
          />
        </el-form-item>

        <el-form-item label="Webhook URL" prop="webhook_url">
          <el-input v-model="spaceForm.webhook_url" placeholder="请输入Webhook URL（可选）" />
        </el-form-item>
      </el-form>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="spaceDialogVisible = false">取消</el-button>
          <el-button type="primary" :loading="dialogLoading" @click="handleSpaceSubmit">
            确认
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- API密钥对话框 -->
    <el-dialog
      v-model="apiKeyDialogVisible"
      title="API密钥"
      width="600px"
      :close-on-click-modal="false"
    >
      <div class="api-key-container">
        <p class="api-key-desc">API密钥用于外部访问您的软件空间，请妥善保管：</p>
        <div class="api-key-box">
          <el-input v-model="currentApiKey" type="textarea" :rows="3" readonly />
          <el-button type="primary" @click="copyApiKey">
            <el-icon><CopyDocument /></el-icon>
            复制
          </el-button>
        </div>
        <div class="api-key-actions">
          <el-button type="warning" @click="regenerateApiKey">
            <el-icon><RefreshRight /></el-icon>
            重新生成
          </el-button>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { defineComponent, ref, reactive, computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { formatDateTime } from '@/utils/common'

export default defineComponent({
  name: 'SoftwareList',
  setup() {
    const store = useStore()
    const router = useRouter()

    // 数据
    const spaces = ref([])
    const loading = ref(false)
    const searchKeyword = ref('')
    const sortProp = ref('')
    const sortOrder = ref('')

    // 分页
    const currentPage = ref(1)
    const pageSize = ref(20)
    const total = ref(0)

    // 对话框相关
    const spaceDialogVisible = ref(false)
    const dialogTitle = ref('创建软件空间')
    const dialogLoading = ref(false)
    const isEdit = ref(false)
    const currentSpaceId = ref(null)

    // 表单
    const spaceForm = reactive({
      name: '',
      author: '',
      description: '',
      webhook_url: '',
    })

    const spaceRules = {
      name: [{ required: true, message: '请输入软件名称', trigger: 'blur' }],
    }

    const spaceFormRef = ref(null)

    // API密钥对话框
    const apiKeyDialogVisible = ref(false)
    const currentApiKey = ref('')

    // 计算属性
    const filteredSpaces = computed(() => {
      if (!spaces.value || !Array.isArray(spaces.value)) return []
      let result = Array.isArray(spaces.value) ? [...spaces.value] : []
      // 搜索过滤
      if (searchKeyword.value) {
        const keyword = searchKeyword.value.toLowerCase()
        result = result.filter(
          space =>
            (space.name && space.name.toLowerCase().includes(keyword)) ||
            (space.author && space.author.toLowerCase().includes(keyword)) ||
            (space.description && space.description.toLowerCase().includes(keyword))
        )
      }
      // 排序
      if (sortProp.value && sortOrder.value) {
        result.sort((a, b) => {
          let valueA = a[sortProp.value]
          let valueB = b[sortProp.value]

          // 处理日期
          if (sortProp.value === 'created_at') {
            valueA = new Date(valueA).getTime()
            valueB = new Date(valueB).getTime()
          }

          if (sortOrder.value === 'ascending') {
            return valueA > valueB ? 1 : -1
          } else {
            return valueA < valueB ? 1 : -1
          }
        })
      }

      // 分页
      const start = (currentPage.value - 1) * pageSize.value
      const end = start + pageSize.value
      return result.slice(start, end)
    })

    // 获取软件空间列表
    const getSpaces = async () => {
      try {
        loading.value = true

        const response = await store.dispatch('software/getSpaces')
        spaces.value = response.data
        total.value = response.data.length
      } catch (error) {
        console.error('获取软件空间列表失败:', error)
      } finally {
        loading.value = false
      }
    }

    // 搜索
    const handleSearch = () => {
      currentPage.value = 1
    }

    // 排序变化
    const handleSortChange = ({ prop, order }) => {
      sortProp.value = prop
      sortOrder.value = order
      currentPage.value = 1
    }

    // 分页大小变化
    const handleSizeChange = size => {
      pageSize.value = size
      currentPage.value = 1
    }

    // 当前页变化
    const handleCurrentChange = page => {
      currentPage.value = page
    }

    // 显示创建对话框
    const showCreateDialog = () => {
      dialogTitle.value = '创建软件空间'
      isEdit.value = false
      currentSpaceId.value = null
      resetForm()
      spaceDialogVisible.value = true
    }

    // 编辑软件空间
    const editSpace = space => {
      dialogTitle.value = '编辑软件空间'
      isEdit.value = true
      currentSpaceId.value = space.id

      // 填充表单
      spaceForm.name = space.name
      spaceForm.author = space.author
      spaceForm.description = space.description
      spaceForm.webhook_url = space.webhook_url

      spaceDialogVisible.value = true
    }

    // 查看软件空间
    const viewSpace = space => {
      router.push(`/software/${space.id}`)
    }

    // 确认删除
    const confirmDelete = space => {
      ElMessageBox.confirm(
        `确定要删除软件空间"${space.name}"吗？此操作不可逆，所有相关数据将被删除。`,
        '删除确认',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning',
        }
      )
        .then(async () => {
          try {
            await store.dispatch('software/deleteSpace', space.id)
            ElMessage.success('删除成功')
            getSpaces()
          } catch (error) {
            console.error('删除软件空间失败:', error)
          }
        })
        .catch(() => {
          // 用户取消删除
        })
    }

    // 提交表单
    const handleSpaceSubmit = async () => {
      if (!spaceFormRef.value) return

      try {
        await spaceFormRef.value.validate()

        dialogLoading.value = true

        if (isEdit.value) {
          // 编辑软件空间
          await store.dispatch('software/updateSpace', {
            spaceId: currentSpaceId.value,
            spaceData: spaceForm,
          })
          ElMessage.success('更新成功')
        } else {
          // 创建软件空间
          const response = await store.dispatch('software/createSpace', spaceForm)
          ElMessage.success('创建成功')

          // 创建成功后显示API密钥
          currentApiKey.value = response.data.api_key
          apiKeyDialogVisible.value = true
        }

        spaceDialogVisible.value = false
        getSpaces()
      } catch (error) {
        console.error('操作失败:', error)
      } finally {
        dialogLoading.value = false
      }
    }

    // 重置表单
    const resetForm = () => {
      spaceForm.name = ''
      spaceForm.author = ''
      spaceForm.description = ''
      spaceForm.webhook_url = ''

      if (spaceFormRef.value) {
        spaceFormRef.value.resetFields()
      }
    }

    // 关闭对话框
    const handleDialogClose = () => {
      resetForm()
    }

    // 复制API密钥
    const copyApiKey = async () => {
      try {
        await navigator.clipboard.writeText(currentApiKey.value)
        ElMessage.success('API密钥已复制到剪贴板')
      } catch (error) {
        ElMessage.error('复制失败，请手动复制')
      }
    }

    // 重新生成API密钥
    const regenerateApiKey = async () => {
      try {
        ElMessageBox.confirm('确定要重新生成API密钥吗？旧的API密钥将立即失效。', '确认操作', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning',
        })
          .then(async () => {
            const response = await store.dispatch('software/regenerateApiKey', currentSpaceId.value)
            currentApiKey.value = response.data.api_key
            ElMessage.success('API密钥已重新生成')
          })
          .catch(() => {
            // 用户取消操作
          })
      } catch (error) {
        console.error('重新生成API密钥失败:', error)
      }
    }

    onMounted(() => {
      getSpaces()
    })

    return {
      spaces,
      loading,
      searchKeyword,
      filteredSpaces,
      currentPage,
      pageSize,
      total,
      spaceDialogVisible,
      dialogTitle,
      dialogLoading,
      isEdit,
      currentSpaceId,
      spaceForm,
      spaceRules,
      spaceFormRef,
      apiKeyDialogVisible,
      currentApiKey,
      handleSearch,
      handleSortChange,
      handleSizeChange,
      handleCurrentChange,
      showCreateDialog,
      editSpace,
      viewSpace,
      confirmDelete,
      handleSpaceSubmit,
      handleDialogClose,
      copyApiKey,
      regenerateApiKey,
      formatDateTime,
    }
  },
})
</script>

<style scoped>
.software-list-container {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0;
  font-size: 24px;
  font-weight: 500;
}

.search-bar {
  margin-bottom: 20px;
  width: 300px;
}

.pagination-container {
  margin-top: 20px;
  text-align: right;
}

.api-key-container {
  padding: 10px 0;
}

.api-key-desc {
  margin-bottom: 15px;
  color: #606266;
}

.api-key-box {
  display: flex;
  margin-bottom: 15px;
}

.api-key-box .el-textarea {
  flex: 1;
  margin-right: 10px;
}

.api-key-actions {
  text-align: right;
}

@media (max-width: 768px) {
  .software-list-container {
    padding: 10px;
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .page-header .el-button {
    margin-top: 10px;
  }

  .search-bar {
    width: 100%;
  }

  .pagination-container {
    text-align: center;
  }

  .api-key-box {
    flex-direction: column;
  }

  .api-key-box .el-textarea {
    margin-right: 0;
    margin-bottom: 10px;
  }

  .api-key-actions {
    text-align: center;
  }
}
</style>
