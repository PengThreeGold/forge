<template>
  <div class="app-layout" :class="{ 'dark-theme': isDarkTheme }">
    <!-- 头部导航 -->
    <app-header />

    <!-- 侧边栏 -->
    <app-sidebar :class="{ 'mobile-open': sidebarMobileOpen }" />

    <!-- 移动端遮罩层 -->
    <div v-if="isMobile && !sidebarCollapsed" class="sidebar-overlay" @click="toggleSidebar"></div>

    <!-- 主内容区 -->
    <main
      class="app-main"
      :class="{
        'sidebar-collapsed': sidebarCollapsed,
        'mobile-sidebar-open': isMobile && !sidebarCollapsed,
      }"
    >
      <div class="page-container">
        <!-- 面包屑导航 -->
        <el-breadcrumb v-if="breadcrumbList.length" separator="/" class="page-breadcrumb">
          <el-breadcrumb-item v-for="item in breadcrumbList" :key="item.path" :to="item.path">
            <el-icon v-if="item.icon">
              <component :is="item.icon" />
            </el-icon>
            {{ item.title }}
          </el-breadcrumb-item>
        </el-breadcrumb>

        <!-- 路由视图 -->
        <router-view v-slot="{ Component }">
          <transition name="fade-transform" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </div>
    </main>
  </div>
</template>

<script>
import { defineComponent, computed, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useStore } from 'vuex'
import AppHeader from './Header.vue'
import AppSidebar from './Sidebar.vue'
import {
  DataLine,
  FolderOpened,
  TrendCharts,
  Setting,
  Document,
  DocumentCopy,
  Edit,
  Lock,
  Shop,
} from '@element-plus/icons-vue'

export default defineComponent({
  name: 'Layout',
  components: {
    AppHeader,
    AppSidebar,
  },
  setup() {
    const store = useStore()
    const route = useRoute()

    // 计算属性
    const sidebarCollapsed = computed(() => store.state.sidebarCollapsed)
    const isDarkTheme = computed(() => store.state.theme === 'dark')
    const isMobile = ref(window.innerWidth <= 768)

    // 侧边栏移动端状态
    const sidebarMobileOpen = ref(false)

    // 面包屑导航
    const breadcrumbList = computed(() => {
      const breadcrumbs = []

      // 根据路由生成面包屑
      if (route.path === '/') {
        breadcrumbs.push({
          title: '仪表盘',
          path: '/',
          icon: 'DataLine',
        })
      } else if (route.path.startsWith('/software')) {
        breadcrumbs.push({
          title: '仪表盘',
          path: '/',
          icon: 'DataLine',
        })
        breadcrumbs.push({
          title: '软件管理',
          path: '/software',
          icon: 'FolderOpened',
        })

        if (route.path === '/software/create') {
          breadcrumbs.push({
            title: '创建软件空间',
            path: '/software/create',
            icon: 'Document',
          })
        } else if (route.path.includes('/edit')) {
          breadcrumbs.push({
            title: '编辑软件空间',
            path: route.path,
            icon: 'Edit',
          })
        } else if (route.path.includes('/releases')) {
          breadcrumbs.push({
            title: '版本发布',
            path: route.path,
            icon: 'DocumentCopy',
          })
        } else if (route.params.id) {
          breadcrumbs.push({
            title: '软件详情',
            path: route.path,
            icon: 'Document',
          })
        } else {
          breadcrumbs.push({
            title: '软件列表',
            path: '/software',
            icon: 'Document',
          })
        }
      } else if (route.path === '/statistics') {
        breadcrumbs.push({
          title: '仪表盘',
          path: '/',
          icon: 'DataLine',
        })
        breadcrumbs.push({
          title: '统计分析',
          path: '/statistics',
          icon: 'TrendCharts',
        })
      } else if (route.path.startsWith('/settings')) {
        breadcrumbs.push({
          title: '系统管理',
          path: '/settings',
          icon: 'Setting',
        })

        if (route.path === '/settings') {
          breadcrumbs.push({
            title: '系统设置',
            path: '/settings',
            icon: 'Setting',
          })
        } else if (route.path === '/permissions') {
          breadcrumbs.push({
            title: '权限管理',
            path: '/permissions',
            icon: 'Lock',
          })
        }
      } else if (route.path.startsWith('/public')) {
        breadcrumbs.push({
          title: '软件商店',
          path: '/public',
          icon: 'Shop',
        })

        if (route.params.id) {
          breadcrumbs.push({
            title: '软件详情',
            path: route.path,
            icon: 'Document',
          })
        }
      }

      return breadcrumbs
    })

    // 切换侧边栏
    const toggleSidebar = () => {
      store.dispatch('toggleSidebar')
      if (isMobile.value) {
        sidebarMobileOpen.value = false
      }
    }

    // 监听窗口大小变化
    const handleResize = () => {
      isMobile.value = window.innerWidth <= 768
      if (!isMobile.value) {
        sidebarMobileOpen.value = false
      }
    }

    // 监听侧边栏状态变化
    watch(sidebarCollapsed, newVal => {
      if (isMobile.value && !newVal) {
        sidebarMobileOpen.value = true
      } else {
        sidebarMobileOpen.value = false
      }
    })

    // 初始化
    window.addEventListener('resize', handleResize)

    return {
      sidebarCollapsed,
      isDarkTheme,
      isMobile,
      sidebarMobileOpen,
      breadcrumbList,
      toggleSidebar,
      DataLine,
      FolderOpened,
      TrendCharts,
      Setting,
      Document,
      DocumentCopy,
      Edit,
      Lock,
      Shop,
    }
  },
})
</script>

<style scoped>
.app-layout {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #f0f2f5;
  transition: background-color 0.3s;
}

.dark-theme .app-layout {
  background-color: #141414;
}

.app-main {
  flex: 1;
  margin-left: 220px;
  margin-top: 60px;
  padding: 0;
  transition:
    margin-left 0.3s,
    margin-top 0.3s;
  overflow-y: auto;
  height: calc(100vh - 60px);
}

.app-main.sidebar-collapsed {
  margin-left: 64px;
}

.mobile-sidebar-open {
  position: fixed;
  left: 0;
  right: 0;
  z-index: 1001;
}

.page-container {
  padding: 20px;
  min-height: 100%;
}

.page-breadcrumb {
  margin-bottom: 20px;
  padding: 12px 16px;
  background-color: #fff;
  border-radius: 4px;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
}

.dark-theme .page-breadcrumb {
  background-color: #1d2935;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.2);
}

.sidebar-overlay {
  position: fixed;
  top: 60px;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 999;
}

/* 页面切换动画 */
.fade-transform-enter-active,
.fade-transform-leave-active {
  transition: all 0.3s;
}

.fade-transform-enter-from {
  opacity: 0;
  transform: translateX(30px);
}

.fade-transform-leave-to {
  opacity: 0;
  transform: translateX(-30px);
}

/* 移动端适配 */
@media (max-width: 768px) {
  .app-main {
    margin-left: 0;
  }

  .app-main.sidebar-collapsed {
    margin-left: 0;
  }

  .page-container {
    padding: 10px;
  }

  .page-breadcrumb {
    padding: 8px 12px;
  }
}
</style>
