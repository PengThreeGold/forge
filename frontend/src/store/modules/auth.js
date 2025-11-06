import api from "@/api";

const state = {
  token: localStorage.getItem("token") || "",
  refreshToken: localStorage.getItem("refreshToken") || "",
  userInfo: JSON.parse(localStorage.getItem("userInfo") || "null"),
};

const getters = {
  token: (state) => state.token,
  refreshToken: (state) => state.refreshToken,
  userInfo: (state) => state.userInfo,
  isAuthenticated: (state) => !!state.token,
};

const mutations = {
  SET_TOKEN(state, token) {
    state.token = token;
    localStorage.setItem("token", token);
  },
  SET_REFRESH_TOKEN(state, refreshToken) {
    state.refreshToken = refreshToken;
    localStorage.setItem("refreshToken", refreshToken);
  },
  SET_USER_INFO(state, userInfo) {
    state.userInfo = userInfo;
    localStorage.setItem("userInfo", JSON.stringify(userInfo));
  },
  CLEAR_AUTH(state) {
    state.token = "";
    state.refreshToken = "";
    state.userInfo = null;
    localStorage.removeItem("token");
    localStorage.removeItem("refreshToken");
    localStorage.removeItem("userInfo");
  },
};

const actions = {
  // 登录
  async login({ commit }, credentials) {
    try {
      const response = await api.auth.login(credentials);
      const { access_token, refresh_token, user } = response.data;

      commit("SET_TOKEN", access_token);
      commit("SET_REFRESH_TOKEN", refresh_token);
      commit("SET_USER_INFO", user);

      return { success: true, data: response.data };
    } catch (error) {
      return {
        success: false,
        message: error.response?.data?.detail || "登录失败，请检查用户名和密码",
      };
    }
  },

  // 刷新令牌
  async refreshToken({ commit, state }) {
    if (!state.refreshToken) {
      throw new Error("没有刷新令牌");
    }

    try {
      const response = await api.auth.refresh({
        refresh_token: state.refreshToken,
      });
      const { access_token, refresh_token } = response.data;

      commit("SET_TOKEN", access_token);
      if (refresh_token) {
        commit("SET_REFRESH_TOKEN", refresh_token);
      }

      return access_token;
    } catch (error) {
      // 刷新失败，清除认证信息
      commit("CLEAR_AUTH");
      throw error;
    }
  },

  // 获取用户信息
  async getUserInfo({ commit, state }) {
    if (!state.token) {
      throw new Error("未登录");
    }

    try {
      const response = await api.auth.getProfile();
      const user = response.data;

      commit("SET_USER_INFO", user);
      return user;
    } catch (error) {
      // 获取用户信息失败，可能是令牌过期
      commit("CLEAR_AUTH");
      throw error;
    }
  },

  // 登出
  logout({ commit }) {
    commit("CLEAR_AUTH");
    // 跳转到登录页
    window.location.href = "/login";
  },

  // 修改密码
  async changePassword(context, passwordData) {
    try {
      const response = await api.auth.changePassword(passwordData);
      return { success: true, data: response.data };
    } catch (error) {
      return {
        success: false,
        message: error.response?.data?.detail || "修改密码失败",
      };
    }
  },
};

export default {
  namespaced: true,
  state,
  getters,
  mutations,
  actions,
};
