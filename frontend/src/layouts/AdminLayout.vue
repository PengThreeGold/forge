<template>
  <div class="admin-layout">
    <el-container class="layout-container">
      <el-aside width="200px" class="aside">
        <div class="logo">
          <el-icon><Box /></el-icon>
          <span>Forge</span>
        </div>
        <el-menu
          :default-active="activeMenu"
          :collapse="false"
          :unique-opened="true"
          @select="handleMenuSelect"
        >
          <el-menu-item index="/admin/spaces">
            <el-icon><Grid /></el-icon>
            <span>软件空间</span>
          </el-menu-item>
          <el-menu-item v-if="authStore.isAdmin" index="/admin/users">
            <el-icon><User /></el-icon>
            <span>用户管理</span>
          </el-menu-item>
          <el-menu-item index="/admin/stats">
            <el-icon><DataAnalysis /></el-icon>
            <span>统计分析</span>
          </el-menu-item>
          <el-menu-item index="/admin/profile">
            <el-icon><Setting /></el-icon>
            <span>个人设置</span>
          </el-menu-item>
        </el-menu>
      </el-aside>
      <el-container class="main-container">
        <el-header class="header">
          <div class="header-content">
            <el-breadcrumb separator="/">
              <el-breadcrumb-item :to="{ path: '/admin' }">首页</el-breadcrumb-item>
              <el-breadcrumb-item v-if="breadcrumb">{{ breadcrumb }}</el-breadcrumb-item>
            </el-breadcrumb>
            <div class="user-info">
              <el-dropdown @command="handleCommand" trigger="click">
                <span class="user-name">
                  {{ authStore.user?.username }}
                  <el-icon><ArrowDown /></el-icon>
                </span>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="profile">个人设置</el-dropdown-item>
                    <el-dropdown-item command="logout" divided>退出登录</el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
          </div>
        </el-header>
        <el-main class="main">
          <div class="content-wrapper">
            <router-view v-slot="{ Component }">
              <keep-alive :include="['AdminSpaces', 'AdminUsers', 'AdminStats', 'AdminProfile']">
                <component :is="Component" />
              </keep-alive>
            </router-view>
          </div>
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

// 计算当前激活的菜单
const activeMenu = computed(() => {
  const path = route.path
  if (path.startsWith('/admin/spaces')) return '/admin/spaces'
  if (path.startsWith('/admin/users')) return '/admin/users'
  if (path.startsWith('/admin/stats')) return '/admin/stats'
  if (path.startsWith('/admin/profile')) return '/admin/profile'
  return path
})

// 计算面包屑
const breadcrumb = computed(() => {
  const name = route.name
  const map = {
    'AdminSpaces': '软件空间',
    'AdminSpaceDetail': '空间详情',
    'AdminUsers': '用户管理',
    'AdminStats': '统计分析',
    'AdminProfile': '个人设置'
  }
  return map[name] || ''
})

// 手动处理菜单选择，提高性能
function handleMenuSelect(index) {
  if (route.path !== index) {
    router.push(index)
  }
}

// 处理用户操作
function handleCommand(command) {
  if (command === 'logout') {
    authStore.logout()
    router.push('/login')
  } else if (command === 'profile') {
    router.push('/admin/profile')
  }
}
</script>

<style scoped>
.admin-layout {
  height: 100vh;
  overflow: hidden;
  /* 性能优化 */
  transform: translate3d(0, 0, 0);
  will-change: auto;
}

.layout-container {
  height: 100%;
  /* 优化布局性能 */
  contain: layout style;
}

.aside {
  background: #001529;
  color: #fff;
  overflow-y: auto;
  overflow-x: hidden;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.15);
  /* 性能优化 */
  transform: translate3d(0, 0, 0);
  -webkit-overflow-scrolling: touch;
  backface-visibility: hidden;
  perspective: 1000px;
}

/* 优化侧边栏滚动条 */
.aside::-webkit-scrollbar {
  width: 6px;
}

.aside::-webkit-scrollbar-track {
  background: #002140;
}

.aside::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 3px;
  transition: background 0.3s;
}

.aside::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.3);
}

.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  font-size: 20px;
  font-weight: bold;
  color: #fff;
  border-bottom: 1px solid #002140;
  /* 性能优化 */
  transform: translate3d(0, 0, 0);
  backface-visibility: hidden;
}

.el-menu {
  border-right: none;
  background-color: #001529;
}

:deep(.el-menu-item) {
  color: rgba(255, 255, 255, 0.65);
  position: relative;
  transform: translate3d(0, 0, 0);
  backface-visibility: hidden;
  transition: color 0.15s ease;
}

:deep(.el-menu-item::before) {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #1890ff;
  opacity: 0;
  transition: opacity 0.15s ease;
  pointer-events: none;
  z-index: -1;
}

:deep(.el-menu-item:hover),
:deep(.el-menu-item.is-active) {
  color: #fff;
}

:deep(.el-menu-item:hover::before),
:deep(.el-menu-item.is-active::before) {
  opacity: 1;
}

:deep(.el-menu-item .el-icon) {
  transform: translate3d(0, 0, 0);
  backface-visibility: hidden;
}

:deep(.el-menu-item:hover .el-icon),
:deep(.el-menu-item.is-active .el-icon) {
  transform: translate3d(0, 0, 0) scale(1.05);
  transition: transform 0.15s ease;
}

.main-container {
  height: 100%;
  display: flex;
  flex-direction: column;
  /* 性能优化 */
  transform: translate3d(0, 0, 0);
  contain: layout style;
}

.header {
  background: #fff;
  border-bottom: 1px solid #e4e7ed;
  padding: 0 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  z-index: 10;
  /* 性能优化 */
  transform: translate3d(0, 0, 0);
  backface-visibility: hidden;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 100%;
}

.user-name {
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 8px 12px;
  border-radius: 4px;
  position: relative;
  transition: none;
  /* 性能优化 */
  transform: translate3d(0, 0, 0);
  backface-visibility: hidden;
}

.user-name::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #f5f7fa;
  border-radius: 4px;
  opacity: 0;
  transition: opacity 0.15s ease;
  z-index: -1;
}

.user-name:hover::before {
  opacity: 1;
}

.main {
  background: #f0f2f5;
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.content-wrapper {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 20px;
  min-height: 0;
  /* 性能优化 */
  will-change: scroll-position;
  transform: translateZ(0);
  -webkit-overflow-scrolling: touch;
  contain: layout style paint;
}

/* 优化滚动条样式 */
.content-wrapper::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

.content-wrapper::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

.content-wrapper::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 4px;
  transition: background 0.2s ease;
}

.content-wrapper::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .aside {
    width: 160px !important;
  }
  
  .logo {
    font-size: 16px;
  }
  
  .header-content {
    padding: 0 10px;
  }
  
  .content-wrapper {
    padding: 10px;
  }
}

/* 暗色模式支持 */
@media (prefers-color-scheme: dark) {
  .header {
    background: #141414;
    border-bottom-color: #303030;
  }
  
  .main {
    background: #000;
  }
  
  .content-wrapper::-webkit-scrollbar-track {
    background: #1a1a1a;
  }
  
  .content-wrapper::-webkit-scrollbar-thumb {
    background: #4a4a4a;
  }
  
  .content-wrapper::-webkit-scrollbar-thumb:hover {
    background: #5a5a5a;
  }
}
</style>
