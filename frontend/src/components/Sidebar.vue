<template>
  <aside class="app-sidebar" :class="{ 'dark-theme': isDarkTheme, collapsed: sidebarCollapsed }">
    <div class="sidebar-container">
      <el-menu
        :default-active="activeMenu"
        :collapse="sidebarCollapsed"
        :collapse-transition="false"
        class="sidebar-menu"
        @select="handleSelect"
        :unique-opened="true"
        router
      >
        <!-- 仪表盘 -->
        <el-menu-item index="/">
          <el-icon><DataLine /></el-icon>
          <template #title>仪表盘</template>
        </el-menu-item>

        <!-- 软件管理 -->
        <el-sub-menu index="software">
          <template #title>
            <el-icon><FolderOpened /></el-icon>
            <span>软件管理</span>
          </template>
          <el-menu-item index="/software">软件列表</el-menu-item>
          <el-menu-item index="/software/create">添加软件</el-menu-item>
        </el-sub-menu>

        <!-- 统计分析 -->
        <el-menu-item index="/statistics">
          <el-icon><TrendCharts /></el-icon>
          <template #title>统计分析</template>
        </el-menu-item>

        <!-- 系统设置 -->
        <el-menu-item index="/settings">
          <el-icon><Setting /></el-icon>
          <template #title>系统设置</template>
        </el-menu-item>
      </el-menu>

      <!-- 底部信息 -->
      <div class="sidebar-footer" v-if="!sidebarCollapsed">
        <div class="version-info">
          <div class="version">Forge v1.0.0</div>
          <div class="copyright">© 2023 Forge Team</div>
        </div>
      </div>
    </div>
  </aside>
</template>

<script>
import { defineComponent, computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useStore } from 'vuex'
import { DataLine, FolderOpened, TrendCharts, Setting } from '@element-plus/icons-vue'

export default defineComponent({
  name: 'Sidebar',
  components: {
    DataLine,
    FolderOpened,
    TrendCharts,
    Setting,
  },
  setup() {
    const route = useRoute()
    const router = useRouter()
    const store = useStore()

    // 计算属性
    const sidebarCollapsed = computed(() => store.state.sidebarCollapsed)
    const isDarkTheme = computed(() => store.state.theme === 'dark')

    // 当前激活的菜单项
    const activeMenu = computed(() => {
      return route.path
    })

    // 处理菜单选择
    const handleSelect = index => {
      router.push(index)
    }

    return {
      sidebarCollapsed,
      isDarkTheme,
      activeMenu,
      handleSelect,
    }
  },
})
</script>

<style scoped>
.app-sidebar {
  position: fixed;
  top: 60px;
  left: 0;
  bottom: 0;
  width: 220px;
  background-color: #fff;
  transition:
    width 0.3s,
    background-color 0.3s;
  box-shadow: 1px 0 4px rgba(0, 21, 41, 0.08);
  z-index: 900;
  overflow: hidden;
}

.dark-theme .app-sidebar {
  background-color: #1d2935;
  box-shadow: 1px 0 4px rgba(0, 0, 0, 0.2);
}

.app-sidebar.collapsed {
  width: 64px;
}

.sidebar-container {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.sidebar-menu {
  flex: 1;
  border-right: none;
  background-color: transparent;
}

.sidebar-menu:not(.el-menu--collapse) {
  width: 220px;
}

/* 暗色主题菜单样式 */
.dark-theme :deep(.el-menu) {
  background-color: #1d2935;
}

.dark-theme :deep(.el-menu-item) {
  color: #a8abb2;
}

.dark-theme :deep(.el-menu-item:hover) {
  background-color: rgba(255, 255, 255, 0.06);
  color: #79bbff;
}

.dark-theme :deep(.el-menu-item.is-active) {
  background-color: #1890ff;
  color: #fff;
}

.dark-theme :deep(.el-sub-menu__title) {
  color: #a8abb2;
}

.dark-theme :deep(.el-sub-menu__title:hover) {
  background-color: rgba(255, 255, 255, 0.06);
  color: #79bbff;
}

.dark-theme :deep(.el-sub-menu.is-active .el-sub-menu__title) {
  color: #79bbff;
}

.dark-theme :deep(.el-sub-menu .el-menu) {
  background-color: #0c1220;
}

.dark-theme :deep(.el-sub-menu .el-menu-item) {
  background-color: #0c1220;
}

.dark-theme :deep(.el-sub-menu .el-menu-item.is-active) {
  background-color: #1890ff;
}

.sidebar-footer {
  padding: 16px;
  border-top: 1px solid #f0f0f0;
  transition: all 0.3s;
}

.dark-theme .sidebar-footer {
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.version-info {
  text-align: center;
}

.version {
  font-size: 12px;
  color: #909399;
  margin-bottom: 4px;
}

.copyright {
  font-size: 11px;
  color: #c0c4cc;
}

.dark-theme .version {
  color: #a8abb2;
}

.dark-theme .copyright {
  color: #7c7e81;
}

/* 移动端适配 */
@media (max-width: 768px) {
  .app-sidebar {
    transform: translateX(-100%);
    transition: transform 0.3s;
  }

  .app-sidebar.mobile-open {
    transform: translateX(0);
  }

  .app-sidebar.collapsed {
    width: 220px;
  }
}
</style>
