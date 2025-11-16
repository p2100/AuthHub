/**
 * 认证上下文管理
 */

import { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { apiGet, apiPost, getToken, setToken, clearToken } from '@/utils/api'
import type { UserInfo, TokenResponse } from '@/types/api'

interface AuthContextType {
  user: UserInfo | null
  loading: boolean
  isAuthenticated: boolean
  isAdmin: boolean
  login: (token: string) => Promise<void>
  logout: () => Promise<void>
  refreshUser: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

interface AuthProviderProps {
  children: ReactNode
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<UserInfo | null>(null)
  const [loading, setLoading] = useState(true)

  // 是否已认证
  const isAuthenticated = !!user

  // 是否是管理员（检查global_roles中是否包含admin）
  const isAdmin = user?.global_roles?.includes('admin') ?? false

  // 获取当前用户信息
  const fetchUser = async () => {
    const token = getToken()
    if (!token) {
      setUser(null)
      setLoading(false)
      return
    }

    try {
      const userInfo = await apiGet<UserInfo>('/auth/me')
      setUser(userInfo)
    } catch (error) {
      console.error('获取用户信息失败:', error)
      setUser(null)
      clearToken()
    } finally {
      setLoading(false)
    }
  }

  // 登录（保存token并获取用户信息）
  const login = async (token: string) => {
    setToken(token)
    await fetchUser()
  }

  // 登出
  const logout = async () => {
    try {
      // 调用后端登出API（将token加入黑名单）
      await apiPost('/auth/logout')
    } catch (error) {
      console.error('登出API调用失败:', error)
    } finally {
      // 无论API调用是否成功，都清除本地token
      clearToken()
      setUser(null)
    }
  }

  // 刷新用户信息
  const refreshUser = async () => {
    await fetchUser()
  }

  // 初始化时尝试获取用户信息
  useEffect(() => {
    fetchUser()
  }, [])

  const value: AuthContextType = {
    user,
    loading,
    isAuthenticated,
    isAdmin,
    login,
    logout,
    refreshUser,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

// 自定义Hook用于使用认证上下文
export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth必须在AuthProvider内部使用')
  }
  return context
}


