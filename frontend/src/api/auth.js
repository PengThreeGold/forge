import request from "./index";

export default {
  // 用户登录
  login(data) {
    return request({
      url: "/api/auth/login",
      method: "post",
      data,
    });
  },

  // 刷新访问令牌
  refresh(data) {
    return request({
      url: "/api/auth/refresh",
      method: "post",
      data,
    });
  },

  // 获取当前用户信息
  getProfile() {
    return request({
      url: "/api/auth/profile",
      method: "get",
    });
  },

  // 修改密码
  changePassword(data) {
    return request({
      url: "/api/auth/admin/password",
      method: "put",
      data,
    });
  },
};
