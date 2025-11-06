<template>
  <div class="version-create-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>创建版本</span>
          <el-button @click="goBack">返回</el-button>
        </div>
      </template>

      <el-form
        ref="versionFormRef"
        :model="versionForm"
        :rules="versionRules"
        label-width="100px"
        class="version-form"
      >
        <el-form-item label="软件空间" prop="spaceId">
          <el-select
            v-model="versionForm.spaceId"
            placeholder="请选择软件空间"
            style="width: 100%"
            @change="handleSpaceChange"
          >
            <el-option
              v-for="space in spaceList"
              :key="space.space_id"
              :label="`${space.name} (${space.space_id})`"
              :value="space.space_id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="版本号" prop="version">
          <el-input
            v-model="versionForm.version"
            placeholder="请输入版本号，如：1.0.0"
            maxlength="50"
            show-word-limit
          />
        </el-form-item>

        <el-form-item label="发布说明">
          <el-input
            v-model="versionForm.releaseNote"
            type="textarea"
            :rows="4"
            placeholder="请输入发布说明"
            maxlength="1000"
            show-word-limit
          />
        </el-form-item>

        <el-form-item label="文档链接">
          <el-input
            v-model="versionForm.documentationUrl"
            placeholder="请输入文档链接"
            maxlength="255"
            show-word-limit
          />
        </el-form-item>

        <el-form-item label="立即发布">
          <el-switch
            v-model="versionForm.isPublished"
            active-text="是"
            inactive-text="否"
          />
          <div class="form-tip">
            如果选择是，版本创建后将立即发布，用户可以下载
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
import { ref, reactive, onMounted } from "vue";
import { useStore } from "vuex";
import { useRouter, useRoute } from "vue-router";
import { ElMessage } from "element-plus";
import { validVersion } from "@/utils/validate";

export default {
  name: "VersionCreate",
  setup() {
    const store = useStore();
    const router = useRouter();
    const route = useRoute();

    // 响应式数据
    const versionFormRef = ref(null);
    const loading = ref(false);
    const spaceList = ref([]);

    // 表单数据
    const versionForm = reactive({
      spaceId: "",
      version: "",
      releaseNote: "",
      documentationUrl: "",
      isPublished: false,
    });

    // 表单验证规则
    const versionRules = {
      spaceId: [
        { required: true, message: "请选择软件空间", trigger: "change" },
      ],
      version: [
        { required: true, message: "请输入版本号", trigger: "blur" },
        {
          validator: (rule, value, callback) => {
            if (!validVersion(value)) {
              callback(new Error("请输入有效的语义化版本号，如：1.0.0"));
            } else {
              callback();
            }
          },
          trigger: "blur",
        },
      ],
    };

    // 方法
    const fetchSpaces = async () => {
      try {
        await store.dispatch("space/fetchSpaces");
        spaceList.value = store.getters["space/spaces"];
      } catch (error) {
        ElMessage.error("获取软件空间列表失败");
      }
    };

    const handleSpaceChange = () => {
      // 空间改变时的逻辑
    };

    const handleSubmit = () => {
      if (!versionFormRef.value) return;

      versionFormRef.value.validate(async (valid) => {
        if (valid) {
          loading.value = true;

          try {
            const versionData = {
              space_id: versionForm.spaceId,
              version: versionForm.version,
              release_note: versionForm.releaseNote,
              documentation_url: versionForm.documentationUrl,
              is_published: versionForm.isPublished,
            };

            const result = await store.dispatch(
              "version/createVersion",
              versionData
            );

            if (result.success) {
              ElMessage.success("版本创建成功");
              router.push("/version/list");
            } else {
              ElMessage.error(result.message || "版本创建失败");
            }
          } catch (error) {
            ElMessage.error("版本创建失败");
          } finally {
            loading.value = false;
          }
        }
      });
    };

    const resetForm = () => {
      if (versionFormRef.value) {
        versionFormRef.value.resetFields();
      }
    };

    const goBack = () => {
      router.push("/version/list");
    };

    // 组件挂载
    onMounted(async () => {
      // 检查URL参数中是否有spaceId
      const spaceId = route.query.spaceId;
      if (spaceId) {
        versionForm.spaceId = spaceId;
      }

      await fetchSpaces();
    });

    return {
      versionFormRef,
      loading,
      spaceList,
      versionForm,
      versionRules,
      handleSpaceChange,
      handleSubmit,
      resetForm,
      goBack,
    };
  },
};
</script>

<style lang="scss" scoped>
.version-create-container {
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .version-form {
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
