/**
 * AuthHub TypeScript SDK (轻量版)
 * 
 * 适用于前后端分离架构
 * 核心逻辑在后端，前端只提供辅助工具
 */

// 核心客户端
export { AuthClient } from './auth-client';
export type { AuthConfig, User } from './types';

// React 支持
export { useAuth } from './hooks/useAuth';
export type { UseAuthOptions as UseAuthOptionsReact, UseAuthResult } from './hooks/useAuth';

// Vue 支持
export { useAuth as useAuthVue } from './composables/useAuth';
export type { UseAuthOptions as UseAuthOptionsVue } from './composables/useAuth';

// 类型定义
export * from './types';

// 兼容旧版 - 权限验证相关（仅用于后端 Token 验证场景）
export { TokenVerifier } from './verifier';
export { PermissionChecker } from './checker';
export * from './exceptions';

export const VERSION = '0.2.0';

