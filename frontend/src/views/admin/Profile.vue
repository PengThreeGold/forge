<template>
  <div class="admin-profile">
    <el-card>
      <template #header>
        <h2>个人设置</h2>
      </template>
      <el-descriptions :column="1" border>
        <el-descriptions-item label="用户名">{{ authStore.user?.username }}</el-descriptions-item>
        <el-descriptions-item label="邮箱">{{ authStore.user?.email || '未设置' }}</el-descriptions-item>
        <el-descriptions-item label="角色">
          <el-tag :type="authStore.user?.role === 'admin' ? 'danger' : 'primary'">
            {{ authStore.user?.role === 'admin' ? '管理员' : '用户' }}
          </el-tag>
        </el-descriptions-item>
      </el-descriptions>
    </el-card>
  </div>
</template>

<script setup>
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
</script>

<style scoped>
.admin-profile {
  max-width: 800px;
  margin: 0 auto;
}
</style>
