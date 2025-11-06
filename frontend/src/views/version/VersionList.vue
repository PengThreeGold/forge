<template>
  <div class="version-list-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>软件版本</span>
          <el-button type="primary" @click="handleCreate">
            <el-icon><Plus /></el-icon>
            创建版本
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
          <el-form-item label="版本号">
            <el-input
              v-model="filterForm.version"
              placeholder="请输入版本号"
              clearable
              @keyup.enter="handleSearch"
            />
          </el-form-item>
          <el-form-item label="发布状态">
            <el-select
              v-model="filterForm.isPublished"
              placeholder="请选择发布状态"
              clearable
            >
              <el-option label="已发布" :value="true" />
              <el-option label="未发布" :value="false" />
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

      <!-- 表格区域 -->
      <el-table
        v-loading="loading"
        :data="versionList"
        border
        style="width: 100%"
      >
        <el-table-column type="index" label="#" width="60" />
        <el-table-column prop="space_id" label="软件空间" min-width="120">
          <template #default="{ row }">
            <div>
              <div>{{ getSpaceName(row.space_id) }}</div>
              <div class="text-secondary">({{ row.space_id }})</div>
            </div>
          </template>
        </el-table-column>
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
        <el-table-column prop="total_downloads" label="下载次数" width="100" />
        <el-table-column prop="total_size_human" label="文件大小" width="100" />
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="240" fixed="right">
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
              type="info"
              link
              size="small"
              @click="handleViewFiles(row)"
            >
              <el-icon><FolderOpened /></el-icon>
              文件
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

    <!-- 文件列表对话框 -->
    <el-dialog v-model="fileDialogVisible" title="文件列表" width="80%">
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
    </el-dialog>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted } from "vue";
import { useStore } from "vuex";
import { useRouter, useRoute } from "vue-router";
import { ElMessage, ElMessageBox } from "element-plus";

export default {
  name: "VersionList",
  setup() {
    const store = useStore();
    const router = useRouter();
    const route = useRoute();

    // 响应式数据
    const loading = ref(false);
    const filesLoading = ref(false);
    const versionList = ref([]);
    const fileList = ref([]);
    const fileDialogVisible = ref(false);

    // 过滤表单
    const filterForm = reactive({
      spaceId: "",
      version: "",
      isPublished: "",
    });

    // 分页数据
    const pagination = reactive({
      page: 1,
      size: 10,
      total: 0,
    });

    // 计算属性
    const computedVersionList = computed(
      () => store.getters["version/versions"]
    );
    const total = computed(() => store.getters["version/total"]);
    const spaceList = computed(() => store.getters["space/spaces"]);
    const spaceMap = computed(() => store.getters["space/spaceMap"]);

    // 方法
    const fetchVersions = async () => {
      loading.value = true;
      try {
        const params = {
          skip: (pagination.page - 1) * pagination.size,
          limit: pagination.size,
          ...filterForm,
        };

        // 过滤空值
        Object.keys(params).forEach((key) => {
          if (
            params[key] === "" ||
            params[key] === null ||
            params[key] === undefined
          ) {
            delete params[key];
          }
        });

        await store.dispatch("version/fetchVersions", params);
        versionList.value = computedVersionList.value;
        pagination.total = total.value;
      } catch (error) {
        ElMessage.error("获取版本列表失败");
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
      fetchVersions();
    };

    const resetFilter = () => {
      filterForm.spaceId = "";
      filterForm.version = "";
      filterForm.isPublished = "";
      pagination.page = 1;
      fetchVersions();
    };

    const handleSizeChange = (size) => {
      pagination.size = size;
      pagination.page = 1;
      fetchVersions();
    };

    const handleCurrentChange = (page) => {
      pagination.page = page;
      fetchVersions();
    };

    const handleSpaceChange = () => {
      pagination.page = 1;
      fetchVersions();
    };

    const handleCreate = () => {
      const query = filterForm.spaceId ? { spaceId: filterForm.spaceId } : {};
      router.push({ path: "/version/create", query });
    };

    const handleEdit = (row) => {
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

    const handleViewFiles = async (row) => {
      filesLoading.value = true;
      fileDialogVisible.value = true;

      try {
        const result = await store.dispatch(
          "version/fetchArchitectureFiles",
          row.id
        );
        if (result.success) {
          fileList.value = result.data || [];
        } else {
          ElMessage.error(result.message || "获取文件列表失败");
        }
      } catch (error) {
        ElMessage.error("获取文件列表失败");
      } finally {
        filesLoading.value = false;
      }
    };

    const handleDelete = (row) => {
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

    const handleDeleteFile = (row) => {
      ElMessageBox.confirm(
        `确定要删除文件 "${row.filename}" 吗？此操作不可恢复。`,
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
              "version/deleteArchitectureFile",
              {
                versionId: row.version_id,
                fileId: row.id,
              }
            );

            if (result.success) {
              ElMessage.success("删除成功");
              // 刷新文件列表
              handleViewFiles({ id: row.version_id });
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

    const getSpaceName = (spaceId) => {
      return spaceMap.value[spaceId]?.name || spaceId;
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
    onMounted(async () => {
      // 检查URL参数中是否有spaceId
      const spaceId = route.query.spaceId;
      if (spaceId) {
        filterForm.spaceId = spaceId;
      }

      await fetchSpaces();
      fetchVersions();
    });

    return {
      loading,
      filesLoading,
      versionList,
      fileList,
      fileDialogVisible,
      filterForm,
      pagination,
      spaceList,
      handleSearch,
      resetFilter,
      handleSizeChange,
      handleCurrentChange,
      handleSpaceChange,
      handleCreate,
      handleEdit,
      handleTogglePublish,
      handleViewFiles,
      handleDelete,
      handleDownload,
      handleDeleteFile,
      getSpaceName,
      formatDateTime,
    };
  },
};
</script>

<style lang="scss" scoped>
.version-list-container {
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

  .text-secondary {
    font-size: 12px;
    color: #909399;
  }

  .pagination-container {
    margin-top: 20px;
    display: flex;
    justify-content: center;
  }
}
</style>
