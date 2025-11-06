<template>
  <div class="webhook-list-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>Webhook管理</span>
          <el-button type="primary" @click="goToSpaces">
            <el-icon><FolderOpened /></el-icon>
            管理软件空间
          </el-button>
        </div>
      </template>

      <!-- 搜索区域 -->
      <div class="filter-container">
        <el-form :inline="true" :model="filterForm" class="filter-form">
          <el-form-item label="软件空间">
            <el-select
              v-model="filterForm.spaceId"
              placeholder="请选择软件空间"
              clearable
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
          <el-form-item>
            <el-button type="primary" @click="handleSearch">
              <el-icon><Search /></el-icon>
              搜索
            </el-button>
            <el-button @click="resetFilter">
              <el-icon><Refresh /></el-icon>
              重置
            </el-button>
          </el-form-item>
        </el-form>
      </div>

      <!-- Webhook配置表格 -->
      <el-table
        v-loading="loading"
        :data="webhookList"
        border
        style="width: 100%"
      >
        <el-table-column type="index" label="#" width="60" />
        <el-table-column prop="space_name" label="软件空间" min-width="150" />
        <el-table-column
          prop="webhook_url"
          label="Webhook URL"
          min-width="200"
          show-overflow-tooltip
        />
        <el-table-column prop="webhook_events" label="事件类型" min-width="150">
          <template #default="{ row }">
            <div class="event-tags">
              <el-tag
                v-for="event in row.webhook_events"
                :key="event"
                size="small"
                style="margin-right: 5px; margin-bottom: 5px"
              >
                {{ getEventLabel(event) }}
              </el-tag>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button
              type="primary"
              link
              size="small"
              @click="handleEdit(row)"
            >
              <el-icon><Edit /></el-icon>
              编辑
            </el-button>
            <el-button
              type="success"
              link
              size="small"
              @click="handleTest(row)"
            >
              <el-icon><Connection /></el-icon>
              测试
            </el-button>
            <el-button
              type="danger"
              link
              size="small"
              @click="handleDelete(row)"
            >
              <el-icon><Delete /></el-icon>
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页区域 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.size"
          :page-sizes="[10, 20, 50, 100]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- Webhook测试对话框 -->
    <el-dialog v-model="testDialogVisible" title="测试Webhook" width="500px">
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
      </el-form>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="testDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitTest" :loading="testLoading">
            测试
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, reactive, onMounted, computed } from "vue";
import { useStore } from "vuex";
import { useRouter } from "vue-router";
import { ElMessage } from "element-plus";

export default {
  name: "WebhookList",
  setup() {
    const store = useStore();
    const router = useRouter();

    // 响应式数据
    const loading = ref(false);
    const testLoading = ref(false);
    const webhookList = ref([]);
    const testDialogVisible = ref(false);
    const testFormRef = ref(null);
    const currentWebhook = ref(null);

    // 过滤表单
    const filterForm = reactive({
      spaceId: "",
    });

    // 分页数据
    const pagination = reactive({
      page: 1,
      size: 10,
      total: 0,
    });

    // 测试表单数据
    const testForm = reactive({
      eventType: "download",
      payload: "",
    });

    // 表单验证规则
    const testRules = {
      eventType: [
        { required: true, message: "请选择事件类型", trigger: "change" },
      ],
    };

    // 计算属性
    const spaceList = computed(() => store.getters["space/spaces"]);

    // 方法
    const fetchWebhooks = async () => {
      if (!filterForm.spaceId) {
        webhookList.value = [];
        pagination.total = 0;
        return;
      }

      loading.value = true;
      try {
        const result = await store.dispatch(
          "webhook/getWebhookConfig",
          filterForm.spaceId
        );
        if (result.success) {
          // 将单个webhook配置转换为列表形式
          webhookList.value = [result.data];
          pagination.total = 1;
        }
      } catch (error) {
        ElMessage.error("获取Webhook配置失败");
      } finally {
        loading.value = false;
      }
    };

    const fetchSpaces = async () => {
      try {
        await store.dispatch("space/fetchSpaces");
      } catch (error) {
        ElMessage.error("获取软件空间列表失败");
      }
    };

    const handleSearch = () => {
      pagination.page = 1;
      fetchWebhooks();
    };

    const resetFilter = () => {
      filterForm.spaceId = "";
      pagination.page = 1;
      fetchWebhooks();
    };

    const handleSpaceChange = () => {
      pagination.page = 1;
      fetchWebhooks();
    };

    const handleSizeChange = (size) => {
      pagination.size = size;
      pagination.page = 1;
      fetchWebhooks();
    };

    const handleCurrentChange = (page) => {
      pagination.page = page;
      fetchWebhooks();
    };

    const goToSpaces = () => {
      router.push("/space/list");
    };

    const handleEdit = (row) => {
      router.push(`/webhook/edit/${row.space_id}`);
    };

    const handleTest = (row) => {
      currentWebhook.value = row;
      testForm.eventType = "download";
      testForm.payload = JSON.stringify(
        {
          space_id: row.space_id,
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
      testDialogVisible.value = true;
    };

    const submitTest = () => {
      if (!testFormRef.value) return;

      testFormRef.value.validate(async (valid) => {
        if (valid) {
          testLoading.value = true;

          try {
            const payload = testForm.payload
              ? JSON.parse(testForm.payload)
              : {};
            const result = await store.dispatch("webhook/testWebhook", {
              spaceId: currentWebhook.value.space_id,
              data: {
                event_type: testForm.eventType,
                payload,
              },
            });

            if (result.success) {
              ElMessage.success("Webhook测试成功");
              testDialogVisible.value = false;
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

    const handleDelete = async (row) => {
      try {
        const result = await store.dispatch(
          "webhook/deleteWebhookConfig",
          row.space_id
        );
        if (result.success) {
          ElMessage.success("删除成功");
          fetchWebhooks();
        } else {
          ElMessage.error(result.message || "删除失败");
        }
      } catch (error) {
        ElMessage.error("删除失败");
      }
    };

    const getEventLabel = (eventType) => {
      const eventMap = {
        download: "下载",
        create: "创建",
        update: "更新",
        delete: "删除",
      };
      return eventMap[eventType] || eventType;
    };

    // 组件挂载
    onMounted(async () => {
      await fetchSpaces();
      fetchWebhooks();
    });

    return {
      loading,
      testLoading,
      webhookList,
      testDialogVisible,
      testFormRef,
      currentWebhook,
      filterForm,
      pagination,
      spaceList,
      testForm,
      testRules,
      handleSearch,
      resetFilter,
      handleSpaceChange,
      handleSizeChange,
      handleCurrentChange,
      goToSpaces,
      handleEdit,
      handleTest,
      submitTest,
      handleDelete,
      getEventLabel,
    };
  },
};
</script>

<style lang="scss" scoped>
.webhook-list-container {
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .filter-container {
    margin-bottom: 20px;

    .filter-form {
      .el-form-item {
        margin-bottom: 10px;
      }
    }
  }

  .event-tags {
    display: flex;
    flex-wrap: wrap;
  }

  .pagination-container {
    margin-top: 20px;
    display: flex;
    justify-content: center;
  }
}
</style>
