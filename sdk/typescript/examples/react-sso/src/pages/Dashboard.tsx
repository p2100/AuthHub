import React from 'react';
import { ProtectedRoute } from '@authhub/sdk/components';
import { useSSO } from '@authhub/sdk/hooks';
import { AUTHHUB_URL } from '../config';
import { useNavigate } from 'react-router-dom';

function DashboardContent() {
  const { user, logout } = useSSO({ authhubUrl: AUTHHUB_URL });
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
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
          <span style={{ color: '#666' }}>欢迎, {user?.username}</span>
          <button onClick={handleLogout} style={buttonStyle}>
            登出
          </button>
        </div>
      </div>
      <div style={contentStyle}>
        <div style={cardStyle}>
          <h2 style={{ fontSize: '18px', marginBottom: '16px' }}>用户信息</h2>
          <div style={{ lineHeight: '2' }}>
            <p><strong>用户名:</strong> {user?.username}</p>
            <p><strong>邮箱:</strong> {user?.email || '未设置'}</p>
            <p><strong>用户ID:</strong> {user?.sub}</p>
            <p><strong>全局角色:</strong> {user?.global_roles?.join(', ') || '无'}</p>
          </div>
        </div>
        <div style={cardStyle}>
          <h2 style={{ fontSize: '18px', marginBottom: '16px' }}>SSO 集成说明</h2>
          <p style={{ lineHeight: '1.6', color: '#666' }}>
            这是一个使用 AuthHub SDK 的 React SSO 示例应用。
            通过简单的组件和 Hook，即可实现完整的 SSO 登录流程。
          </p>
          <ul style={{ marginTop: '16px', paddingLeft: '24px', lineHeight: '2', color: '#666' }}>
            <li>使用 <code>LoginPage</code> 组件实现登录页面</li>
            <li>使用 <code>SSOCallback</code> 组件处理回调</li>
            <li>使用 <code>ProtectedRoute</code> 保护路由</li>
            <li>使用 <code>useSSO</code> Hook 管理登录状态</li>
          </ul>
        </div>
      </div>
    </div>
  );
}

function Dashboard() {
  return (
    <ProtectedRoute authhubUrl={AUTHHUB_URL}>
      <DashboardContent />
    </ProtectedRoute>
  );
}

export default Dashboard;

