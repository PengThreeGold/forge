<template>
  <div class="version-edit-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>编辑版本</span>
          <el-button @click="goBack">返回</el-button>
        </div>
      </template>

      <el-form
        ref="versionFormRef"
        :model="versionForm"
        :rules="versionRules"
        label-width="100px"
        class="version-form"
        v-loading="loading"
      >
        <el-form-item label="软件空间">
          <el-input v-model="spaceName" disabled />
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

        <el-form-item label="发布状态" prop="isPublished">
          <el-switch
            v-model="versionForm.isPublished"
            active-text="已发布"
            inactive-text="未发布"
          />
          <div class="form-tip">发布后的版本用户可以下载</div>
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

    <!-- 文件管理 -->
    <el-card style="margin-top: 20px">
      <template #header>
        <div class="card-header">
          <span>文件管理</span>
          <el-upload
            ref="uploadRef"
            :action="uploadUrl"
            :headers="uploadHeaders"
            :before-upload="beforeUpload"
            :on-success="handleUploadSuccess"
            :on-error="handleUploadError"
            :show-file-list="false"
            accept=".zip,.tar,.tar.gz,.tgz,.rar,.7z,.exe,.msi,.dmg,.pkg,.deb,.rpm,.apk,.ipa"
          >
            <el-button type="primary">
              <el-icon><Upload /></el-icon>
              上传文件
            </el-button>
          </el-upload>
        </div>
      </template>

      <el-table
        v-loading="filesLoading"
        :data="fileList"
        border
        style="width: 100%"
      >
        <el-table-column type="index" label="#" width="60" />
        <el-table-column prop="architecture" label="架构" width="120" />
        <el-table-column
          prop="filename"
          label="文件名"
          min-width="180"
          show-overflow-tooltip
        />
        <el-table-column prop="file_size_human" label="文件大小" width="120" />
        <el-table-column
          prop="file_hash"
          label="文件哈希"
          min-width="200"
          show-overflow-tooltip
        />
        <el-table-column prop="downloads" label="下载次数" width="100" />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button
              type="primary"
              link
              size="small"
              @click="handleDownload(row)"
            >
              <el-icon><Download /></el-icon>
              下载
            </el-button>
            <el-button
              type="danger"
              link
              size="small"
              @click="handleDeleteFile(row)"
            >
              <el-icon><Delete /></el-icon>
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script>
import { ref, reactive, onMounted, computed } from "vue";
import { useStore } from "vuex";
import { useRouter, useRoute } from "vue-router";
import { ElMessage } from "element-plus";
import { validVersion } from "@/utils/validate";

export default {
  name: "VersionEdit",
  setup() {
    const store = useStore();
    const router = useRouter();
    const route = useRoute();

    // 响应式数据
    const versionFormRef = ref(null);
    const uploadRef = ref(null);
    const loading = ref(false);
    const submitting = ref(false);
    const filesLoading = ref(false);
    const fileList = ref([]);

    // 表单数据
    const versionForm = reactive({
      id: "",
      spaceId: "",
      version: "",
      releaseNote: "",
      documentationUrl: "",
      isPublished: false,
    });

    // 原始表单数据，用于重置
    const originalForm = {};

    // 表单验证规则
    const versionRules = {
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

    // 计算属性
    const spaceName = computed(() => {
      const spaceMap = store.getters["space/spaceMap"];
      const space = spaceMap[versionForm.spaceId];
      return space ? `${space.name} (${space.space_id})` : versionForm.spaceId;
    });

    const uploadUrl = computed(() => {
      return `${process.env.VUE_APP_API_BASE_URL}/api/versions/${versionForm.id}/files`;
    });

    const uploadHeaders = computed(() => {
      const token = store.getters["auth/token"];
      return token ? { Authorization: `Bearer ${token}` } : {};
    });

    // 方法
    const fetchVersion = async () => {
      const versionId = route.params.id;
      if (!versionId) {
        ElMessage.error("版本ID不存在");
        router.push("/version/list");
        return;
      }

      loading.value = true;
      try {
        const result = await store.dispatch(
          "version/fetchVersionById",
          versionId
        );
        if (result.success) {
          const version = result.data;
          versionForm.id = version.id;
          versionForm.spaceId = version.space_id;
          versionForm.version = version.version;
          versionForm.releaseNote = version.release_note;
          versionForm.documentationUrl = version.documentation_url;
          versionForm.isPublished = version.is_published;

          // 保存原始数据，用于重置
          Object.assign(originalForm, versionForm);

          // 获取版本的文件列表
          await fetchFiles();
        } else {
          ElMessage.error(result.message || "获取版本信息失败");
          router.push("/version/list");
        }
      } catch (error) {
        ElMessage.error("获取版本信息失败");
        router.push("/version/list");
      } finally {
        loading.value = false;
      }
    };

    const fetchFiles = async () => {
      filesLoading.value = true;
      try {
        const result = await store.dispatch(
          "version/fetchArchitectureFiles",
          versionForm.id
        );
        if (result.success) {
          fileList.value = result.data || [];
        }
      } catch (error) {
        ElMessage.error("获取文件列表失败");
      } finally {
        filesLoading.value = false;
      }
    };

    const beforeUpload = (file) => {
      // 文件大小限制，100MB
      const isLt100M = file.size / 1024 / 1024 < 100;
      if (!isLt100M) {
        ElMessage.error("文件大小不能超过 100MB!");
        return false;
      }

      // 文件类型限制
      const allowedTypes = [
        "application/zip",
        "application/x-tar",
        "application/gzip",
        "application/x-rar-compressed",
        "application/x-7z-compressed",
        "application/x-msdownload",
        "application/x-msi",
        "application/x-apple-diskimage",
        "application/x-newton-compatible-pkg",
        "application/x-debian-package",
        "application/x-rpm",
        "application/vnd.android.package-archive",
        "application/octet-stream",
      ];

      const isValidType =
        allowedTypes.includes(file.type) ||
        file.name.match(
          /\.(zip|tar|gz|tgz|rar|7z|exe|msi|dmg|pkg|deb|rpm|apk|ipa)$/i
        );

      if (!isValidType) {
        ElMessage.error("只能上传压缩包、安装包或可执行文件!");
        return false;
      }

      return true;
    };

    const handleUploadSuccess = () => {
      ElMessage.success("文件上传成功");
      fetchFiles(); // 刷新文件列表
    };

    const handleUploadError = () => {
      ElMessage.error("文件上传失败");
    };

    const handleSubmit = () => {
      if (!versionFormRef.value) return;

      versionFormRef.value.validate(async (valid) => {
        if (valid) {
          submitting.value = true;

          try {
            const versionData = {
              version: versionForm.version,
              release_note: versionForm.releaseNote,
              documentation_url: versionForm.documentationUrl,
              is_published: versionForm.isPublished,
            };

            const result = await store.dispatch("version/updateVersion", {
              versionId: versionForm.id,
              versionData,
            });

            if (result.success) {
              ElMessage.success("版本更新成功");
              // 更新原始数据
              Object.assign(originalForm, versionForm);
            } else {
              ElMessage.error(result.message || "版本更新失败");
            }
          } catch (error) {
            ElMessage.error("版本更新失败");
          } finally {
            submitting.value = false;
          }
        }
      });
    };

    const resetForm = () => {
      Object.assign(versionForm, originalForm);
      if (versionFormRef.value) {
        versionFormRef.value.clearValidate();
      }
    };

    const goBack = () => {
      router.push("/version/list");
    };

    const handleDownload = async (row) => {
      try {
        const result = await store.dispatch("version/downloadFile", row.id);
        if (result.success) {
          // 创建下载链接
          const url = window.URL.createObjectURL(new Blob([result.data]));
          const link = document.createElement("a");
          link.href = url;
          link.setAttribute("download", row.filename);
          document.body.appendChild(link);
          link.click();
          document.body.removeChild(link);
          window.URL.revokeObjectURL(url);

          ElMessage.success("下载成功");
        } else {
          ElMessage.error(result.message || "下载失败");
        }
      } catch (error) {
        ElMessage.error("下载失败");
      }
    };

    const handleDeleteFile = async (row) => {
      try {
        const result = await store.dispatch("version/deleteArchitectureFile", {
          versionId: versionForm.id,
          fileId: row.id,
        });

        if (result.success) {
          ElMessage.success("删除成功");
          fetchFiles(); // 刷新文件列表
        } else {
          ElMessage.error(result.message || "删除失败");
        }
      } catch (error) {
        ElMessage.error("删除失败");
      }
    };

    // 组件挂载
    onMounted(() => {
      fetchVersion();
    });

    return {
      versionFormRef,
      uploadRef,
      loading,
      submitting,
      filesLoading,
      fileList,
      versionForm,
      versionRules,
      spaceName,
      uploadUrl,
      uploadHeaders,
      beforeUpload,
      handleUploadSuccess,
      handleUploadError,
      handleSubmit,
      resetForm,
      goBack,
      handleDownload,
      handleDeleteFile,
    };
  },
};
</script>

<style lang="scss" scoped>
.version-edit-container {
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
