# TypeScript SDK 构建修复文档

## 修复日期
2025-11-17

## 问题描述

在运行 `./scripts/publish-typescript.sh dry-run` 时遇到以下问题:

1. **ESLint 配置缺失**: ESLint 找不到配置文件
2. **Jest 测试失败**: 没有找到测试文件,且没有配置 `passWithNoTests`
3. **构建失败**:
   - Vue 和 React 依赖无法解析(应该标记为 external)
   - TypeScript 类型导出错误
   - 类型定义不完整导致编译失败

## 根本原因

### 1. ESLint 配置缺失
- SDK 项目缺少 `.eslintrc.json` 配置文件
- 导致 `pnpm lint` 命令失败

### 2. Jest 配置问题
- 缺少 `jest.config.js` 配置文件
- 默认情况下,没有测试时 Jest 会返回错误码

### 3. 构建配置问题
- **类型导出错误**: `index.ts` 试图从 `auth-client` 导出 `AuthConfig` 和 `User`,但它们实际定义在 `types.ts`
- **AuthClient 功能不完整**: 缺少前端需要的 `getCurrentUser()`, `login()`, `logout()` 方法
- **Vue/React 依赖问题**: 没有标记为 external,构建时尝试打包进 bundle
- **TypeScript 类型问题**: 
  - `RoleConfig.permissions` 类型定义为 `PermissionItem[]`,但实际使用时是 `string[]`
  - `PermissionConfig` 缺少 `route_patterns` 属性
  - `TokenPayload` 可选属性处理不当

## 修复方案

### 1. 添加 ESLint 配置

创建 `/sdk/typescript/.eslintrc.json`:

```json
{
  "parser": "@typescript-eslint/parser",
  "extends": [
    "eslint:recommended",
    "plugin:@typescript-eslint/recommended"
  ],
  "plugins": ["@typescript-eslint"],
  "parserOptions": {
    "ecmaVersion": 2020,
    "sourceType": "module",
    "project": "./tsconfig.json"
  },
  "env": {
    "node": true,
    "es6": true
  },
  "rules": {
    "@typescript-eslint/explicit-module-boundary-types": "off",
    "@typescript-eslint/no-explicit-any": "warn",
    "@typescript-eslint/no-unused-vars": ["warn", { 
      "argsIgnorePattern": "^_",
      "varsIgnorePattern": "^_" 
    }]
  },
  "ignorePatterns": ["dist", "node_modules", "*.js"]
}
```

### 2. 添加 Jest 配置

创建 `/sdk/typescript/jest.config.js`:

```javascript
module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'node',
  roots: ['<rootDir>/src'],
  testMatch: ['**/__tests__/**/*.ts', '**/?(*.)+(spec|test).ts'],
  moduleFileExtensions: ['ts', 'tsx', 'js', 'jsx', 'json', 'node'],
  collectCoverageFrom: [
    'src/**/*.ts',
    '!src/**/*.d.ts',
    '!src/**/__tests__/**'
  ],
  // 允许无测试时通过
  passWithNoTests: true
};
```

### 3. 修复类型导出

修改 `/sdk/typescript/src/index.ts`:

```typescript
// 修改前
export type { AuthConfig, User } from './auth-client';

// 修改后
export type { AuthConfig, User } from './types';
```

### 4. 完善 AuthClient 功能

修改 `/sdk/typescript/src/auth-client.ts`:

- 添加 `getCurrentUser()` 方法
- 添加 `login()` 方法
- 添加 `logout()` 方法
- 构造函数支持 `AuthConfig` 对象(同时兼容旧的字符串参数)

### 5. 更新构建配置

修改 `/sdk/typescript/package.json`:

```json
{
  "scripts": {
    "build": "tsup src/index.ts --format cjs,esm --dts --external react --external vue",
    "dev": "tsup src/index.ts --format cjs,esm --dts --external react --external vue --watch"
  },
  "peerDependencies": {
    "react": ">=18.0.0",
    "vue": ">=3.0.0"
  },
  "peerDependenciesMeta": {
    "react": { "optional": true },
    "vue": { "optional": true }
  },
  "devDependencies": {
    "@types/react": "^18.2.0",
    "ts-jest": "^29.1.1"
  }
}
```

### 6. 修复类型定义

修改 `/sdk/typescript/src/types.ts`:

```typescript
// 修复 RoleConfig
export interface RoleConfig {
  id: number;
  code: string;
  name: string;
  permissions: string[]; // 权限代码数组，如 ["user:read", "user:write"]
}

// 添加 route_patterns
export interface PermissionConfig {
  version: string;
  roles: Record<string, RoleConfig>;
  routes?: RouteConfig[];
  route_patterns?: RoutePatternConfig[];
}

// 添加 RoutePatternConfig
export interface RoutePatternConfig {
  pattern: string;
  method: string;
  role: string;
  priority: number;
}

// 添加 AuthHubOptions
export interface AuthHubOptions {
  authhubUrl: string;
  systemId: string;
  systemToken: string;
  namespace: string;
  enableCache?: boolean;
  syncInterval?: number;
}
```

### 7. 修复可选属性处理

修改 `/sdk/typescript/src/checker.ts`,正确处理 `TokenPayload` 的可选属性:

```typescript
// 修改前
const userRoles = tokenPayload.system_roles[this.namespace] || [];

// 修改后
const systemRoles = tokenPayload.system_roles || {};
const userRoles = systemRoles[this.namespace] || [];
```

### 8. 更新 tsconfig.json

添加 DOM 类型支持:

```json
{
  "compilerOptions": {
    "lib": ["ES2020", "DOM"]
  }
}
```

## 验证结果

执行以下命令验证修复:

```bash
cd /Users/leo/code/work/AuthHub/sdk/typescript

# 1. 安装依赖
pnpm install

# 2. Lint 检查
pnpm lint
# ✅ 通过 (有一些警告,但不影响构建)

# 3. 测试
pnpm test
# ✅ 通过 (No tests found, exiting with code 0)

# 4. 构建
pnpm build
# ✅ 成功生成:
#   - dist/index.js (CJS)
#   - dist/index.mjs (ESM)
#   - dist/index.d.ts (类型定义)
#   - dist/index.d.mts (ESM 类型定义)
```

## 输出文件

构建成功后生成的文件:

```
dist/
├── index.d.mts   (6.3KB) - ESM 类型定义
├── index.d.ts    (6.3KB) - CJS 类型定义
├── index.js      (10KB)  - CommonJS 格式
└── index.mjs     (7.9KB) - ES Module 格式
```

## 后续建议

1. **添加测试用例**: 为核心功能添加单元测试
2. **完善 ESLint 规则**: 修复现有的 13 个警告
3. **添加 CI/CD**: 在 GitHub Actions 中自动运行 lint、test、build
4. **版本管理**: 考虑使用 `changesets` 进行版本管理

## 相关文件

- `/sdk/typescript/.eslintrc.json` - ESLint 配置
- `/sdk/typescript/jest.config.js` - Jest 配置
- `/sdk/typescript/src/index.ts` - 主入口文件
- `/sdk/typescript/src/auth-client.ts` - 认证客户端
- `/sdk/typescript/src/types.ts` - 类型定义
- `/sdk/typescript/src/checker.ts` - 权限检查器
- `/sdk/typescript/package.json` - 包配置
- `/sdk/typescript/tsconfig.json` - TypeScript 配置

