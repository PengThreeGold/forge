<template>
  <div class="webhook-edit-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>编辑Webhook配置</span>
          <el-button @click="goBack">返回</el-button>
        </div>
      </template>

      <el-form
        ref="webhookFormRef"
        :model="webhookForm"
        :rules="webhookRules"
        label-width="100px"
        class="webhook-form"
        v-loading="loading"
      >
        <el-form-item label="软件空间">
          <el-input v-model="spaceName" disabled />
        </el-form-item>

        <el-form-item label="Webhook URL" prop="webhookUrl">
          <el-input
            v-model="webhookForm.webhookUrl"
            placeholder="请输入Webhook URL，用于接收事件通知"
            maxlength="255"
            show-word-limit
          />
          <div class="form-tip">
            当软件空间有新版本发布、下载等事件时，系统会向此URL发送通知
          </div>
        </el-form-item>

        <el-form-item label="密钥">
          <el-input
            v-model="webhookForm.webhookSecret"
            type="password"
            placeholder="请输入Webhook密钥，用于验证请求来源"
            maxlength="255"
            show-password
          />
          <div class="form-tip">
            Webhook密钥用于验证请求的合法性，请妥善保管
          </div>
        </el-form-item>

        <el-form-item label="事件类型" prop="webhookEvents">
          <el-checkbox-group v-model="webhookForm.webhookEvents">
            <el-checkbox label="download">下载事件</el-checkbox>
            <el-checkbox label="create">创建事件</el-checkbox>
            <el-checkbox label="update">更新事件</el-checkbox>
            <el-checkbox label="delete">删除事件</el-checkbox>
          </el-checkbox-group>
          <div class="form-tip">选择需要触发Webhook的事件类型</div>
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

    <!-- Webhook测试 -->
    <el-card style="margin-top: 20px">
      <template #header>
        <div class="card-header">
          <span>测试Webhook</span>
        </div>
      </template>

      <el-form
        ref="testFormRef"
        :model="testForm"
        :rules="testRules"
        label-width="100px"
      >
        <el-form-item label="事件类型" prop="eventType">
          <el-select
            v-model="testForm.eventType"
            placeholder="请选择事件类型"
            style="width: 100%"
          >
            <el-option label="下载" value="download" />
            <el-option label="创建" value="create" />
            <el-option label="更新" value="update" />
            <el-option label="删除" value="delete" />
          </el-select>
        </el-form-item>

        <el-form-item label="测试数据">
          <el-input
            v-model="testForm.payload"
            type="textarea"
            :rows="6"
            placeholder="请输入测试数据（JSON格式）"
          />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="submitTest" :loading="testLoading">
            测试
          </el-button>
          <el-button @click="resetTestForm">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script>
import { ref, reactive, onMounted, computed } from "vue";
import { useStore } from "vuex";
import { useRouter, useRoute } from "vue-router";
import { ElMessage } from "element-plus";

export default {
  name: "WebhookEdit",
  setup() {
    const store = useStore();
    const router = useRouter();
    const route = useRoute();

    // 响应式数据
    const webhookFormRef = ref(null);
    const testFormRef = ref(null);
    const loading = ref(false);
    const submitting = ref(false);
    const testLoading = ref(false);

    // 表单数据
    const webhookForm = reactive({
      spaceId: "",
      webhookUrl: "",
      webhookSecret: "",
      webhookEvents: [],
    });

    // 原始表单数据，用于重置
    const originalForm = {};

    // 测试表单数据
    const testForm = reactive({
      eventType: "download",
      payload: "",
    });

    // 表单验证规则
    const webhookRules = {
      webhookUrl: [
        { required: false, message: "请输入Webhook URL", trigger: "blur" },
        { type: "url", message: "请输入正确的URL格式", trigger: "blur" },
      ],
      webhookEvents: [
        {
          type: "array",
          required: true,
          message: "请选择至少一个事件类型",
          trigger: "change",
        },
      ],
    };

    const testRules = {
      eventType: [
        { required: true, message: "请选择事件类型", trigger: "change" },
      ],
    };

    // 计算属性
    const spaceName = computed(() => {
      const spaceMap = store.getters["space/spaceMap"];
      const space = spaceMap[webhookForm.spaceId];
      return space ? `${space.name} (${space.space_id})` : webhookForm.spaceId;
    });

    // 方法
    const fetchWebhook = async () => {
      const spaceId = route.params.id;
      if (!spaceId) {
        ElMessage.error("软件空间ID不存在");
        router.push("/webhook/list");
        return;
      }

      loading.value = true;
      try {
        const result = await store.dispatch(
          "webhook/getWebhookConfig",
          spaceId
        );
        if (result.success) {
          const webhook = result.data;
          webhookForm.spaceId = spaceId;
          webhookForm.webhookUrl = webhook.webhook_url || "";
          webhookForm.webhookSecret = webhook.webhook_secret || "";
          webhookForm.webhookEvents = webhook.webhook_events || [];

          // 保存原始数据，用于重置
          Object.assign(originalForm, webhookForm);

          // 设置测试数据
          testForm.payload = JSON.stringify(
            {
              space_id: spaceId,
              event_type: "download",
              data: {
                version: "1.0.0",
                architecture: "x86_64",
                filename: "example.exe",
              },
            },
            null,
            2
          );
        } else {
          ElMessage.error(result.message || "获取Webhook配置失败");
          router.push("/webhook/list");
        }
      } catch (error) {
        ElMessage.error("获取Webhook配置失败");
        router.push("/webhook/list");
      } finally {
        loading.value = false;
      }
    };

    const handleSubmit = () => {
      if (!webhookFormRef.value) return;

      webhookFormRef.value.validate(async (valid) => {
        if (valid) {
          submitting.value = true;

          try {
            const webhookData = {
              webhook_url: webhookForm.webhookUrl,
              webhook_secret: webhookForm.webhookSecret,
              webhook_events: webhookForm.webhookEvents,
            };

            const result = await store.dispatch("webhook/updateWebhookConfig", {
              spaceId: webhookForm.spaceId,
              data: webhookData,
            });

            if (result.success) {
              ElMessage.success("Webhook配置更新成功");
              // 更新原始数据
              Object.assign(originalForm, webhookForm);
            } else {
              ElMessage.error(result.message || "Webhook配置更新失败");
            }
          } catch (error) {
            ElMessage.error("Webhook配置更新失败");
          } finally {
            submitting.value = false;
          }
        }
      });
    };

    const resetForm = () => {
      Object.assign(webhookForm, originalForm);
      if (webhookFormRef.value) {
        webhookFormRef.value.clearValidate();
      }
    };

    const submitTest = () => {
      if (!testFormRef.value) return;

      testFormRef.value.validate(async (valid) => {
        if (valid) {
          testLoading.value = true;

          try {
            let payload;
            try {
              payload = testForm.payload ? JSON.parse(testForm.payload) : {};
            } catch (error) {
              ElMessage.error("测试数据格式错误，请输入有效的JSON");
              testLoading.value = false;
              return;
            }

            const result = await store.dispatch("webhook/testWebhook", {
              spaceId: webhookForm.spaceId,
              data: {
                event_type: testForm.eventType,
                payload,
              },
            });

            if (result.success) {
              ElMessage.success("Webhook测试成功");
            } else {
              ElMessage.error(result.message || "Webhook测试失败");
            }
          } catch (error) {
            ElMessage.error("Webhook测试失败");
          } finally {
            testLoading.value = false;
          }
        }
      });
    };

    const resetTestForm = () => {
      testForm.eventType = "download";
      testForm.payload = JSON.stringify(
        {
          space_id: webhookForm.spaceId,
          event_type: "download",
          data: {
            version: "1.0.0",
            architecture: "x86_64",
            filename: "example.exe",
          },
        },
        null,
        2
      );
      if (testFormRef.value) {
        testFormRef.value.clearValidate();
      }
    };

    const goBack = () => {
      router.push("/webhook/list");
    };

    // 组件挂载
    onMounted(() => {
      fetchWebhook();
    });

    return {
      webhookFormRef,
      testFormRef,
      loading,
      submitting,
      testLoading,
      webhookForm,
      originalForm,
      testForm,
      webhookRules,
      testRules,
      spaceName,
      handleSubmit,
      resetForm,
      submitTest,
      resetTestForm,
      goBack,
    };
  },
};
</script>

<style lang="scss" scoped>
.webhook-edit-container {
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .webhook-form {
    max-width: 600px;
    margin: 0 auto;

    .form-tip {
      font-size: 12px;
      color: #909399;
      margin-top: 5px;
      line-height: 1.4;
    }
  }
}
</style>
