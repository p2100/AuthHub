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

// ========== 用户相关类型 ==========

export interface User {
  id: number
  feishu_user_id: string
  username: string
  email?: string
  avatar?: string
  mobile?: string
  dept_ids?: string[]
  dept_names?: string[]
  status: string
  last_login?: string
  created_at: string
}

export interface UserListResponse {
  total: number
  items: User[]
}

export interface UserStatusUpdate {
  status: 'active' | 'inactive'
}

export interface UserRole {
  role_id: number
  role_code: string
  role_name: string
  namespace: string
  assigned_at: string
  created_by?: number
}

export interface UserPermissionDetail {
  global_roles: string[]
  system_roles: Record<string, string[]>
  global_resources: Record<string, string[]>
  system_resources: Record<string, Record<string, string[]>>
  roles: UserRole[]
}

// ========== 系统相关类型 ==========

export interface System {
  id: number
  code: string
  name: string
  description: string
  api_endpoint: string
  status: string
  created_at: string
}

export interface SystemWithToken extends System {
  system_token: string
}

export interface SystemCreate {
  code: string
  name: string
  description?: string
  api_endpoint?: string
}

export interface SystemUpdate {
  name?: string
  description?: string
  api_endpoint?: string
}

export interface SystemStatusUpdate {
  status: 'active' | 'inactive'
}

// ========== 角色相关类型 ==========

export interface Role {
  id: number
  code: string
  name: string
  namespace: string
  system_id?: number
  description: string
  created_at: string
}

export interface RoleCreate {
  code: string
  name: string
  namespace: string
  system_id?: number
  description?: string
}

export interface RoleUpdate {
  name?: string
  description?: string
}

export interface UpdateRolePermissions {
  permission_ids: number[]
}

export interface AssignRoleRequest {
  user_id: number
  role_id: number
}

// ========== 权限相关类型 ==========

export interface Permission {
  id: number
  code: string
  name: string
  namespace: string
  resource_type: string
  action: string
}

export interface PermissionCreate {
  code: string
  name: string
  namespace: string
  system_id?: number
  resource_type?: string
  action?: string
  description?: string
}

export interface PermissionUpdate {
  name?: string
  description?: string
  resource_type?: string
  action?: string
}

export interface RoutePattern {
  id: number
  system_id: number
  role_id: number
  pattern: string
  method: string
  priority: number
  description?: string
  created_at: string
}

export interface RoutePatternCreate {
  system_id: number
  role_id: number
  pattern: string
  method?: string
  priority?: number
  description?: string
}

export interface RoutePatternUpdate {
  pattern?: string
  method?: string
  priority?: number
  description?: string
}

export interface ResourceBinding {
  id: number
  user_id: number
  namespace: string
  resource_type: string
  resource_id: string
  system_id?: number
  action: string
  created_at: string
  created_by: number
}

export interface ResourceBindingCreate {
  user_id: number
  namespace: string
  resource_type: string
  resource_ids: string[]
  system_id?: number
  action?: string
}


