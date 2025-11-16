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
 * 清除token
 */
export function clearToken(): void {
  localStorage.removeItem('auth_token')
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

    // 处理401未授权 - 跳转到登录页
    if (response.status === 401) {
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


