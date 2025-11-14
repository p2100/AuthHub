/**
 * 类型定义
 */

export interface AuthHubOptions {
  authhubUrl: string;
  systemId: string;
  systemToken: string;
  namespace: string;
  redisUrl?: string;
  enableCache?: boolean;
  syncInterval?: number;
}

export interface TokenPayload {
  sub: string;
  user_type: 'user' | 'system';
  username?: string;
  email?: string;
  dept_ids?: number[];
  dept_names?: string[];
  global_roles: string[];
  system_roles: Record<string, string[]>;
  global_resources: Record<string, number[]>;
  system_resources: Record<string, Record<string, number[]>>;
  iat: number;
  exp: number;
  jti: string;
}

export interface PermissionConfig {
  version: string;
  updated_at: number;
  namespace: string;
  roles: Record<string, RoleConfig>;
  permissions: Record<string, PermissionInfo>;
  route_patterns: RoutePattern[];
}

export interface RoleConfig {
  id: number;
  name: string;
  description?: string;
  permissions: string[];
}

export interface PermissionInfo {
  id: number;
  name: string;
  resource_type: string;
  action: string;
}

export interface RoutePattern {
  role: string;
  pattern: string;
  method: string;
  priority: number;
}

