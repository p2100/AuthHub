/**
 * useAuth Hook
 */

import { useState, useEffect } from 'react';
import type { TokenPayload } from '../types';

// 全局客户端实例(需要在应用初始化时设置)
let globalClient: any = null;

export function initClient(client: any) {
  globalClient = client;
}

export function useAuth() {
  const [user, setUser] = useState<TokenPayload | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const loadUser = async () => {
      try {
        // 从localStorage获取token
        const token = localStorage.getItem('authhub_token');
        if (token && globalClient) {
          const userInfo = await globalClient.verifyToken(token);
          setUser(userInfo);
        }
      } catch (error) {
        console.error('验证Token失败:', error);
        localStorage.removeItem('authhub_token');
      } finally {
        setIsLoading(false);
      }
    };

    loadUser();
  }, []);

  const login = (token: string) => {
    localStorage.setItem('authhub_token', token);
    if (globalClient) {
      globalClient.verifyToken(token).then(setUser);
    }
  };

  const logout = () => {
    localStorage.removeItem('authhub_token');
    setUser(null);
  };

  return {
    user,
    isAuthenticated: !!user,
    isLoading,
    login,
    logout,
  };
}

