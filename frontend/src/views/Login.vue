<template>
  <div class="login-container">
    <el-card class="login-card">
      <template #header>
        <div class="card-header">
          <img src="@/assets/logo.png" alt="Forge" class="logo" />
          <h2 class="title">Forge 软件发布管理平台</h2>
        </div>
      </template>

      <el-form
        ref="loginFormRef"
        :model="loginForm"
        :rules="loginRules"
        class="login-form"
        autocomplete="on"
        label-position="left"
      >
        <el-form-item prop="username">
          <el-input
            ref="usernameRef"
            v-model="loginForm.username"
            placeholder="用户名"
            name="username"
            type="text"
            tabindex="1"
            autocomplete="on"
            prefix-icon="User"
          />
        </el-form-item>

        <el-tooltip
          v-model="capsTooltip"
          content="大写锁定已开启"
          placement="right"
          manual
        >
          <el-form-item prop="password">
            <el-input
              ref="passwordRef"
              v-model="loginForm.password"
              :type="passwordVisible ? 'text' : 'password'"
              placeholder="密码"
              name="password"
              tabindex="2"
              autocomplete="on"
              prefix-icon="Lock"
              @keyup="checkCapslock"
              @blur="capsTooltip = false"
              @keyup.enter="handleLogin"
            >
              <template #suffix>
                <el-icon
                  class="show-pwd"
                  @click="passwordVisible = !passwordVisible"
                >
                  <View v-if="passwordVisible" />
                  <Hide v-else />
                </el-icon>
              </template>
            </el-input>
          </el-form-item>
        </el-tooltip>

        <el-button
          :loading="loading"
          type="primary"
          style="width: 100%; margin-bottom: 30px"
          @click="handleLogin"
        >
          登录
        </el-button>

        <div class="tips">
          <div class="tip-item">
            <el-icon><InfoFilled /></el-icon>
            <span>默认账号: admin</span>
          </div>
          <div class="tip-item">
            <el-icon><InfoFilled /></el-icon>
            <span>默认密码: 123456</span>
          </div>
        </div>
      </el-form>
    </el-card>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useStore } from "vuex";
import { ElMessage } from "element-plus";
import { validUsername } from "@/utils/validate";

export default {
  name: "LoginView",
  setup() {
    const route = useRoute();
    const router = useRouter();
    const store = useStore();

    // 响应式数据
    const loginFormRef = ref(null);
    const usernameRef = ref(null);
    const passwordRef = ref(null);
    const loading = ref(false);
    const passwordVisible = ref(false);
    const capsTooltip = ref(false);
    const redirect = ref("");

    // 表单数据
    const loginForm = reactive({
      username: "admin",
      password: "123456",
    });

    // 表单验证规则
    const loginRules = {
      username: [
        { required: true, message: "请输入用户名", trigger: "blur" },
        { validator: validateUsername, trigger: "blur" },
      ],
      password: [
        { required: true, message: "请输入密码", trigger: "blur" },
        { min: 6, message: "密码长度不能少于6位", trigger: "blur" },
      ],
    };

    // 验证用户名
    function validateUsername(rule, value, callback) {
      if (!validUsername(value)) {
        callback(new Error("请输入正确的用户名"));
      } else {
        callback();
      }
    }

    // 检查大写锁定
    function checkCapslock(e) {
      const { key } = e;
      capsTooltip.value = key && key.length === 1 && key >= "A" && key <= "Z";
    }

    // 处理登录
    function handleLogin() {
      loginFormRef.value.validate(async (valid) => {
        if (valid) {
          loading.value = true;

          try {
            const result = await store.dispatch("auth/login", loginForm);

            if (result.success) {
              ElMessage.success("登录成功");

              // 获取重定向地址
              const redirectPath = route.query.redirect || "/dashboard";
              router.push(redirectPath);
            } else {
              ElMessage.error(result.message || "登录失败");
            }
          } catch (error) {
            ElMessage.error("登录失败，请稍后再试");
          } finally {
            loading.value = false;
          }
        }
      });
    }

    // 组件挂载后的操作
    onMounted(() => {
      // 如果用户名输入框为空，则聚焦
      if (loginForm.username === "") {
        usernameRef.value?.focus();
      } else if (loginForm.password === "") {
        passwordRef.value?.focus();
      }
    });

    return {
      loginFormRef,
      usernameRef,
      passwordRef,
      loading,
      passwordVisible,
      capsTooltip,
      redirect,
      loginForm,
      loginRules,
      checkCapslock,
      handleLogin,
    };
  },
};
</script>

<style lang="scss" scoped>
$bg: #2d3a4b;
$light_gray: #fff;
$cursor: #fff;

@supports (-webkit-mask: none) and (not (caret-color: $cursor)) {
  .login-container .el-input {
    input {
      color: $cursor;
    }

    input::first-line {
      color: $light_gray;
    }
  }
}

.login-container {
  min-height: 100vh;
  width: 100%;
  background: linear-gradient(135deg, #1a365d 0%, #2a4365 100%);
  overflow: hidden;
  display: flex;
  justify-content: center;
  align-items: center;

  .login-card {
    width: 400px;
    max-width: 90%;

    .card-header {
      text-align: center;

      .logo {
        width: 80px;
        height: 80px;
        margin-bottom: 10px;
      }

      .title {
        margin: 0;
        color: #303133;
        font-size: 22px;
        font-weight: 600;
      }
    }

    .login-form {
      .el-input {
        display: inline-block;
        height: 47px;
        width: 85%;

        input {
          background: transparent;
          border: 0px;
          -webkit-appearance: none;
          border-radius: 0px;
          padding: 12px 5px 12px 15px;
          color: #606266;
          height: 47px;
          caret-color: #606266;

          &:-webkit-autofill {
            box-shadow: 0 0 0px 1000px #f5f7fa inset !important;
            -webkit-text-fill-color: #606266 !important;
          }
        }
      }

      .el-form-item {
        border: 1px solid rgba(0, 0, 0, 0.1);
        background: rgba(255, 255, 255, 0.7);
        border-radius: 5px;
        color: #454545;
        margin-bottom: 20px;

        &:hover {
          border-color: #409eff;
        }
      }

      .show-pwd {
        position: absolute;
        right: 10px;
        top: 7px;
        font-size: 16px;
        color: #889aa4;
        cursor: pointer;
        user-select: none;

        &:hover {
          color: #409eff;
        }
      }
    }

    .tips {
      font-size: 14px;
      color: #606266;

      .tip-item {
        display: flex;
        align-items: center;
        margin-bottom: 8px;

        .el-icon {
          margin-right: 8px;
          color: #909399;
        }
      }
    }
  }
}
</style>
