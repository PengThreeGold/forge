<template>
  <div class="software-edit-container" v-loading="loading">
    <div class="page-header">
      <div class="page-title">
        <el-button icon="ArrowLeft" circle @click="goBack" />
        <h2>{{ isEdit ? '编辑软件空间' : '创建软件空间' }}</h2>
      </div>
    </div>
    
    <el-card shadow="hover" class="edit-card">
      <el-form
        ref="spaceFormRef"
        :model="spaceForm"
        :rules="spaceRules"
        label-width="120px"
      >
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
            :rows="6"
            placeholder="请输入软件描述"
          />
        </el-form-item>
        
        <el-form-item label="Webhook URL" prop="webhook_url">
          <el-input v-model="spaceForm.webhook_url" placeholder="请输入Webhook URL（可选）" />
          <div class="form-tip">
            用于接收软件下载、版本发布等事件通知的回调地址
          </div>
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" :loading="submitLoading" @click="handleSubmit">
            {{ isEdit ? '更新' : '创建' }}
          </el-button>
          <el-button @click="goBack">取消</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script>
import { defineComponent, ref, reactive, onMounted } from 'vue'
import { useStore } from 'vuex'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'

export default defineComponent({
  name: 'SoftwareEdit',
  setup() {
    const store = useStore()
    const router = useRouter()
    const route = useRoute()
    
    // 数据
    const loading = ref(false)
    const submitLoading = ref(false)
    const isEdit = ref(false)
    const spaceId = ref(null)
    
    // 表单
    const spaceForm = reactive({
      name: '',
      author: '',
      description: '',
      webhook_url: ''
    })
    
    const spaceRules = {
      name: [
        { required: true, message: '请输入软件名称', trigger: 'blur' }
      ]
    }
    
    const spaceFormRef = ref(null)
    
    // 获取软件空间详情
    const getSpaceDetail = async () => {
      try {
        loading.value = true
        
        const response = await store.dispatch('software/getSpace', spaceId.value)
        
        // 填充表单
        spaceForm.name = response.data.name
        spaceForm.author = response.data.author || ''
        spaceForm.description = response.data.description || ''
        spaceForm.webhook_url = response.data.webhook_url || ''
      } catch (error) {
        console.error('获取软件空间详情失败:', error)
        ElMessage.error('获取软件空间详情失败')
      } finally {
        loading.value = false
      }
    }
    
    // 处理提交
    const handleSubmit = async () => {
      if (!spaceFormRef.value) return
      
      try {
        await spaceFormRef.value.validate()
        
        submitLoading.value = true
        
        if (isEdit.value) {
          // 更新软件空间
          await store.dispatch('software/updateSpace', {
            spaceId: spaceId.value,
            spaceData: spaceForm
          })
          ElMessage.success('更新成功')
        } else {
          // 创建软件空间
          await store.dispatch('software/createSpace', spaceForm)
          ElMessage.success('创建成功')
        }
        
        // 返回列表页
        goBack()
      } catch (error) {
        console.error('操作失败:', error)
      } finally {
        submitLoading.value = false
      }
    }
    
    // 返回上一页
    const goBack = () => {
      router.push('/software')
    }
    
    onMounted(() => {
      // 检查是否是编辑模式
      if (route.params.id) {
        isEdit.value = true
        spaceId.value = parseInt(route.params.id)
        getSpaceDetail()
      }
    })
    
    return {
      loading,
      submitLoading,
      isEdit,
      spaceForm,
      spaceRules,
      spaceFormRef,
      handleSubmit,
      goBack
    }
  }
})
</script>

<style scoped>
.software-edit-container {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-title {
  display: flex;
  align-items: center;
}

.page-title h2 {
  margin: 0 0 0 10px;
  font-size: 24px;
  font-weight: 500;
}

.edit-card {
  max-width: 800px;
  margin: 0 auto;
}

.form-tip {
  color: #909399;
  font-size: 12px;
  margin-top: 5px;
  line-height: 1.5;
}

@media (max-width: 768px) {
  .software-edit-container {
    padding: 10px;
  }
  
  .page-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .page-title h2 {
    font-size: 20px;
  }
  
  .edit-card {
    margin: 0;
  }
}

.dark-theme .form-tip {
  color: #a8abb2;
}
</style>