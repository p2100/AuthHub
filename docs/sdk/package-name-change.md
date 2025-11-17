# TypeScript SDK 包名变更说明

## 变更时间
2025-11-17

## 变更原因

在尝试发布 `@authhub/sdk` 到 npm 时遇到 404 错误:

```
npm error 404 Not Found - PUT https://registry.npmjs.org/@authhub%2fsdk - Not found
npm error 404  '@authhub/sdk@0.1.0' is not in this registry.
```

**原因**: `@authhub` 这个组织 scope 在 npm 上不存在,且当前账号无权创建或发布到该 scope。

## 解决方案

将包名改为使用个人 scope: `@chenjing194/authhub-sdk`

这样可以:
- ✅ 立即发布,无需额外权限
- ✅ 保持 scoped package 的优势
- ✅ 避免命名冲突
- ✅ 以后可以转移到组织 scope

## 变更内容

### 1. package.json

```diff
- "name": "@authhub/sdk",
+ "name": "@chenjing194/authhub-sdk",
```

### 2. README.md

安装命令:
```diff
- npm install @authhub/sdk
+ npm install @chenjing194/authhub-sdk
```

导入语句:
```diff
- import { useAuth } from '@authhub/sdk';
+ import { useAuth } from '@chenjing194/authhub-sdk';
```

## 使用说明

### 安装

```bash
npm install @chenjing194/authhub-sdk
# 或
yarn add @chenjing194/authhub-sdk
# 或
pnpm add @chenjing194/authhub-sdk
```

### React 使用

```typescript
import { useAuth } from '@chenjing194/authhub-sdk';

function App() {
  const { user, loading, isAuthenticated, login, logout } = useAuth({
    backendUrl: 'http://localhost:8001'
  });

  // ... 你的代码
}
```

### Vue 使用

```typescript
import { useAuthVue } from '@chenjing194/authhub-sdk';

export default {
  setup() {
    const { user, loading, isAuthenticated, login, logout } = useAuthVue({
      backendUrl: 'http://localhost:8001'
    });

    // ... 你的代码
  }
}
```

### 原生 TypeScript 使用

```typescript
import { AuthClient } from '@chenjing194/authhub-sdk';

const client = new AuthClient({
  backendUrl: 'http://localhost:8001'
});

// 获取当前用户
const user = await client.getCurrentUser();

// 刷新 token
const tokens = await client.refreshToken(refreshToken);
```

## 发布步骤

现在可以正常发布了:

```bash
# 干运行测试
./scripts/publish-typescript.sh dry-run

# 正式发布
./scripts/publish-typescript.sh prod
```

## 未来迁移计划

如果将来需要迁移到组织 scope (`@authhub/sdk`):

1. 在 npm 创建 `@authhub` 组织
2. 添加发布权限
3. 使用 npm 的包迁移功能或发布新版本
4. 将旧包标记为 deprecated,指向新包

## 相关文件

- `/sdk/typescript/package.json` - 包配置
- `/sdk/typescript/README.md` - 文档
- `/scripts/publish-typescript.sh` - 发布脚本

