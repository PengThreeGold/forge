import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import App from './App.vue'
import router from './router'
import './assets/nprogress-custom.css'
import './assets/element-performance.css'

const app = createApp(App)

// 注册所有图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

// 使用插件
app.use(createPinia())
app.use(router)
app.use(ElementPlus, {
  // 优化配置
  size: 'default',
  zIndex: 3000
})

// 全局错误处理
app.config.errorHandler = (err, instance, info) => {
  console.error('Global error:', err, info)
}

app.mount('#app')
