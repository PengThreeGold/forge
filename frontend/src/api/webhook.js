import request from "./index";

export default {
  // 获取Webhook配置
  getWebhookConfig(spaceId) {
    return request({
      url: `/api/spaces/${spaceId}/webhook`,
      method: "get",
    });
  },

  // 更新Webhook配置
  updateWebhookConfig(spaceId, data) {
    return request({
      url: `/api/spaces/${spaceId}/webhook`,
      method: "put",
      data,
    });
  },

  // 删除Webhook配置
  deleteWebhookConfig(spaceId) {
    return request({
      url: `/api/spaces/${spaceId}/webhook`,
      method: "delete",
    });
  },

  // 获取Webhook日志
  getWebhookLogs(params = {}) {
    return request({
      url: "/api/admin/webhook/logs",
      method: "get",
      params,
    });
  },

  // 测试Webhook
  testWebhook(spaceId, data) {
    return request({
      url: `/api/spaces/${spaceId}/webhook/test`,
      method: "post",
      data,
    });
  },
};
