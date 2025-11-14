/**
 * useRole Hook
 */

import { useAuth } from './useAuth';

// 全局客户端实例
let globalClient: any = null;

export function initClient(client: any) {
  globalClient = client;
}

export function useRole(role: string): boolean {
  const { user, isAuthenticated } = useAuth();

  if (!isAuthenticated || !user || !globalClient) {
    return false;
  }

  // 检查全局角色或系统角色
  if (role.includes(':')) {
    const [namespace, roleName] = role.split(':', 2);
    if (namespace === 'global') {
      return globalClient.hasGlobalRole(user, roleName);
    }
  }

  return globalClient.hasSystemRole(user, role);
}

