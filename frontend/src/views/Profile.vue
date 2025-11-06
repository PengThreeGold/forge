<template>
  <div class="profile-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>个人资料</span>
        </div>
      </template>

      <!-- 用户信息展示 -->
      <div class="profile-info">
        <div class="avatar-container">
          <el-avatar :size="100" :src="userInfo?.avatar || defaultAvatar">
            {{ userInfo?.username?.charAt(0).toUpperCase() || "U" }}
          </el-avatar>
          <div class="avatar-text">
            <h3>{{ userInfo?.username || "用户名" }}</h3>
            <el-tag :type="userInfo?.role === 'admin' ? 'danger' : 'info'">
              {{ userInfo?.role === "admin" ? "管理员" : "普通用户" }}
            </el-tag>
          </div>
        </div>

        <el-descriptions :column="2" border>
          <el-descriptions-item label="用户名">
            {{ userInfo?.username || "-" }}
          </el-descriptions-item>
          <el-descriptions-item label="角色">
            <el-tag :type="userInfo?.role === 'admin' ? 'danger' : 'info'">
              {{ userInfo?.role === "admin" ? "管理员" : "普通用户" }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="邮箱">
            {{ userInfo?.email || "-" }}
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="userInfo?.is_active ? 'success' : 'info'">
              {{ userInfo?.is_active ? "激活" : "停用" }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="创建时间" span="2">
            {{ formatDateTime(userInfo?.created_at) }}
          </el-descriptions-item>
          <el-descriptions-item label="更新时间" span="2">
            {{ formatDateTime(userInfo?.updated_at) }}
          </el-descriptions-item>
        </el-descriptions>
      </div>

      <!-- 操作按钮 -->
      <div class="profile-actions">
        <el-button type="primary" @click="showPasswordDialog = true">
          <el-icon><Lock /></el-icon>
          修改密码
        </el-button>
        <el-button @click="refreshUserInfo">
          <el-icon><Refresh /></el-icon>
          刷新信息
        </el-button>
      </div>
    </el-card>

    <!-- 修改密码对话框 -->
    <el-dialog
      v-model="showPasswordDialog"
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
          <el-button @click="showPasswordDialog = false">取消</el-button>
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
import { ref, reactive, computed } from "vue";
import { useStore } from "vuex";
import { ElMessage } from "element-plus";

export default {
  name: "ProfileView",
  setup() {
    const store = useStore();

    // 响应式数据
    const showPasswordDialog = ref(false);
    const passwordLoading = ref(false);
    const passwordFormRef = ref(null);

    // 计算属性
    const userInfo = computed(() => store.getters["auth/userInfo"]);
    const defaultAvatar = ref(
      "https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png"
    );

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
    const refreshUserInfo = async () => {
      try {
        await store.dispatch("auth/getUserInfo");
        ElMessage.success("用户信息已刷新");
      } catch (error) {
        ElMessage.error("刷新用户信息失败");
      }
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
              showPasswordDialog.value = false;
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

    const formatDateTime = (dateString) => {
      if (!dateString) return "-";
      const date = new Date(dateString);
      return date.toLocaleString("zh-CN", {
        year: "numeric",
        month: "2-digit",
        day: "2-digit",
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit",
      });
    };

    return {
      showPasswordDialog,
      passwordLoading,
      passwordFormRef,
      userInfo,
      defaultAvatar,
      passwordForm,
      passwordRules,
      refreshUserInfo,
      resetPasswordForm,
      submitPasswordChange,
      formatDateTime,
    };
  },
};
</script>

<style lang="scss" scoped>
.profile-container {
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .profile-info {
    .avatar-container {
      display: flex;
      align-items: center;
      margin-bottom: 30px;

      .avatar-text {
        margin-left: 20px;

        h3 {
          margin: 0 0 10px;
          font-size: 24px;
          font-weight: 600;
        }
      }
    }
  }

  .profile-actions {
    margin-top: 30px;
    text-align: center;

    .el-button {
      margin: 0 10px;
    }
  }
}
</style>
