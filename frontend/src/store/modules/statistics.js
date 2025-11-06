import api from "@/api";

const state = {
  systemStats: null,
  spaceStats: [],
  dailyDownloadStats: [],
  versionDownloadStats: [],
  loading: false,
};

const getters = {
  systemStats: (state) => state.systemStats,
  spaceStats: (state) => state.spaceStats,
  dailyDownloadStats: (state) => state.dailyDownloadStats,
  versionDownloadStats: (state) => state.versionDownloadStats,
  loading: (state) => state.loading,
  // 获取最近7天的下载统计
  recentDownloadStats: (state) => {
    if (!state.dailyDownloadStats.length) return [];
    return state.dailyDownloadStats.slice(-7);
  },
  // 获取下载量最高的前5个空间
  topDownloadedSpaces: (state) => {
    if (!state.spaceStats.length) return [];
    return [...state.spaceStats]
      .sort((a, b) => b.total_downloads - a.total_downloads)
      .slice(0, 5);
  },
};

const mutations = {
  SET_SYSTEM_STATS(state, stats) {
    state.systemStats = stats;
  },
  SET_SPACE_STATS(state, stats) {
    state.spaceStats = stats;
  },
  SET_DAILY_DOWNLOAD_STATS(state, stats) {
    state.dailyDownloadStats = stats;
  },
  SET_VERSION_DOWNLOAD_STATS(state, stats) {
    state.versionDownloadStats = stats;
  },
  SET_LOADING(state, loading) {
    state.loading = loading;
  },
};

const actions = {
  // 获取系统统计
  async fetchSystemStats({ commit }) {
    commit("SET_LOADING", true);
    try {
      const response = await api.statistics.getSystemStats();
      commit("SET_SYSTEM_STATS", response.data);
      return { success: true, data: response.data };
    } catch (error) {
      return {
        success: false,
        message: error.response?.data?.detail || "获取系统统计失败",
      };
    } finally {
      commit("SET_LOADING", false);
    }
  },

  // 获取软件空间统计
  async fetchSpaceStats({ commit }, params = {}) {
    commit("SET_LOADING", true);
    try {
      const response = await api.statistics.getSpaceStats(params);
      commit("SET_SPACE_STATS", response.data);
      return { success: true, data: response.data };
    } catch (error) {
      return {
        success: false,
        message: error.response?.data?.detail || "获取软件空间统计失败",
      };
    } finally {
      commit("SET_LOADING", false);
    }
  },

  // 获取每日下载统计
  async fetchDailyDownloadStats({ commit }, params = {}) {
    commit("SET_LOADING", true);
    try {
      const response = await api.statistics.getDailyDownloadStats(params);
      commit("SET_DAILY_DOWNLOAD_STATS", response.data);
      return { success: true, data: response.data };
    } catch (error) {
      return {
        success: false,
        message: error.response?.data?.detail || "获取每日下载统计失败",
      };
    } finally {
      commit("SET_LOADING", false);
    }
  },

  // 获取版本下载统计
  async fetchVersionDownloadStats({ commit }, params = {}) {
    commit("SET_LOADING", true);
    try {
      const response = await api.statistics.getVersionDownloadStats(params);
      commit("SET_VERSION_DOWNLOAD_STATS", response.data);
      return { success: true, data: response.data };
    } catch (error) {
      return {
        success: false,
        message: error.response?.data?.detail || "获取版本下载统计失败",
      };
    } finally {
      commit("SET_LOADING", false);
    }
  },

  // 获取所有统计数据
  async fetchAllStatistics({ dispatch }) {
    const systemStats = await dispatch("fetchSystemStats");
    if (!systemStats.success) return systemStats;

    const spaceStats = await dispatch("fetchSpaceStats");
    if (!spaceStats.success) return spaceStats;

    const dailyStats = await dispatch("fetchDailyDownloadStats");
    if (!dailyStats.success) return dailyStats;

    return { success: true, message: "所有统计数据获取成功" };
  },

  // 重置统计数据
  resetStatisticsState({ commit }) {
    commit("SET_SYSTEM_STATS", null);
    commit("SET_SPACE_STATS", []);
    commit("SET_DAILY_DOWNLOAD_STATS", []);
    commit("SET_VERSION_DOWNLOAD_STATS", []);
    commit("SET_LOADING", false);
  },
};

export default {
  namespaced: true,
  state,
  getters,
  mutations,
  actions,
};
