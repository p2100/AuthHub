/**
 * SSOCallback Component
 * 
 * 自动处理SSO回调
 */

import React, { useEffect, useState } from 'react';
import { SSOClient } from '../sso';

export interface SSOCallbackProps {
  authhubUrl: string;
  onSuccess?: (token: string) => void;
  onError?: (error: Error) => void;
  redirectTo?: string;
  loadingComponent?: React.ReactNode;
  errorComponent?: (error: Error) => React.ReactNode;
}

/**
 * SSO回调组件
 * 
 * 放置在回调路由页面，自动处理code交换
 * 
 * @example
 * ```tsx
 * // /auth/callback 页面
 * function CallbackPage() {
 *   return (
 *     <SSOCallback
 *       authhubUrl="http://localhost:8000"
 *       redirectTo="/dashboard"
 *       onSuccess={() => console.log('登录成功')}
 *     />
 *   );
 * }
 * ```
 */
export const SSOCallback: React.FC<SSOCallbackProps> = ({
  authhubUrl,
  onSuccess,
  onError,
  redirectTo = '/',
  loadingComponent,
  errorComponent,
}) => {
  const [error, setError] = useState<Error | null>(null);
  const [isProcessing, setIsProcessing] = useState(true);

  useEffect(() => {
    const handleCallback = async () => {
      try {
        // 从URL获取code和state
        const urlParams = new URLSearchParams(window.location.search);
        const code = urlParams.get('code');
        const state = urlParams.get('state');

        if (!code) {
          throw new Error('缺少授权码');
        }

        // 创建SSO客户端
        const ssoClient = new SSOClient(authhubUrl);

        // 交换Token
        const token = await ssoClient.handleCallback(code, state || undefined);

        // 回调成功处理
        onSuccess?.(token);

        // 获取返回URL
        const returnUrl = sessionStorage.getItem('authhub_return_url') || redirectTo;
        sessionStorage.removeItem('authhub_return_url');

        // 延迟跳转，让用户看到成功提示
        setTimeout(() => {
          window.location.href = returnUrl;
        }, 500);
      } catch (err) {
        const error = err instanceof Error ? err : new Error('登录失败');
        setError(error);
        setIsProcessing(false);
        onError?.(error);
      }
    };

    handleCallback();
  }, [authhubUrl, onSuccess, onError, redirectTo]);

  // 错误状态
  if (error) {
    if (errorComponent) {
      return <>{errorComponent(error)}</>;
    }

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
        <div
          style={{
            textAlign: 'center',
            padding: '48px',
            backgroundColor: '#fff',
            borderRadius: '12px',
            boxShadow: '0 4px 20px rgba(0, 0, 0, 0.1)',
            maxWidth: '400px',
          }}
        >
          <div
            style={{
              width: '64px',
              height: '64px',
              margin: '0 auto 24px',
              backgroundColor: '#ff4d4f',
              borderRadius: '50%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '32px',
              color: 'white',
            }}
          >
            ✕
          </div>
          <h2 style={{ fontSize: '24px', marginBottom: '12px', color: '#333' }}>登录失败</h2>
          <p style={{ fontSize: '14px', color: '#666', marginBottom: '24px' }}>
            {error.message}
          </p>
          <button
            onClick={() => window.history.back()}
            style={{
              padding: '10px 24px',
              fontSize: '14px',
              backgroundColor: '#1890ff',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
            }}
          >
            返回
          </button>
        </div>
      </div>
    );
  }

  // 加载状态
  if (isProcessing) {
    if (loadingComponent) {
      return <>{loadingComponent}</>;
    }

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
          <div
            style={{
              width: '48px',
              height: '48px',
              margin: '0 auto 24px',
              border: '4px solid #f0f0f0',
              borderTop: '4px solid #1890ff',
              borderRadius: '50%',
              animation: 'spin 1s linear infinite',
            }}
          />
          <p style={{ fontSize: '16px', color: '#666' }}>正在登录...</p>
          <style>
            {`
              @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
              }
            `}
          </style>
        </div>
      </div>
    );
  }

  return null;
};

