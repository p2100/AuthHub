# React SSO Example

这是一个使用 AuthHub SDK 的 React SSO 示例应用。

## 功能展示

- ✅ 使用 `LoginPage` 组件的登录页面
- ✅ 使用 `SSOCallback` 组件的回调处理
- ✅ 使用 `ProtectedRoute` 保护的路由
- ✅ 使用 `useSSO` hook 的状态管理
- ✅ 完整的登录/登出流程

## 快速开始

### 1. 安装依赖

```bash
npm install
# or
pnpm install
```

### 2. 配置

修改 `src/config.ts` 中的配置：

```typescript
export const AUTHHUB_URL = 'http://localhost:8000'; // AuthHub服务地址
```

### 3. 启动开发服务器

```bash
npm run dev
```

访问 http://localhost:5173

## 项目结构

```
src/
  ├── App.tsx           # 主应用组件
  ├── config.ts         # 配置文件
  ├── main.tsx          # 入口文件
  └── pages/
      ├── Login.tsx     # 登录页面
      ├── Callback.tsx  # SSO回调页面
      ├── Dashboard.tsx # 仪表板(受保护)
      └── Profile.tsx   # 用户资料(受保护)
```

## 使用说明

### 1. 基础登录页面

```tsx
import { LoginPage } from '@authhub/sdk/components';

function Login() {
  return (
    <LoginPage
      authhubUrl="http://localhost:8000"
      title="我的应用"
      subtitle="使用飞书账号登录"
    />
  );
}
```

### 2. SSO回调处理

```tsx
import { SSOCallback } from '@authhub/sdk/components';

function Callback() {
  return (
    <SSOCallback
      authhubUrl="http://localhost:8000"
      redirectTo="/dashboard"
      onSuccess={() => console.log('登录成功')}
    />
  );
}
```

### 3. 保护路由

```tsx
import { ProtectedRoute } from '@authhub/sdk/components';

function Dashboard() {
  return (
    <ProtectedRoute authhubUrl="http://localhost:8000">
      <div>这是受保护的内容</div>
    </ProtectedRoute>
  );
}
```

### 4. 使用 Hook

```tsx
import { useSSO } from '@authhub/sdk/hooks';

function MyComponent() {
  const { isAuthenticated, user, login, logout } = useSSO({
    authhubUrl: 'http://localhost:8000',
  });

  if (!isAuthenticated) {
    return <button onClick={login}>登录</button>;
  }

  return (
    <div>
      <p>欢迎, {user?.username}</p>
      <button onClick={logout}>登出</button>
    </div>
  );
}
```

## 许可证

MIT

