# AuthHub TypeScript SDK

AuthHub统一权限平台的TypeScript/JavaScript SDK,支持React、Express、Next.js等框架。

## 功能特性

- ✅ **SSO 登录集成** - 开箱即用的登录组件和Hooks
- ✅ 本地Token验证(RS256)
- ✅ 本地权限校验(零网络开销)
- ✅ React/Vue 组件和 Hooks/Composables
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

### 2. React SSO 登录(推荐)

#### 方式一: 使用开箱即用的登录组件

```typescript
import { LoginPage, SSOCallback, ProtectedRoute } from '@authhub/sdk/components';

// 登录页面
function Login() {
  return (
    <LoginPage
      authhubUrl="http://localhost:8000"
      title="我的应用"
      subtitle="使用飞书账号登录"
    />
  );
}

// 回调页面
function Callback() {
  return (
    <SSOCallback
      authhubUrl="http://localhost:8000"
      redirectTo="/dashboard"
    />
  );
}

// 受保护的页面
function Dashboard() {
  return (
    <ProtectedRoute authhubUrl="http://localhost:8000">
      <div>这是受保护的内容</div>
    </ProtectedRoute>
  );
}
```

#### 方式二: 使用 SSO Hook

```typescript
import { useSSO } from '@authhub/sdk/hooks';

function MyComponent() {
  const { isAuthenticated, user, login, logout } = useSSO({
    authhubUrl: 'http://localhost:8000'
  });
  
  if (!isAuthenticated) {
    return <button onClick={login}>登录</button>;
  }
  
  return (
    <div>
      <h1>Hello, {user?.username}</h1>
      <button onClick={logout}>登出</button>
    </div>
  );
}
```

### 3. Vue SSO 登录

#### 方式一: 使用开箱即用的登录组件

```vue
<template>
  <!-- 登录页面 -->
  <LoginPage
    :authhubUrl="AUTHHUB_URL"
    title="我的应用"
    subtitle="使用飞书账号登录"
  />
  
  <!-- 回调页面 -->
  <SSOCallback
    :authhubUrl="AUTHHUB_URL"
    redirectTo="/dashboard"
  />
  
  <!-- 受保护的视图 -->
  <ProtectedView :authhubUrl="AUTHHUB_URL">
    <div>这是受保护的内容</div>
  </ProtectedView>
</template>

<script setup>
import { LoginPage, SSOCallback, ProtectedView } from '@authhub/sdk/components/vue';
const AUTHHUB_URL = 'http://localhost:8000';
</script>
```

#### 方式二: 使用 SSO Composable

```vue
<template>
  <div v-if="!isAuthenticated">
    <button @click="login">登录</button>
  </div>
  <div v-else>
    <h1>Hello, {{ user?.username }}</h1>
    <button @click="logout">登出</button>
  </div>
</template>

<script setup>
import { useSSO } from '@authhub/sdk/composables';

const { isAuthenticated, user, login, logout } = useSSO({
  authhubUrl: 'http://localhost:8000'
});
</script>
```

### 4. React 权限检查

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

### 5. Express中间件

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

### 6. Next.js中间件

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

