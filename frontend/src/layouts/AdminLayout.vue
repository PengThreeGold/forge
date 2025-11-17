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
          router
          :collapse="false"
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
              <el-dropdown @command="handleCommand">
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
              <transition name="fade" mode="out-in">
                <component :is="Component" />
              </transition>
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

const activeMenu = computed(() => {
  const path = route.path
  if (path.startsWith('/admin/spaces')) return '/admin/spaces'
  if (path.startsWith('/admin/users')) return '/admin/users'
  if (path.startsWith('/admin/stats')) return '/admin/stats'
  if (path.startsWith('/admin/profile')) return '/admin/profile'
  return path
})

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
}

.layout-container {
  height: 100%;
}

.aside {
  background: #001529;
  color: #fff;
  overflow-y: auto;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.15);
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
}

.el-menu {
  border-right: none;
  background-color: #001529;
}

:deep(.el-menu-item) {
  color: rgba(255, 255, 255, 0.65);
}

:deep(.el-menu-item:hover),
:deep(.el-menu-item.is-active) {
  background-color: #1890ff !important;
  color: #fff;
}

.main-container {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.header {
  background: #fff;
  border-bottom: 1px solid #e4e7ed;
  padding: 0 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  z-index: 10;
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
  padding: 20px;
  min-height: 0;
}

/* 添加页面切换动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
