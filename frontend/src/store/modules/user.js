import api from "@/api";

const state = {
  users: [],
  currentUser: null,
  total: 0,
  loading: false,
};

const getters = {
  users: (state) => state.users,
  currentUser: (state) => state.currentUser,
  total: (state) => state.total,
  loading: (state) => state.loading,
};

const mutations = {
  SET_USERS(state, users) {
    state.users = users;
  },
  SET_CURRENT_USER(state, user) {
    state.currentUser = user;
  },
  SET_TOTAL(state, total) {
    state.total = total;
  },
  SET_LOADING(state, loading) {
    state.loading = loading;
  },
  ADD_USER(state, user) {
    state.users.unshift(user);
    state.total += 1;
  },
  UPDATE_USER(state, updatedUser) {
    const index = state.users.findIndex((user) => user.id === updatedUser.id);
    if (index !== -1) {
      state.users.splice(index, 1, updatedUser);
    }
    if (state.currentUser && state.currentUser.id === updatedUser.id) {
      state.currentUser = updatedUser;
    }
  },
  DELETE_USER(state, userId) {
    const index = state.users.findIndex((user) => user.id === userId);
    if (index !== -1) {
      state.users.splice(index, 1);
      state.total -= 1;
    }
  },
};

const actions = {
  // 获取用户列表
  async fetchUsers({ commit }, params = {}) {
    commit("SET_LOADING", true);
    try {
      const response = await api.user.getUsers(params);
      commit("SET_USERS", response.data.items || []);
      commit("SET_TOTAL", response.data.total || 0);
      return { success: true, data: response.data };
    } catch (error) {
      return {
        success: false,
        message: error.response?.data?.detail || "获取用户列表失败",
      };
    } finally {
      commit("SET_LOADING", false);
    }
  },

  // 根据ID获取用户详情
  async fetchUserById({ commit }, userId) {
    commit("SET_LOADING", true);
    try {
      const response = await api.user.getUserById(userId);
      commit("SET_CURRENT_USER", response.data);
      return { success: true, data: response.data };
    } catch (error) {
      return {
        success: false,
        message: error.response?.data?.detail || "获取用户详情失败",
      };
    } finally {
      commit("SET_LOADING", false);
    }
  },

  // 创建用户
  async createUser({ commit }, userData) {
    try {
      const response = await api.user.createUser(userData);
      commit("ADD_USER", response.data);
      return { success: true, data: response.data };
    } catch (error) {
      return {
        success: false,
        message: error.response?.data?.detail || "创建用户失败",
      };
    }
  },

  // 更新用户
  async updateUser({ commit }, { userId, userData }) {
    try {
      const response = await api.user.updateUser(userId, userData);
      commit("UPDATE_USER", response.data);
      return { success: true, data: response.data };
    } catch (error) {
      return {
        success: false,
        message: error.response?.data?.detail || "更新用户失败",
      };
    }
  },

  // 删除用户
  async deleteUser({ commit }, userId) {
    try {
      await api.user.deleteUser(userId);
      commit("DELETE_USER", userId);
      return { success: true };
    } catch (error) {
      return {
        success: false,
        message: error.response?.data?.detail || "删除用户失败",
      };
    }
  },

  // 重置用户状态
  resetUserState({ commit }) {
    commit("SET_USERS", []);
    commit("SET_CURRENT_USER", null);
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
