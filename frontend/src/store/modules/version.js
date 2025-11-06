import api from "@/api";

const state = {
  versions: [],
  currentVersion: null,
  total: 0,
  loading: false,
  // 按空间ID分组的版本
  versionsBySpace: {},
  // 架构文件映射
  architectureFiles: {},
};

const getters = {
  versions: (state) => state.versions,
  currentVersion: (state) => state.currentVersion,
  total: (state) => state.total,
  loading: (state) => state.loading,
  // 获取指定空间的版本
  versionsBySpace: (state) => (spaceId) => state.versionsBySpace[spaceId] || [],
  // 获取已发布的版本
  publishedVersions: (state) =>
    state.versions.filter((version) => version.is_published),
  // 获取未发布的版本
  unpublishedVersions: (state) =>
    state.versions.filter((version) => !version.is_published),
  // 获取已完成的版本
  completedVersions: (state) =>
    state.versions.filter((version) => version.is_ready),
  // 获取未完成的版本
  incompleteVersions: (state) =>
    state.versions.filter((version) => !version.is_ready),
  // 获取版本的架构文件
  architectureFiles: (state) => (versionId) =>
    state.architectureFiles[versionId] || [],
};

const mutations = {
  SET_VERSIONS(state, versions) {
    state.versions = versions;
  },
  SET_CURRENT_VERSION(state, version) {
    state.currentVersion = version;
  },
  SET_TOTAL(state, total) {
    state.total = total;
  },
  SET_LOADING(state, loading) {
    state.loading = loading;
  },
  SET_VERSIONS_BY_SPACE(state, { spaceId, versions }) {
    state.versionsBySpace = {
      ...state.versionsBySpace,
      [spaceId]: versions,
    };
  },
  SET_ARCHITECTURE_FILES(state, { versionId, files }) {
    state.architectureFiles = {
      ...state.architectureFiles,
      [versionId]: files,
    };
  },
  ADD_VERSION(state, version) {
    state.versions.unshift(version);

    // 更新按空间分组的版本
    const spaceId = version.space_id;
    if (state.versionsBySpace[spaceId]) {
      state.versionsBySpace[spaceId].unshift(version);
    } else {
      state.versionsBySpace[spaceId] = [version];
    }

    state.total += 1;
  },
  UPDATE_VERSION(state, updatedVersion) {
    const index = state.versions.findIndex(
      (version) => version.id === updatedVersion.id
    );
    if (index !== -1) {
      state.versions.splice(index, 1, updatedVersion);
    }

    if (state.currentVersion && state.currentVersion.id === updatedVersion.id) {
      state.currentVersion = updatedVersion;
    }

    // 更新按空间分组的版本
    const spaceId = updatedVersion.space_id;
    if (state.versionsBySpace[spaceId]) {
      const spaceVersionIndex = state.versionsBySpace[spaceId].findIndex(
        (version) => version.id === updatedVersion.id
      );
      if (spaceVersionIndex !== -1) {
        state.versionsBySpace[spaceId].splice(
          spaceVersionIndex,
          1,
          updatedVersion
        );
      }
    }
  },
  DELETE_VERSION(state, versionId) {
    const index = state.versions.findIndex(
      (version) => version.id === versionId
    );
    let spaceId = null;

    if (index !== -1) {
      spaceId = state.versions[index].space_id;
      state.versions.splice(index, 1);
      state.total -= 1;
    }

    if (state.currentVersion && state.currentVersion.id === versionId) {
      state.currentVersion = null;
    }

    // 更新按空间分组的版本
    if (spaceId && state.versionsBySpace[spaceId]) {
      const spaceVersionIndex = state.versionsBySpace[spaceId].findIndex(
        (version) => version.id === versionId
      );
      if (spaceVersionIndex !== -1) {
        state.versionsBySpace[spaceId].splice(spaceVersionIndex, 1);
      }
    }

    // 删除版本的架构文件
    delete state.architectureFiles[versionId];
  },
  ADD_ARCHITECTURE_FILE(state, { versionId, file }) {
    if (!state.architectureFiles[versionId]) {
      state.architectureFiles[versionId] = [];
    }
    state.architectureFiles[versionId].push(file);

    // 更新当前版本的架构文件列表
    if (state.currentVersion && state.currentVersion.id === versionId) {
      state.currentVersion.architecture_files = [
        ...state.architectureFiles[versionId],
      ];
    }
  },
  DELETE_ARCHITECTURE_FILE(state, { versionId, fileId }) {
    if (state.architectureFiles[versionId]) {
      const index = state.architectureFiles[versionId].findIndex(
        (file) => file.id === fileId
      );
      if (index !== -1) {
        state.architectureFiles[versionId].splice(index, 1);
      }
    }

    // 更新当前版本的架构文件列表
    if (state.currentVersion && state.currentVersion.id === versionId) {
      state.currentVersion.architecture_files =
        state.architectureFiles[versionId] || [];
    }
  },
};

const actions = {
  // 获取版本列表
  async fetchVersions({ commit }, params = {}) {
    commit("SET_LOADING", true);
    try {
      const response = await api.version.getVersions(params);
      commit("SET_VERSIONS", response.data.items || []);
      commit("SET_TOTAL", response.data.total || 0);
      return { success: true, data: response.data };
    } catch (error) {
      return {
        success: false,
        message: error.response?.data?.detail || "获取版本列表失败",
      };
    } finally {
      commit("SET_LOADING", false);
    }
  },

  // 根据空间ID获取版本列表
  async fetchVersionsBySpace({ commit }, { spaceId, params = {} }) {
    commit("SET_LOADING", true);
    try {
      const response = await api.version.getVersionsBySpace(spaceId, params);
      const versions = response.data.items || [];
      commit("SET_VERSIONS_BY_SPACE", { spaceId, versions });
      return { success: true, data: response.data };
    } catch (error) {
      return {
        success: false,
        message: error.response?.data?.detail || "获取版本列表失败",
      };
    } finally {
      commit("SET_LOADING", false);
    }
  },

  // 根据ID获取版本详情
  async fetchVersionById({ commit }, versionId) {
    commit("SET_LOADING", true);
    try {
      const response = await api.version.getVersionById(versionId);
      commit("SET_CURRENT_VERSION", response.data);
      return { success: true, data: response.data };
    } catch (error) {
      return {
        success: false,
        message: error.response?.data?.detail || "获取版本详情失败",
      };
    } finally {
      commit("SET_LOADING", false);
    }
  },

  // 创建版本
  async createVersion({ commit }, versionData) {
    try {
      const response = await api.version.createVersion(versionData);
      commit("ADD_VERSION", response.data);
      return { success: true, data: response.data };
    } catch (error) {
      return {
        success: false,
        message: error.response?.data?.detail || "创建版本失败",
      };
    }
  },

  // 更新版本
  async updateVersion({ commit }, { versionId, versionData }) {
    try {
      const response = await api.version.updateVersion(versionId, versionData);
      commit("UPDATE_VERSION", response.data);
      return { success: true, data: response.data };
    } catch (error) {
      return {
        success: false,
        message: error.response?.data?.detail || "更新版本失败",
      };
    }
  },

  // 删除版本
  async deleteVersion({ commit }, versionId) {
    try {
      await api.version.deleteVersion(versionId);
      commit("DELETE_VERSION", versionId);
      return { success: true };
    } catch (error) {
      return {
        success: false,
        message: error.response?.data?.detail || "删除版本失败",
      };
    }
  },

  // 发布版本
  async publishVersion({ commit }, versionId) {
    try {
      const response = await api.version.publishVersion(versionId);
      commit("UPDATE_VERSION", response.data);
      return { success: true, data: response.data };
    } catch (error) {
      return {
        success: false,
        message: error.response?.data?.detail || "发布版本失败",
      };
    }
  },

  // 取消发布版本
  async unpublishVersion({ commit }, versionId) {
    try {
      const response = await api.version.unpublishVersion(versionId);
      commit("UPDATE_VERSION", response.data);
      return { success: true, data: response.data };
    } catch (error) {
      return {
        success: false,
        message: error.response?.data?.detail || "取消发布版本失败",
      };
    }
  },

  // 获取版本的架构文件
  async fetchArchitectureFiles({ commit }, versionId) {
    try {
      const response = await api.version.getArchitectureFiles(versionId);
      commit("SET_ARCHITECTURE_FILES", { versionId, files: response.data });
      return { success: true, data: response.data };
    } catch (error) {
      return {
        success: false,
        message: error.response?.data?.detail || "获取架构文件失败",
      };
    }
  },

  // 上传架构文件
  async uploadArchitectureFile({ commit }, { versionId, formData }) {
    try {
      const response = await api.version.uploadArchitectureFile(
        versionId,
        formData
      );
      commit("ADD_ARCHITECTURE_FILE", { versionId, file: response.data });
      return { success: true, data: response.data };
    } catch (error) {
      return {
        success: false,
        message: error.response?.data?.detail || "上传文件失败",
      };
    }
  },

  // 删除架构文件
  async deleteArchitectureFile({ commit }, { versionId, fileId }) {
    try {
      await api.version.deleteArchitectureFile(fileId);
      commit("DELETE_ARCHITECTURE_FILE", { versionId, fileId });
      return { success: true };
    } catch (error) {
      return {
        success: false,
        message: error.response?.data?.detail || "删除文件失败",
      };
    }
  },

  // 重置版本状态
  resetVersionState({ commit }) {
    commit("SET_VERSIONS", []);
    commit("SET_CURRENT_VERSION", null);
    commit("SET_TOTAL", 0);
    commit("SET_LOADING", false);
    commit("SET_VERSIONS_BY_SPACE", {});
    commit("SET_ARCHITECTURE_FILES", {});
  },
};

export default {
  namespaced: true,
  state,
  getters,
  mutations,
  actions,
};
