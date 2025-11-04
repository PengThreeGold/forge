<template>
  <div class="permission-management-container">
    <div class="page-header">
      <h2>权限管理</h2>
      <div class="header-actions">
        <el-button type="primary" @click="showCreateRoleDialog">
          <el-icon><Plus /></el-icon>
          创建角色
        </el-button>
      </div>
    </div>

    <el-row :gutter="24">
      <!-- 角色列表 -->
      <el-col :span="12">
        <el-card shadow="never" class="role-card">
          <template #header>
            <div class="card-header">
              <span>角色列表</span>
              <el-input
                v-model="roleSearchKeyword"
                placeholder="搜索角色..."
                prefix-icon="Search"
                clearable
                size="small"
                class="search-input"
              />
            </div>
          </template>

          <el-table
            v-loading="roleLoading"
            :data="filteredRoles"
            style="width: 100%"
            highlight-current-row
            @row-click="handleRoleSelect"
          >
            <el-table-column prop="name" label="角色名称" />
            <el-table-column prop="description" label="描述" />
            <el-table-column prop="user_count" label="用户数量" width="100" />
            <el-table-column label="操作" width="180">
              <template #default="scope">
                <el-button type="primary" size="small" @click.stop="editRole(scope.row)">
                  编辑
                </el-button>
                <el-button
                  type="danger"
                  size="small"
                  :disabled="scope.row.is_system"
                  @click.stop="confirmDeleteRole(scope.row)"
                >
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>

      <!-- 权限详情 -->
      <el-col :span="12">
        <el-card shadow="never" class="permission-card">
          <template #header>
            <span>权限配置</span>
          </template>

          <div v-if="!currentRole" class="empty-permission">
            <el-empty description="请选择一个角色查看权限" />
          </div>

          <div v-else>
            <div class="role-info">
              <h3>{{ currentRole.name }}</h3>
              <p>{{ currentRole.description }}</p>
            </div>

            <el-divider>权限列表</el-divider>

            <el-tree
              ref="permissionTreeRef"
              :data="permissionTree"
              :props="{ label: 'name', children: 'children' }"
              node-key="id"
              show-checkbox
              :default-checked-keys="currentRole.permissions"
              class="permission-tree"
              @check="handlePermissionCheck"
            />
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 创建/编辑角色对话框 -->
    <el-dialog
      v-model="roleDialogVisible"
      :title="isEditing ? '编辑角色' : '创建角色'"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form ref="roleFormRef" :model="roleForm" :rules="roleRules" label-width="100px">
        <el-form-item label="角色名称" prop="name">
          <el-input
            v-model="roleForm.name"
            placeholder="请输入角色名称"
            :disabled="isEditing && roleForm.is_system"
          />
        </el-form-item>

        <el-form-item label="角色描述" prop="description">
          <el-input
            v-model="roleForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入角色描述"
          />
        </el-form-item>

        <el-form-item label="是否系统角色">
          <el-switch
            v-model="roleForm.is_system"
            :disabled="isEditing"
            active-text="是"
            inactive-text="否"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="roleDialogVisible = false">取消</el-button>
          <el-button type="primary" :loading="roleDialogLoading" @click="handleRoleSubmit">
            确认
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { defineComponent, ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'

export default defineComponent({
  name: 'PermissionManagement',
  setup() {
    // 数据
    const roles = ref([])
    const currentRole = ref(null)
    const roleLoading = ref(false)
    const roleSearchKeyword = ref('')

    // 对话框相关
    const roleDialogVisible = ref(false)
    const roleDialogLoading = ref(false)
    const isEditing = ref(false)

    // 表单
    const roleForm = reactive({
      name: '',
      description: '',
      is_system: false,
    })

    const roleRules = {
      name: [{ required: true, message: '请输入角色名称', trigger: 'blur' }],
      description: [{ required: true, message: '请输入角色描述', trigger: 'blur' }],
    }

    const roleFormRef = ref(null)
    const permissionTreeRef = ref(null)

    // 权限树数据
    const permissionTreeData = [
      {
        id: 'software:read',
        name: '查看软件',
        children: [
          { id: 'software:list', name: '查看软件列表' },
          { id: 'software:view', name: '查看软件详情' },
          { id: 'software:stats', name: '查看软件统计' },
        ],
      },
      {
        id: 'software:write',
        name: '管理软件',
        children: [
          { id: 'software:create', name: '创建软件' },
          { id: 'software:edit', name: '编辑软件' },
          { id: 'software:delete', name: '删除软件' },
        ],
      },
      {
        id: 'version:write',
        name: '管理版本',
        children: [
          { id: 'version:create', name: '创建版本' },
          { id: 'version:edit', name: '编辑版本' },
          { id: 'version:delete', name: '删除版本' },
          { id: 'version:publish', name: '发布版本' },
          { id: 'version:download', name: '下载版本' },
        ],
      },
      {
        id: 'user:read',
        name: '查看用户',
        children: [
          { id: 'user:list', name: '查看用户列表' },
          { id: 'user:view', name: '查看用户详情' },
          { id: 'user:stats', name: '查看用户统计' },
        ],
      },
      {
        id: 'user:write',
        name: '管理用户',
        children: [
          { id: 'user:create', name: '创建用户' },
          { id: 'user:edit', name: '编辑用户' },
          { id: 'user:delete', name: '删除用户' },
          { id: 'user:role', name: '分配角色' },
        ],
      },
      {
        id: 'system:admin',
        name: '系统管理',
        children: [
          { id: 'system:settings', name: '系统设置' },
          { id: 'system:logs', name: '查看日志' },
          { id: 'system:backup', name: '系统备份' },
          { id: 'system:restore', name: '系统恢复' },
        ],
      },
    ]

    // 计算属性
    const filteredRoles = computed(() => {
      if (!roleSearchKeyword.value) {
        return roles.value
      }

      const keyword = roleSearchKeyword.value.toLowerCase()
      return roles.value.filter(
        role =>
          role.name.toLowerCase().includes(keyword) ||
          role.description.toLowerCase().includes(keyword)
      )
    })

    const permissionTree = computed(() => {
      return permissionTreeData
    })

    // 获取角色列表
    const getRoles = async () => {
      try {
        roleLoading.value = true

        // 模拟数据，实际应用中应从API获取
        const mockRoles = [
          {
            id: 1,
            name: '超级管理员',
            description: '拥有系统所有权限',
            is_system: true,
            user_count: 1,
            permissions: Object.values(
              permissionTreeData.reduce((acc, group) => {
                group.children.forEach(item => {
                  acc[item.id] = item.id
                })
                return acc
              }, {})
            ),
          },
          {
            id: 2,
            name: '软件开发者',
            description: '可以管理自己的软件和版本',
            is_system: false,
            user_count: 3,
            permissions: [
              'software:read',
              'software:list',
              'software:view',
              'software:stats',
              'software:create',
              'software:edit',
              'version:write',
              'version:create',
              'version:edit',
              'version:delete',
              'version:publish',
              'version:download',
            ],
          },
          {
            id: 3,
            name: '访客',
            description: '只能查看已发布的软件',
            is_system: false,
            user_count: 5,
            permissions: ['software:read', 'software:list', 'software:view', 'version:download'],
          },
        ]

        roles.value = mockRoles
      } catch (error) {
        console.error('获取角色列表失败:', error)
      } finally {
        roleLoading.value = false
      }
    }

    // 选择角色
    const handleRoleSelect = role => {
      currentRole.value = role

      // 设置权限树的选中状态
      if (permissionTreeRef.value) {
        setTimeout(() => {
          if (permissionTreeRef.value && permissionTreeRef.value.setCheckedKeys) {
            permissionTreeRef.value.setCheckedKeys(role.permissions || [])
          }
        }, 100)
      }
    }

    // 权限勾选变化
    const handlePermissionCheck = (data, checked) => {
      if (!currentRole.value) return

      // 获取所有选中的权限ID
      const checkedKeys = permissionTreeRef.value.getCheckedKeys()
      currentRole.value.permissions = checkedKeys
    }

    // 显示创建角色对话框
    const showCreateRoleDialog = () => {
      isEditing.value = false
      resetRoleForm()
      roleDialogVisible.value = true
    }

    // 编辑角色
    const editRole = role => {
      isEditing.value = true
      currentRole.value = { ...role }

      // 填充表单
      roleForm.name = role.name
      roleForm.description = role.description
      roleForm.is_system = role.is_system

      roleDialogVisible.value = true
    }

    // 确认删除角色
    const confirmDeleteRole = role => {
      ElMessageBox.confirm(`确定要删除角色"${role.name}"吗？此操作不可逆。`, '删除确认', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      })
        .then(async () => {
          try {
            // 这里应调用API删除角色
            ElMessage.success('删除成功')
            getRoles()

            // 如果删除的是当前选中的角色，清空选中状态
            if (currentRole.value && currentRole.value.id === role.id) {
              currentRole.value = null
            }
          } catch (error) {
            console.error('删除角色失败:', error)
          }
        })
        .catch(() => {
          // 用户取消删除
        })
    }

    // 处理角色表单提交
    const handleRoleSubmit = async () => {
      if (!roleFormRef.value) return

      try {
        await roleFormRef.value.validate()

        roleDialogLoading.value = true

        if (isEditing.value) {
          // 更新角色
          // 这里应调用API更新角色
          ElMessage.success('更新成功')

          // 更新本地数据
          const index = roles.value.findIndex(r => r.id === currentRole.value.id)
          if (index !== -1) {
            roles.value[index] = {
              ...currentRole.value,
              name: roleForm.name,
              description: roleForm.description,
              is_system: roleForm.is_system,
            }
          }
        } else {
          // 创建角色
          // 这里应调用API创建角色
          ElMessage.success('创建成功')

          // 添加到本地数据
          const newRole = {
            id: Date.now(),
            name: roleForm.name,
            description: roleForm.description,
            is_system: roleForm.is_system,
            user_count: 0,
            permissions: [],
          }
          roles.value.unshift(newRole)
        }

        roleDialogVisible.value = false
      } catch (error) {
        console.error('操作失败:', error)
      } finally {
        roleDialogLoading.value = false
      }
    }

    // 重置角色表单
    const resetRoleForm = () => {
      roleForm.name = ''
      roleForm.description = ''
      roleForm.is_system = false

      if (roleFormRef.value) {
        roleFormRef.value.resetFields()
      }
    }

    onMounted(() => {
      getRoles()
    })

    return {
      roles,
      currentRole,
      roleLoading,
      roleSearchKeyword,
      filteredRoles,
      roleDialogVisible,
      roleDialogLoading,
      isEditing,
      roleForm,
      roleRules,
      roleFormRef,
      permissionTree,
      permissionTreeRef,
      handleRoleSelect,
      handlePermissionCheck,
      showCreateRoleDialog,
      editRole,
      confirmDeleteRole,
      handleRoleSubmit,
      resetRoleForm,
      Plus,
    }
  },
})
</script>

<style scoped>
.permission-management-container {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-header h2 {
  margin: 0;
  font-size: 24px;
  font-weight: 500;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.search-input {
  width: 200px;
}

.role-card,
.permission-card {
  height: calc(100vh - 200px);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

:deep(.el-card__body) {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.empty-permission {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.role-info {
  margin-bottom: 20px;
}

.role-info h3 {
  margin: 0 0 8px 0;
  color: #303133;
}

.role-info p {
  margin: 0;
  color: #606266;
}

.permission-tree {
  flex: 1;
  overflow-y: auto;
  max-height: 400px;
}

/* 暗色主题 */
.dark-theme .page-header h2 {
  color: #e5eaf3;
}

.dark-theme .role-info h3 {
  color: #e5eaf3;
}

.dark-theme .role-info p {
  color: #cfd3dc;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .permission-management-container {
    padding: 10px;
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }

  .search-input {
    width: 100%;
  }
}

@media (max-width: 768px) {
  :deep(.el-col) {
    margin-bottom: 20px;
  }

  .role-card,
  .permission-card {
    height: auto;
    min-height: 400px;
  }
}
</style>
