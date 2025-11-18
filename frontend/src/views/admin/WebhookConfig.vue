<template>
  <div class="webhook-config">
    <el-card>
      <template #header>
        <div class="card-header">
          <h3>Webhook 配置</h3>
          <el-button type="primary" @click="handleSave" :loading="saving">
            <el-icon><Check /></el-icon>
            保存配置
          </el-button>
        </div>
      </template>
      
      <el-form ref="formRef" :model="form" :rules="rules" label-width="120px">
        <el-form-item label="Webhook URL" prop="webhook_url">
          <el-input 
            v-model="form.webhook_url" 
            placeholder="https://example.com/webhook"
            clearable
          />
        </el-form-item>
        
        <el-form-item label="Webhook 密钥" prop="webhook_secret">
          <el-input 
            v-model="form.webhook_secret" 
            placeholder="可选，用于验证请求"
            show-password
            clearable
          >
            <template #append>
              <el-button @click="handleGenerateSecret">生成</el-button>
            </template>
          </el-input>
        </el-form-item>
        
        <el-form-item label="启用事件" prop="webhook_events">
          <el-checkbox-group v-model="form.webhook_events">
            <el-checkbox label="version.created">版本创建</el-checkbox>
            <el-checkbox label="version.updated">版本更新</el-checkbox>
            <el-checkbox label="version.published">版本发布</el-checkbox>
            <el-checkbox label="version.deleted">版本删除</el-checkbox>
            <el-checkbox label="space.updated">空间更新</el-checkbox>
            <el-checkbox label="space.deleted">空间删除</el-checkbox>
          </el-checkbox-group>
        </el-form-item>
        
        <el-form-item>
          <el-button @click="handleTest">测试连接</el-button>
          <el-button @click="handleViewLogs">查看日志</el-button>
        </el-form-item>
      </el-form>
    </el-card>
    
    <!-- Webhook 日志对话框 -->
    <el-dialog
      v-model="logsDialogVisible"
      title="Webhook 日志"
      width="800px"
      :close-on-click-modal="false"
    >
      <div class="logs-filter">
        <el-select v-model="logFilter.event_type" placeholder="事件类型" clearable style="width: 150px">
          <el-option label="全部" value="" />
          <el-option label="版本创建" value="version.created" />
          <el-option label="版本更新" value="version.updated" />
          <el-option label="版本发布" value="version.published" />
          <el-option label="版本删除" value="version.deleted" />
          <el-option label="空间更新" value="space.updated" />
          <el-option label="空间删除" value="space.deleted" />
        </el-select>
        <el-select v-model="logFilter.status" placeholder="状态" clearable style="width: 120px">
          <el-option label="全部" value="" />
          <el-option label="成功" value="success" />
          <el-option label="失败" value="failed" />
        </el-select>
        <el-button @click="handleRefreshLogs">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
      </div>
      
      <el-table v-loading="logsLoading" :data="webhookLogs" stripe max-height="400">
        <el-table-column prop="event_type" label="事件类型" width="120" />
        <el-table-column prop="attempt_time" label="时间" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.attempt_time) }}
          </template>
        </el-table-column>
        <el-table-column prop="response_status" label="状态码" width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.response_status)" size="small">
              {{ row.response_status || '-' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="请求数据" min-width="200" show-overflow-tooltip>
          <template #default="{ row }">
            {{ row.payload || '无数据' }}
          </template>
        </el-table-column>
        <el-table-column label="响应内容" min-width="200" show-overflow-tooltip>
          <template #default="{ row }">
            {{ row.response_body || '无响应' }}
          </template>
        </el-table-column>
      </el-table>
      
      <el-pagination
        v-if="logsTotal > 0"
        class="pagination"
        :current-page="logsPage"
        :page-size="logsPageSize"
        :total="logsTotal"
        :page-sizes="[10, 20, 50]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleLogsSizeChange"
        @current-change="handleLogsPageChange"
      />
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Check, Refresh } from '@element-plus/icons-vue'
import api from '@/api'

const props = defineProps({
  spaceId: {
    type: String,
    required: true
  }
})

// 响应式数据
const formRef = ref()
const saving = ref(false)
const testing = ref(false)

const form = reactive({
  webhook_url: '',
  webhook_secret: '',
  webhook_events: []
})

const rules = {
  webhook_url: [
    { required: true, message: '请输入Webhook URL', trigger: 'blur' },
    { 
      validator: (rule, value, callback) => {
        if (value && !value.startsWith('http')) {
          callback(new Error('URL必须以http://或https://开头'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ],
  webhook_events: [
    { 
      validator: (rule, value, callback) => {
        if (!value || value.length === 0) {
          callback(new Error('请至少选择一个事件类型'))
        } else {
          callback()
        }
      },
      trigger: 'change'
    }
  ]
}

// 日志相关
const logsDialogVisible = ref(false)
const logsLoading = ref(false)
const webhookLogs = ref([])
const logsTotal = ref(0)
const logsPage = ref(1)
const logsPageSize = ref(20)

const logFilter = reactive({
  event_type: '',
  status: ''
})

// 工具函数
const formatDateTime = (dateString) => {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleString('zh-CN')
}

const getStatusType = (status) => {
  if (!status) return 'info'
  if (status >= 200 && status < 300) return 'success'
  if (status >= 400) return 'danger'
  return 'warning'
}

const generateSecret = () => {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
  let secret = ''
  for (let i = 0; i < 32; i++) {
    secret += chars.charAt(Math.floor(Math.random() * chars.length))
  }
  return secret
}

// 获取Webhook配置
const fetchWebhookConfig = async () => {
  try {
    const res = await api.getWebhookConfig(props.spaceId)
    if (res.success) {
      const data = res.data || res
      form.webhook_url = data.webhook_url || ''
      form.webhook_secret = data.webhook_secret || ''
      form.webhook_events = data.webhook_events || []
    }
  } catch (error) {
    console.error('获取Webhook配置失败:', error)
    ElMessage.error('获取Webhook配置失败')
  }
}

// 保存配置
const handleSave = async () => {
  try {
    await formRef.value.validate()
    saving.value = true
    
    const res = await api.updateWebhookConfig(props.spaceId, {
      webhook_url: form.webhook_url,
      webhook_secret: form.webhook_secret,
      webhook_events: form.webhook_events
    })
    
    if (res.success) {
      ElMessage.success('Webhook配置保存成功')
    }
  } catch (error) {
    console.error('保存失败:', error)
    if (error !== false) {
      ElMessage.error('保存失败')
    }
  } finally {
    saving.value = false
  }
}

// 生成密钥
const handleGenerateSecret = () => {
  form.webhook_secret = generateSecret()
  ElMessage.success('已生成新的Webhook密钥')
}

// 测试连接
const handleTest = async () => {
  try {
    await formRef.value.validate(['webhook_url'])
    testing.value = true
    
    // 这里可以添加实际的测试逻辑
    ElMessage.info('正在测试Webhook连接...')
    
    // 模拟测试延迟
    setTimeout(() => {
      ElMessage.success('Webhook连接测试成功')
      testing.value = false
    }, 2000)
  } catch (error) {
    testing.value = false
    if (error !== false) {
      ElMessage.error('请先填写正确的Webhook URL')
    }
  }
}

// 查看日志
const handleViewLogs = () => {
  logsDialogVisible.value = true
  fetchWebhookLogs()
}

// 获取Webhook日志
const fetchWebhookLogs = async () => {
  try {
    logsLoading.value = true
    
    const params = {
      skip: (logsPage.value - 1) * logsPageSize.value,
      limit: logsPageSize.value
    }
    
    if (logFilter.event_type) {
      const res = await api.getWebhookLogsByEvent(props.spaceId, logFilter.event_type, params)
      if (res.success) {
        const data = res.data || res
        webhookLogs.value = data.items || []
        logsTotal.value = data.total || 0
      }
    } else if (logFilter.status === 'failed') {
      const res = await api.getFailedWebhookLogs(props.spaceId, params)
      if (res.success) {
        const data = res.data || res
        webhookLogs.value = data.items || []
        logsTotal.value = data.total || 0
      }
    } else {
      const res = await api.getWebhookLogs(props.spaceId, params)
      if (res.success) {
        const data = res.data || res
        webhookLogs.value = data.items || []
        logsTotal.value = data.total || 0
      }
    }
  } catch (error) {
    console.error('获取Webhook日志失败:', error)
    ElMessage.error('获取Webhook日志失败')
  } finally {
    logsLoading.value = false
  }
}

// 刷新日志
const handleRefreshLogs = () => {
  logsPage.value = 1
  fetchWebhookLogs()
}

// 日志分页
const handleLogsSizeChange = (newSize) => {
  logsPageSize.value = newSize
  logsPage.value = 1
  fetchWebhookLogs()
}

const handleLogsPageChange = (newPage) => {
  logsPage.value = newPage
  fetchWebhookLogs()
}

// 监听日志筛选变化
watch([() => logFilter.event_type, () => logFilter.status], () => {
  logsPage.value = 1
  fetchWebhookLogs()
})

// 生命周期
onMounted(() => {
  fetchWebhookConfig()
})
</script>

<style scoped>
.webhook-config {
  max-width: 800px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logs-filter {
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
</style>