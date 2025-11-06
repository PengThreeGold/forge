<template>
  <div class="layout-container">
    <el-container>
      <!-- 侧边栏 -->
      <el-aside :width="sidebarWidth" class="sidebar-container">
        <Sidebar />
      </el-aside>

      <el-container>
        <!-- 顶部导航栏 -->
        <el-header height="60px" class="header-container">
          <Navbar />
        </el-header>

        <!-- 主要内容区域 -->
        <el-main class="main-container">
          <router-view v-slot="{ Component }">
            <transition name="fade-transform" mode="out-in">
              <keep-alive :include="cachedViews">
                <component :is="Component" :key="key" />
              </keep-alive>
            </transition>
          </router-view>
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script>
import { computed } from "vue";
import { useRoute } from "vue-router";
import { useStore } from "vuex";
import Navbar from "./components/Navbar.vue";
import Sidebar from "./components/Sidebar.vue";

export default {
  name: "AppLayout",
  components: {
    Navbar,
    Sidebar,
  },
  setup() {
    const route = useRoute();
    const store = useStore();

    // 计算侧边栏宽度
    const sidebarWidth = computed(() => {
      return store.state.sidebarCollapsed ? "64px" : "210px";
    });

    // 计算缓存视图
    const cachedViews = computed(() => {
      return store.state.cachedViews || [];
    });

    // 计算路由键，用于强制刷新
    const key = computed(() => {
      return route.path;
    });

    return {
      sidebarWidth,
      cachedViews,
      key,
    };
  },
};
</script>

<style lang="scss" scoped>
.layout-container {
  height: 100vh;

  .el-container {
    height: 100%;
  }

  .sidebar-container {
    background-color: #304156;
    transition: width 0.28s;
    overflow: hidden;
    box-shadow: 2px 0 6px rgba(0, 21, 41, 0.35);
  }

  .header-container {
    background-color: #fff;
    box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
    padding: 0;
    display: flex;
    align-items: center;
    justify-content: space-between;
    z-index: 10;
  }

  .main-container {
    background-color: #f0f2f5;
    padding: 0;
    overflow: auto;
  }
}

// 过渡动画
.fade-transform-enter-active,
.fade-transform-leave-active {
  transition: all 0.3s;
}

.fade-transform-enter-from {
  opacity: 0;
  transform: translateX(-30px);
}

.fade-transform-leave-to {
  opacity: 0;
  transform: translateX(30px);
}
</style>
