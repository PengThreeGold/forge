<template>
  <header class="app-header" :class="{ 'dark-theme': isDarkTheme }">
    <div class="header-left">
      <div class="menu-toggle" @click="toggleSidebar">
        <el-icon :size="24">
          <Fold v-if="!sidebarCollapsed" />
          <Expand v-else />
        </el-icon>
      </div>

      <div class="logo" @click="goHome">
        <span class="logo-text">Forge</span>
      </div>
    </div>

    <div class="header-right">
      <!-- 主题切换 -->
      <el-tooltip content="切换主题" placement="bottom" effect="light">
        <div class="theme-switch" @click="toggleTheme">
          <el-icon :size="20">
            <Moon v-if="isDarkTheme" />
            <Sunny v-else />
          </el-icon>
        </div>
      </el-tooltip>

      <!-- 用户信息 -->
      <el-dropdown trigger="click" @command="handleCommand">
        <div class="user-info">
          <el-avatar :size="32" :icon="UserFilled" />
          <span class="username">{{ username }}</span>
          <el-icon :size="16">
            <ArrowDown />
          </el-icon>
        </div>

        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item command="profile">
              <el-icon><User /></el-icon>
              个人资料
            </el-dropdown-item>
            <el-dropdown-item command="settings">
              <el-icon><Setting /></el-icon>
              系统设置
            </el-dropdown-item>
            <el-dropdown-item divided command="logout">
              <el-icon><SwitchButton /></el-icon>
              退出登录
            </el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
  </header>
</template>

<script>
import { defineComponent, computed, ref } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'
import {
  Fold,
  Expand,
  Moon,
  Sunny,
  UserFilled,
  ArrowDown,
  User,
  Setting,
  SwitchButton,
} from '@element-plus/icons-vue'

export default defineComponent({
  name: 'Header',
  components: {
    Fold,
    Expand,
    Moon,
    Sunny,
    UserFilled,
    ArrowDown,
    User,
    Setting,
    SwitchButton,
  },
  setup() {
    const store = useStore()
    const router = useRouter()

    // 计算属性
    const username = computed(() => store.state.auth.user?.username || '管理员')
    const sidebarCollapsed = computed(() => store.state.sidebarCollapsed)
    const isDarkTheme = computed(() => store.state.theme === 'dark')

    // 切换侧边栏
    const toggleSidebar = () => {
      store.dispatch('toggleSidebar')
    }

    // 切换主题
    const toggleTheme = () => {
      store.dispatch('setTheme', isDarkTheme.value ? 'light' : 'dark')
    }

    // 返回首页
    const goHome = () => {
      router.push('/')
    }

    // 处理下拉菜单命令
    const handleCommand = command => {
      switch (command) {
        case 'profile':
          router.push('/settings')
          break
        case 'settings':
          router.push('/settings')
          break
        case 'logout':
          handleLogout()
          break
      }
    }

    // 处理退出登录
    const handleLogout = async () => {
      try {
        await store.dispatch('auth/logout')
        router.push('/login')
      } catch (error) {
        console.error('退出登录失败:', error)
      }
    }

    return {
      username,
      sidebarCollapsed,
      isDarkTheme,
      toggleSidebar,
      toggleTheme,
      goHome,
      handleCommand,
    }
  },
})
</script>

<style scoped>
.app-header {
  height: 60px;
  padding: 0 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  background-color: #fff;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  transition: background-color 0.3s;
}

.dark-theme .app-header {
  background-color: #1d2935;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.2);
}

.header-left {
  display: flex;
  align-items: center;
}

.menu-toggle {
  cursor: pointer;
  margin-right: 16px;
  color: #606266;
  transition: color 0.3s;
}

.menu-toggle:hover {
  color: #409eff;
}

.dark-theme .menu-toggle {
  color: #a8abb2;
}

.dark-theme .menu-toggle:hover {
  color: #79bbff;
}

.logo {
  display: flex;
  align-items: center;
  cursor: pointer;
}

.logo-text {
  font-size: 20px;
  font-weight: bold;
  color: #409eff;
  margin-left: 8px;
}

.dark-theme .logo-text {
  color: #79bbff;
}

.header-right {
  display: flex;
  align-items: center;
}

.theme-switch {
  margin-right: 20px;
  cursor: pointer;
  color: #606266;
  transition: color 0.3s;
}

.theme-switch:hover {
  color: #409eff;
}

.dark-theme .theme-switch {
  color: #a8abb2;
}

.dark-theme .theme-switch:hover {
  color: #79bbff;
}

.user-info {
  display: flex;
  align-items: center;
  cursor: pointer;
  padding: 0 8px;
  border-radius: 4px;
  transition: background-color 0.3s;
}

.user-info:hover {
  background-color: rgba(0, 0, 0, 0.04);
}

.dark-theme .user-info:hover {
  background-color: rgba(255, 255, 255, 0.06);
}

.username {
  margin: 0 8px;
  font-size: 14px;
  color: #303133;
}

.dark-theme .username {
  color: #e5eaf3;
}

@media (max-width: 768px) {
  .app-header {
    padding: 0 10px;
  }

  .username {
    display: none;
  }
}
</style>
