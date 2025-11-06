import request from "./index";

export default {
  // 获取用户列表
  getUsers(params = {}) {
    return request({
      url: "/api/admin/users",
      method: "get",
      params,
    });
  },

  // 根据ID获取用户详情
  getUserById(userId) {
    return request({
      url: `/api/admin/users/${userId}`,
      method: "get",
    });
  },

  // 创建用户
  createUser(data) {
    return request({
      url: "/api/admin/users",
      method: "post",
      data,
    });
  },

  // 更新用户
  updateUser(userId, data) {
    return request({
      url: `/api/admin/users/${userId}`,
      method: "put",
      data,
    });
  },

  // 删除用户
  deleteUser(userId) {
    return request({
      url: `/api/admin/users/${userId}`,
      method: "delete",
    });
  },
};
