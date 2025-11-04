import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import './assets/css/global.css'
import './assets/css/variables.scss'

// 创建Vue应用实例
const app = createApp(App)

// 注册Element Plus图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

// 使用插件
app.use(store)
app.use(router)
app.use(ElementPlus, {
  size: 'default',
  zIndex: 3000,
})

// 初始化应用
store
  .dispatch('initApp')
  .then(() => {
    // 挂载应用
    app.mount('#app')
  })
  .catch(error => {
    console.error('应用初始化失败:', error)
    app.mount('#app')
  })
