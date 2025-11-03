<template>
  <div class="not-found-container">
    <div class="not-found-content">
      <div class="error-code">404</div>
      <div class="error-message">抱歉，您访问的页面不存在</div>
      <div class="error-description">
        您可能输入了错误的URL，或者页面已被移动或删除。
      </div>
      <div class="actions">
        <el-button type="primary" @click="goHome">返回首页</el-button>
        <el-button @click="goBack">返回上一页</el-button>
      </div>
    </div>
  </div>
</template>

<script>
import { defineComponent } from 'vue'
import { useRouter } from 'vue-router'

export default defineComponent({
  name: 'NotFound',
  setup() {
    const router = useRouter()
    
    // 返回首页
    const goHome = () => {
      router.push('/')
    }
    
    // 返回上一页
    const goBack = () => {
      router.go(-1)
    }
    
    return {
      goHome,
      goBack
    }
  }
})
</script>

<style scoped>
.not-found-container {
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f5f7fa;
}

.not-found-content {
  text-align: center;
  padding: 40px;
}

.error-code {
  font-size: 120px;
  font-weight: bold;
  color: #409EFF;
  line-height: 1;
  margin-bottom: 20px;
}

.error-message {
  font-size: 24px;
  color: #303133;
  margin-bottom: 16px;
  font-weight: 500;
}

.error-description {
  font-size: 16px;
  color: #606266;
  margin-bottom: 32px;
  max-width: 500px;
  margin-left: auto;
  margin-right: auto;
}

.actions {
  display: flex;
  justify-content: center;
  gap: 16px;
}

.dark-theme .not-found-container {
  background-color: #1f2937;
}

.dark-theme .error-code {
  color: #79bbff;
}

.dark-theme .error-message {
  color: #e5eaf3;
}

.dark-theme .error-description {
  color: #a8abb2;
}

@media (max-width: 768px) {
  .error-code {
    font-size: 80px;
  }
  
  .error-message {
    font-size: 20px;
  }
  
  .error-description {
    font-size: 14px;
  }
  
  .actions {
    flex-direction: column;
    align-items: center;
  }
}
</style>