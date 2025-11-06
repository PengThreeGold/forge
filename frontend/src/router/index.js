import { createRouter, createWebHistory } from "vue-router";
import store from "@/store";

// 路由懒加载
const Login = () => import("@/views/Login.vue");
const Layout = () => import("@/layout/index.vue");
const Dashboard = () => import("@/views/Dashboard.vue");
const SpaceList = () => import("@/views/space/SpaceList.vue");
const SpaceCreate = () => import("@/views/space/SpaceCreate.vue");
const SpaceEdit = () => import("@/views/space/SpaceEdit.vue");
const VersionList = () => import("@/views/version/VersionList.vue");
const VersionCreate = () => import("@/views/version/VersionCreate.vue");
const VersionEdit = () => import("@/views/version/VersionEdit.vue");
const UserList = () => import("@/views/user/UserList.vue");
const UserCreate = () => import("@/views/user/UserCreate.vue");
const UserEdit = () => import("@/views/user/UserEdit.vue");
const Statistics = () => import("@/views/statistics/Statistics.vue");
const WebhookList = () => import("@/views/webhook/WebhookList.vue");
const WebhookEdit = () => import("@/views/webhook/WebhookEdit.vue");
const Profile = () => import("@/views/Profile.vue");
const PublicDownload = () => import("@/views/PublicDownload.vue");

const routes = [
  {
    path: "/login",
    name: "Login",
    component: Login,
    meta: {
      title: "登录",
      requiresAuth: false,
    },
  },
  {
    path: "/",
    component: Layout,
    redirect: "/dashboard",
    meta: { requiresAuth: true },
    children: [
      {
        path: "dashboard",
        name: "Dashboard",
        component: Dashboard,
        meta: {
          title: "仪表板",
          icon: "DataBoard",
          requiresAuth: true,
        },
      },
    ],
  },
  {
    path: "/space",
    component: Layout,
    redirect: "/space/list",
    meta: { requiresAuth: true },
    children: [
      {
        path: "list",
        name: "SpaceList",
        component: SpaceList,
        meta: {
          title: "软件空间",
          icon: "FolderOpened",
          requiresAuth: true,
        },
      },
      {
        path: "create",
        name: "SpaceCreate",
        component: SpaceCreate,
        meta: {
          title: "创建软件空间",
          requiresAuth: true,
        },
      },
      {
        path: "edit/:id",
        name: "SpaceEdit",
        component: SpaceEdit,
        meta: {
          title: "编辑软件空间",
          requiresAuth: true,
        },
      },
    ],
  },
  {
    path: "/version",
    component: Layout,
    redirect: "/version/list",
    meta: { requiresAuth: true },
    children: [
      {
        path: "list",
        name: "VersionList",
        component: VersionList,
        meta: {
          title: "软件版本",
          icon: "Document",
          requiresAuth: true,
        },
      },
      {
        path: "create",
        name: "VersionCreate",
        component: VersionCreate,
        meta: {
          title: "创建版本",
          requiresAuth: true,
        },
      },
      {
        path: "edit/:id",
        name: "VersionEdit",
        component: VersionEdit,
        meta: {
          title: "编辑版本",
          requiresAuth: true,
        },
      },
    ],
  },
  {
    path: "/user",
    component: Layout,
    redirect: "/user/list",
    meta: { requiresAuth: true },
    children: [
      {
        path: "list",
        name: "UserList",
        component: UserList,
        meta: {
          title: "用户管理",
          icon: "User",
          requiresAuth: true,
          roles: ["admin"],
        },
      },
      {
        path: "create",
        name: "UserCreate",
        component: UserCreate,
        meta: {
          title: "创建用户",
          requiresAuth: true,
          roles: ["admin"],
        },
      },
      {
        path: "edit/:id",
        name: "UserEdit",
        component: UserEdit,
        meta: {
          title: "编辑用户",
          requiresAuth: true,
          roles: ["admin"],
        },
      },
    ],
  },
  {
    path: "/statistics",
    component: Layout,
    redirect: "/statistics/overview",
    meta: { requiresAuth: true },
    children: [
      {
        path: "overview",
        name: "Statistics",
        component: Statistics,
        meta: {
          title: "统计分析",
          icon: "TrendCharts",
          requiresAuth: true,
        },
      },
    ],
  },
  {
    path: "/webhook",
    component: Layout,
    redirect: "/webhook/list",
    meta: { requiresAuth: true },
    children: [
      {
        path: "list",
        name: "WebhookList",
        component: WebhookList,
        meta: {
          title: "Webhook管理",
          icon: "Link",
          requiresAuth: true,
        },
      },
      {
        path: "edit/:id",
        name: "WebhookEdit",
        component: WebhookEdit,
        meta: {
          title: "编辑Webhook",
          requiresAuth: true,
        },
      },
    ],
  },
  {
    path: "/profile",
    component: Layout,
    meta: { requiresAuth: true },
    children: [
      {
        path: "",
        name: "Profile",
        component: Profile,
        meta: {
          title: "个人资料",
          requiresAuth: true,
        },
      },
    ],
  },
  {
    path: "/download/:spaceId/:version",
    name: "PublicDownload",
    component: PublicDownload,
    meta: {
      title: "软件下载",
      requiresAuth: false,
    },
  },
  // 404页面
  {
    path: "/:pathMatch(.*)*",
    redirect: "/dashboard",
  },
];

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes,
});

// 路由守卫
router.beforeEach((to, from, next) => {
  // 设置页面标题
  document.title = to.meta.title
    ? `${to.meta.title} - Forge`
    : "Forge 软件发布管理平台";

  // 检查是否需要认证
  if (to.meta.requiresAuth) {
    const token = store.getters.token;

    if (!token) {
      // 未登录，重定向到登录页
      next({
        path: "/login",
        query: { redirect: to.fullPath },
      });
      return;
    }

    // 检查用户角色权限
    if (to.meta.roles && to.meta.roles.length > 0) {
      const userRole = store.getters.userInfo?.role;
      if (!to.meta.roles.includes(userRole)) {
        // 权限不足，重定向到仪表板
        next("/dashboard");
        return;
      }
    }
  }

  next();
});

export default router;
