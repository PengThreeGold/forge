<template>
  <div class="user-list-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>用户管理</span>
          <el-button type="primary" @click="handleCreate">
            <el-icon><Plus /></el-icon>
            新增用户
          </el-button>
        </div>
      </template>

      <!-- 搜索区域 -->
      <div class="filter-container">
        <el-form :inline="true" :model="filterForm" class="filter-form">
          <el-form-item label="用户名">
            <el-input
              v-model="filterForm.username"
              placeholder="请输入用户名"
              clearable
              @keyup.enter="handleSearch"
            />
          </el-form-item>
          <el-form-item label="角色">
            <el-select
              v-model="filterForm.role"
              placeholder="请选择角色"
              clearable
            >
              <el-option label="管理员" value="admin" />
              <el-option label="普通用户" value="user" />
            </el-select>
          </el-form-item>
          <el-form-item label="状态">
            <el-select
              v-model="filterForm.isActive"
              placeholder="请选择状态"
              clearable
            >
              <el-option label="激活" :value="true" />
              <el-option label="停用" :value="false" />
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
      <el-table v-loading="loading" :data="userList" border style="width: 100%">
        <el-table-column type="index" label="#" width="60" />
        <el-table-column prop="username" label="用户名" min-width="120" />
        <el-table-column
          prop="email"
          label="邮箱"
          min-width="180"
          show-overflow-tooltip
        />
        <el-table-column prop="role" label="角色" width="100">
          <template #default="{ row }">
            <el-tag :type="row.role === 'admin' ? 'danger' : 'info'">
              {{ row.role === "admin" ? "管理员" : "普通用户" }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="is_active" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'info'">
              {{ row.is_active ? "激活" : "停用" }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="220" fixed="right">
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
              type="warning"
              link
              size="small"
              @click="handleResetPassword(row)"
            >
              <el-icon><Key /></el-icon>
              重置密码
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
  name: "UserList",
  setup() {
    const store = useStore();
    const router = useRouter();

    // 响应式数据
    const loading = ref(false);
    const userList = ref([]);

    // 过滤表单
    const filterForm = reactive({
      username: "",
      role: "",
      isActive: "",
    });

    // 分页数据
    const pagination = reactive({
      page: 1,
      size: 10,
      total: 0,
    });

    // 计算属性
    const computedUserList = computed(() => store.getters["user/users"]);
    const total = computed(() => store.getters["user/total"]);

    // 方法
    const fetchUsers = async () => {
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

        await store.dispatch("user/fetchUsers", params);
        userList.value = computedUserList.value;
        pagination.total = total.value;
      } catch (error) {
        ElMessage.error("获取用户列表失败");
      } finally {
        loading.value = false;
      }
    };

    const handleSearch = () => {
      pagination.page = 1;
      fetchUsers();
    };

    const resetFilter = () => {
      filterForm.username = "";
      filterForm.role = "";
      filterForm.isActive = "";
      pagination.page = 1;
      fetchUsers();
    };

    const handleSizeChange = (size) => {
      pagination.size = size;
      pagination.page = 1;
      fetchUsers();
    };

    const handleCurrentChange = (page) => {
      pagination.page = page;
      fetchUsers();
    };

    const handleCreate = () => {
      router.push("/user/create");
    };

    const handleEdit = (row) => {
      router.push(`/user/edit/${row.id}`);
    };

    const handleResetPassword = (user) => {
      ElMessageBox.prompt("请输入新密码", "重置密码", {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        inputType: "password",
        inputValidator: (password) => {
          if (!password || password.length < 6) {
            return "密码长度不能少于6位";
          }
          return true;
        },
      })
        .then(({ value }) => {
          // 调用重置密码API
          // 注意：这里的API调用是示例，实际使用时需要替换为真实的API
          // store.dispatch("user/resetPassword", { userId: user.id, password: value })
          console.log(`新密码: ${value}`);
          ElMessage.success(`已为用户 ${user.username} 重置密码`);
        })
        .catch(() => {
          // 用户取消操作
        });
    };

    const handleDelete = (row) => {
      ElMessageBox.confirm(
        `确定要删除用户 "${row.username}" 吗？此操作不可恢复。`,
        "警告",
        {
          confirmButtonText: "确定",
          cancelButtonText: "取消",
          type: "warning",
        }
      )
        .then(async () => {
          try {
            const result = await store.dispatch("user/deleteUser", row.id);
            if (result.success) {
              ElMessage.success("删除成功");
              fetchUsers();
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
      fetchUsers();
    });

    return {
      loading,
      userList,
      filterForm,
      pagination,
      handleSearch,
      resetFilter,
      handleSizeChange,
      handleCurrentChange,
      handleCreate,
      handleEdit,
      handleResetPassword,
      handleDelete,
      formatDateTime,
    };
  },
};
</script>

<style lang="scss" scoped>
.user-list-container {
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
