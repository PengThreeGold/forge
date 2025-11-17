import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  {
    path: '/',
    redirect: '/public'
  },
  {
    path: '/public',
    component: () => import('@/layouts/PublicLayout.vue'),
    children: [
      {
        path: '',
        name: 'PublicHome',
        component: () => import('@/views/public/Home.vue')
      },
      {
        path: 'spaces/:id',
        name: 'PublicSpace',
        component: () => import('@/views/public/SpaceDetail.vue')
      }
    ]
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/auth/Login.vue')
  },
  {
    path: '/admin',
    component: () => import('@/layouts/AdminLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        redirect: '/admin/spaces'
      },
      {
        path: 'spaces',
        name: 'AdminSpaces',
        component: () => import('@/views/admin/Spaces.vue')
      },
      {
        path: 'spaces/:id',
        name: 'AdminSpaceDetail',
        component: () => import('@/views/admin/SpaceDetail.vue')
      },
      {
        path: 'users',
        name: 'AdminUsers',
        component: () => import('@/views/admin/Users.vue'),
        meta: { requiresAdmin: true }
      },
      {
        path: 'stats',
        name: 'AdminStats',
        component: () => import('@/views/admin/Stats.vue')
      },
      {
        path: 'profile',
        name: 'AdminProfile',
        component: () => import('@/views/admin/Profile.vue')
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  
  // 确保在检查权限前已获取用户信息
  if (authStore.isAuthenticated && !authStore.user) {
    try {
      await authStore.fetchProfile()
      // 获取用户信息后重新检查权限
      checkAuthAndRedirect(to, next, authStore)
    } catch (error) {
      // 获取用户信息失败，跳转到登录页
      next({ name: 'Login' })
    }
  } else {
    checkAuthAndRedirect(to, next, authStore)
  }
})

function checkAuthAndRedirect(to, next, authStore) {
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next({ name: 'Login', query: { redirect: to.fullPath } })
  } else if (to.meta.requiresAdmin && authStore.user?.role !== 'admin') {
    ElMessage.error('权限不足，需要管理员权限')
    next({ name: 'AdminSpaces' })
  } else {
    next()
  }
}

export default router
