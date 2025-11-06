import request from "./index";

export default {
  // 获取软件空间列表
  getSpaces(params = {}) {
    return request({
      url: "/api/spaces",
      method: "get",
      params,
    });
  },

  // 根据ID获取软件空间详情
  getSpaceById(spaceId) {
    return request({
      url: `/api/spaces/${spaceId}`,
      method: "get",
    });
  },

  // 创建软件空间
  createSpace(data) {
    return request({
      url: "/api/spaces",
      method: "post",
      data,
    });
  },

  // 更新软件空间
  updateSpace(spaceId, data) {
    return request({
      url: `/api/spaces/${spaceId}`,
      method: "put",
      data,
    });
  },

  // 删除软件空间
  deleteSpace(spaceId) {
    return request({
      url: `/api/spaces/${spaceId}`,
      method: "delete",
    });
  },

  // 更新软件空间状态
  updateSpaceStatus(spaceId, status) {
    return request({
      url: `/api/spaces/${spaceId}/status`,
      method: "put",
      data: { status },
    });
  },
};
