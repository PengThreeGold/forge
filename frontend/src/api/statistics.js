import request from "./index";

export default {
  // 获取系统统计
  getSystemStats() {
    return request({
      url: "/api/admin/stats/system",
      method: "get",
    });
  },

  // 获取软件空间统计
  getSpaceStats(params = {}) {
    return request({
      url: "/api/admin/stats/spaces",
      method: "get",
      params,
    });
  },

  // 获取每日下载统计
  getDailyDownloadStats(params = {}) {
    return request({
      url: "/api/admin/stats/downloads/daily",
      method: "get",
      params,
    });
  },

  // 获取版本下载统计
  getVersionDownloadStats(params = {}) {
    return request({
      url: "/api/admin/stats/downloads/versions",
      method: "get",
      params,
    });
  },
};
