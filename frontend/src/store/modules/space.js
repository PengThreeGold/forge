import api from "@/api";

const state = {
  spaces: [],
  currentSpace: null,
  total: 0,
  loading: false,
};

const getters = {
  spaces: (state) => state.spaces,
  currentSpace: (state) => state.currentSpace,
  total: (state) => state.total,
  loading: (state) => state.loading,
  // 获取活跃的空间
  activeSpaces: (state) =>
    state.spaces.filter((space) => space.status === "active"),
  // 获取空间ID映射
  spaceMap: (state) => {
    const map = {};
    state.spaces.forEach((space) => {
      map[space.space_id] = space;
    });
    return map;
  },
};

const mutations = {
  SET_SPACES(state, spaces) {
    state.spaces = spaces;
  },
  SET_CURRENT_SPACE(state, space) {
    state.currentSpace = space;
  },
  SET_TOTAL(state, total) {
    state.total = total;
  },
  SET_LOADING(state, loading) {
    state.loading = loading;
  },
  ADD_SPACE(state, space) {
    state.spaces.unshift(space);
    state.total += 1;
  },
  UPDATE_SPACE(state, updatedSpace) {
    const index = state.spaces.findIndex(
      (space) => space.space_id === updatedSpace.space_id
    );
    if (index !== -1) {
      state.spaces.splice(index, 1, updatedSpace);
    }
    if (
      state.currentSpace &&
      state.currentSpace.space_id === updatedSpace.space_id
    ) {
      state.currentSpace = updatedSpace;
    }
  },
  DELETE_SPACE(state, spaceId) {
    const index = state.spaces.findIndex((space) => space.space_id === spaceId);
    if (index !== -1) {
      state.spaces.splice(index, 1);
      state.total -= 1;
    }
    if (state.currentSpace && state.currentSpace.space_id === spaceId) {
      state.currentSpace = null;
    }
  },
  UPDATE_SPACE_STATUS(state, { spaceId, status }) {
    const index = state.spaces.findIndex((space) => space.space_id === spaceId);
    if (index !== -1) {
      state.spaces[index].status = status;
    }
    if (state.currentSpace && state.currentSpace.space_id === spaceId) {
      state.currentSpace.status = status;
    }
  },
};

const actions = {
  // 获取软件空间列表
  async fetchSpaces({ commit }, params = {}) {
    commit("SET_LOADING", true);
    try {
      const response = await api.space.getSpaces(params);
      commit("SET_SPACES", response.data.items || []);
      commit("SET_TOTAL", response.data.total || 0);
      return { success: true, data: response.data };
    } catch (error) {
      return {
        success: false,
        message: error.response?.data?.detail || "获取软件空间列表失败",
      };
    } finally {
      commit("SET_LOADING", false);
    }
  },

  // 根据ID获取软件空间详情
  async fetchSpaceById({ commit }, spaceId) {
    commit("SET_LOADING", true);
    try {
      const response = await api.space.getSpaceById(spaceId);
      commit("SET_CURRENT_SPACE", response.data);
      return { success: true, data: response.data };
    } catch (error) {
      return {
        success: false,
        message: error.response?.data?.detail || "获取软件空间详情失败",
      };
    } finally {
      commit("SET_LOADING", false);
    }
  },

  // 创建软件空间
  async createSpace({ commit }, spaceData) {
    try {
      const response = await api.space.createSpace(spaceData);
      commit("ADD_SPACE", response.data);
      return { success: true, data: response.data };
    } catch (error) {
      return {
        success: false,
        message: error.response?.data?.detail || "创建软件空间失败",
      };
    }
  },

  // 更新软件空间
  async updateSpace({ commit }, { spaceId, spaceData }) {
    try {
      const response = await api.space.updateSpace(spaceId, spaceData);
      commit("UPDATE_SPACE", response.data);
      return { success: true, data: response.data };
    } catch (error) {
      return {
        success: false,
        message: error.response?.data?.detail || "更新软件空间失败",
      };
    }
  },

  // 删除软件空间
  async deleteSpace({ commit }, spaceId) {
    try {
      await api.space.deleteSpace(spaceId);
      commit("DELETE_SPACE", spaceId);
      return { success: true };
    } catch (error) {
      return {
        success: false,
        message: error.response?.data?.detail || "删除软件空间失败",
      };
    }
  },

  // 更新软件空间状态
  async updateSpaceStatus({ commit }, { spaceId, status }) {
    try {
      await api.space.updateSpaceStatus(spaceId, status);
      commit("UPDATE_SPACE_STATUS", { spaceId, status });
      return { success: true };
    } catch (error) {
      return {
        success: false,
        message: error.response?.data?.detail || "更新软件空间状态失败",
      };
    }
  },

  // 重置软件空间状态
  resetSpaceState({ commit }) {
    commit("SET_SPACES", []);
    commit("SET_CURRENT_SPACE", null);
    commit("SET_TOTAL", 0);
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
