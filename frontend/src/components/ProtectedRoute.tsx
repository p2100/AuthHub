/**
 * 路由守卫组件
 * 保护需要管理员权限的路由
 */

import { ReactNode } from 'react'
import { Navigate } from 'react-router-dom'
import { Spin, Result, Button } from 'antd'
import { useAuth } from '@/contexts/AuthContext'

interface ProtectedRouteProps {
  children: ReactNode
}

export default function ProtectedRoute({ children }: ProtectedRouteProps) {
  const { user, loading, isAuthenticated, isAdmin } = useAuth()

  // 加载中显示loading
  if (loading) {
    return (
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        height: '100vh'
      }}>
        <Spin size="large" tip="加载中..." />
      </div>
    )
  }

  // 未登录，重定向到登录页
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  // 已登录但不是管理员，显示权限不足
  if (!isAdmin) {
    return (
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        height: '100vh',
        padding: '24px'
      }}>
        <Result
          status="403"
          title="权限不足"
          subTitle={`抱歉，您（${user?.username}）没有管理员权限，无法访问此页面。`}
          extra={
            <Button type="primary" onClick={() => window.location.href = '/login'}>
              返回登录
            </Button>
          }
        />
      </div>
    )
  }

  // 已登录且是管理员，渲染子组件
  return <>{children}</>
}


