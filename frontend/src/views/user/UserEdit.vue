<template>
  <div class="user-edit-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>编辑用户</span>
          <el-button @click="goBack">返回</el-button>
        </div>
      </template>

      <el-form
        ref="userFormRef"
        :model="userForm"
        :rules="userRules"
        label-width="100px"
        class="user-form"
        v-loading="loading"
      >
        <el-form-item label="用户名" prop="username">
          <el-input
            v-model="userForm.username"
            placeholder="请输入用户名"
            maxlength="50"
            show-word-limit
          />
        </el-form-item>

        <el-form-item label="邮箱" prop="email">
          <el-input
            v-model="userForm.email"
            type="email"
            placeholder="请输入邮箱地址"
            maxlength="100"
            show-word-limit
          />
        </el-form-item>

        <el-form-item label="角色" prop="role">
          <el-select
            v-model="userForm.role"
            placeholder="请选择角色"
            style="width: 100%"
          >
            <el-option label="管理员" value="admin" />
            <el-option label="普通用户" value="user" />
          </el-select>
        </el-form-item>

        <el-form-item label="状态" prop="isActive">
          <el-switch
            v-model="userForm.isActive"
            active-text="激活"
            inactive-text="停用"
          />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="handleSubmit" :loading="submitting">
            保存
          </el-button>
          <el-button @click="resetForm">重置</el-button>
          <el-button @click="goBack">取消</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from "vue";
import { useStore } from "vuex";
import { useRouter, useRoute } from "vue-router";
import { ElMessage } from "element-plus";
import { validEmail } from "@/utils/validate";

export default {
  name: "UserEdit",
  setup() {
    const store = useStore();
    const router = useRouter();
    const route = useRoute();

    // 响应式数据
    const userFormRef = ref(null);
    const loading = ref(false);
    const submitting = ref(false);

    // 表单数据
    const userForm = reactive({
      id: "",
      username: "",
      email: "",
      role: "user",
      isActive: true,
    });

    // 原始表单数据，用于重置
    const originalForm = {};

    // 表单验证规则
    const userRules = {
      username: [
        { required: true, message: "请输入用户名", trigger: "blur" },
        {
          min: 3,
          max: 50,
          message: "用户名长度在 3 到 50 个字符",
          trigger: "blur",
        },
      ],
      email: [
        { required: false, message: "请输入邮箱地址", trigger: "blur" },
        { type: "email", message: "请输入正确的邮箱地址", trigger: "blur" },
        {
          validator: (rule, value, callback) => {
            if (value && !validEmail(value)) {
              callback(new Error("请输入正确的邮箱地址"));
            } else {
              callback();
            }
          },
          trigger: "blur",
        },
      ],
      role: [{ required: true, message: "请选择角色", trigger: "change" }],
    };

    // 方法
    const fetchUser = async () => {
      const userId = route.params.id;
      if (!userId) {
        ElMessage.error("用户ID不存在");
        router.push("/user/list");
        return;
      }

      loading.value = true;
      try {
        const result = await store.dispatch("user/fetchUserById", userId);
        if (result.success) {
          const user = result.data;
          userForm.id = user.id;
          userForm.username = user.username;
          userForm.email = user.email;
          userForm.role = user.role;
          userForm.isActive = user.is_active;

          // 保存原始数据，用于重置
          Object.assign(originalForm, userForm);
        } else {
          ElMessage.error(result.message || "获取用户信息失败");
          router.push("/user/list");
        }
      } catch (error) {
        ElMessage.error("获取用户信息失败");
        router.push("/user/list");
      } finally {
        loading.value = false;
      }
    };

    const handleSubmit = () => {
      if (!userFormRef.value) return;

      userFormRef.value.validate(async (valid) => {
        if (valid) {
          submitting.value = true;

          try {
            const userData = {
              username: userForm.username,
              email: userForm.email,
              role: userForm.role,
              is_active: userForm.isActive,
            };

            const result = await store.dispatch("user/updateUser", {
              userId: userForm.id,
              userData,
            });

            if (result.success) {
              ElMessage.success("用户更新成功");
              router.push("/user/list");
            } else {
              ElMessage.error(result.message || "用户更新失败");
            }
          } catch (error) {
            ElMessage.error("用户更新失败");
          } finally {
            submitting.value = false;
          }
        }
      });
    };

    const resetForm = () => {
      Object.assign(userForm, originalForm);
      if (userFormRef.value) {
        userFormRef.value.clearValidate();
      }
    };

    const goBack = () => {
      router.push("/user/list");
    };

    // 组件挂载
    onMounted(() => {
      fetchUser();
    });

    return {
      userFormRef,
      loading,
      submitting,
      userForm,
      userRules,
      handleSubmit,
      resetForm,
      goBack,
    };
  },
};
</script>

<style lang="scss" scoped>
.user-edit-container {
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .user-form {
    max-width: 600px;
    margin: 0 auto;
  }
}
</style>
