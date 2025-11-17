import React, { useEffect } from 'react';
import { useAuth } from '../hooks/useAuth';
import { useNavigate } from 'react-router-dom';
import { AUTH_CONFIG } from '../config';

function Dashboard() {
  const { user, logout, isAuthenticated, loading } = useAuth(AUTH_CONFIG);
  const navigate = useNavigate();

  useEffect(() => {
    if (!loading && !isAuthenticated) {
      navigate('/login');
    }
  }, [loading, isAuthenticated, navigate]);

  if (loading) {
    return <div style={{ padding: '24px', textAlign: 'center' }}>加载中...</div>;
  }

  if (!user) {
    return null;
  }

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const containerStyle: React.CSSProperties = {
    minHeight: '100vh',
    backgroundColor: '#f5f5f5',
  };

  const headerStyle: React.CSSProperties = {
    backgroundColor: 'white',
    boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)',
    padding: '16px 24px',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
  };

  const contentStyle: React.CSSProperties = {
    padding: '24px',
    maxWidth: '1200px',
    margin: '0 auto',
  };

  const cardStyle: React.CSSProperties = {
    backgroundColor: 'white',
    borderRadius: '8px',
    padding: '24px',
    boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)',
    marginBottom: '16px',
  };

  const buttonStyle: React.CSSProperties = {
    padding: '8px 16px',
    backgroundColor: '#ff4d4f',
    color: 'white',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
    fontSize: '14px',
  };

  return (
    <div style={containerStyle}>
      <div style={headerStyle}>
        <h1 style={{ fontSize: '20px', fontWeight: 600 }}>React SSO 示例</h1>
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <span style={{ color: '#666' }}>欢迎, {user.username}</span>
          <button onClick={handleLogout} style={buttonStyle}>
            登出
          </button>
        </div>
      </div>
      <div style={contentStyle}>
        <div style={cardStyle}>
          <h2 style={{ fontSize: '18px', marginBottom: '16px' }}>用户信息</h2>
          <div style={{ lineHeight: '2' }}>
            <p>
              <strong>用户名:</strong> {user.username}
            </p>
            <p>
              <strong>邮箱:</strong> {user.email || '未设置'}
            </p>
            <p>
              <strong>用户ID:</strong> {user.sub}
            </p>
            <p>
              <strong>全局角色:</strong> {user.global_roles?.join(', ') || '无'}
            </p>
          </div>
        </div>
        <div style={cardStyle}>
          <h2 style={{ fontSize: '18px', marginBottom: '16px' }}>轻量级 SDK 架构</h2>
          <p style={{ lineHeight: '1.6', color: '#666', marginBottom: '16px' }}>
            这是一个使用 AuthHub 轻量级 SDK 的 React 示例应用。
            所有 OAuth 逻辑都在后端处理，前端只需要一个简单的 Hook。
          </p>
          <div
            style={{
              padding: '16px',
              backgroundColor: '#f5f5f5',
              borderRadius: '6px',
              fontSize: '13px',
              color: '#666',
            }}
          >
            <p style={{ margin: '0 0 8px', fontWeight: 500 }}>✨ 核心特性：</p>
            <ul style={{ margin: 0, paddingLeft: '20px', lineHeight: '1.8' }}>
              <li>
                <strong>安全</strong>：Token 存储在 HttpOnly Cookie，无法被 JS 访问
              </li>
              <li>
                <strong>简单</strong>：前端只需要一个 <code>useAuth</code> Hook
              </li>
              <li>
                <strong>标准</strong>：遵循前后端分离的最佳实践
              </li>
              <li>
                <strong>灵活</strong>：后端可以是任何框架（FastAPI、Express 等）
              </li>
            </ul>
          </div>
        </div>
        <div style={cardStyle}>
          <h2 style={{ fontSize: '18px', marginBottom: '16px' }}>集成步骤</h2>
          <ol style={{ paddingLeft: '24px', lineHeight: '2', color: '#666' }}>
            <li>在后端使用 Python SDK 的 <code>setup_sso()</code></li>
            <li>在前端使用 <code>useAuth</code> Hook</li>
            <li>就这么简单！🎉</li>
          </ol>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
