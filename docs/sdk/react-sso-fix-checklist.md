# React SSO 示例修复清单

## 📋 已完成的修改

### ✅ 前端修改

**文件**: `sdk/typescript/examples/react-sso/src/lib/auth-client.ts`

- [x] 修改参数名：`return_url` → `redirect`
- [x] 添加路径转换逻辑：相对路径 → 完整 URL
- [x] 兼容已有完整 URL 的情况

**代码变更**:
```typescript
// 之前
url.searchParams.set('return_url', returnUrl);

// 之后
const fullReturnUrl = returnUrl.startsWith('http')
  ? returnUrl
  : window.location.origin + returnUrl;
url.searchParams.set('redirect', fullReturnUrl);
```

---

### ✅ 后端修改

**文件**: `sdk/python/examples/fastapi_sso_example.py`

- [x] 添加 CORS 中间件配置
- [x] 新增 `/api/me` 接口
- [x] 确保 `/api/me` 不在公开路由中
- [x] 添加调试接口 `/debug/cookies`（可选）

**关键配置**:
```python
# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,  # 必须！
    allow_methods=["*"],
    allow_headers=["*"],
)

# setup_sso 配置
public_routes=["/health", "/docs", "/openapi.json"]  # 不包含 /api/me
```

---

### ✅ 文档更新

- [x] 创建详细修复文档：`docs/sdk/react-sso-redirect-fix.md`
- [x] 更新示例 README：`sdk/typescript/examples/react-sso/README.md`
- [x] 创建修复清单：`docs/sdk/react-sso-fix-checklist.md`（本文件）

---

## 🔍 关键问题与解决方案

| 问题 | 原因 | 解决方案 | 影响 |
|------|------|---------|------|
| 登录后跳转到后端 | 参数名不匹配 + 相对路径 | 使用 `redirect` + 完整 URL | ✅ 正确跳转回前端 |
| /api/me 返回 401 | 接口在公开路由中 | 移除公开路由配置 | ✅ 中间件验证 Token |
| 跨域 Cookie 无法传递 | 缺少 CORS 配置 | 添加 CORS + allow_credentials | ✅ Cookie 正常工作 |

---

## 🧪 测试验证

### 功能测试

- [x] 点击登录按钮能跳转到飞书
- [x] 飞书登录后跳转回前端 `http://localhost:5173/dashboard`
- [x] Dashboard 显示用户信息（用户名、邮箱、角色等）
- [x] 刷新页面后仍保持登录状态
- [x] 登出功能正常工作

### 技术验证

- [x] 浏览器开发者工具能看到 `authhub_token` Cookie
- [x] Cookie 设置为 `HttpOnly`
- [x] `/api/me` 请求返回 200 状态码
- [x] 浏览器控制台无 CORS 错误
- [x] 登录 URL 包含 `redirect=http://localhost:5173/dashboard`

---

## 📝 开发者注意事项

### 1. 参数名约定

后端 FastAPI SSO 中间件使用的参数名是 `redirect`，不是 `return_url`。前端必须使用一致的参数名。

### 2. 完整 URL 的重要性

在跨域场景下，必须传递完整 URL（包含协议和域名），否则后端会将其理解为后端自己的路径。

```javascript
// ❌ 错误
url.searchParams.set('redirect', '/dashboard');

// ✅ 正确
url.searchParams.set('redirect', 'http://localhost:5173/dashboard');
```

### 3. /api/me 路由配置

**不要**将 `/api/me` 添加到公开路由中，否则中间件会跳过 Token 验证，导致 `request.state.user` 为空。

```python
# ❌ 错误
public_routes=["/health", "/api/me"]

# ✅ 正确  
public_routes=["/health"]
```

### 4. CORS 配置

`allow_credentials=True` 是必须的，否则浏览器不会在跨域请求中携带 Cookie。

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,  # ⚠️ 必须！
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 5. SameSite 策略

开发环境使用 `samesite="lax"` 即可。生产环境建议根据实际情况选择：
- `lax`：大多数场景适用
- `strict`：更严格，某些跨站场景可能有问题
- `none`：需要配合 `secure=True`（HTTPS）

---

## 🚀 生产环境配置

### 前端配置

更新 `src/config.ts`：
```typescript
export const BACKEND_URL = 'https://api.yourdomain.com';
```

### 后端配置

```python
# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://app.yourdomain.com"],  # 前端生产域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# setup_sso 配置
setup_sso(
    app,
    client=authhub_client,
    cookie_secure=True,  # HTTPS 环境必须
    cookie_httponly=True,
    cookie_samesite="lax",
    ...
)
```

### 飞书回调配置

在飞书开放平台配置回调地址：
```
https://api.yourdomain.com/auth/callback
```

---

## 🐛 常见问题排查

### 问题 1: 登录后还是跳到后端

**检查**：
1. 前端代码是否使用了 `redirect` 参数（不是 `return_url`）
2. 是否传递了完整 URL（包含 `http://` 或 `https://`）
3. 查看浏览器地址栏，确认登录 URL 中的 `redirect` 参数值

### 问题 2: /api/me 返回 401

**检查**：
1. `/api/me` 是否在 `public_routes` 中（不应该在）
2. Cookie 是否正确设置（开发者工具查看）
3. 前端请求是否带 `withCredentials: true`
4. CORS 是否配置了 `allow_credentials=True`

### 问题 3: CORS 错误

**检查**：
1. 后端是否添加了 `CORSMiddleware`
2. `allow_origins` 是否包含前端域名
3. `allow_credentials` 是否为 `True`
4. 前端域名和后端配置是否完全匹配（包括端口）

### 问题 4: Cookie 未设置

**检查**：
1. 浏览器开发者工具 → Application → Cookies
2. 查看 `http://localhost:8001` 下是否有 `authhub_token`
3. 如果没有，查看后端日志是否有错误
4. 访问 `http://localhost:8001/debug/cookies` 查看 Cookie 状态

---

## 📚 相关文档

- [详细修复文档](./react-sso-redirect-fix.md)
- [React SSO 示例 README](../../sdk/typescript/examples/react-sso/README.md)
- [Python SDK SSO 集成指南](../../sdk/python/README.md)
- [FastAPI SSO 中间件源码](../../sdk/python/authhub_sdk/middleware/fastapi_sso.py)

---

## ✨ 修复效果

### 修复前
```
用户点击登录 → 飞书授权 → 跳转到 http://localhost:8001/dashboard (后端)
❌ 停留在后端页面，显示 JSON 数据
```

### 修复后
```
用户点击登录 → 飞书授权 → 跳转到 http://localhost:5173/dashboard (前端)
✅ 前端页面显示用户信息，UI 完整
```

---

**最后更新**: 2025-11-17  
**修复状态**: ✅ 已完成并验证

