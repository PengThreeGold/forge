/**
 * 判断是否为外部链接
 * @param {string} path
 * @returns {Boolean}
 */
export function isExternal(path) {
  return /^(https?:|mailto:|tel:)/.test(path);
}

/**
 * 验证用户名
 * @param {string} username
 * @returns {Boolean}
 */
export function validUsername(username) {
  const valid_map = ["admin", "editor"];
  return valid_map.indexOf(username.trim()) >= 0;
}

/**
 * 验证密码
 * @param {string} password
 * @returns {Boolean}
 */
export function validPassword(password) {
  return password.length >= 6;
}

/**
 * 验证邮箱
 * @param {string} email
 * @returns {Boolean}
 */
export function validEmail(email) {
  const re =
    /^(([^<>()\\[\]\\.,;:\s@"]+(\.[^<>()\\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
  return re.test(email);
}

/**
 * 验证URL
 * @param {string} url
 * @returns {Boolean}
 */
export function validURL(url) {
  const re =
    /^(https?:\/\/)([0-9a-z.]+)(:[0-9]+)?([/0-9a-z.]+)?(\?[0-9a-z&=]+)?(#[0-9-a-z]+)?/i;
  return re.test(url);
}

/**
 * 验证版本号
 * @param {string} version
 * @returns {Boolean}
 */
export function validVersion(version) {
  // 语义化版本号正则表达式，如 1.0.0, 1.0.0-beta, 1.0.0-beta.1
  const re =
    /^(\d+)\.(\d+)\.(\d+)(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$/;
  return re.test(version);
}
