/**
 * LoginButton Component
 * 
 * 开箱即用的登录按钮组件
 */

import React from 'react';
import { useSSO } from '../hooks/useSSO';

export interface LoginButtonProps {
  authhubUrl: string;
  redirectUri?: string;
  className?: string;
  style?: React.CSSProperties;
  children?: React.ReactNode;
  onLoginSuccess?: (user: any) => void;
}

/**
 * 登录按钮组件
 * 
 * @example
 * ```tsx
 * <LoginButton authhubUrl="http://localhost:8000">
 *   使用飞书登录
 * </LoginButton>
 * ```
 */
export const LoginButton: React.FC<LoginButtonProps> = ({
  authhubUrl,
  redirectUri,
  className,
  style,
  children = '登录',
  onLoginSuccess,
}) => {
  const { login, isLoading } = useSSO({
    authhubUrl,
    redirectUri,
    onLoginSuccess,
  });

  const defaultStyle: React.CSSProperties = {
    padding: '10px 20px',
    fontSize: '16px',
    backgroundColor: '#1890ff',
    color: 'white',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
    transition: 'background-color 0.3s',
    ...style,
  };

  return (
    <button
      onClick={login}
      disabled={isLoading}
      className={className}
      style={defaultStyle}
      onMouseEnter={(e) => {
        e.currentTarget.style.backgroundColor = '#40a9ff';
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.backgroundColor = '#1890ff';
      }}
    >
      {isLoading ? '加载中...' : children}
    </button>
  );
};

