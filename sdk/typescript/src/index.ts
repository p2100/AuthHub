/**
 * AuthHub TypeScript SDK
 */

export { AuthHubClient } from './client';
export { TokenVerifier } from './verifier';
export { PermissionChecker } from './checker';
export * from './types';
export * from './exceptions';

// SSO
export { SSOClient } from './sso';
export { TokenManager } from './tokenManager';

// React Hooks (仅在React环境)
export * from './hooks';

// Vue Composables (仅在Vue环境)
export * from './composables';

// React Components
export * from './components';

// 中间件
export * from './middleware';

export const VERSION = '0.1.0';

