/**
 * LoginPage Component
 * 
 * 完整的登录页面组件
 */

import React from 'react';
import { useSSO } from '../hooks/useSSO';

export interface LoginPageProps {
  authhubUrl: string;
  redirectUri?: string;
  title?: string;
  subtitle?: string;
  logo?: string;
  backgroundColor?: string;
  onLoginSuccess?: (user: any) => void;
}

/**
 * 登录页面组件
 * 
 * @example
 * ```tsx
 * <LoginPage
 *   authhubUrl="http://localhost:8000"
 *   title="AuthHub 统一认证"
 *   subtitle="使用飞书账号登录"
 * />
 * ```
 */
export const LoginPage: React.FC<LoginPageProps> = ({
  authhubUrl,
  redirectUri,
  title = 'AuthHub',
  subtitle = '统一认证平台',
  logo,
  backgroundColor = 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
  onLoginSuccess,
}) => {
  const { login, isLoading } = useSSO({
    authhubUrl,
    redirectUri,
    onLoginSuccess,
  });

  const containerStyle: React.CSSProperties = {
    minHeight: '100vh',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    background: backgroundColor,
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
  };

  const cardStyle: React.CSSProperties = {
    backgroundColor: 'white',
    borderRadius: '12px',
    boxShadow: '0 4px 20px rgba(0, 0, 0, 0.1)',
    padding: '48px',
    width: '100%',
    maxWidth: '400px',
    textAlign: 'center',
  };

  const logoStyle: React.CSSProperties = {
    width: '80px',
    height: '80px',
    marginBottom: '24px',
    borderRadius: '50%',
  };

  const titleStyle: React.CSSProperties = {
    fontSize: '28px',
    fontWeight: 600,
    marginBottom: '8px',
    color: '#333',
  };

  const subtitleStyle: React.CSSProperties = {
    fontSize: '14px',
    color: '#666',
    marginBottom: '32px',
  };

  const buttonStyle: React.CSSProperties = {
    width: '100%',
    padding: '14px',
    fontSize: '16px',
    fontWeight: 500,
    backgroundColor: '#1890ff',
    color: 'white',
    border: 'none',
    borderRadius: '6px',
    cursor: 'pointer',
    transition: 'all 0.3s',
  };

  return (
    <div style={containerStyle}>
      <div style={cardStyle}>
        {logo && <img src={logo} alt="Logo" style={logoStyle} />}
        <h1 style={titleStyle}>{title}</h1>
        <p style={subtitleStyle}>{subtitle}</p>
        <button
          onClick={login}
          disabled={isLoading}
          style={buttonStyle}
          onMouseEnter={(e) => {
            e.currentTarget.style.backgroundColor = '#40a9ff';
            e.currentTarget.style.transform = 'translateY(-2px)';
            e.currentTarget.style.boxShadow = '0 4px 12px rgba(24, 144, 255, 0.3)';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.backgroundColor = '#1890ff';
            e.currentTarget.style.transform = 'translateY(0)';
            e.currentTarget.style.boxShadow = 'none';
          }}
        >
          {isLoading ? '加载中...' : '使用飞书登录'}
        </button>
      </div>
    </div>
  );
};

