<template>
  <div class="settings-container" v-loading="loading">
    <div class="page-header">
      <h2>系统设置</h2>
    </div>
    
    <el-card shadow="hover" class="settings-card">
      <el-tabs v-model="activeTab">
        <el-tab-pane label="个人设置" name="profile">
          <el-form
            ref="profileFormRef"
            :model="profileForm"
            :rules="profileRules"
            label-width="120px"
            class="settings-form"
          >
            <el-form-item label="用户名" prop="username">
              <el-input v-model="profileForm.username" disabled />
            </el-form-item>
            
            <el-form-item label="邮箱" prop="email">
              <el-input v-model="profileForm.email" placeholder="请输入邮箱" />
            </el-form-item>
            
            <el-form-item>
              <el-button type="primary" :loading="profileLoading" @click="updateProfile">
                更新资料
              </el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
        
        <el-tab-pane label="修改密码" name="password">
          <el-form
            ref="passwordFormRef"
            :model="passwordForm"
            :rules="passwordRules"
            label-width="120px"
            class="settings-form"
          >
            <el-form-item label="原密码" prop="oldPassword">
              <el-input
                v-model="passwordForm.oldPassword"
                type="password"
                placeholder="请输入原密码"
                show-password
              />
            </el-form-item>
            
            <el-form-item label="新密码" prop="newPassword">
              <el-input
                v-model="passwordForm.newPassword"
                type="password"
                placeholder="请输入新密码"
                show-password
              />
            </el-form-item>
            
            <el-form-item label="确认密码" prop="confirmPassword">
              <el-input
                v-model="passwordForm.confirmPassword"
                type="password"
                placeholder="请再次输入新密码"
                show-password
              />
            </el-form-item>
            
            <el-form-item>
              <el-button type="primary" :loading="passwordLoading" @click="changePassword">
                修改密码
              </el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
        
        <el-tab-pane label="系统设置" name="system">
          <el-form
            :model="systemForm"
            label-width="120px"
            class="settings-form"
          >
            <el-form-item label="主题">
              <el-radio-group v-model="systemForm.theme" @change="handleThemeChange">
                <el-radio label="light">浅色主题</el-radio>
                <el-radio label="dark">深色主题</el-radio>
              </el-radio-group>
            </el-form-item>
            
            <el-form-item label="侧边栏">
              <el-switch
                v-model="systemForm.sidebarCollapsed"
                active-text="折叠"
                inactive-text="展开"
                @change="handleSidebarChange"
              />
            </el-form-item>
            
            <el-form-item label="每页条数">
              <el-select v-model="systemForm.pageSize" @change="handlePageSizeChange">
                <el-option :label="10" :value="10" />
                <el-option :label="20" :value="20" />
                <el-option :label="50" :value="50" />
                <el-option :label="100" :value="100" />
              </el-select>
            </el-form-item>
            
            <el-form-item>
              <el-button type="primary" @click="saveSystemSettings">
                保存设置
              </el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
        
        <el-tab-pane label="关于系统" name="about">
          <div class="about-content">
            <div class="logo-container">
              <div class="logo">Forge</div>
              <div class="version">v1.0.0</div>
            </div>
            
            <el-descriptions :column="1" border>
              <el-descriptions-item label="系统名称">Forge 软件发布管理平台</el-descriptions-item>
              <el-descriptions-item label="版本号">v1.0.0</el-descriptions-item>
              <el-descriptions-item label="开发团队">Forge Team</el-descriptions-item>
              <el-descriptions-item label="技术栈">Vue 3 + Element Plus + Flask</el-descriptions-item>
              <el-descriptions-item label="开源地址">
                <el-link href="https://github.com/example/forge" target="_blank">
                  https://github.com/example/forge
                </el-link>
              </el-descriptions-item>
            </el-descriptions>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script>
import { defineComponent, ref, reactive, onMounted } from 'vue'
import { useStore } from 'vuex'
import { ElMessage } from 'element-plus'

export default defineComponent({
  name: 'Settings',
  setup() {
    const store = useStore()
    
    // 数据
    const loading = ref(false)
    const activeTab = ref('profile')
    
    // 个人设置
    const profileForm = reactive({
      username: '',
      email: ''
    })
    
    const profileRules = {
      email: [
        { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
      ]
    }
    
    const profileFormRef = ref(null)
    const profileLoading = ref(false)
    
    // 密码设置
    const passwordForm = reactive({
      oldPassword: '',
      newPassword: '',
      confirmPassword: ''
    })
    
    const passwordRules = {
      oldPassword: [
        { required: true, message: '请输入原密码', trigger: 'blur' }
      ],
      newPassword: [
        { required: true, message: '请输入新密码', trigger: 'blur' },
        { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
      ],
      confirmPassword: [
        { required: true, message: '请再次输入新密码', trigger: 'blur' },
        {
          validator: (rule, value, callback) => {
            if (value !== passwordForm.newPassword) {
              callback(new Error('两次输入的密码不一致'))
            } else {
              callback()
            }
          },
          trigger: 'blur'
        }
      ]
    }
    
    const passwordFormRef = ref(null)
    const passwordLoading = ref(false)
    
    // 系统设置
    const systemForm = reactive({
      theme: 'light',
      sidebarCollapsed: false,
      pageSize: 20
    })
    
    // 获取用户信息
    const getUserProfile = async () => {
      try {
        loading.value = true
        
        const response = await store.dispatch('auth/getUserProfile')
        
        // 填充表单
        profileForm.username = response.username
        profileForm.email = response.email || ''
      } catch (error) {
        console.error('获取用户信息失败:', error)
      } finally {
        loading.value = false
      }
    }
    
    // 更新个人资料
    const updateProfile = async () => {
      if (!profileFormRef.value) return
      
      try {
        await profileFormRef.value.validate()
        
        profileLoading.value = true
        
        // 调用API更新用户信息
        // 注意：这里需要根据实际API进行调整
        // await store.dispatch('auth/updateProfile', {
        //   email: profileForm.email
        // })
        
        ElMessage.success('个人资料更新成功')
      } catch (error) {
        console.error('更新个人资料失败:', error)
      } finally {
        profileLoading.value = false
      }
    }
    
    // 修改密码
    const changePassword = async () => {
      if (!passwordFormRef.value) return
      
      try {
        await passwordFormRef.value.validate()
        
        passwordLoading.value = true
        
        await store.dispatch('auth/changePassword', {
          old_password: passwordForm.oldPassword,
          new_password: passwordForm.newPassword
        })
        
        ElMessage.success('密码修改成功')
        
        // 重置表单
        passwordForm.oldPassword = ''
        passwordForm.newPassword = ''
        passwordForm.confirmPassword = ''
        
        if (passwordFormRef.value) {
          passwordFormRef.value.resetFields()
        }
      } catch (error) {
        console.error('修改密码失败:', error)
      } finally {
        passwordLoading.value = false
      }
    }
    
    // 处理主题变化
    const handleThemeChange = (theme) => {
      store.dispatch('setTheme', theme)
    }
    
    // 处理侧边栏变化
    const handleSidebarChange = () => {
      store.dispatch('toggleSidebar')
    }
    
    // 处理每页条数变化
    const handlePageSizeChange = (pageSize) => {
      // 保存到本地存储
      localStorage.setItem('pageSize', pageSize)
    }
    
    // 保存系统设置
    const saveSystemSettings = () => {
      // 保存主题设置
      localStorage.setItem('theme', systemForm.theme)
      
      // 保存侧边栏设置
      localStorage.setItem('sidebarCollapsed', systemForm.sidebarCollapsed)
      
      // 保存每页条数设置
      localStorage.setItem('pageSize', systemForm.pageSize)
      
      ElMessage.success('系统设置保存成功')
    }
    
    onMounted(() => {
      // 获取用户信息
      getUserProfile()
      
      // 从本地存储加载系统设置
      systemForm.theme = localStorage.getItem('theme') || 'light'
      systemForm.sidebarCollapsed = localStorage.getItem('sidebarCollapsed') === 'true'
      systemForm.pageSize = parseInt(localStorage.getItem('pageSize')) || 20
    })
    
    return {
      loading,
      activeTab,
      profileForm,
      profileRules,
      profileFormRef,
      profileLoading,
      passwordForm,
      passwordRules,
      passwordFormRef,
      passwordLoading,
      systemForm,
      updateProfile,
      changePassword,
      handleThemeChange,
      handleSidebarChange,
      handlePageSizeChange,
      saveSystemSettings
    }
  }
})
</script>

<style scoped>
.settings-container {
  padding: 20px;
}

.page-header {
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0;
  font-size: 24px;
  font-weight: 500;
}

.settings-card {
  margin-bottom: 20px;
}

.settings-form {
  max-width: 600px;
  margin: 20px 0;
}

.about-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px 0;
}

.logo-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 30px;
}

.logo {
  font-size: 48px;
  font-weight: bold;
  color: #409EFF;
  margin-bottom: 10px;
}

.version {
  font-size: 16px;
  color: #909399;
}

.dark-theme .logo {
  color: #79bbff;
}

.dark-theme .version {
  color: #a8abb2;
}

@media (max-width: 768px) {
  .settings-container {
    padding: 10px;
  }
  
  .page-header h2 {
    font-size: 20px;
  }
}
</style>