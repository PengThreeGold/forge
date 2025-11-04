import { createRouter, createWebHistory } from 'vue-router'
import store from '../store'

// 路由组件懒加载
const Login = () => import('../views/Login.vue')
const Dashboard = () => import('../views/Dashboard.vue')
const SoftwareList = () => import('../views/SoftwareList.vue')
const SoftwareDetail = () => import('../views/SoftwareDetail.vue')
const SoftwareEdit = () => import('../views/SoftwareEdit.vue')
const SoftwareRelease = () => import('../views/SoftwareRelease.vue')
const Statistics = () => import('../views/Statistics.vue')
const Settings = () => import('../views/Settings.vue')
const PermissionManagement = () => import('../views/PermissionManagement.vue')
const PublicSoftware = () => import('../views/PublicSoftware.vue')
const PublicSoftwareDetail = () => import('../views/PublicSoftwareDetail.vue')
const NotFound = () => import('../views/NotFound.vue')

// 路由配置
const routes = [
  {
    path: '/',
    redirect: '/public',
  },
  {
    path: '/public',
    name: 'PublicSoftware',
    component: PublicSoftware,
    meta: { title: '软件商店' },
  },
  {
    path: '/public/:id',
    name: 'PublicSoftwareDetail',
    component: PublicSoftwareDetail,
    meta: { title: '软件详情' },
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { title: '登录' },
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: Dashboard,
    meta: { requiresAuth: true, title: '仪表盘' },
  },
  {
    path: '/software',
    name: 'SoftwareList',
    component: SoftwareList,
    meta: { requiresAuth: true, title: '软件空间' },
  },
  {
    path: '/software/create',
    name: 'SoftwareCreate',
    component: SoftwareEdit,
    meta: { requiresAuth: true, title: '创建软件空间' },
  },
  {
    path: '/software/:id',
    name: 'SoftwareDetail',
    component: SoftwareDetail,
    meta: { requiresAuth: true, title: '软件详情' },
  },
  {
    path: '/software/:id/edit',
    name: 'SoftwareEdit',
    component: SoftwareEdit,
    meta: { requiresAuth: true, title: '编辑软件空间' },
  },
  {
    path: '/software/:id/releases',
    name: 'SoftwareRelease',
    component: SoftwareRelease,
    meta: { requiresAuth: true, title: '版本发布' },
  },
  {
    path: '/statistics',
    name: 'Statistics',
    component: Statistics,
    meta: { requiresAuth: true, title: '统计分析' },
  },
  {
    path: '/settings',
    name: 'Settings',
    component: Settings,
    meta: { requiresAuth: true, title: '系统设置' },
  },
  {
    path: '/permissions',
    name: 'PermissionManagement',
    component: PermissionManagement,
    meta: { requiresAuth: true, title: '权限管理' },
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: NotFound,
    meta: { title: '页面不存在' },
  },
]

// 创建路由实例
const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes,
})

// 全局路由守卫
router.beforeEach((to, from, next) => {
  // 设置页面标题
  if (to.meta.title) {
    document.title = `${to.meta.title} - Forge`
  }

  // 检查是否需要认证
  if (to.matched.some(record => record.meta.requiresAuth)) {
    // 检查用户是否已登录
    if (!store.getters.isAuthenticated) {
      // 如果未登录，重定向到登录页
      next({
        path: '/login',
        query: { redirect: to.fullPath },
      })
    } else {
      // 已登录，继续导航
      next()
    }
  } else {
    // 不需要认证的路由，直接放行
    next()
  }
})

// 路由后置钩子
router.afterEach(() => {
  // 滚动到顶部
  window.scrollTo(0, 0)
})

export default router
