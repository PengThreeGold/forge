<template>
  <div class="sidebar-wrapper">
    <!-- Logo区域 -->
    <div class="logo-container" :class="{ 'is-collapsed': sidebarCollapsed }">
      <router-link to="/dashboard" class="logo-link">
        <img
          v-if="!sidebarCollapsed"
          src="@/assets/logo.png"
          alt="Forge"
          class="logo-img"
        />
        <img
          v-else
          src="@/assets/logo-mini.png"
          alt="Forge"
          class="logo-img-mini"
        />
        <h1 v-if="!sidebarCollapsed" class="logo-title">Forge</h1>
      </router-link>
    </div>

    <!-- 菜单区域 -->
    <el-scrollbar wrap-class="scrollbar-wrapper">
      <el-menu
        :default-active="activeMenu"
        :collapse="sidebarCollapsed"
        :unique-opened="true"
        :collapse-transition="false"
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409EFF"
        mode="vertical"
        router
      >
        <sidebar-item
          v-for="route in routes"
          :key="route.path"
          :item="route"
          :base-path="route.path"
        />
      </el-menu>
    </el-scrollbar>
  </div>
</template>

<script>
import { computed } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useStore } from "vuex";
import SidebarItem from "./SidebarItem.vue";

export default {
  name: "SideBar",
  components: {
    SidebarItem,
  },
  setup() {
    const route = useRoute();
    const router = useRouter();
    const store = useStore();

    // 计算侧边栏折叠状态
    const sidebarCollapsed = computed(() => store.state.sidebarCollapsed);

    // 计算当前激活的菜单项
    const activeMenu = computed(() => {
      const { meta, path } = route;
      if (meta.activeMenu) {
        return meta.activeMenu;
      }
      return path;
    });

    // 获取路由配置，过滤掉隐藏的路由
    const routes = computed(() => {
      return router.options.routes
        .filter((route) => {
          if (route.meta && route.meta.requiresAuth && !route.meta.hidden) {
            // 检查用户角色权限
            if (route.meta.roles && route.meta.roles.length > 0) {
              const userRole = store.getters["auth/userInfo"]?.role;
              return route.meta.roles.includes(userRole);
            }
            return true;
          }
          return false;
        })
        .filter(
          (route) =>
            route.path !== "/" && route.path !== "/login" && !route.meta?.hidden
        );
    });

    return {
      sidebarCollapsed,
      activeMenu,
      routes,
    };
  },
};
</script>

<style lang="scss" scoped>
.sidebar-wrapper {
  height: 100%;
  overflow: hidden;

  .logo-container {
    height: 50px;
    padding: 10px;
    display: flex;
    align-items: center;
    background: #2b2f3a;

    &.is-collapsed {
      padding: 10px 5px;
      justify-content: center;
    }

    .logo-link {
      display: flex;
      align-items: center;
      text-decoration: none;

      .logo-img {
        width: 32px;
        height: 32px;
        margin-right: 10px;
      }

      .logo-img-mini {
        width: 32px;
        height: 32px;
      }

      .logo-title {
        color: #fff;
        font-size: 18px;
        font-weight: 600;
        margin: 0;
        white-space: nowrap;
      }
    }
  }

  .scrollbar-wrapper {
    height: calc(100% - 50px);
    overflow-x: hidden !important;
  }

  .el-menu {
    border-right: none;
    width: 100%;

    &:not(.el-menu--collapse) {
      width: 210px;
    }
  }
}

// 当菜单折叠时，调整一些样式
:deep(.el-menu--collapse) {
  .el-sub-menu__title span {
    height: 0;
    width: 0;
    overflow: hidden;
    visibility: hidden;
    display: inline-block;
  }

  .el-menu-item,
  .el-sub-menu__title {
    text-align: center;
  }
}
</style>
