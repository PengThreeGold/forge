<template>
  <div v-if="!item.hidden">
    <!-- 没有子菜单的情况 -->
    <template v-if="!hasChildren(item)">
      <el-menu-item
        :index="resolvePath(item.path)"
        :class="{ 'submenu-title-noDropdown': !isNest }"
      >
        <el-icon v-if="item.meta?.icon">
          <component :is="item.meta.icon" />
        </el-icon>
        <template #title>
          {{ item.meta?.title }}
        </template>
      </el-menu-item>
    </template>

    <!-- 有子菜单的情况 -->
    <el-sub-menu v-else :index="resolvePath(item.path)" popper-append-to-body>
      <template #title>
        <el-icon v-if="item.meta?.icon">
          <component :is="item.meta.icon" />
        </el-icon>
        <span>{{ item.meta?.title }}</span>
      </template>

      <sidebar-item
        v-for="child in item.children"
        :key="child.path"
        :item="child"
        :is-nest="true"
        :base-path="resolvePath(item.path)"
      />
    </el-sub-menu>
  </div>
</template>

<script>
import { isExternal } from "@/utils/validate";
import path from "path-browserify";

export default {
  name: "SidebarItem",
  props: {
    item: {
      type: Object,
      required: true,
    },
    isNest: {
      type: Boolean,
      default: false,
    },
    basePath: {
      type: String,
      default: "",
    },
  },
  setup(props) {
    // 判断是否有子菜单
    const hasChildren = (route) => {
      const showingChildren = route.children?.filter((child) => {
        if (child.meta?.hidden) {
          return false;
        }
        return true;
      });

      if (showingChildren?.length > 0) {
        return true;
      }

      return false;
    };

    // 解析路径
    const resolvePath = (routePath) => {
      if (isExternal(routePath)) {
        return routePath;
      }

      if (isExternal(props.basePath)) {
        return props.basePath;
      }

      return path.resolve(props.basePath, routePath);
    };

    return {
      hasChildren,
      resolvePath,
    };
  },
};
</script>

<style lang="scss" scoped>
.submenu-title-noDropdown {
  &:hover {
    background-color: #263445 !important;
  }

  &.is-active {
    background-color: #263445 !important;
  }
}

.el-menu-item,
.el-sub-menu__title {
  &:hover {
    background-color: #263445 !important;
  }

  &.is-active {
    background-color: #409eff !important;

    .el-icon {
      color: #fff;
    }

    span {
      color: #fff;
    }
  }
}
</style>
