# AuthHub Python SDK

AuthHub统一权限平台的Python SDK,提供本地Token验证和权限校验功能。

## 功能特性

- ✅ 本地Token验证(RS256)
- ✅ 本地权限校验(零网络开销)
- ✅ 配置自动同步
- ✅ 权限变更实时通知
- ✅ 装饰器支持
- ✅ FastAPI/Flask/Django中间件

## 安装

```bash
# 基础安装
pip install authhub-sdk

# 包含FastAPI支持
pip install authhub-sdk[fastapi]

# 包含Flask支持
pip install authhub-sdk[flask]

# 包含Django支持
pip install authhub-sdk[django]
```

## 快速开始

### 1. 初始化SDK

```python
from authhub_sdk import AuthHubClient

client = AuthHubClient(
    authhub_url="https://authhub.company.com",
    system_id="system_a",
    system_token="your_system_token",
    namespace="system_a",
    redis_url="redis://localhost:6379"
)
```

### 2. 使用装饰器

```python
from authhub_sdk.decorators import require_auth, require_role, require_permission

@require_auth
def get_user_profile(user_info):
    return {"user": user_info}

@require_role("editor")
def edit_document(doc_id, user_info):
    # 编辑文档
    pass

@require_permission("document", "write")
def create_document(user_info):
    # 创建文档
    pass
```

### 3. FastAPI集成

```python
from fastapi import FastAPI
from authhub_sdk.middleware.fastapi import AuthHubMiddleware

app = FastAPI()
app.add_middleware(AuthHubMiddleware, client=client)

@app.get("/api/documents")
async def get_documents(request: Request):
    user = request.state.user  # 自动注入用户信息
    return {"documents": []}
```

### 4. 手动验证

```python
token = "eyJhbGc..."

# 验证Token
user_info = client.verify_token(token)

# 检查权限
has_permission = client.check_permission(
    user_info, 
    resource="document", 
    action="write"
)

# 检查路由权限
has_route_access = client.check_route(
    user_info,
    path="/api/documents/123",
    method="GET"
)
```

## 文档

完整文档请访问: https://docs.authhub.com/sdk/python

## 许可证

MIT License

