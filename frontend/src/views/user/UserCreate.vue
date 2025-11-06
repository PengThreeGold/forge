<template>
  <div class="user-create-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>新增用户</span>
          <el-button @click="goBack">返回</el-button>
        </div>
      </template>

      <el-form
        ref="userFormRef"
        :model="userForm"
        :rules="userRules"
        label-width="100px"
        class="user-form"
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

        <el-form-item label="密码" prop="password">
          <el-input
            v-model="userForm.password"
            type="password"
            placeholder="请输入密码"
            show-password
            maxlength="100"
          />
        </el-form-item>

        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input
            v-model="userForm.confirmPassword"
            type="password"
            placeholder="请再次输入密码"
            show-password
            maxlength="100"
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
          <el-button type="primary" @click="handleSubmit" :loading="loading">
            创建
          </el-button>
          <el-button @click="resetForm">重置</el-button>
          <el-button @click="goBack">取消</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script>
import { ref, reactive } from "vue";
import { useStore } from "vuex";
import { useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import { validPassword } from "@/utils/validate";

export default {
  name: "UserCreate",
  setup() {
    const store = useStore();
    const router = useRouter();

    // 响应式数据
    const userFormRef = ref(null);
    const loading = ref(false);

    // 表单数据
    const userForm = reactive({
      username: "",
      email: "",
      password: "",
      confirmPassword: "",
      role: "user",
      isActive: true,
    });

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
      ],
      password: [
        { required: true, message: "请输入密码", trigger: "blur" },
        {
          validator: (rule, value, callback) => {
            if (!validPassword(value)) {
              callback(new Error("密码长度不能少于6位"));
            } else {
              callback();
            }
          },
          trigger: "blur",
        },
      ],
      confirmPassword: [
        { required: true, message: "请再次输入密码", trigger: "blur" },
        {
          validator: (rule, value, callback) => {
            if (value !== userForm.password) {
              callback(new Error("两次输入的密码不一致"));
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
    const handleSubmit = () => {
      if (!userFormRef.value) return;

      userFormRef.value.validate(async (valid) => {
        if (valid) {
          loading.value = true;

          try {
          // 创建用户数据副本，移除 confirmPassword 字段
          const userData = { ...userForm };
          delete userData.confirmPassword;
          const result = await store.dispatch("user/createUser", userData);

            if (result.success) {
              ElMessage.success("用户创建成功");
              router.push("/user/list");
            } else {
              ElMessage.error(result.message || "用户创建失败");
            }
          } catch (error) {
            ElMessage.error("用户创建失败");
          } finally {
            loading.value = false;
          }
        }
      });
    };

    const resetForm = () => {
      if (userFormRef.value) {
        userFormRef.value.resetFields();
      }
    };

    const goBack = () => {
      router.push("/user/list");
    };

    return {
      userFormRef,
      loading,
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
.user-create-container {
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
