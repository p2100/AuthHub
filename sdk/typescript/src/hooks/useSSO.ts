/**
 * React SSO Hook
 * 
 * 提供SSO登录状态管理和操作方法
 */

import { useState, useEffect, useCallback } from 'react';
import { SSOClient } from '../sso';
import { TokenManager } from '../tokenManager';
import type { TokenPayload } from '../types';

export interface UseSSOOptions {
  authhubUrl: string;
  redirectUri?: string;
  onLoginSuccess?: (user: TokenPayload) => void;
  onLogout?: () => void;
}

export interface UseSSOResult {
  isAuthenticated: boolean;
  user: TokenPayload | null;
  isLoading: boolean;
  login: () => Promise<void>;
  logout: () => void;
  refresh: () => void;
}

/**
 * SSO Hook
 * 
 * @example
 * ```tsx
 * function App() {
 *   const { isAuthenticated, user, login, logout } = useSSO({
 *     authhubUrl: 'http://localhost:8000'
 *   });
 * 
 *   if (!isAuthenticated) {
 *     return <button onClick={login}>登录</button>;
 *   }
 * 
 *   return (
 *     <div>
 *       <p>欢迎, {user?.username}</p>
 *       <button onClick={logout}>登出</button>
 *     </div>
 *   );
 * }
 * ```
 */
export function useSSO(options: UseSSOOptions): UseSSOResult {
  const { authhubUrl, redirectUri, onLoginSuccess, onLogout } = options;

  const [ssoClient] = useState(() => new SSOClient(authhubUrl));
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState<TokenPayload | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  /**
   * 刷新认证状态
   */
  const refresh = useCallback(() => {
    const authenticated = ssoClient.isAuthenticated();
    setIsAuthenticated(authenticated);

    if (authenticated) {
      const currentUser = ssoClient.getCurrentUser();
      setUser(currentUser);
    } else {
      setUser(null);
    }
  }, [ssoClient]);

  /**
   * 初始化认证状态
   */
  useEffect(() => {
    setIsLoading(true);
    refresh();
    setIsLoading(false);
  }, [refresh]);

  /**
   * 监听storage事件(支持多标签页同步)
   */
  useEffect(() => {
    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === 'authhub_token' || e.key === 'authhub_token_payload') {
        refresh();
      }
    };

    window.addEventListener('storage', handleStorageChange);
    return () => window.removeEventListener('storage', handleStorageChange);
  }, [refresh]);

  /**
   * 登录
   */
  const login = useCallback(async () => {
    try {
      await ssoClient.login(redirectUri);
    } catch (error) {
      console.error('登录失败:', error);
      throw error;
    }
  }, [ssoClient, redirectUri]);

  /**
   * 登出
   */
  const logout = useCallback(() => {
    ssoClient.logout();
    setIsAuthenticated(false);
    setUser(null);
    onLogout?.();
  }, [ssoClient, onLogout]);

  return {
    isAuthenticated,
    user,
    isLoading,
    login,
    logout,
    refresh,
  };
}

