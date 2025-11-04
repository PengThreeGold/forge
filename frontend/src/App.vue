<template>
  <div id="app" :class="{ 'dark-theme': isDarkTheme }">
    <template v-if="$route.path !== '/login'">
      <layout />
    </template>
    <template v-else>
      <router-view />
    </template>
  </div>
</template>

<script>
import { defineComponent, computed } from 'vue'
import { useStore } from 'vuex'
import Layout from './components/Layout.vue'

export default defineComponent({
  name: 'App',
  components: {
    Layout,
  },
  setup() {
    const store = useStore()

    // 计算属性
    const isDarkTheme = computed(() => store.state.theme === 'dark')

    // 检查系统主题偏好
    const checkTheme = () => {
      if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
        document.body.classList.add('dark-theme')
      } else {
        document.body.classList.remove('dark-theme')
      }

      // 监听系统主题变化
      if (window.matchMedia) {
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', e => {
          if (e.matches) {
            document.body.classList.add('dark-theme')
          } else {
            document.body.classList.remove('dark-theme')
          }
        })
      }
    }

    // 初始化
    checkTheme()

    return {
      isDarkTheme,
    }
  },
})
</script>

<style>
/* 全局样式 */
#app {
  font-family:
    'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', '微软雅黑',
    Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
  height: 100vh;
  overflow: hidden;
}

/* 暗色主题 */
.dark-theme {
  --el-bg-color: #1a1a1a;
  --el-text-color-primary: #e5eaf3;
  --el-text-color-regular: #cfd3dc;
  --el-border-color: #4c4d4f;
  --el-fill-color-blank: #1a1a1a;
  --el-fill-color-light: #262727;
  --el-fill-color-lighter: #2b2b2d;
  --el-mask-color: rgba(0, 0, 0, 0.8);
}

/* 滚动条样式 */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-thumb {
  background-color: #909399;
  border-radius: 4px;
}

.dark-theme ::-webkit-scrollbar-thumb {
  background-color: #606266;
}

::-webkit-scrollbar-track {
  background-color: #f5f7fa;
}

.dark-theme ::-webkit-scrollbar-track {
  background-color: #2b2b2d;
}

/* 过渡动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.slide-fade-enter-active {
  transition: all 0.3s ease-out;
}

.slide-fade-leave-active {
  transition: all 0.3s cubic-bezier(1, 0.5, 0.8, 1);
}

.slide-fade-enter-from,
.slide-fade-leave-to {
  transform: translateX(20px);
  opacity: 0;
}

/* 全局布局样式 */
.layout-container {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.layout-header {
  height: 60px;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
  z-index: 10;
}

.layout-main {
  flex: 1;
  display: flex;
  overflow: hidden;
}

.layout-sidebar {
  width: 220px;
  box-shadow: 2px 0 8px 0 rgba(29, 35, 41, 0.05);
  transition: width 0.3s;
  z-index: 5;
}

.layout-content {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  background-color: #f0f2f5;
}

.dark-theme .layout-content {
  background-color: #141414;
}
</style>
