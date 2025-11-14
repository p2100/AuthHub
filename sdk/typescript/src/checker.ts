/**
 * 权限检查器
 */

import type { TokenPayload, PermissionConfig } from './types';

export class PermissionChecker {
  constructor(private namespace: string) {}

  /**
   * 检查权限
   */
  checkPermission(
    tokenPayload: TokenPayload,
    resource: string,
    action: string,
    config: PermissionConfig
  ): boolean {
    // 1. 全局管理员
    if (tokenPayload.global_roles.includes('admin')) {
      return true;
    }

    // 2. 构建权限代码
    const permCode = `${resource}:${action}`;

    // 3. 检查系统角色
    const userRoles = tokenPayload.system_roles[this.namespace] || [];

    for (const roleName of userRoles) {
      const roleConfig = config.roles[roleName];
      if (!roleConfig) continue;

      const rolePermissions = roleConfig.permissions;

      // 检查精确匹配
      if (rolePermissions.includes(permCode)) {
        return true;
      }

      // 检查通配符
      if (rolePermissions.includes(`${resource}:*`) || rolePermissions.includes('*:*')) {
        return true;
      }
    }

    return false;
  }

  /**
   * 检查路由权限
   */
  checkRoute(
    tokenPayload: TokenPayload,
    path: string,
    method: string,
    config: PermissionConfig
  ): boolean {
    // 全局管理员
    if (tokenPayload.global_roles.includes('admin')) {
      return true;
    }

    // 获取用户的系统角色
    const userRoles = tokenPayload.system_roles[this.namespace] || [];

    // 遍历路由规则(按优先级排序)
    const sortedPatterns = [...config.route_patterns].sort(
      (a, b) => b.priority - a.priority
    );

    for (const patternRule of sortedPatterns) {
      // 检查角色
      if (!userRoles.includes(patternRule.role)) {
        continue;
      }

      // 检查方法
      if (patternRule.method !== '*' && patternRule.method !== method) {
        continue;
      }

      // 正则匹配路径
      const regex = new RegExp(patternRule.pattern);
      if (regex.test(path)) {
        return true;
      }
    }

    return false;
  }

  /**
   * 检查资源访问权限
   */
  checkResourceAccess(
    tokenPayload: TokenPayload,
    resourceType: string,
    resourceId: number
  ): boolean {
    // 检查全局资源
    const globalResources = tokenPayload.global_resources[resourceType] || [];
    if (globalResources.includes(resourceId)) {
      return true;
    }

    // 检查系统资源
    const namespaceResources = tokenPayload.system_resources[this.namespace] || {};
    const resources = namespaceResources[resourceType] || [];
    if (resources.includes(resourceId)) {
      return true;
    }

    return false;
  }
}

