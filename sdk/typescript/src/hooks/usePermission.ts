/**
 * usePermission Hook
 */

import { useAuth } from './useAuth';

// 全局客户端实例
let globalClient: any = null;

export function initClient(client: any) {
  globalClient = client;
}

export function usePermission(resource: string, action: string): boolean {
  const { user, isAuthenticated } = useAuth();

  if (!isAuthenticated || !user || !globalClient) {
    return false;
  }

  return globalClient.checkPermission(user, resource, action);
}

