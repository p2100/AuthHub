<!-- 5cf6d106-2ea0-40cc-9a93-adf49f0925c3 67c9377e-db60-431c-a9e2-04c1e4a8aa7c -->
# Refresh Token 自动刷新迁移计划

## 架构设计

采用 Redis 存储 + Token Rotation 机制：

- Access Token: 60分钟有效期
- Refresh Token: 7天有效期，每次刷新生成新的 refresh token
- 存储方式: Redis（key: `refresh_token:{token}`, value: user_id, TTL: 7天）

## 实施阶段

### 阶段一：后端核心实现

#### 1. 修改 Schema 定义

文件: `backend/app/schemas/auth.py`

修改 `TokenResponse` 类：

```python
class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str  # 新增
    token_type: str = "bearer"
    expires_in: int = 3600
    refresh_expires_in: int = 604800  # 7天
```

新增 `RefreshTokenRequest` 类：

```python
class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(..., description="Refresh Token")
```

#### 2. 扩展 JWT Handler

文件: `backend/app/core/security.py`

在 `JWTHandler` 类中新增方法：

```python
def create_refresh_token(self, user_id: int) -> str:
    """生成 refresh token 并存储到 Redis"""
    token = secrets.token_urlsafe(64)
    redis_client.setex(
        f"refresh_token:{token}",
        7 * 24 * 3600,
        str(user_id)
    )
    return token

def verify_refresh_token(self, token: str) -> Optional[int]:
    """验证 refresh token"""
    user_id = redis_client.get(f"refresh_token:{token}")
    return int(user_id) if user_id else None

def revoke_refresh_token(self, token: str):
    """撤销 refresh token"""
    redis_client.delete(f"refresh_token:{token}")
```

#### 3. 修改登录回调接口

文件: `backend/app/auth/router.py`

修改 `feishu_callback` 和 `exchange_sso_token` 函数，在返回时生成 refresh token：

```python
# 在生成 access_token 后
refresh_token = jwt_handler.create_refresh_token(user.id)

return TokenResponse(
    access_token=token,
    refresh_token=refresh_token,
    token_type="bearer",
    expires_in=3600,
    refresh_expires_in=604800
)
```

#### 4. 新增 refresh 端点

文件: `backend/app/auth/router.py`

```python
@router.post("/refresh", response_model=TokenResponse)
async def refresh_access_token(
    request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    刷新访问令牌
    
    使用 refresh token 获取新的 access token 和 refresh token（rotation）
    """
    # 1. 验证 refresh token
    user_id = jwt_handler.verify_refresh_token(request.refresh_token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    
    # 2. 获取用户信息
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # 3. 收集权限
    permission_collector = PermissionCollector(db)
    user_permissions = await permission_collector.collect(user.id)
    
    # 4. 撤销旧的 refresh token（rotation）
    jwt_handler.revoke_refresh_token(request.refresh_token)
    
    # 5. 生成新的 tokens
    access_token = jwt_handler.create_access_token(...)
    new_refresh_token = jwt_handler.create_refresh_token(user.id)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
        expires_in=3600,
        refresh_expires_in=604800
    )
```

#### 5. 修改登出接口

文件: `backend/app/auth/router.py`

在 `logout` 函数中添加 refresh token 撤销：

```python
@router.post("/logout")
async def logout(
    current_user: dict = Depends(get_current_user),
    refresh_token: Optional[str] = None
):
    # 撤销 access token（黑名单）
    jti = current_user.get("jti", "")
    if jti:
        jwt_handler.add_to_blacklist(jti, expire_seconds=3600)
    
    # 撤销 refresh token
    if refresh_token:
        jwt_handler.revoke_refresh_token(refresh_token)
    
    return {"message": "登出成功"}
```

### 阶段二：前端实现

#### 6. 修改 API Utils

文件: `frontend/src/utils/api.ts`

扩展 token 管理函数：

```typescript
// 存储 refresh token
export function setRefreshToken(token: string): void {
  localStorage.setItem('refresh_token', token)
}

export function getRefreshToken(): string | null {
  return localStorage.getItem('refresh_token')
}

// 清除时也要清除 refresh token
export function clearToken(): void {
  localStorage.removeItem('auth_token')
  localStorage.removeItem('refresh_token')
}
```

新增刷新函数并修改请求拦截器：

```typescript
let isRefreshing = false
let refreshSubscribers: Array<(token: string) => void> = []

async function refreshAccessToken(): Promise<boolean> {
  if (isRefreshing) {
    return new Promise((resolve) => {
      refreshSubscribers.push((token: string) => {
        resolve(!!token)
      })
    })
  }

  isRefreshing = true
  const refreshToken = getRefreshToken()
  
  if (!refreshToken) {
    isRefreshing = false
    return false
  }

  try {
    const response = await fetch(`${API_BASE_URL}/auth/refresh`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: refreshToken })
    })

    if (response.ok) {
      const data = await response.json()
      setToken(data.access_token)
      setRefreshToken(data.refresh_token)
      
      // 通知等待的请求
      refreshSubscribers.forEach(cb => cb(data.access_token))
      refreshSubscribers = []
      isRefreshing = false
      return true
    }
  } catch (error) {
    console.error('Token refresh failed:', error)
  }

  isRefreshing = false
  return false
}

// 修改 request 函数
async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  // ... 原有代码 ...
  
  if (response.status === 401) {
    // 尝试刷新 token
    const refreshed = await refreshAccessToken()
    if (refreshed) {
      // 重试原请求
      return request<T>(endpoint, options)
    }
    
    // 刷新失败，跳转登录
    clearToken()
    window.location.href = '/login'
    throw new ApiRequestError('未授权，请重新登录', 401)
  }
  
  // ... 其他代码 ...
}
```

#### 7. 修改 AuthContext

文件: `frontend/src/contexts/AuthContext.tsx`

修改 login 函数以保存 refresh token：

```typescript
const login = async (accessToken: string, refreshToken: string) => {
  setToken(accessToken)
  setRefreshToken(refreshToken)
  await fetchUser()
}
```

修改 logout 函数：

```typescript
const logout = async () => {
  const refreshToken = getRefreshToken()
  try {
    await apiPost('/auth/logout', { refresh_token: refreshToken })
  } catch (error) {
    console.error('登出API调用失败:', error)
  } finally {
    clearToken()
    setUser(null)
  }
}
```

#### 8. 修改登录回调页面

文件: `frontend/src/pages/Login/Callback.tsx`

更新以接收 refresh_token：

```typescript
const tokenData = await apiGet<TokenResponse>(`/auth/feishu/callback?code=${code}`)
await login(tokenData.access_token, tokenData.refresh_token)
```

#### 9. 更新 TypeScript 类型

文件: `frontend/src/types/api.ts`

```typescript
export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
  refresh_expires_in: number
}
```

### 阶段三：Python SDK 升级

#### 10. 扩展 SSO Client

文件: `sdk/python/authhub_sdk/sso.py`

修改 `exchange_token` 和 `handle_callback` 返回 refresh token：

```python
def exchange_token(self, code: str, state: Optional[str] = None) -> Dict[str, str]:
    """返回包含 refresh_token 的完整响应"""
    # ... 原有代码 ...
    return response.json()  # 包含 access_token 和 refresh_token

def handle_callback(self, code: str, state: Optional[str] = None) -> Dict[str, str]:
    """返回完整的 token 数据"""
    return self.exchange_token(code, state)
```

#### 11. 扩展 AuthHub Client

文件: `sdk/python/authhub_sdk/client.py`

新增 refresh token 方法：

```python
def refresh_token(self, refresh_token: str) -> Dict[str, str]:
    """
    刷新访问令牌
    
    Args:
        refresh_token: Refresh Token
        
    Returns:
        新的 token 数据（包含 access_token 和 refresh_token）
    """
    try:
        response = requests.post(
            f"{self.authhub_url}/api/v1/auth/refresh",
            json={"refresh_token": refresh_token},
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise Exception(f"Token刷新失败: {str(e)}")
```

#### 12. 更新 FastAPI SSO 中间件

文件: `sdk/python/authhub_sdk/middleware/fastapi_sso.py`

修改 `callback` 路由以设置 refresh token cookie：

```python
@app.get(callback_path)
async def callback(request: Request, code: str, state: Optional[str] = None, ...):
    # 交换 Token
    token_data = sso_client.handle_callback(code, state)
    access_token = token_data["access_token"]
    refresh_token = token_data["refresh_token"]
    
    response = RedirectResponse(url=redirect_url)
    response.set_cookie(
        key=cookie_name,
        value=access_token,
        max_age=cookie_max_age,
        httponly=cookie_httponly,
        secure=cookie_secure,
        samesite=cookie_samesite,
    )
    response.set_cookie(
        key=f"{cookie_name}_refresh",
        value=refresh_token,
        max_age=7 * 24 * 3600,  # 7天
        httponly=True,
        secure=cookie_secure,
        samesite=cookie_samesite,
    )
    return response
```

添加 token 自动刷新逻辑到中间件：

```python
async def dispatch(self, request: Request, call_next: Callable):
    # ... 原有验证逻辑 ...
    
    # Token 验证失败，尝试刷新
    except Exception as e:
        refresh_token = request.cookies.get(f"{self.cookie_name}_refresh")
        if refresh_token:
            try:
                new_tokens = self.client.refresh_token(refresh_token)
                request.state.user = self.client.verify_token(new_tokens["access_token"])
                
                # 设置新 cookies
                response = await call_next(request)
                response.set_cookie(self.cookie_name, new_tokens["access_token"], ...)
                response.set_cookie(f"{self.cookie_name}_refresh", new_tokens["refresh_token"], ...)
                return response
            except:
                pass
        
        # 刷新失败，重定向登录
        if self.login_required and self.redirect_to_login:
            return RedirectResponse(url=f"{self.login_path}?redirect={path}")
```

### 阶段四：TypeScript SDK 升级

#### 13. 扩展 TokenManager

文件: `sdk/typescript/src/tokenManager.ts`

添加 refresh token 管理：

```typescript
const REFRESH_TOKEN_KEY = 'authhub_refresh_token';

export class TokenManager {
  static setRefreshToken(token: string): void {
    if (typeof window === 'undefined') return;
    localStorage.setItem(REFRESH_TOKEN_KEY, token);
  }

  static getRefreshToken(): string | null {
    if (typeof window === 'undefined') return null;
    return localStorage.getItem(REFRESH_TOKEN_KEY);
  }

  static clear(): void {
    this.removeToken();
    if (typeof window === 'undefined') return;
    localStorage.removeItem(REFRESH_TOKEN_KEY);
  }
}
```

#### 14. 扩展 SSO Client

文件: `sdk/typescript/src/sso.ts`

更新接口和方法：

```typescript
export interface SSOTokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
  refresh_expires_in: number;
}

async handleCallback(code: string, state?: string): Promise<SSOTokenResponse> {
  const tokenData = await this.exchangeToken(code, state);
  
  // 存储两个 token
  TokenManager.setToken(tokenData.access_token);
  TokenManager.setRefreshToken(tokenData.refresh_token);
  
  // 解析并存储 payload
  try {
    const payload = await this.verifier.verify(tokenData.access_token);
    TokenManager.setTokenPayload(payload);
  } catch (error) {
    console.warn('Token验证失败，但仍然存储:', error);
  }

  return tokenData;
}
```

#### 15. 新增 AuthClient 刷新方法

文件: `sdk/typescript/src/auth-client.ts`（如不存在则创建）

```typescript
export class AuthClient {
  private authhubUrl: string;

  constructor(authhubUrl: string) {
    this.authhubUrl = authhubUrl.replace(/\/$/, '');
  }

  async refreshToken(refreshToken: string): Promise<SSOTokenResponse> {
    try {
      const response = await axios.post<SSOTokenResponse>(
        `${this.authhubUrl}/api/v1/auth/refresh`,
        { refresh_token: refreshToken }
      );
      return response.data;
    } catch (error) {
      throw new Error(`Token刷新失败: ${error}`);
    }
  }
}
```

#### 16. 更新 React Hooks

文件: `sdk/typescript/src/hooks/useAuth.ts`

添加自动刷新逻辑：

```typescript
// 在 useAuth hook 中添加刷新逻辑
const refreshAccessToken = async (): Promise<boolean> => {
  const refreshToken = TokenManager.getRefreshToken();
  if (!refreshToken) return false;

  try {
    const authClient = new AuthClient(authhubUrl);
    const newTokens = await authClient.refreshToken(refreshToken);
    
    TokenManager.setToken(newTokens.access_token);
    TokenManager.setRefreshToken(newTokens.refresh_token);
    
    return true;
  } catch {
    return false;
  }
};
```

### 阶段五：文档更新

#### 17. 更新 API 文档

文件: `docs/authentication-implementation.md`

添加 refresh token 相关章节：

- Token 刷新流程说明
- `/auth/refresh` API 文档
- Token rotation 机制说明
- 安全最佳实践

#### 18. 更新 SSO 集成指南

文件: `docs/sso-integration-guide.md`

更新所有代码示例，展示如何处理 refresh token：

- 前端集成示例
- Python SDK 使用示例
- TypeScript SDK 使用示例
- Cookie 和 localStorage 的选择建议

#### 19. 新增迁移指南

文件: `docs/refresh-token-migration-guide.md`（新建）

为现有用户提供升级指南：

- Breaking changes 说明
- 升级步骤
- 代码迁移示例
- 常见问题解答

### 阶段六：测试与验证

#### 20. 后端测试

- 测试 refresh token 生成和验证
- 测试 token rotation 机制
- 测试并发刷新请求
- 测试过期 token 处理
- 测试 Redis 存储和 TTL

#### 21. 前端测试

- 测试自动刷新功能
- 测试并发请求时的刷新逻辑
- 测试 token 过期后的重定向
- 测试登出时的 token 清理

#### 22. SDK 测试

- 测试 Python SDK 的 refresh 方法
- 测试 TypeScript SDK 的 refresh 方法
- 测试中间件的自动刷新
- 测试 React/Vue 组件的集成

#### 23. 集成测试

- 测试完整的登录-刷新-登出流程
- 测试跨系统的 SSO 场景
- 测试高并发下的性能
- 验证 Redis 内存使用

## 向后兼容说明

由于选择了方案 2a（直接升级，不兼容旧版本），所有客户端必须同步升级：

1. 后端部署后，旧的登录请求将返回新格式（包含 refresh_token）
2. 旧客户端会忽略 refresh_token 字段，继续使用 access_token（60分钟后过期需重新登录）
3. 新客户端会同时使用两个 token，享受自动刷新功能

建议部署顺序：

1. 后端先部署（向前兼容）
2. 前端和 SDK 尽快升级
3. 通知所有使用方在 1 周内完成升级

## 预计工作量

- 后端开发：4-6 小时
- 前端开发：3-4 小时
- Python SDK：2-3 小时
- TypeScript SDK：2-3 小时
- 测试验证：4-6 小时
- 文档更新：2-3 小时

总计：17-25 小时（约 2-3 个工作日）

### To-dos

- [ ] 修改 backend/app/schemas/auth.py，更新 TokenResponse 和新增 RefreshTokenRequest
- [ ] 扩展 backend/app/core/security.py 的 JWTHandler，添加 refresh token 生成/验证/撤销方法
- [ ] 修改 backend/app/auth/router.py 的登录回调接口，返回 refresh_token
- [ ] 在 backend/app/auth/router.py 新增 /auth/refresh 端点
- [ ] 修改 backend/app/auth/router.py 的登出接口，撤销 refresh token
- [ ] 修改 frontend/src/utils/api.ts，添加 refresh token 管理和自动刷新逻辑
- [ ] 修改 frontend/src/contexts/AuthContext.tsx，处理 refresh token
- [ ] 修改 frontend/src/pages/Login/Callback.tsx，接收并保存 refresh_token
- [ ] 更新 frontend/src/types/api.ts 的 TokenResponse 类型定义
- [ ] 修改 sdk/python/authhub_sdk/sso.py，返回完整 token 数据
- [ ] 扩展 sdk/python/authhub_sdk/client.py，添加 refresh_token 方法
- [ ] 更新 sdk/python/authhub_sdk/middleware/fastapi_sso.py，添加自动刷新逻辑
- [ ] 扩展 sdk/typescript/src/tokenManager.ts，添加 refresh token 管理
- [ ] 修改 sdk/typescript/src/sso.ts，处理 refresh token
- [ ] 创建/更新 sdk/typescript/src/auth-client.ts，添加 refreshToken 方法
- [ ] 更新 sdk/typescript/src/hooks/useAuth.ts，添加自动刷新逻辑
- [ ] 更新 docs/authentication-implementation.md，添加 refresh token API 文档
- [ ] 更新 docs/sso-integration-guide.md，更新代码示例
- [ ] 新增 docs/refresh-token-migration-guide.md 迁移指南
- [ ] 测试后端 refresh token 功能（生成、验证、rotation、过期处理）
- [ ] 测试前端自动刷新功能和用户体验
- [ ] 测试 Python 和 TypeScript SDK 的 refresh 功能
- [ ] 完整集成测试和性能验证