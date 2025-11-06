<template>
  <div class="space-list-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>软件空间</span>
          <el-button type="primary" @click="handleCreate">
            <el-icon><Plus /></el-icon>
            创建空间
          </el-button>
        </div>
      </template>

      <!-- 搜索区域 -->
      <div class="filter-container">
        <el-form :inline="true" :model="filterForm" class="filter-form">
          <el-form-item label="空间ID">
            <el-input
              v-model="filterForm.spaceId"
              placeholder="请输入空间ID"
              clearable
              @keyup.enter="handleSearch"
            />
          </el-form-item>
          <el-form-item label="软件名称">
            <el-input
              v-model="filterForm.name"
              placeholder="请输入软件名称"
              clearable
              @keyup.enter="handleSearch"
            />
          </el-form-item>
          <el-form-item label="状态">
            <el-select
              v-model="filterForm.status"
              placeholder="请选择状态"
              clearable
            >
              <el-option label="激活" value="active" />
              <el-option label="停用" value="inactive" />
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
        :data="spaceList"
        border
        style="width: 100%"
      >
        <el-table-column type="index" label="#" width="60" />
        <el-table-column
          prop="space_id"
          label="空间ID"
          min-width="120"
          show-overflow-tooltip
        />
        <el-table-column
          prop="name"
          label="软件名称"
          min-width="120"
          show-overflow-tooltip
        />
        <el-table-column
          prop="description"
          label="描述"
          min-width="180"
          show-overflow-tooltip
        />
        <el-table-column
          prop="author"
          label="作者"
          width="100"
          show-overflow-tooltip
        />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'info'">
              {{ row.status === "active" ? "激活" : "停用" }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="280" fixed="right">
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
              @click="handleViewVersions(row)"
            >
              <el-icon><Document /></el-icon>
              版本管理
            </el-button>
            <el-button
              type="warning"
              link
              size="small"
              @click="handleToggleStatus(row)"
            >
              <el-icon><Switch /></el-icon>
              {{ row.status === "active" ? "停用" : "激活" }}
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
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted } from "vue";
import { useStore } from "vuex";
import { useRouter } from "vue-router";
import { ElMessage, ElMessageBox } from "element-plus";

export default {
  name: "SpaceList",
  setup() {
    const store = useStore();
    const router = useRouter();

    // 响应式数据
    const loading = ref(false);
    const spaceList = ref([]);

    // 过滤表单
    const filterForm = reactive({
      spaceId: "",
      name: "",
      status: "",
    });

    // 分页数据
    const pagination = reactive({
      page: 1,
      size: 10,
      total: 0,
    });

    // 计算属性
    const computedSpaceList = computed(() => store.getters["space/spaces"]);
    const total = computed(() => store.getters["space/total"]);

    // 方法
    const fetchSpaces = async () => {
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

        await store.dispatch("space/fetchSpaces", params);
        spaceList.value = computedSpaceList.value;
        pagination.total = total.value;
      } catch (error) {
        ElMessage.error("获取软件空间列表失败");
      } finally {
        loading.value = false;
      }
    };

    const handleSearch = () => {
      pagination.page = 1;
      fetchSpaces();
    };

    const resetFilter = () => {
      filterForm.spaceId = "";
      filterForm.name = "";
      filterForm.status = "";
      pagination.page = 1;
      fetchSpaces();
    };

    const handleSizeChange = (size) => {
      pagination.size = size;
      pagination.page = 1;
      fetchSpaces();
    };

    const handleCurrentChange = (page) => {
      pagination.page = page;
      fetchSpaces();
    };

    const handleCreate = () => {
      router.push("/space/create");
    };

    const handleEdit = (row) => {
      router.push(`/space/edit/${row.space_id}`);
    };

    const handleViewVersions = (row) => {
      router.push(`/version/list?spaceId=${row.space_id}`);
    };

    const handleToggleStatus = async (row) => {
      const newStatus = row.status === "active" ? "inactive" : "active";
      const actionText = newStatus === "active" ? "激活" : "停用";

      try {
        const result = await store.dispatch("space/updateSpaceStatus", {
          spaceId: row.space_id,
          status: newStatus,
        });

        if (result.success) {
          ElMessage.success(`${actionText}成功`);
          fetchSpaces();
        } else {
          ElMessage.error(result.message || `${actionText}失败`);
        }
      } catch (error) {
        ElMessage.error(`${actionText}失败`);
      }
    };

    const handleDelete = (row) => {
      ElMessageBox.confirm(
        `确定要删除软件空间 "${row.name}" 吗？此操作不可恢复。`,
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
              "space/deleteSpace",
              row.space_id
            );
            if (result.success) {
              ElMessage.success("删除成功");
              fetchSpaces();
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
      fetchSpaces();
    });

    return {
      loading,
      spaceList,
      filterForm,
      pagination,
      handleSearch,
      resetFilter,
      handleSizeChange,
      handleCurrentChange,
      handleCreate,
      handleEdit,
      handleViewVersions,
      handleToggleStatus,
      handleDelete,
      formatDateTime,
    };
  },
};
</script>

<style lang="scss" scoped>
.space-list-container {
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

  .pagination-container {
    margin-top: 20px;
    display: flex;
    justify-content: center;
  }
}
</style>
