/**
 * React 认证 Hook (轻量版)
 */

import { useState, useEffect, useCallback } from 'react';
import { AuthClient } from '../auth-client';
import type { User } from '../types';

export interface UseAuthOptions {
  backendUrl: string;
  loginPath?: string;
  logoutPath?: string;
  mePath?: string;
  onLogout?: () => void;
}

export interface UseAuthResult {
  user: User | null;
  loading: boolean;
  isAuthenticated: boolean;
  login: (returnUrl?: string) => void;
  logout: () => Promise<void>;
  refresh: () => Promise<void>;
}

/**
 * 认证 Hook
 * 
 * @example
 * ```tsx
 * function App() {
 *   const { user, loading, isAuthenticated, login, logout } = useAuth({
 *     backendUrl: 'http://localhost:8001'
 *   });
 * 
 *   if (loading) return <div>Loading...</div>;
 *   
 *   if (!isAuthenticated) {
 *     return <button onClick={() => login()}>登录</button>;
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
    options.onLogout?.();
  }, [client, options]);

  return {
    user,
    loading,
    isAuthenticated: user !== null,
    login,
    logout,
    refresh,
  };
}
