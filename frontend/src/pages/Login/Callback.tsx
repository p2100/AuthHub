/**
 * 飞书登录回调页面
 */

import { useEffect, useState, useRef } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { Spin, Result, Button } from 'antd'
import { apiGet } from '@/utils/api'
import { useAuth } from '@/contexts/AuthContext'
import type { TokenResponse } from '@/types/api'

export default function LoginCallback() {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const { login } = useAuth()
  const [error, setError] = useState<string>('')
  const [processing, setProcessing] = useState(true)
  // 使用ref防止React.StrictMode导致的重复调用
  const hasProcessed = useRef(false)

  useEffect(() => {
    // 如果已经处理过，直接返回
    if (hasProcessed.current) {
      return
    }
    
    hasProcessed.current = true

    const handleCallback = async () => {
      // 获取授权码
      const code = searchParams.get('code')
      
      if (!code) {
        setError('缺少授权码')
        setProcessing(false)
        return
      }

      try {
        // 调用后端回调接口换取token
        const tokenData = await apiGet<TokenResponse>(`/auth/feishu/callback?code=${code}`)
        
        // 保存access token和refresh token并获取用户信息
        await login(tokenData.access_token, tokenData.refresh_token)
        
        // 登录成功，跳转到仪表盘
        navigate('/dashboard', { replace: true })
      } catch (err: any) {
        console.error('登录回调处理失败:', err)
        setError(err.message || '登录失败，请重试')
        setProcessing(false)
      }
    }

    handleCallback()
  }, [searchParams, login, navigate])

  // 处理中显示loading
  if (processing) {
    return (
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        height: '100vh',
        flexDirection: 'column',
        gap: '16px'
      }}>
        <Spin size="large" />
        <p style={{ color: '#666' }}>正在登录中，请稍候...</p>
      </div>
    )
  }

  // 显示错误
  return (
    <div style={{
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      height: '100vh',
      padding: '24px'
    }}>
      <Result
        status="error"
        title="登录失败"
        subTitle={error}
        extra={
          <Button type="primary" onClick={() => navigate('/login')}>
            返回登录
          </Button>
        }
      />
    </div>
  )
}

