/**
 * 应用配置
 */

import type { UseAuthOptions } from './hooks/useAuth';

export const BACKEND_URL = 'http://localhost:8001';

/**
 * AuthHub 认证配置
 * 
 * 这些路径必须与后端 setup_sso() 配置的路径一致
 */
export const AUTH_CONFIG: UseAuthOptions = {
  backendUrl: BACKEND_URL,
  loginPath: '/auth/login',    // 与后端 setup_sso 的 login_path 一致
  logoutPath: '/auth/logout',  // 与后端 setup_sso 的 logout_path 一致
  mePath: '/api/me',           // 后端提供的用户信息接口
};
