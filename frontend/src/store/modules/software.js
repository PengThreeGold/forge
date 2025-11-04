import * as softwareApi from '@/api/software'

const state = {
  spaces: [],
  currentSpace: null,
  versions: [],
  currentVersion: null,
  loading: false,
  error: null,
}

const getters = {
  spaces: state => state.spaces,
  currentSpace: state => state.currentSpace,
  versions: state => state.versions,
  currentVersion: state => state.currentVersion,
  loading: state => state.loading,
  error: state => state.error,

  // 根据ID获取软件空间
  spaceById: state => id => state.spaces.find(space => space.id === id),

  // 根据ID获取软件版本
  versionById: state => id => state.versions.find(version => version.id === id),

  // 获取当前空间的最新版本
  latestVersion: state => {
    if (!state.versions.length) return null
    return state.versions.reduce((latest, version) => {
      return new Date(version.created_at) > new Date(latest.created_at) ? version : latest
    })
  },

  // 获取已发布的版本
  publishedVersions: state => state.versions.filter(version => version.is_published),
}

const mutations = {
  SET_SPACES(state, spaces) {
    state.spaces = spaces
  },

  ADD_SPACE(state, space) {
    state.spaces.unshift(space)
  },

  UPDATE_SPACE(state, updatedSpace) {
    const index = state.spaces.findIndex(space => space.id === updatedSpace.id)
    if (index !== -1) {
      state.spaces.splice(index, 1, updatedSpace)
    }
  },

  DELETE_SPACE(state, spaceId) {
    state.spaces = state.spaces.filter(space => space.id !== spaceId)
  },

  SET_CURRENT_SPACE(state, space) {
    state.currentSpace = space
  },

  SET_VERSIONS(state, versions) {
    state.versions = versions
  },

  ADD_VERSION(state, version) {
    state.versions.unshift(version)
  },

  UPDATE_VERSION(state, updatedVersion) {
    const index = state.versions.findIndex(version => version.id === updatedVersion.id)
    if (index !== -1) {
      state.versions.splice(index, 1, updatedVersion)
    }
  },

  DELETE_VERSION(state, versionId) {
    state.versions = state.versions.filter(version => version.id !== versionId)
  },

  SET_CURRENT_VERSION(state, version) {
    state.currentVersion = version
  },

  SET_LOADING(state, loading) {
    state.loading = loading
  },

  SET_ERROR(state, error) {
    state.error = error
  },

  CLEAR_ERROR(state) {
    state.error = null
  },

  CLEAR_STATE(state) {
    state.spaces = []
    state.currentSpace = null
    state.versions = []
    state.currentVersion = null
    state.error = null
  },
}

const actions = {
  // 获取所有软件空间
  async getSpaces({ commit }) {
    try {
      commit('SET_LOADING', true)
      commit('CLEAR_ERROR')

      const response = await softwareApi.getSpaces()
      commit('SET_SPACES', response.data)

      commit('SET_LOADING', false)
      return response
    } catch (error) {
      commit('SET_LOADING', false)
      commit('SET_ERROR', error.response?.data?.message || '获取软件空间列表失败')
      throw error
    }
  },

  // 创建软件空间
  async createSpace({ commit }, spaceData) {
    try {
      commit('SET_LOADING', true)
      commit('CLEAR_ERROR')

      const response = await softwareApi.createSpace(spaceData)
      commit('ADD_SPACE', response.data)

      commit('SET_LOADING', false)
      return response
    } catch (error) {
      commit('SET_LOADING', false)
      commit('SET_ERROR', error.response?.data?.message || '创建软件空间失败')
      throw error
    }
  },

  // 获取软件空间详情
  async getSpace({ commit }, spaceId) {
    try {
      commit('SET_LOADING', true)
      commit('CLEAR_ERROR')

      const response = await softwareApi.getSpace(spaceId)
      commit('SET_CURRENT_SPACE', response.data)

      commit('SET_LOADING', false)
      return response
    } catch (error) {
      commit('SET_LOADING', false)
      commit('SET_ERROR', error.response?.data?.message || '获取软件空间详情失败')
      throw error
    }
  },

  // 更新软件空间
  async updateSpace({ commit }, { spaceId, spaceData }) {
    try {
      commit('SET_LOADING', true)
      commit('CLEAR_ERROR')

      const response = await softwareApi.updateSpace(spaceId, spaceData)
      commit('UPDATE_SPACE', response.data)

      // 如果当前空间是更新后的空间，也更新当前空间
      if (state.currentSpace && state.currentSpace.id === response.data.id) {
        commit('SET_CURRENT_SPACE', response.data)
      }

      commit('SET_LOADING', false)
      return response
    } catch (error) {
      commit('SET_LOADING', false)
      commit('SET_ERROR', error.response?.data?.message || '更新软件空间失败')
      throw error
    }
  },

  // 删除软件空间
  async deleteSpace({ commit }, spaceId) {
    try {
      commit('SET_LOADING', true)
      commit('CLEAR_ERROR')

      await softwareApi.deleteSpace(spaceId)
      commit('DELETE_SPACE', spaceId)

      // 如果删除的是当前空间，清空当前空间
      if (state.currentSpace && state.currentSpace.id === spaceId) {
        commit('SET_CURRENT_SPACE', null)
      }

      commit('SET_LOADING', false)
      return { success: true }
    } catch (error) {
      commit('SET_LOADING', false)
      commit('SET_ERROR', error.response?.data?.message || '删除软件空间失败')
      throw error
    }
  },

  // 重新生成API密钥
  async regenerateApiKey({ commit }, spaceId) {
    try {
      commit('SET_LOADING', true)
      commit('CLEAR_ERROR')

      const response = await softwareApi.regenerateApiKey(spaceId)

      // 更新软件空间信息
      const space = state.spaces.find(s => s.id === spaceId)
      if (space) {
        const updatedSpace = { ...space, api_key: response.data.api_key }
        commit('UPDATE_SPACE', updatedSpace)

        if (state.currentSpace && state.currentSpace.id === spaceId) {
          commit('SET_CURRENT_SPACE', updatedSpace)
        }
      }

      commit('SET_LOADING', false)
      return response
    } catch (error) {
      commit('SET_LOADING', false)
      commit('SET_ERROR', error.response?.data?.message || '重新生成API密钥失败')
      throw error
    }
  },

  // 获取软件版本列表
  async getVersions({ commit }, spaceId) {
    try {
      commit('SET_LOADING', true)
      commit('CLEAR_ERROR')

      const response = await softwareApi.getVersions(spaceId)
      commit('SET_VERSIONS', response.data)

      commit('SET_LOADING', false)
      return response
    } catch (error) {
      commit('SET_LOADING', false)
      commit('SET_ERROR', error.response?.data?.message || '获取软件版本列表失败')
      throw error
    }
  },

  // 创建软件版本
  async createVersion({ commit }, { spaceId, versionData }) {
    try {
      commit('SET_LOADING', true)
      commit('CLEAR_ERROR')

      // 创建FormData用于文件上传
      const formData = new FormData()
      formData.append('file', versionData.file)
      formData.append('version', versionData.version)

      if (versionData.release_note) {
        formData.append('release_note', versionData.release_note)
      }

      if (versionData.documentation_url) {
        formData.append('documentation_url', versionData.documentation_url)
      }

      const response = await softwareApi.createVersion(spaceId, formData)
      commit('ADD_VERSION', response.data)

      commit('SET_LOADING', false)
      return response
    } catch (error) {
      commit('SET_LOADING', false)
      commit('SET_ERROR', error.response?.data?.message || '创建软件版本失败')
      throw error
    }
  },

  // 获取软件版本详情
  async getVersion({ commit }, versionId) {
    try {
      commit('SET_LOADING', true)
      commit('CLEAR_ERROR')

      const response = await softwareApi.getVersion(versionId)
      commit('SET_CURRENT_VERSION', response.data)

      commit('SET_LOADING', false)
      return response
    } catch (error) {
      commit('SET_LOADING', false)
      commit('SET_ERROR', error.response?.data?.message || '获取软件版本详情失败')
      throw error
    }
  },

  // 更新软件版本
  async updateVersion({ commit }, { versionId, versionData }) {
    try {
      commit('SET_LOADING', true)
      commit('CLEAR_ERROR')

      const response = await softwareApi.updateVersion(versionId, versionData)
      commit('UPDATE_VERSION', response.data)

      // 如果当前版本是更新后的版本，也更新当前版本
      if (state.currentVersion && state.currentVersion.id === response.data.id) {
        commit('SET_CURRENT_VERSION', response.data)
      }

      commit('SET_LOADING', false)
      return response
    } catch (error) {
      commit('SET_LOADING', false)
      commit('SET_ERROR', error.response?.data?.message || '更新软件版本失败')
      throw error
    }
  },

  // 删除软件版本
  async deleteVersion({ commit }, versionId) {
    try {
      commit('SET_LOADING', true)
      commit('CLEAR_ERROR')

      await softwareApi.deleteVersion(versionId)
      commit('DELETE_VERSION', versionId)

      // 如果删除的是当前版本，清空当前版本
      if (state.currentVersion && state.currentVersion.id === versionId) {
        commit('SET_CURRENT_VERSION', null)
      }

      commit('SET_LOADING', false)
      return { success: true }
    } catch (error) {
      commit('SET_LOADING', false)
      commit('SET_ERROR', error.response?.data?.message || '删除软件版本失败')
      throw error
    }
  },

  // 发布/下架软件版本
  async publishVersion({ commit }, { versionId, publish }) {
    try {
      commit('SET_LOADING', true)
      commit('CLEAR_ERROR')

      const response = await softwareApi.publishVersion(versionId, { publish })
      commit('UPDATE_VERSION', response.data)

      // 如果当前版本是更新后的版本，也更新当前版本
      if (state.currentVersion && state.currentVersion.id === response.data.id) {
        commit('SET_CURRENT_VERSION', response.data)
      }

      commit('SET_LOADING', false)
      return response
    } catch (error) {
      commit('SET_LOADING', false)
      commit(
        'SET_ERROR',
        error.response?.data?.message || (publish ? '发布软件版本失败' : '下架软件版本失败')
      )
      throw error
    }
  },

  // 下载软件版本
  async downloadVersion({ commit }, versionId) {
    try {
      commit('SET_LOADING', true)
      commit('CLEAR_ERROR')

      const response = await softwareApi.downloadVersion(versionId)

      commit('SET_LOADING', false)
      return response
    } catch (error) {
      commit('SET_LOADING', false)
      commit('SET_ERROR', error.response?.data?.message || '下载软件版本失败')
      throw error
    }
  },

  // 清空状态
  clearState({ commit }) {
    commit('CLEAR_STATE')
  },
}

export default {
  namespaced: true,
  state,
  getters,
  mutations,
  actions,
}
