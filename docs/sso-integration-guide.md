# SSO 登录集成指南

本指南详细说明如何在业务系统中集成 AuthHub SSO 登录功能。

## 概述

AuthHub SDK 提供了完整的 SSO 登录模块，支持 **FastAPI**、**React** 和 **Vue** 框架。通过简单的配置，业务系统可以快速接入飞书 SSO 登录，无需自行实现复杂的 OAuth 流程。

## 核心特性

- ✅ **开箱即用** - 提供完整的登录组件和中间件
- ✅ **自动化处理** - 自动处理授权码交换和 Token 存储
- ✅ **安全可靠** - Cookie (FastAPI) 和 localStorage (前端) 安全存储
- ✅ **状态同步** - 支持多标签页登录状态同步
- ✅ **路由保护** - 内置路由保护组件和中间件
- ✅ **类型安全** - 完整的 TypeScript 类型支持

## 登录流程

```
用户 → 点击登录 → SDK 获取登录 URL → 跳转到飞书
  ↓
飞书授权 → 回调到业务系统 → SDK 自动交换 Token
  ↓
存储 Token → 重定向到目标页面 → 完成登录
```

---

## FastAPI 集成

### 1. 安装依赖

```bash
pip install authhub-sdk[fastapi]
```

### 2. 基础集成

```python
from fastapi import FastAPI, Request
from authhub_sdk import AuthHubClient
from authhub_sdk.middleware.fastapi_sso import AuthHubSSOMiddleware

app = FastAPI()

# 初始化 AuthHub 客户端
client = AuthHubClient(
    authhub_url="http://localhost:8000",
    system_id="1",
    system_token="your_system_token",
    namespace="system_a",
    redis_url="redis://localhost:6379"
)

# 添加 SSO 中间件（一行代码完成集成！）
app.add_middleware(
    AuthHubSSOMiddleware,
    client=client,
    callback_path="/auth/callback",      # SSO 回调路径
    login_path="/auth/login",            # 登录路径
    logout_path="/auth/logout",          # 登出路径
    cookie_name="authhub_token",         # Cookie 名称
    cookie_secure=True,                  # 生产环境设为 True
    cookie_httponly=True,                # 防止 XSS
    cookie_samesite="lax",               # 防止 CSRF
    cookie_max_age=3600,                 # 1 小时
    public_routes=['/health', '/docs'],  # 公开路由
    login_required=True,                 # 要求登录
    redirect_to_login=True,              # 未登录时重定向
    after_login_redirect="/dashboard"    # 登录成功后重定向
)

@app.get("/dashboard")
async def dashboard(request: Request):
    """受保护的路由 - 需要登录"""
    user = request.state.user  # 自动注入用户信息
    return {"user": user.get("username")}
```

### 3. 自动提供的路由

中间件会自动注册以下路由：

| 路由 | 方法 | 说明 |
|------|------|------|
| `/auth/login` | GET | 触发 SSO 登录，跳转到飞书授权页 |
| `/auth/callback` | GET | SSO 回调处理（自动交换 Token） |
| `/auth/logout` | GET/POST | 登出，清除 Cookie |

### 4. 配置说明

#### Cookie 配置

```python
cookie_secure=True      # 仅 HTTPS 传输（生产环境必须）
cookie_httponly=True    # 禁止 JavaScript 访问（防 XSS）
cookie_samesite="lax"   # 防 CSRF 攻击
cookie_max_age=3600     # 过期时间（秒）
```

#### 认证配置

```python
login_required=True          # 是否要求登录
redirect_to_login=True       # 未登录时是否重定向到登录页
public_routes=['/health']    # 不需要登录的路由列表
after_login_redirect="/"     # 登录成功后的默认重定向地址
```

### 5. 使用用户信息

```python
@app.get("/api/profile")
async def get_profile(request: Request):
    user = request.state.user
    
    return {
        "username": user.get("username"),
        "email": user.get("email"),
        "roles": user.get("global_roles", []),
        "system_roles": user.get("system_roles", {})
    }
```

---

## React 集成

### 1. 安装依赖

```bash
npm install @authhub/sdk
# or
pnpm add @authhub/sdk
```

### 2. 方式一：使用开箱即用的组件（推荐）

#### 2.1 配置路由

```tsx
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { LoginPage, SSOCallback, ProtectedRoute } from '@authhub/sdk/components';

const AUTHHUB_URL = 'http://localhost:8000';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* 登录页面 */}
        <Route path="/login" element={
          <LoginPage
            authhubUrl={AUTHHUB_URL}
            title="我的应用"
            subtitle="使用飞书账号登录"
          />
        } />
        
        {/* SSO 回调页面 */}
        <Route path="/auth/callback" element={
          <SSOCallback
            authhubUrl={AUTHHUB_URL}
            redirectTo="/dashboard"
            onSuccess={(token) => console.log('登录成功', token)}
          />
        } />
        
        {/* 受保护的页面 */}
        <Route path="/dashboard" element={
          <ProtectedRoute authhubUrl={AUTHHUB_URL}>
            <Dashboard />
          </ProtectedRoute>
        } />
      </Routes>
    </BrowserRouter>
  );
}
```

#### 2.2 使用登录按钮

```tsx
import { LoginButton } from '@authhub/sdk/components';

function MyPage() {
  return (
    <LoginButton authhubUrl="http://localhost:8000">
      使用飞书登录
    </LoginButton>
  );
}
```

### 3. 方式二：使用 SSO Hook

```tsx
import { useSSO } from '@authhub/sdk/hooks';

function MyComponent() {
  const { 
    isAuthenticated,  // 是否已登录
    user,             // 用户信息
    isLoading,        // 加载状态
    login,            // 登录方法
    logout,           // 登出方法
    refresh           // 刷新状态
  } = useSSO({
    authhubUrl: 'http://localhost:8000',
    onLoginSuccess: (user) => {
      console.log('登录成功:', user);
    },
    onLogout: () => {
      console.log('已登出');
    }
  });

  if (isLoading) {
    return <div>加载中...</div>;
  }

  if (!isAuthenticated) {
    return <button onClick={login}>登录</button>;
  }

  return (
    <div>
      <h1>欢迎, {user?.username}</h1>
      <button onClick={logout}>登出</button>
    </div>
  );
}
```

### 4. 组件 API

#### LoginPage

完整的登录页面组件。

```tsx
<LoginPage
  authhubUrl="http://localhost:8000"  // AuthHub 服务地址（必填）
  redirectUri="/auth/callback"         // 回调地址（可选）
  title="我的应用"                      // 标题（可选）
  subtitle="使用飞书账号登录"           // 副标题（可选）
  logo="/logo.png"                     // Logo 图片（可选）
  backgroundColor="linear-gradient..." // 背景色（可选）
  onLoginSuccess={(user) => {}}        // 登录成功回调（可选）
/>
```

#### SSOCallback

自动处理 SSO 回调的组件。

```tsx
<SSOCallback
  authhubUrl="http://localhost:8000"  // AuthHub 服务地址（必填）
  redirectTo="/dashboard"              // 登录成功后重定向（可选）
  onSuccess={(token) => {}}            // 成功回调（可选）
  onError={(error) => {}}              // 失败回调（可选）
  loadingComponent={<Loading />}       // 自定义加载组件（可选）
  errorComponent={(error) => <Error />} // 自定义错误组件（可选）
/>
```

#### ProtectedRoute

路由保护组件，未登录用户会被重定向到登录页。

```tsx
<ProtectedRoute
  authhubUrl="http://localhost:8000"  // AuthHub 服务地址（必填）
  redirectUri="/auth/callback"         // 回调地址（可选）
  fallback={<Loading />}               // 加载时显示（可选）
  unauthorizedComponent={<Unauthorized />} // 未授权显示（可选）
>
  <YourProtectedContent />
</ProtectedRoute>
```

---

## Vue 集成

### 1. 安装依赖

```bash
npm install @authhub/sdk
# or
pnpm add @authhub/sdk
```

### 2. 方式一：使用开箱即用的组件（推荐）

#### 2.1 配置路由

```typescript
// router.ts
import { createRouter, createWebHistory } from 'vue-router';
import Login from './pages/Login.vue';
import Callback from './pages/Callback.vue';
import Dashboard from './pages/Dashboard.vue';

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/login', component: Login },
    { path: '/auth/callback', component: Callback },
    { path: '/dashboard', component: Dashboard },
  ],
});

export default router;
```

#### 2.2 登录页面

```vue
<template>
  <LoginPage
    :authhubUrl="AUTHHUB_URL"
    title="我的应用"
    subtitle="使用飞书账号登录"
    :onLoginSuccess="handleLoginSuccess"
  />
</template>

<script setup>
import { LoginPage } from '@authhub/sdk/components/vue';

const AUTHHUB_URL = 'http://localhost:8000';

const handleLoginSuccess = (user) => {
  console.log('登录成功:', user);
};
</script>
```

#### 2.3 回调页面

```vue
<template>
  <SSOCallback
    :authhubUrl="AUTHHUB_URL"
    redirectTo="/dashboard"
    :onSuccess="handleSuccess"
    :onError="handleError"
  />
</template>

<script setup>
import { SSOCallback } from '@authhub/sdk/components/vue';

const AUTHHUB_URL = 'http://localhost:8000';

const handleSuccess = (token) => {
  console.log('Token交换成功:', token);
};

const handleError = (error) => {
  console.error('登录失败:', error);
};
</script>
```

#### 2.4 受保护的页面

```vue
<template>
  <ProtectedView :authhubUrl="AUTHHUB_URL">
    <div>
      <h1>欢迎, {{ user?.username }}</h1>
      <button @click="handleLogout">登出</button>
    </div>
  </ProtectedView>
</template>

<script setup>
import { useRouter } from 'vue-router';
import { ProtectedView } from '@authhub/sdk/components/vue';
import { useSSO } from '@authhub/sdk/composables';

const AUTHHUB_URL = 'http://localhost:8000';
const router = useRouter();

const { user, logout } = useSSO({ authhubUrl: AUTHHUB_URL });

const handleLogout = () => {
  logout();
  router.push('/login');
};
</script>
```

### 3. 方式二：使用 SSO Composable

```vue
<template>
  <div v-if="isLoading">
    <p>加载中...</p>
  </div>
  <div v-else-if="!isAuthenticated">
    <button @click="login">登录</button>
  </div>
  <div v-else>
    <h1>欢迎, {{ user?.username }}</h1>
    <button @click="logout">登出</button>
  </div>
</template>

<script setup>
import { useSSO } from '@authhub/sdk/composables';

const { 
  isAuthenticated,  // 是否已登录
  user,             // 用户信息
  isLoading,        // 加载状态
  login,            // 登录方法
  logout,           // 登出方法
  refresh           // 刷新状态
} = useSSO({
  authhubUrl: 'http://localhost:8000',
  onLoginSuccess: (user) => {
    console.log('登录成功:', user);
  },
  onLogout: () => {
    console.log('已登出');
  }
});
</script>
```

---

## 最佳实践

### 1. 环境配置

使用环境变量管理配置：

```typescript
// config.ts
export const AUTHHUB_URL = process.env.VITE_AUTHHUB_URL || 'http://localhost:8000';
```

```bash
# .env
VITE_AUTHHUB_URL=https://authhub.company.com
```

### 2. 错误处理

```tsx
<SSOCallback
  authhubUrl={AUTHHUB_URL}
  onError={(error) => {
    // 记录错误日志
    console.error('SSO登录失败:', error);
    
    // 显示友好提示
    toast.error('登录失败，请重试');
    
    // 重定向到登录页
    setTimeout(() => {
      window.location.href = '/login';
    }, 2000);
  }}
/>
```

### 3. Token 过期处理

SDK 会自动检查 Token 是否过期，过期时会触发重新登录。

```tsx
const { isAuthenticated, refresh } = useSSO({ authhubUrl: AUTHHUB_URL });

// 定期刷新状态
useEffect(() => {
  const interval = setInterval(() => {
    refresh();
  }, 60000); // 每分钟检查一次

  return () => clearInterval(interval);
}, [refresh]);
```

### 4. 多标签页同步

SDK 通过 `localStorage` 事件自动支持多标签页登录状态同步。当用户在一个标签页登出时，其他标签页会自动感知。

### 5. 生产环境配置

#### FastAPI

```python
# 生产环境必须启用安全设置
app.add_middleware(
    AuthHubSSOMiddleware,
    client=client,
    cookie_secure=True,      # 仅 HTTPS
    cookie_httponly=True,    # 防 XSS
    cookie_samesite="lax",   # 防 CSRF
)
```

#### 前端

```typescript
// 确保使用 HTTPS
const AUTHHUB_URL = 'https://authhub.company.com';
```

---

## 故障排查

### 常见问题

#### 1. 回调后显示"缺少授权码"

**原因：** 飞书回调地址配置错误。

**解决：** 确保在飞书开放平台配置的回调地址与 SDK 中的 `callback_path` 或 `redirectUri` 一致。

#### 2. Token 交换失败

**原因：** AuthHub 服务地址不正确或网络不通。

**解决：** 检查 `authhubUrl` 配置，确保可以访问。

#### 3. Cookie 未设置

**原因：** 浏览器阻止了第三方 Cookie。

**解决：** 使用相同域名或配置 `SameSite=None; Secure`。

#### 4. 无限重定向循环

**原因：** 登录页面未添加到 `public_routes`。

**解决：** 在 FastAPI 中将登录路由添加到 `public_routes`。

---

## 示例项目

完整的示例项目可以在 SDK 仓库中找到：

- **FastAPI:** `sdk/python/examples/fastapi_sso_example.py`
- **React:** `sdk/typescript/examples/react-sso/`
- **Vue:** `sdk/typescript/examples/vue-sso/`

---

## 技术支持

如有问题，请联系技术支持或查阅完整文档：

- 文档: https://docs.authhub.com
- GitHub: https://github.com/yourcompany/authhub

