<template>
  <div class="init-admin">
    <el-card class="init-card">
      <template #header>
        <h2>初始化管理员账户</h2>
      </template>
      
      <el-alert
        v-if="!needsInit"
        title="系统已初始化"
        type="success"
        description="管理员账户已存在，无需再次初始化"
        show-icon
        :closable="false"
      />
      
      <div v-else>
        <el-alert
          title="首次使用系统"
          type="warning"
          description="请设置管理员账户，此操作只能执行一次"
          show-icon
          :closable="false"
          style="margin-bottom: 20px"
        />
        
        <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
          <el-form-item label="用户名" prop="username">
            <el-input 
              v-model="form.username" 
              placeholder="请输入管理员用户名"
              maxlength="50"
              show-word-limit
            />
          </el-form-item>
          
          <el-form-item label="邮箱" prop="email">
            <el-input 
              v-model="form.email" 
              type="email"
              placeholder="请输入邮箱地址（可选）"
            />
          </el-form-item>
          
          <el-form-item label="密码" prop="password">
            <el-input 
              v-model="form.password" 
              type="password" 
              show-password
              placeholder="请输入密码"
            />
          </el-form-item>
          
          <el-form-item label="确认密码" prop="confirmPassword">
            <el-input 
              v-model="form.confirmPassword" 
              type="password" 
              show-password
              placeholder="请再次输入密码"
            />
          </el-form-item>
          
          <el-form-item>
            <el-button type="primary" :loading="loading" @click="handleSubmit">
              创建管理员账户
            </el-button>
            <el-button @click="handleReset">重置</el-button>
          </el-form-item>
        </el-form>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import api from '@/api'

const router = useRouter()

// 响应式数据
const formRef = ref()
const loading = ref(false)
const needsInit = ref(false)

const form = reactive({
  username: '',
  email: '',
  password: '',
  confirmPassword: ''
})

// 表单验证规则
const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 50, message: '用户名长度应在3-50个字符之间', trigger: 'blur' },
    { 
      pattern: /^[a-zA-Z0-9_-]+$/,
      message: '用户名只能包含字母、数字、下划线和连字符',
      trigger: 'blur'
    }
  ],
  email: [
    { 
      validator: (rule, value, callback) => {
        if (value && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) {
          callback(new Error('请输入有效的邮箱地址'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 100, message: '密码长度应在6-100个字符之间', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    { 
      validator: (rule, value, callback) => {
        if (value !== form.password) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

// 检查是否需要初始化
const checkInitStatus = async () => {
  try {
    // 尝试调用初始化接口，如果返回错误说明已经初始化
    const res = await api.initAdmin({})
    if (res.code === 400 || res.code === 403) {
      needsInit.value = false
    } else {
      needsInit.value = true
    }
  } catch (error) {
    // 如果返回403错误，说明已经初始化
    if (error.response?.status === 403) {
      needsInit.value = false
    } else {
      // 其他错误，假设需要初始化
      needsInit.value = true
    }
  }
}

// 提交表单
const handleSubmit = async () => {
  try {
    await formRef.value.validate()
    loading.value = true
    
    const res = await api.initAdmin({
      username: form.username,
      email: form.email || null,
      password: form.password
    })
    
    if (res.success) {
      ElMessage.success('管理员账户创建成功！')
      // 跳转到登录页面
      router.push('/login')
    }
  } catch (error) {
    console.error('创建管理员账户失败:', error)
    if (error !== false) { // 表单验证错误时不显示
      ElMessage.error('创建管理员账户失败')
    }
  } finally {
    loading.value = false
  }
}

// 重置表单
const handleReset = () => {
  formRef.value.resetFields()
}

// 生命周期
onMounted(() => {
  checkInitStatus()
})
</script>

<style scoped>
.init-admin {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.init-card {
  width: 100%;
  max-width: 500px;
  margin: 20px;
}

.init-card h2 {
  margin: 0;
  text-align: center;
  color: #303133;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .init-card {
    margin: 10px;
  }
}
</style>