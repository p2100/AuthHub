import React from 'react';
import { useAuth } from '../hooks/useAuth';
import { BACKEND_URL } from '../config';

function Login() {
  const { login, loading } = useAuth({ backendUrl: BACKEND_URL });

  const handleLogin = () => {
    login('/dashboard');
  };

  return (
    <div
      style={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
      }}
    >
      <div
        style={{
          width: '100%',
          maxWidth: '420px',
          padding: '48px 40px',
          backgroundColor: 'white',
          borderRadius: '16px',
          boxShadow: '0 20px 60px rgba(0, 0, 0, 0.3)',
        }}
      >
        <div style={{ textAlign: 'center', marginBottom: '40px' }}>
          <div
            style={{
              width: '80px',
              height: '80px',
              margin: '0 auto 24px',
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              borderRadius: '20px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '36px',
              fontWeight: 'bold',
              color: 'white',
              boxShadow: '0 10px 25px rgba(102, 126, 234, 0.4)',
            }}
          >
            A
          </div>
          <h1 style={{ fontSize: '28px', fontWeight: 700, marginBottom: '8px', color: '#1a1a1a' }}>
            React SSO 示例
          </h1>
          <p style={{ fontSize: '14px', color: '#666' }}>使用 AuthHub 轻量级 SDK</p>
        </div>

        <button
          onClick={handleLogin}
          disabled={loading}
          style={{
            width: '100%',
            padding: '14px',
            fontSize: '16px',
            fontWeight: 500,
            backgroundColor: loading ? '#40a9ff' : '#1890ff',
            color: 'white',
            border: 'none',
            borderRadius: '6px',
            cursor: loading ? 'not-allowed' : 'pointer',
            transition: 'all 0.3s',
          }}
          onMouseEnter={(e) => {
            if (!loading) {
              e.currentTarget.style.backgroundColor = '#40a9ff';
              e.currentTarget.style.transform = 'translateY(-2px)';
              e.currentTarget.style.boxShadow = '0 4px 12px rgba(24, 144, 255, 0.3)';
            }
          }}
          onMouseLeave={(e) => {
            if (!loading) {
              e.currentTarget.style.backgroundColor = '#1890ff';
              e.currentTarget.style.transform = 'translateY(0)';
              e.currentTarget.style.boxShadow = 'none';
            }
          }}
        >
          {loading ? '加载中...' : '使用飞书登录'}
        </button>

        <div
          style={{
            marginTop: '32px',
            padding: '16px',
            backgroundColor: '#f5f5f5',
            borderRadius: '8px',
            fontSize: '13px',
            color: '#666',
          }}
        >
          <p style={{ margin: '0 0 8px', fontWeight: 500 }}>💡 轻量级架构说明：</p>
          <ul style={{ margin: 0, paddingLeft: '20px', lineHeight: '1.6' }}>
            <li>点击登录后跳转到业务后端</li>
            <li>后端处理 OAuth 流程</li>
            <li>前端只需要一个 Hook</li>
            <li>Token 安全存储在 HttpOnly Cookie</li>
          </ul>
        </div>
      </div>
    </div>
  );
}

export default Login;
