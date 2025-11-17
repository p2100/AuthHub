/**
 * 轻量级认证客户端 (示例本地版本)
 * 实际项目中应该从 @authhub/sdk 导入
 */

import { useState, useEffect, useCallback } from 'react';
import axios from 'axios';

export interface User {
  sub: string;
  username: string;
  email?: string;
  global_roles?: string[];
  system_roles?: Record<string, string[]>;
}

export interface UseAuthOptions {
  backendUrl: string;
  loginPath?: string;
  logoutPath?: string;
  mePath?: string;
}

export interface UseAuthResult {
  user: User | null;
  loading: boolean;
  isAuthenticated: boolean;
  login: (returnUrl?: string) => void;
  logout: () => Promise<void>;
  refresh: () => Promise<void>;
}

class AuthClient {
  private config: Required<UseAuthOptions>;

  constructor(config: UseAuthOptions) {
    this.config = {
      backendUrl: config.backendUrl.replace(/\/$/, ''),
      loginPath: config.loginPath || '/auth/login',
      logoutPath: config.logoutPath || '/auth/logout',
      mePath: config.mePath || '/api/me',
    };
  }

  login(returnUrl?: string): void {
    const url = new URL(this.config.loginPath, this.config.backendUrl);
    if (returnUrl) {
      // 将相对路径转换为完整的前端 URL
      const fullReturnUrl = returnUrl.startsWith('http')
        ? returnUrl
        : window.location.origin + returnUrl;
      // 后端期望的参数名是 'redirect' 而不是 'return_url'
      url.searchParams.set('redirect', fullReturnUrl);
    }
    window.location.href = url.toString();
  }

  async logout(): Promise<void> {
    try {
      await axios.post(
        `${this.config.backendUrl}${this.config.logoutPath}`,
        {},
        { withCredentials: true }
      );
    } catch (error) {
      console.error('Logout failed:', error);
    }
  }

  async getCurrentUser(): Promise<User | null> {
    try {
      const response = await axios.get(
        `${this.config.backendUrl}${this.config.mePath}`,
        { withCredentials: true }
      );
      return response.data;
    } catch (error: any) {
      if (error.response?.status === 401) {
        return null;
      }
      console.error('Get current user failed:', error);
      return null;
    }
  }
}

export function useAuth(options: UseAuthOptions): UseAuthResult {
  const [client] = useState(() => new AuthClient(options));
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(async () => {
    try {
      const currentUser = await client.getCurrentUser();
      setUser(currentUser);
    } catch (error) {
      console.error('Failed to refresh user:', error);
      setUser(null);
    }
  }, [client]);

  useEffect(() => {
    const init = async () => {
      setLoading(true);
      await refresh();
      setLoading(false);
    };
    init();
  }, [refresh]);

  const login = useCallback(
    (returnUrl?: string) => {
      client.login(returnUrl || window.location.pathname);
    },
    [client]
  );

  const logout = useCallback(async () => {
    await client.logout();
    setUser(null);
  }, [client]);

  return {
    user,
    loading,
    isAuthenticated: user !== null,
    login,
    logout,
    refresh,
  };
}

