/**
 * ProtectedRoute Component
 * 
 * 路由保护组件
 */

import React from 'react';
import { useSSO } from '../hooks/useSSO';

export interface ProtectedRouteProps {
  authhubUrl: string;
  redirectUri?: string;
  fallback?: React.ReactNode;
  unauthorizedComponent?: React.ReactNode;
  children: React.ReactNode;
}

/**
 * 受保护的路由组件
 * 
 * 未登录用户会被重定向到登录页
 * 
 * @example
 * ```tsx
 * <ProtectedRoute authhubUrl="http://localhost:8000">
 *   <Dashboard />
 * </ProtectedRoute>
 * ```
 */
export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
  authhubUrl,
  redirectUri,
  fallback,
  unauthorizedComponent,
  children,
}) => {
  const { isAuthenticated, isLoading, login } = useSSO({
    authhubUrl,
    redirectUri,
  });

  // 加载中
  if (isLoading) {
    if (fallback) {
      return <>{fallback}</>;
    }

    return (
      <div
        style={{
          minHeight: '100vh',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        <div
          style={{
            width: '48px',
            height: '48px',
            border: '4px solid #f0f0f0',
            borderTop: '4px solid #1890ff',
            borderRadius: '50%',
            animation: 'spin 1s linear infinite',
          }}
        />
        <style>
          {`
            @keyframes spin {
              0% { transform: rotate(0deg); }
              100% { transform: rotate(360deg); }
            }
          `}
        </style>
      </div>
    );
  }

  // 未登录
  if (!isAuthenticated) {
    if (unauthorizedComponent) {
      return <>{unauthorizedComponent}</>;
    }

    // 自动触发登录
    React.useEffect(() => {
      login();
    }, [login]);

    return (
      <div
        style={{
          minHeight: '100vh',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
        }}
      >
        <div style={{ textAlign: 'center' }}>
          <p style={{ fontSize: '16px', color: '#666', marginBottom: '16px' }}>
            需要登录才能访问
          </p>
          <p style={{ fontSize: '14px', color: '#999' }}>正在跳转到登录页...</p>
        </div>
      </div>
    );
  }

  // 已登录，显示内容
  return <>{children}</>;
};

