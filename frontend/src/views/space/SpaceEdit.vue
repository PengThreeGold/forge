<template>
  <div class="space-edit-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>编辑软件空间</span>
          <el-button @click="goBack">返回</el-button>
        </div>
      </template>

      <el-form
        ref="spaceFormRef"
        :model="spaceForm"
        :rules="spaceRules"
        label-width="100px"
        class="space-form"
        v-loading="loading"
      >
        <el-form-item label="空间ID">
          <el-input
            v-model="spaceForm.spaceId"
            disabled
            placeholder="空间ID创建后不可修改"
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
          <el-button type="primary" @click="handleSubmit" :loading="submitting">
            保存
          </el-button>
          <el-button @click="resetForm">重置</el-button>
          <el-button @click="goBack">取消</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 版本管理 -->
    <el-card style="margin-top: 20px">
      <template #header>
        <div class="card-header">
          <span>版本管理</span>
          <el-button type="primary" @click="handleCreateVersion">
            <el-icon><Plus /></el-icon>
            创建版本
          </el-button>
        </div>
      </template>

      <el-table
        v-loading="versionsLoading"
        :data="versionList"
        border
        style="width: 100%"
      >
        <el-table-column type="index" label="#" width="60" />
        <el-table-column prop="version" label="版本号" min-width="100" />
        <el-table-column
          prop="release_note"
          label="发布说明"
          min-width="180"
          show-overflow-tooltip
        />
        <el-table-column prop="is_published" label="发布状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_published ? 'success' : 'info'">
              {{ row.is_published ? "已发布" : "未发布" }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="is_ready" label="完成状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_ready ? 'success' : 'warning'">
              {{ row.is_ready ? "已完成" : "未完成" }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button
              type="primary"
              link
              size="small"
              @click="handleEditVersion(row)"
            >
              <el-icon><Edit /></el-icon>
              编辑
            </el-button>
            <el-button
              :type="row.is_published ? 'warning' : 'success'"
              link
              size="small"
              @click="handleTogglePublish(row)"
            >
              <el-icon
                ><Promotion v-if="!row.is_published" /><Remove v-else
              /></el-icon>
              {{ row.is_published ? "取消发布" : "发布" }}
            </el-button>
            <el-button
              type="danger"
              link
              size="small"
              @click="handleDeleteVersion(row)"
            >
              <el-icon><Delete /></el-icon>
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
        <el-pagination
          v-model:current-page="versionPagination.page"
          v-model:page-size="versionPagination.size"
          :page-sizes="[10, 20, 50, 100]"
          :total="versionPagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleVersionSizeChange"
          @current-change="handleVersionCurrentChange"
        />
      </div>
    </el-card>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from "vue";
import { useStore } from "vuex";
import { useRouter, useRoute } from "vue-router";
import { ElMessage, ElMessageBox } from "element-plus";

export default {
  name: "SpaceEdit",
  setup() {
    const store = useStore();
    const router = useRouter();
    const route = useRoute();

    // 响应式数据
    const spaceFormRef = ref(null);
    const loading = ref(false);
    const submitting = ref(false);
    const versionsLoading = ref(false);
    const versionList = ref([]);

    // 表单数据
    const spaceForm = reactive({
      spaceId: "",
      name: "",
      description: "",
      author: "",
      status: "active",
      webhookUrl: "",
    });

    // 原始表单数据，用于重置
    const originalForm = {};

    // 版本分页数据
    const versionPagination = reactive({
      page: 1,
      size: 10,
      total: 0,
    });

    // 表单验证规则
    const spaceRules = {
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
    const fetchSpace = async () => {
      const spaceId = route.params.id;
      if (!spaceId) {
        ElMessage.error("软件空间ID不存在");
        router.push("/space/list");
        return;
      }

      loading.value = true;
      try {
        const result = await store.dispatch("space/fetchSpaceById", spaceId);
        if (result.success) {
          const space = result.data;
          spaceForm.spaceId = space.space_id;
          spaceForm.name = space.name;
          spaceForm.description = space.description;
          spaceForm.author = space.author;
          spaceForm.status = space.status;
          spaceForm.webhookUrl = space.webhook_url;

          // 保存原始数据，用于重置
          Object.assign(originalForm, spaceForm);

          // 获取该空间的版本列表
          await fetchVersions();
        } else {
          ElMessage.error(result.message || "获取软件空间信息失败");
          router.push("/space/list");
        }
      } catch (error) {
        ElMessage.error("获取软件空间信息失败");
        router.push("/space/list");
      } finally {
        loading.value = false;
      }
    };

    const fetchVersions = async () => {
      versionsLoading.value = true;
      try {
        const params = {
          skip: (versionPagination.page - 1) * versionPagination.size,
          limit: versionPagination.size,
        };

        const result = await store.dispatch("version/fetchVersionsBySpace", {
          spaceId: spaceForm.spaceId,
          params,
        });

        if (result.success) {
          versionList.value = result.data.items || [];
          versionPagination.total = result.data.total || 0;
        }
      } catch (error) {
        ElMessage.error("获取版本列表失败");
      } finally {
        versionsLoading.value = false;
      }
    };

    const handleSubmit = () => {
      if (!spaceFormRef.value) return;

      spaceFormRef.value.validate(async (valid) => {
        if (valid) {
          submitting.value = true;

          try {
            const spaceData = {
              name: spaceForm.name,
              description: spaceForm.description,
              author: spaceForm.author,
              status: spaceForm.status,
              webhook_url: spaceForm.webhookUrl,
            };

            const result = await store.dispatch("space/updateSpace", {
              spaceId: spaceForm.spaceId,
              spaceData,
            });

            if (result.success) {
              ElMessage.success("软件空间更新成功");
              // 更新原始数据
              Object.assign(originalForm, spaceForm);
            } else {
              ElMessage.error(result.message || "软件空间更新失败");
            }
          } catch (error) {
            ElMessage.error("软件空间更新失败");
          } finally {
            submitting.value = false;
          }
        }
      });
    };

    const resetForm = () => {
      Object.assign(spaceForm, originalForm);
      if (spaceFormRef.value) {
        spaceFormRef.value.clearValidate();
      }
    };

    const goBack = () => {
      router.push("/space/list");
    };

    const handleCreateVersion = () => {
      router.push(`/version/create?spaceId=${spaceForm.spaceId}`);
    };

    const handleEditVersion = (row) => {
      router.push(`/version/edit/${row.id}`);
    };

    const handleTogglePublish = async (row) => {
      const action = row.is_published ? "取消发布" : "发布";

      try {
        ElMessageBox.confirm(
          `确定要${action}版本 "${row.version}" 吗？`,
          "提示",
          {
            confirmButtonText: "确定",
            cancelButtonText: "取消",
            type: "warning",
          }
        )
          .then(async () => {
            const result = row.is_published
              ? await store.dispatch("version/unpublishVersion", row.id)
              : await store.dispatch("version/publishVersion", row.id);

            if (result.success) {
              ElMessage.success(`${action}成功`);
              fetchVersions();
            } else {
              ElMessage.error(result.message || `${action}失败`);
            }
          })
          .catch(() => {
            // 用户取消操作
          });
      } catch (error) {
        ElMessage.error(`${action}失败`);
      }
    };

    const handleDeleteVersion = (row) => {
      ElMessageBox.confirm(
        `确定要删除版本 "${row.version}" 吗？此操作不可恢复。`,
        "警告",
        {
          confirmButtonText: "确定",
          cancelButtonText: "取消",
          type: "warning",
        }
      )
        .then(async () => {
          try {
            const result = await store.dispatch(
              "version/deleteVersion",
              row.id
            );
            if (result.success) {
              ElMessage.success("删除成功");
              fetchVersions();
            } else {
              ElMessage.error(result.message || "删除失败");
            }
          } catch (error) {
            ElMessage.error("删除失败");
          }
        })
        .catch(() => {
          // 用户取消操作
        });
    };

    const handleVersionSizeChange = (size) => {
      versionPagination.size = size;
      versionPagination.page = 1;
      fetchVersions();
    };

    const handleVersionCurrentChange = (page) => {
      versionPagination.page = page;
      fetchVersions();
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

    // 组件挂载
    onMounted(() => {
      fetchSpace();
    });

    return {
      spaceFormRef,
      loading,
      submitting,
      versionsLoading,
      versionList,
      spaceForm,
      spaceRules,
      versionPagination,
      handleSubmit,
      resetForm,
      goBack,
      handleCreateVersion,
      handleEditVersion,
      handleTogglePublish,
      handleDeleteVersion,
      handleVersionSizeChange,
      handleVersionCurrentChange,
      formatDateTime,
    };
  },
};
</script>

<style lang="scss" scoped>
.space-edit-container {
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

  .pagination-container {
    margin-top: 20px;
    display: flex;
    justify-content: center;
  }
}
</style>
