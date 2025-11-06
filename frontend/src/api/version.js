import request from "./index";

export default {
  // 获取版本列表
  getVersions(params = {}) {
    return request({
      url: "/api/versions",
      method: "get",
      params,
    });
  },

  // 根据空间ID获取版本列表
  getVersionsBySpace(spaceId, params = {}) {
    return request({
      url: `/api/spaces/${spaceId}/versions`,
      method: "get",
      params,
    });
  },

  // 根据ID获取版本详情
  getVersionById(versionId) {
    return request({
      url: `/api/versions/${versionId}`,
      method: "get",
    });
  },

  // 创建版本
  createVersion(data) {
    return request({
      url: "/api/versions",
      method: "post",
      data,
    });
  },

  // 更新版本
  updateVersion(versionId, data) {
    return request({
      url: `/api/versions/${versionId}`,
      method: "put",
      data,
    });
  },

  // 删除版本
  deleteVersion(versionId) {
    return request({
      url: `/api/versions/${versionId}`,
      method: "delete",
    });
  },

  // 发布版本
  publishVersion(versionId) {
    return request({
      url: `/api/versions/${versionId}/publish`,
      method: "post",
    });
  },

  // 取消发布版本
  unpublishVersion(versionId) {
    return request({
      url: `/api/versions/${versionId}/unpublish`,
      method: "post",
    });
  },

  // 获取版本的架构文件
  getArchitectureFiles(versionId) {
    return request({
      url: `/api/versions/${versionId}/files`,
      method: "get",
    });
  },

  // 上传架构文件
  uploadArchitectureFile(versionId, formData) {
    return request({
      url: `/api/versions/${versionId}/files`,
      method: "post",
      data: formData,
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });
  },

  // 删除架构文件
  deleteArchitectureFile(fileId) {
    return request({
      url: `/api/files/${fileId}`,
      method: "delete",
    });
  },

  // 下载文件
  downloadFile(fileId) {
    return request({
      url: `/api/files/${fileId}/download`,
      method: "get",
      responseType: "blob",
    });
  },

  // 获取公共下载链接
  getPublicDownloadUrl(spaceId, version) {
    return `${request.defaults.baseURL}/api/public/download/${spaceId}/${version}`;
  },
};
