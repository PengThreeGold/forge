<template>
  <div class="public-layout">
    <el-container>
      <el-header class="header">
        <div class="header-content">
          <div class="logo">
            <el-icon><Box /></el-icon>
            <span>Forge</span>
          </div>
          <el-menu mode="horizontal" :default-active="activeMenu" router>
            <el-menu-item index="/public">首页</el-menu-item>
            <el-menu-item index="/login">登录</el-menu-item>
          </el-menu>
        </div>
      </el-header>
      <el-main class="main">
        <router-view />
      </el-main>
      <el-footer class="footer">
        <p>&copy; 2025 Forge 软件发布管理平台. All rights reserved.</p>
      </el-footer>
    </el-container>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const activeMenu = computed(() => route.path)
</script>

<style scoped>
.public-layout {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.header {
  background: #fff;
  border-bottom: 1px solid #e4e7ed;
  padding: 0;
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 100%;
  padding: 0 20px;
}

.logo {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 24px;
  font-weight: bold;
  color: #409eff;
}

.main {
  flex: 1;
  background: #f5f7fa;
  overflow-y: auto;
}

.footer {
  background: #fff;
  border-top: 1px solid #e4e7ed;
  text-align: center;
  color: #909399;
  padding: 20px;
}
</style>
