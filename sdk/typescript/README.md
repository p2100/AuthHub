# AuthHub TypeScript SDK

AuthHub统一权限平台的TypeScript/JavaScript SDK,支持React、Express、Next.js等框架。

## 功能特性

- ✅ 本地Token验证(RS256)
- ✅ 本地权限校验(零网络开销)
- ✅ React Hooks
- ✅ Express/Koa/Next.js中间件
- ✅ TypeScript类型支持
- ✅ 配置自动同步

## 安装

```bash
npm install @authhub/sdk
# or
yarn add @authhub/sdk
# or
pnpm add @authhub/sdk
```

## 快速开始

### 1. 初始化SDK

```typescript
import { AuthHubClient } from '@authhub/sdk';

const client = new AuthHubClient({
  authhubUrl: 'https://authhub.company.com',
  systemId: 'system_a',
  systemToken: 'your_system_token',
  namespace: 'system_a',
  redisUrl: 'redis://localhost:6379',
});
```

### 2. React Hooks

```typescript
import { useAuth, usePermission } from '@authhub/sdk/hooks';

function MyComponent() {
  const { user, isAuthenticated } = useAuth();
  const canEdit = usePermission('document', 'write');
  
  if (!isAuthenticated) {
    return <Login />;
  }
  
  return (
    <div>
      <h1>Hello, {user.username}</h1>
      {canEdit && <button>Edit</button>}
    </div>
  );
}
```

### 3. Express中间件

```typescript
import express from 'express';
import { authHubMiddleware } from '@authhub/sdk/middleware/express';

const app = express();

app.use(authHubMiddleware(client));

app.get('/api/documents', (req, res) => {
  const user = req.user; // 自动注入用户信息
  res.json({ documents: [] });
});
```

### 4. Next.js中间件

```typescript
// middleware.ts
import { authHubMiddleware } from '@authhub/sdk/middleware/nextjs';

export default authHubMiddleware(client);

export const config = {
  matcher: '/api/:path*',
};
```

## 文档

完整文档请访问: https://docs.authhub.com/sdk/typescript

## 许可证

MIT License

