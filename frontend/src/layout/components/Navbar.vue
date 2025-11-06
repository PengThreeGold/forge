<template>
  <div class="navbar-container">
    <!-- 左侧：汉堡菜单和面包屑 -->
    <div class="navbar-left">
      <div class="hamburger-container" @click="toggleSidebar">
        <el-icon
          class="hamburger-icon"
          :class="{ 'is-active': !sidebarCollapsed }"
        >
          <Expand v-if="sidebarCollapsed" />
          <Fold v-else />
        </el-icon>
      </div>

      <!-- 面包屑导航 -->
      <el-breadcrumb separator="/" class="breadcrumb-container">
        <el-breadcrumb-item
          v-for="item in breadcrumbs"
          :key="item.path"
          :to="item.path"
        >
          {{ item.title }}
        </el-breadcrumb-item>
      </el-breadcrumb>
    </div>

    <!-- 右侧：用户菜单和设置 -->
    <div class="navbar-right">
      <!-- 全屏按钮 -->
      <div class="right-menu-item" @click="toggleFullScreen">
        <el-icon>
          <FullScreen />
        </el-icon>
      </div>

      <!-- 用户头像和下拉菜单 -->
      <el-dropdown class="avatar-container" trigger="click">
        <div class="avatar-wrapper">
          <el-avatar :size="32" :src="userInfo?.avatar || defaultAvatar">
            {{ userInfo?.username?.charAt(0).toUpperCase() || "U" }}
          </el-avatar>
          <span class="user-name">{{ userInfo?.username || "用户" }}</span>
          <el-icon class="el-icon--right">
            <CaretBottom />
          </el-icon>
        </div>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item @click="goToProfile">
              <el-icon><User /></el-icon>
              个人资料
            </el-dropdown-item>
            <el-dropdown-item @click="changePassword">
              <el-icon><Lock /></el-icon>
              修改密码
            </el-dropdown-item>
            <el-dropdown-item divided @click="logout">
              <el-icon><SwitchButton /></el-icon>
              退出登录
            </el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>

    <!-- 修改密码对话框 -->
    <el-dialog
      v-model="passwordDialogVisible"
      title="修改密码"
      width="500px"
      @close="resetPasswordForm"
    >
      <el-form
        ref="passwordFormRef"
        :model="passwordForm"
        :rules="passwordRules"
        label-width="100px"
      >
        <el-form-item label="原密码" prop="oldPassword">
          <el-input
            v-model="passwordForm.oldPassword"
            type="password"
            show-password
            placeholder="请输入原密码"
          />
        </el-form-item>
        <el-form-item label="新密码" prop="newPassword">
          <el-input
            v-model="passwordForm.newPassword"
            type="password"
            show-password
            placeholder="请输入新密码"
          />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input
            v-model="passwordForm.confirmPassword"
            type="password"
            show-password
            placeholder="请再次输入新密码"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="passwordDialogVisible = false">取消</el-button>
          <el-button
            type="primary"
            @click="submitPasswordChange"
            :loading="passwordLoading"
          >
            确定
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { computed, ref, reactive } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useStore } from "vuex";
import { ElMessage, ElMessageBox } from "element-plus";

export default {
  name: "NavBar",
  setup() {
    const route = useRoute();
    const router = useRouter();
    const store = useStore();

    // 响应式数据
    const passwordDialogVisible = ref(false);
    const passwordLoading = ref(false);
    const passwordFormRef = ref(null);

    // 计算属性
    const sidebarCollapsed = computed(() => store.state.sidebarCollapsed);
    const userInfo = computed(() => store.getters["auth/userInfo"]);
    const defaultAvatar = ref(
      "https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png"
    );

    // 面包屑导航
    const breadcrumbs = computed(() => {
      const matched = route.matched.filter(
        (item) => item.meta && item.meta.title
      );
      const first = matched[0];

      if (first && first.name !== "Dashboard") {
        matched.unshift({
          path: "/dashboard",
          meta: { title: "首页" },
        });
      }

      return matched.map((item) => ({
        path: item.path,
        title: item.meta.title,
      }));
    });

    // 表单数据
    const passwordForm = reactive({
      oldPassword: "",
      newPassword: "",
      confirmPassword: "",
    });

    // 表单验证规则
    const passwordRules = {
      oldPassword: [
        { required: true, message: "请输入原密码", trigger: "blur" },
      ],
      newPassword: [
        { required: true, message: "请输入新密码", trigger: "blur" },
        { min: 6, message: "密码长度不能少于6位", trigger: "blur" },
      ],
      confirmPassword: [
        { required: true, message: "请再次输入新密码", trigger: "blur" },
        {
          validator: (rule, value, callback) => {
            if (value !== passwordForm.newPassword) {
              callback(new Error("两次输入的密码不一致"));
            } else {
              callback();
            }
          },
          trigger: "blur",
        },
      ],
    };

    // 方法
    const toggleSidebar = () => {
      store.dispatch("toggleSidebar");
    };

    const toggleFullScreen = () => {
      if (!document.fullscreenElement) {
        document.documentElement.requestFullscreen();
      } else {
        document.exitFullscreen();
      }
    };

    const goToProfile = () => {
      router.push("/profile");
    };

    const changePassword = () => {
      passwordDialogVisible.value = true;
    };

    const resetPasswordForm = () => {
      passwordForm.oldPassword = "";
      passwordForm.newPassword = "";
      passwordForm.confirmPassword = "";
      passwordFormRef.value?.resetFields();
    };

    const submitPasswordChange = async () => {
      if (!passwordFormRef.value) return;

      await passwordFormRef.value.validate(async (valid) => {
        if (valid) {
          passwordLoading.value = true;

          try {
            const result = await store.dispatch("auth/changePassword", {
              old_password: passwordForm.oldPassword,
              new_password: passwordForm.newPassword,
            });

            if (result.success) {
              ElMessage.success("密码修改成功");
              passwordDialogVisible.value = false;
              resetPasswordForm();
            } else {
              ElMessage.error(result.message || "密码修改失败");
            }
          } catch (error) {
            ElMessage.error("密码修改失败");
          } finally {
            passwordLoading.value = false;
          }
        }
      });
    };

    const logout = () => {
      ElMessageBox.confirm("确定要退出登录吗？", "提示", {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        type: "warning",
      })
        .then(() => {
          store.dispatch("auth/logout");
        })
        .catch(() => {
          // 用户取消操作
        });
    };

    return {
      sidebarCollapsed,
      userInfo,
      defaultAvatar,
      breadcrumbs,
      passwordDialogVisible,
      passwordLoading,
      passwordFormRef,
      passwordForm,
      passwordRules,
      toggleSidebar,
      toggleFullScreen,
      goToProfile,
      changePassword,
      resetPasswordForm,
      submitPasswordChange,
      logout,
    };
  },
};
</script>

<style lang="scss" scoped>
.navbar-container {
  height: 60px;
  line-height: 60px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
  width: 100%;

  .navbar-left {
    display: flex;
    align-items: center;

    .hamburger-container {
      cursor: pointer;
      transition: background 0.3s;
      border-radius: 4px;
      padding: 5px;
      margin-right: 15px;

      &:hover {
        background: rgba(0, 0, 0, 0.025);
      }

      .hamburger-icon {
        font-size: 20px;
        color: #606266;

        &.is-active {
          transform: rotate(180deg);
        }
      }
    }

    .breadcrumb-container {
      font-size: 14px;
    }
  }

  .navbar-right {
    display: flex;
    align-items: center;

    .right-menu-item {
      display: inline-block;
      padding: 0 8px;
      font-size: 18px;
      color: #606266;
      vertical-align: text-bottom;
      cursor: pointer;

      &:hover {
        color: #409eff;
      }
    }

    .avatar-container {
      margin-left: 10px;

      .avatar-wrapper {
        display: flex;
        align-items: center;
        cursor: pointer;

        .user-name {
          margin-left: 10px;
          margin-right: 5px;
          font-size: 14px;
          color: #606266;
        }
      }
    }
  }
}
</style>
