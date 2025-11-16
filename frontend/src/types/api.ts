/**
 * API类型定义
 */

// 统计数据响应
export interface StatsResponse {
  system_count: number
  user_count: number
  role_count: number
}

// 用户信息
export interface UserInfo {
  sub: string // 用户ID
  username: string
  email: string
  user_type: string
  global_roles: string[] // 全局角色，包含 "admin" 表示管理员
  dept_ids: string[]
  dept_names: string[]
  exp: number // 过期时间
  iat: number // 签发时间
  jti: string // Token ID
}

// Token响应
export interface TokenResponse {
  access_token: string
  token_type: string
  expires_in: number
}

// API错误响应
export interface ApiError {
  detail: string
}


