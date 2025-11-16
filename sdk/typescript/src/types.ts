/**
 * AuthHub SDK Types (轻量版)
 */

export interface User {
  sub: string;
  username: string;
  email?: string;
  global_roles?: string[];
  system_roles?: Record<string, string[]>;
  dept_ids?: number[];
  dept_names?: string[];
}

export interface AuthConfig {
  backendUrl: string;
  loginPath?: string;
  logoutPath?: string;
  mePath?: string;
}

// 兼容旧版类型（用于权限验证 SDK）
export interface TokenPayload extends User {
  global_resources?: Record<string, number[]>;
  system_resources?: Record<string, Record<string, number[]>>;
  exp: number;
  iat: number;
  jti: string;
  email: string; // 必填
  global_roles: string[]; // 必填
}

export interface PermissionConfig {
  version: string;
  roles: Record<string, RoleConfig>;
  routes: RouteConfig[];
}

export interface RoleConfig {
  id: number;
  code: string;
  name: string;
  permissions: PermissionItem[];
}

export interface PermissionItem {
  resource: string;
  actions: string[];
}

export interface RouteConfig {
  id: number;
  path: string;
  method: string;
  roles: string[];
}
