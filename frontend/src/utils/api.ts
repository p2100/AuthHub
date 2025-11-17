/**
 * API工具函数
 */

import type { ApiError } from '@/types/api'

const API_BASE_URL = '/api/v1'

/**
 * API错误类
 */
export class ApiRequestError extends Error {
  constructor(
    message: string,
    public status: number,
    public response?: any
  ) {
    super(message)
    this.name = 'ApiRequestError'
  }
}

/**
 * 获取存储的token
 */
export function getToken(): string | null {
  return localStorage.getItem('auth_token')
}

/**
 * 设置token
 */
export function setToken(token: string): void {
  localStorage.setItem('auth_token', token)
}

/**
 * 获取refresh token
 */
export function getRefreshToken(): string | null {
  return localStorage.getItem('refresh_token')
}

/**
 * 设置refresh token
 */
export function setRefreshToken(token: string): void {
  localStorage.setItem('refresh_token', token)
}

/**
 * 清除token
 */
export function clearToken(): void {
  localStorage.removeItem('auth_token')
  localStorage.removeItem('refresh_token')
}

// Refresh token 状态管理（防止并发刷新）
let isRefreshing = false
let refreshSubscribers: Array<(token: string) => void> = []

/**
 * 通知等待的订阅者
 */
function onRefreshed(token: string) {
  refreshSubscribers.forEach(callback => callback(token))
  refreshSubscribers = []
}

/**
 * 添加刷新订阅者
 */
function addRefreshSubscriber(callback: (token: string) => void) {
  refreshSubscribers.push(callback)
}

/**
 * 刷新 access token
 */
async function refreshAccessToken(): Promise<boolean> {
  // 如果正在刷新，等待刷新完成
  if (isRefreshing) {
    return new Promise((resolve) => {
      addRefreshSubscriber((token: string) => {
        resolve(!!token)
      })
    })
  }

  const refreshToken = getRefreshToken()
  if (!refreshToken) {
    return false
  }

  isRefreshing = true

  try {
    const response = await fetch(`${API_BASE_URL}/auth/refresh`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ refresh_token: refreshToken }),
    })

    if (response.ok) {
      const data = await response.json()
      setToken(data.access_token)
      setRefreshToken(data.refresh_token)

      // 通知等待的请求
      onRefreshed(data.access_token)
      isRefreshing = false
      return true
    } else {
      isRefreshing = false
      return false
    }
  } catch (error) {
    console.error('Token刷新失败:', error)
    isRefreshing = false
    return false
  }
}

/**
 * 封装的fetch请求
 */
async function request<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const token = getToken()

  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...options.headers,
  }

  // 如果有token，添加Authorization头
  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }

  const url = endpoint.startsWith('http') ? endpoint : `${API_BASE_URL}${endpoint}`

  try {
    const response = await fetch(url, {
      ...options,
      headers,
    })

    // 处理401未授权 - 尝试刷新token
    if (response.status === 401) {
      // 尝试刷新token
      const refreshed = await refreshAccessToken()
      if (refreshed) {
        // 刷新成功，重试原请求
        return request<T>(endpoint, options)
      }

      // 刷新失败，清除token并跳转登录页
      clearToken()
      if (window.location.pathname !== '/login') {
        window.location.href = '/login'
      }
      throw new ApiRequestError('未授权，请重新登录', 401)
    }

    // 处理403无权限
    if (response.status === 403) {
      throw new ApiRequestError('无权限访问', 403)
    }

    // 处理其他错误状态
    if (!response.ok) {
      const errorData: ApiError = await response.json().catch(() => ({
        detail: '请求失败'
      }))
      throw new ApiRequestError(
        errorData.detail || `请求失败: ${response.status}`,
        response.status,
        errorData
      )
    }

    // 处理无内容响应
    if (response.status === 204) {
      return {} as T
    }

    return await response.json()
  } catch (error) {
    if (error instanceof ApiRequestError) {
      throw error
    }
    throw new ApiRequestError(
      error instanceof Error ? error.message : '网络请求失败',
      0
    )
  }
}

/**
 * GET请求
 */
export async function apiGet<T>(endpoint: string): Promise<T> {
  return request<T>(endpoint, { method: 'GET' })
}

/**
 * POST请求
 */
export async function apiPost<T>(
  endpoint: string,
  data?: any
): Promise<T> {
  return request<T>(endpoint, {
    method: 'POST',
    body: data ? JSON.stringify(data) : undefined,
  })
}

/**
 * PUT请求
 */
export async function apiPut<T>(
  endpoint: string,
  data?: any
): Promise<T> {
  return request<T>(endpoint, {
    method: 'PUT',
    body: data ? JSON.stringify(data) : undefined,
  })
}

/**
 * DELETE请求
 */
export async function apiDelete<T>(endpoint: string): Promise<T> {
  return request<T>(endpoint, { method: 'DELETE' })
}


