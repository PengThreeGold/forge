<template>
  <div class="space-create-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>创建软件空间</span>
          <el-button @click="goBack">返回</el-button>
        </div>
      </template>

      <el-form
        ref="spaceFormRef"
        :model="spaceForm"
        :rules="spaceRules"
        label-width="100px"
        class="space-form"
      >
        <el-form-item label="空间ID" prop="spaceId">
          <el-input
            v-model="spaceForm.spaceId"
            placeholder="请输入空间ID，只能包含字母、数字、连字符和下划线"
            maxlength="50"
            show-word-limit
          />
          <div class="form-tip">空间ID创建后不可修改，将用于URL和API路径</div>
        </el-form-item>

        <el-form-item label="软件名称" prop="name">
          <el-input
            v-model="spaceForm.name"
            placeholder="请输入软件名称"
            maxlength="100"
            show-word-limit
          />
        </el-form-item>

        <el-form-item label="描述">
          <el-input
            v-model="spaceForm.description"
            type="textarea"
            :rows="4"
            placeholder="请输入软件描述"
            maxlength="500"
            show-word-limit
          />
        </el-form-item>

        <el-form-item label="作者">
          <el-input
            v-model="spaceForm.author"
            placeholder="请输入作者名称"
            maxlength="100"
            show-word-limit
          />
        </el-form-item>

        <el-form-item label="状态" prop="status">
          <el-radio-group v-model="spaceForm.status">
            <el-radio label="active">激活</el-radio>
            <el-radio label="inactive">停用</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="Webhook URL">
          <el-input
            v-model="spaceForm.webhookUrl"
            placeholder="请输入Webhook URL，用于接收事件通知"
            maxlength="255"
            show-word-limit
          />
          <div class="form-tip">
            当软件空间有新版本发布、下载等事件时，系统会向此URL发送通知
          </div>
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

export default {
  name: "SpaceCreate",
  setup() {
    const store = useStore();
    const router = useRouter();

    // 响应式数据
    const spaceFormRef = ref(null);
    const loading = ref(false);

    // 表单数据
    const spaceForm = reactive({
      spaceId: "",
      name: "",
      description: "",
      author: "",
      status: "active",
      webhookUrl: "",
    });

    // 表单验证规则
    const spaceRules = {
      spaceId: [
        { required: true, message: "请输入空间ID", trigger: "blur" },
        {
          min: 3,
          max: 50,
          message: "空间ID长度在 3 到 50 个字符",
          trigger: "blur",
        },
        {
          pattern: /^[a-zA-Z0-9_-]+$/,
          message: "空间ID只能包含字母、数字、连字符和下划线",
          trigger: "blur",
        },
      ],
      name: [
        { required: true, message: "请输入软件名称", trigger: "blur" },
        {
          min: 1,
          max: 100,
          message: "软件名称长度在 1 到 100 个字符",
          trigger: "blur",
        },
      ],
      status: [{ required: true, message: "请选择状态", trigger: "change" }],
    };

    // 方法
    const handleSubmit = () => {
      if (!spaceFormRef.value) return;

      spaceFormRef.value.validate(async (valid) => {
        if (valid) {
          loading.value = true;

          try {
            const spaceData = {
              space_id: spaceForm.spaceId,
              name: spaceForm.name,
              description: spaceForm.description,
              author: spaceForm.author,
              status: spaceForm.status,
              webhook_url: spaceForm.webhookUrl,
            };

            const result = await store.dispatch("space/createSpace", spaceData);

            if (result.success) {
              ElMessage.success("软件空间创建成功");
              router.push("/space/list");
            } else {
              ElMessage.error(result.message || "软件空间创建失败");
            }
          } catch (error) {
            ElMessage.error("软件空间创建失败");
          } finally {
            loading.value = false;
          }
        }
      });
    };

    const resetForm = () => {
      if (spaceFormRef.value) {
        spaceFormRef.value.resetFields();
      }
    };

    const goBack = () => {
      router.push("/space/list");
    };

    return {
      spaceFormRef,
      loading,
      spaceForm,
      spaceRules,
      handleSubmit,
      resetForm,
      goBack,
    };
  },
};
</script>

<style lang="scss" scoped>
.space-create-container {
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .space-form {
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
