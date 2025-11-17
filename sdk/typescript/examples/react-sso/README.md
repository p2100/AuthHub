# AuthHub React SSO 示例 (轻量版)

这是一个使用 **AuthHub TypeScript SDK** (`@chenjing194/authhub-sdk`) 的 React SSO 示例应用。

## 核心理念

这个示例展示了**前后端分离架构**下的最佳实践：

- **前端**：使用 AuthHub SDK 的 `useAuth` Hook（从 npm 包导入）
- **后端**：使用完整的 Python SDK 处理所有 OAuth 逻辑
- **Token**：存储在 HttpOnly Cookie 中，无法被 JavaScript 访问

## 功能

- ✅ **飞书 SSO 登录**：点击按钮跳转到业务后端
- ✅ **自动回调处理**：后端完成 OAuth 流程，回跳到前端
- ✅ **安全的 Token 管理**：HttpOnly Cookie
- ✅ **简单的状态管理**：只需一个 `useAuth` Hook
- ✅ **用户信息展示**：从后端 API 获取
- ✅ **登出功能**：清除 Cookie
- ✅ **跨域支持**：后端配置 CORS，支持前后端分离

## 前置要求

1. **运行 AuthHub 服务** (默认 http://localhost:8000)
2. **运行业务后端** (FastAPI 示例，默认 http://localhost:8001)
3. **配置飞书应用的回调地址** (`http://127.0.0.1:8001/auth/callback`)

## 配置

修改 `src/config.ts`:

```typescript
export const BACKEND_URL = 'http://localhost:8001'; // 你的业务后端地址

export const AUTH_CONFIG = {
  backendUrl: BACKEND_URL,
  loginPath: '/auth/login',    // 必须与后端 setup_sso 的 login_path 一致
  logoutPath: '/auth/logout',  // 必须与后端 setup_sso 的 logout_path 一致
  mePath: '/api/me',           // 后端提供的用户信息接口
};
```

**重要提示**：
- `backendUrl` 是你的业务后端地址，不是 AuthHub 地址
- 路径配置必须与后端 `setup_sso()` 的配置保持一致
- SDK 默认路径是 `/api/v1/auth/*`，但本示例使用 `/auth/*` 以简化配置

## 运行步骤

### 1. 启动 AuthHub 服务

```bash
cd ../../../backend
uvicorn app.main:app --port 8000
```

### 2. 启动业务后端（FastAPI 示例）

```bash
cd ../sdk/python/examples
python fastapi_sso_example.py
```

这将在 http://localhost:8001 启动后端服务。

### 3. 安装前端依赖并启动

```bash
cd ../../typescript/examples/react-sso

# 安装依赖
npm install
# 或者
pnpm install
# 或者
yarn install

# 启动开发服务器
npm run dev
```

访问 http://localhost:5173

## 项目结构

```
src/
├── hooks/
│   └── useAuth.ts      # 重新导出 SDK 的 useAuth
├── pages/
│   ├── Login.tsx       # 登录页面（简单的按钮 + 跳转）
│   ├── Callback.tsx    # 回调页面（后端已处理，直接重定向）
│   └── Dashboard.tsx   # 用户仪表板（展示用户信息）
├── config.ts           # 配置文件（业务后端地址）
└── App.tsx            # 应用入口
```

**注意**：本示例使用 `@chenjing194/authhub-sdk` npm 包，不再包含本地实现的 `auth-client.ts`。

## 核心代码

### 前端（超简单）

```tsx
import { useAuth } from '@chenjing194/authhub-sdk';
import { BACKEND_URL } from './config';

function App() {
  const { user, loading, isAuthenticated, login, logout } = useAuth({
    backendUrl: BACKEND_URL
  });

  if (loading) return <div>Loading...</div>;
  
  if (!isAuthenticated) {
    return <button onClick={() => login()}>登录</button>;
  }

  return (
    <div>
      <p>欢迎, {user?.username}</p>
      <button onClick={logout}>登出</button>
    </div>
  );
}
```

**注意**：直接从 `@chenjing194/authhub-sdk` 导入 `useAuth`，无需本地实现。

### 后端（一行集成）

```python
from fastapi import FastAPI
from authhub_sdk import AuthHubClient
from authhub_sdk.middleware.fastapi_sso import setup_sso

app = FastAPI()
authhub_client = AuthHubClient(...)

# 一行代码完成 SSO 集成！
setup_sso(app, client=authhub_client)

# 提供用户信息接口
@app.get("/api/me")
async def get_me(request: Request):
    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(status_code=401, detail="未登录")
    return user
```

## 工作流程

```
1. 用户点击"登录"按钮
   ↓
2. 前端跳转到业务后端 /auth/login?redirect=http://localhost:5173/dashboard
   ↓
3. 后端生成飞书 OAuth URL 并重定向
   ↓
4. 用户在飞书完成登录
   ↓
5. 飞书回调到业务后端 /auth/callback
   ↓
6. 后端交换 Token，设置 HttpOnly Cookie
   ↓
7. 后端重定向回前端 http://localhost:5173/dashboard
   ↓
8. 前端从后端 /api/me 获取用户信息（携带 Cookie）
   ↓
9. 展示用户信息
```

**关键点**：
- 前端传递**完整的 URL**（`http://localhost:5173/dashboard`）而不是相对路径
- 后端设置 Cookie 后重定向回前端
- 前端后续请求自动携带 Cookie 进行认证

## 与传统 SDK 的对比

| 特性 | 轻量版（本示例） | 传统版 |
|------|----------------|--------|
| **前端代码量** | ~100 行 | ~500 行 |
| **OAuth 处理** | 后端 | 前端 |
| **Token 存储** | HttpOnly Cookie | localStorage |
| **安全性** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **复杂度** | 低 | 中 |
| **适用场景** | 前后端分离 | 纯前端应用 |

## 注意事项

### 1. CORS 配置

确保业务后端正确配置 CORS，允许前端域名访问：

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # 前端地址
    allow_credentials=True,  # 重要！允许携带 Cookie
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 2. Cookie 配置

生产环境建议使用：

```python
setup_sso(
    app,
    client=authhub_client,
    cookie_secure=True,      # HTTPS 环境
    cookie_httponly=True,    # 防止 XSS 攻击
    cookie_samesite="lax",   # 防止 CSRF 攻击
)
```

### 3. 飞书回调地址

在飞书开放平台配置：
- `http://127.0.0.1:8001/auth/callback` (开发)
- `https://yourdomain.com/auth/callback` (生产)

### 4. 网络问题

如果遇到 SSL 证书问题无法安装依赖，可以：

```bash
# 使用 npm
npm config set strict-ssl false
npm install

# 或者使用国内镜像
npm config set registry https://registry.npmmirror.com
npm install
```

## 为什么选择轻量版？

1. **更安全**：Token 在 HttpOnly Cookie 中，JS 无法访问
2. **更简单**：前端只需要一个 Hook，无需处理复杂的 OAuth 流程
3. **更标准**：遵循前后端分离的最佳实践
4. **更灵活**：后端可以使用任何语言/框架

## 了解更多

- [TypeScript SDK 文档](../../README.md)
- [Python SDK 文档](../../../python/README.md)
- [FastAPI SSO 示例](../../../python/examples/fastapi_sso_example.py)
