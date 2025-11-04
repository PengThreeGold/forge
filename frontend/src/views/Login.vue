<template>
  <div class="login-container">
    <div class="login-box">
      <div class="login-header">
        <h1>Forge</h1>
        <p>软件发布管理平台</p>
      </div>

      <el-form
        ref="loginFormRef"
        :model="loginForm"
        :rules="loginRules"
        class="login-form"
        @keyup.enter="handleLogin"
      >
        <el-form-item prop="username">
          <el-input
            v-model="loginForm.username"
            placeholder="用户名"
            prefix-icon="User"
            size="large"
          />
        </el-form-item>

        <el-form-item prop="password">
          <el-input
            v-model="loginForm.password"
            type="password"
            placeholder="密码"
            prefix-icon="Lock"
            show-password
            size="large"
          />
        </el-form-item>

        <el-form-item>
          <el-button
            :loading="loading"
            type="primary"
            size="large"
            class="login-button"
            @click="handleLogin"
          >
            登录
          </el-button>
        </el-form-item>
      </el-form>

      <div class="login-footer">
        <p v-if="initAdminRequired" class="init-admin-tip">尚未初始化管理员账户，请先初始化</p>
        <el-button v-if="initAdminRequired" type="text" @click="showInitAdminDialog">
          初始化管理员账户
        </el-button>
      </div>
    </div>

    <!-- 初始化管理员对话框 -->
    <el-dialog
      v-model="initAdminDialogVisible"
      title="初始化管理员账户"
      width="400px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="initAdminFormRef"
        :model="initAdminForm"
        :rules="initAdminRules"
        label-width="100px"
      >
        <el-form-item label="用户名" prop="username">
          <el-input v-model="initAdminForm.username" placeholder="请输入管理员用户名" />
        </el-form-item>

        <el-form-item label="密码" prop="password">
          <el-input
            v-model="initAdminForm.password"
            type="password"
            placeholder="请输入密码"
            show-password
          />
        </el-form-item>

        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input
            v-model="initAdminForm.confirmPassword"
            type="password"
            placeholder="请再次输入密码"
            show-password
          />
        </el-form-item>

        <el-form-item label="邮箱" prop="email">
          <el-input v-model="initAdminForm.email" placeholder="请输入邮箱（可选）" />
        </el-form-item>
      </el-form>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="initAdminDialogVisible = false">取消</el-button>
          <el-button type="primary" :loading="initAdminLoading" @click="handleInitAdmin">
            确认
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { defineComponent, ref, reactive, onMounted } from 'vue'
import { useStore } from 'vuex'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'

export default defineComponent({
  name: 'Login',
  setup() {
    const store = useStore()
    const router = useRouter()
    const route = useRoute()

    // 登录表单
    const loginForm = reactive({
      username: '',
      password: '',
    })

    const loginRules = {
      username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
      password: [
        { required: true, message: '请输入密码', trigger: 'blur' },
        { min: 6, message: '密码长度不能少于6位', trigger: 'blur' },
      ],
    }

    const loginFormRef = ref(null)
    const loading = ref(false)

    // 初始化管理员表单
    const initAdminDialogVisible = ref(false)
    const initAdminLoading = ref(false)
    const initAdminRequired = ref(false)

    const initAdminForm = reactive({
      username: 'admin',
      password: '',
      confirmPassword: '',
      email: '',
    })

    const initAdminRules = {
      username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
      password: [
        { required: true, message: '请输入密码', trigger: 'blur' },
        { min: 6, message: '密码长度不能少于6位', trigger: 'blur' },
      ],
      confirmPassword: [
        { required: true, message: '请再次输入密码', trigger: 'blur' },
        {
          validator: (rule, value, callback) => {
            if (value !== initAdminForm.password) {
              callback(new Error('两次输入的密码不一致'))
            } else {
              callback()
            }
          },
          trigger: 'blur',
        },
      ],
      email: [{ type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }],
    }

    const initAdminFormRef = ref(null)

    // 检查是否需要初始化管理员
    const checkInitAdmin = async () => {
      try {
        // 首先检查是否有token
        const hasToken = store.getters.token
        if (!hasToken) {
          // 没有token，调用后端的安全检查接口（GET），不会创建管理员
          try {
            const data = await store.dispatch('auth/checkInitAdmin')
            initAdminRequired.value = !!data && data.init_required === true
          } catch (initError) {
            // 如果检查接口异常，将提示初始化为必需（更安全的默认）
            initAdminRequired.value = true
          }
        } else {
          // 有token，尝试获取用户信息
          await store.dispatch('auth/getUserProfile')
        }
      } catch (error) {
        if (error.response && error.response.status === 401) {
          // token无效，调用后端的安全检查接口
          try {
            const data = await store.dispatch('auth/checkInitAdmin')
            initAdminRequired.value = !!data && data.init_required === true
          } catch (initError) {
            initAdminRequired.value = true
          }
        }
      }
    }

    // 处理登录
    const handleLogin = async () => {
      if (!loginFormRef.value) return

      try {
        await loginFormRef.value.validate()

        loading.value = true
        await store.dispatch('auth/login', {
          username: loginForm.username,
          password: loginForm.password,
        })

        ElMessage.success('登录成功')

        // 跳转到之前的页面或仪表盘
        const redirect = route.query.redirect || '/dashboard'
        router.push(redirect)
      } catch (error) {
        console.error('登录失败:', error)
        // 显示错误消息
        const errorMsg = error.response?.data?.message || '登录失败，请检查用户名和密码'
        ElMessage({
          message: errorMsg,
          type: 'error',
          duration: 5 * 1000,
        })
      } finally {
        loading.value = false
      }
    }

    // 显示初始化管理员对话框
    const showInitAdminDialog = () => {
      initAdminDialogVisible.value = true
    }

    // 处理初始化管理员
    const handleInitAdmin = async () => {
      if (!initAdminFormRef.value) return

      try {
        await initAdminFormRef.value.validate()

        initAdminLoading.value = true

        // 创建管理员账户
        await store.dispatch('auth/initAdmin', {
          username: initAdminForm.username,
          password: initAdminForm.password,
          email: initAdminForm.email,
        })

        ElMessage.success('管理员账户创建成功，请使用新账户登录')

        // 重置表单并关闭对话框
        initAdminFormRef.value.resetFields()
        initAdminDialogVisible.value = false
        initAdminRequired.value = false
      } catch (error) {
        console.error('初始化管理员失败:', error)
        // 显示错误消息
        const errorMsg = error.response?.data?.message || '初始化管理员账户失败'
        ElMessage({
          message: errorMsg,
          type: 'error',
          duration: 5 * 1000,
        })
      } finally {
        initAdminLoading.value = false
      }
    }

    onMounted(() => {
      // 检查是否需要初始化管理员
      checkInitAdmin()

      // 如果已经登录，直接跳转到仪表盘
      if (store.getters.isAuthenticated) {
        router.push('/dashboard')
      }
    })

    return {
      loginForm,
      loginRules,
      loginFormRef,
      loading,
      handleLogin,
      initAdminDialogVisible,
      initAdminLoading,
      initAdminRequired,
      initAdminForm,
      initAdminRules,
      initAdminFormRef,
      showInitAdminDialog,
      handleInitAdmin,
    }
  },
})
</script>

<style scoped>
.login-container {
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: linear-gradient(135deg, #1a2a6c, #b21f1f, #fdbb2d);
  background-size: 150% 150%;
  animation: gradientBG 25s ease infinite;
}

@keyframes gradientBG {
  0% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
  100% {
    background-position: 0% 50%;
  }
}

.login-box {
  width: 400px;
  padding: 40px;
  background: rgba(255, 255, 255, 0.85);
  border-radius: 10px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  /* 进一步减少模糊效果以降低资源消耗 */
  backdrop-filter: blur(1px);
  -webkit-backdrop-filter: blur(1px);
  /* 只在hover时添加过渡效果，减少持续渲染 */
}

.login-box:hover {
  transition:
    transform 0.2s ease,
    box-shadow 0.2s ease;
  transform: translateY(-1px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
}

.login-header {
  text-align: center;
  margin-bottom: 30px;
}

.login-header h1 {
  font-size: 36px;
  font-weight: 700;
  color: #409eff;
  margin: 0 0 10px;
}

.login-header p {
  font-size: 16px;
  color: #606266;
  margin: 0;
}

.login-form {
  margin-top: 20px;
  /* 减少不必要的重绘 */
  transform: translateZ(0);
  will-change: auto;
}

.login-button {
  width: 100%;
}

.login-footer {
  margin-top: 20px;
  text-align: center;
}

.init-admin-tip {
  color: #f56c6c;
  font-size: 14px;
  margin: 0 0 10px;
}

.dark-theme .login-box {
  background: rgba(30, 30, 30, 0.95);
  color: #e5eaf3;
}

.dark-theme .login-header p {
  color: #cfd3dc;
}

.dark-theme .init-admin-tip {
  color: #ef9a9a;
}

@media (max-width: 768px) {
  .login-box {
    width: 90%;
    padding: 30px 20px;
  }

  .login-header h1 {
    font-size: 30px;
  }
}
</style>
