import axios from "axios";
import store from "@/store";
import router from "@/router";
import { ElMessage } from "element-plus";

// 创建axios实例
const request = axios.create({
  baseURL: process.env.VUE_APP_API_BASE_URL || "http://localhost:1110",
  timeout: 30000,
  headers: {
    "Content-Type": "application/json",
  },
});

// 请求拦截器
request.interceptors.request.use(
  (config) => {
    // 添加认证token
    const token = store.getters["auth/token"];
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    // 显示加载状态
    store.dispatch("setLoading", true);

    return config;
  },
  (error) => {
    store.dispatch("setLoading", false);
    return Promise.reject(error);
  }
);

// 响应拦截器
request.interceptors.response.use(
  (response) => {
    store.dispatch("setLoading", false);
    return response;
  },
  async (error) => {
    store.dispatch("setLoading", false);

    const { status, data } = error.response || {};

    // 处理401未授权错误
    if (status === 401) {
      // 尝试刷新token
      const refreshToken = store.getters["auth/refreshToken"];
      if (refreshToken && !error.config._retry) {
        error.config._retry = true;
        try {
          const newToken = await store.dispatch("auth/refreshToken");
          // 重试原始请求
          error.config.headers.Authorization = `Bearer ${newToken}`;
          return request(error.config);
        } catch (refreshError) {
          // 刷新失败，跳转到登录页
          store.dispatch("auth/logout");
          router.push("/login");
          ElMessage.error("登录已过期，请重新登录");
          return Promise.reject(refreshError);
        }
      } else {
        // 没有刷新token或已重试过，直接跳转登录页
        store.dispatch("auth/logout");
        router.push("/login");
        ElMessage.error("登录已过期，请重新登录");
      }
    }
    // 处理403禁止访问错误
    else if (status === 403) {
      ElMessage.error("权限不足，无法访问该资源");
    }
    // 处理404资源不存在错误
    else if (status === 404) {
      ElMessage.error("请求的资源不存在");
    }
    // 处理500服务器错误
    else if (status >= 500) {
      ElMessage.error("服务器错误，请稍后再试");
    }
    // 处理其他错误
    else if (data && data.detail) {
      ElMessage.error(data.detail);
    } else {
      ElMessage.error("请求失败，请稍后再试");
    }

    return Promise.reject(error);
  }
);

// 导出各个API模块
import auth from "./auth";
import user from "./user";
import space from "./space";
import version from "./version";
import statistics from "./statistics";
import webhook from "./webhook";

export default {
  request,
  auth,
  user,
  space,
  version,
  statistics,
  webhook,
};
