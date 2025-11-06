import { createStore } from "vuex";
import auth from "./modules/auth";
import user from "./modules/user";
import space from "./modules/space";
import version from "./modules/version";
import statistics from "./modules/statistics";

export default createStore({
  state: {
    // 侧边栏折叠状态
    sidebarCollapsed: false,
    // 主题设置
    theme: "light",
    // 全局加载状态
    loading: false,
  },
  getters: {
    sidebarCollapsed: (state) => state.sidebarCollapsed,
    theme: (state) => state.theme,
    loading: (state) => state.loading,
  },
  mutations: {
    TOGGLE_SIDEBAR(state) {
      state.sidebarCollapsed = !state.sidebarCollapsed;
    },
    SET_THEME(state, theme) {
      state.theme = theme;
      // 保存到本地存储
      localStorage.setItem("theme", theme);
    },
    SET_LOADING(state, loading) {
      state.loading = loading;
    },
  },
  actions: {
    toggleSidebar({ commit }) {
      commit("TOGGLE_SIDEBAR");
    },
    setTheme({ commit }, theme) {
      commit("SET_THEME", theme);
    },
    setLoading({ commit }, loading) {
      commit("SET_LOADING", loading);
    },
    // 初始化应用设置
    initSettings({ commit }) {
      // 从本地存储恢复主题设置
      const savedTheme = localStorage.getItem("theme");
      if (savedTheme) {
        commit("SET_THEME", savedTheme);
      }
    },
  },
  modules: {
    auth,
    user,
    space,
    version,
    statistics,
  },
});
