/**
 * AuthHub TypeScript SDK
 */

export { AuthHubClient } from './client';
export { TokenVerifier } from './verifier';
export { PermissionChecker } from './checker';
export * from './types';
export * from './exceptions';

// React Hooks (仅在React环境)
export * from './hooks';

// 中间件
export * from './middleware';

export const VERSION = '0.1.0';

