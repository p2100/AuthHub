"""FastAPI SSO集成示例"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware

from authhub_sdk import AuthHubClient
from authhub_sdk.middleware.fastapi_sso import setup_sso

# 创建FastAPI应用
app = FastAPI(title="FastAPI SSO Example")

# 配置CORS - 允许前端访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # 前端地址
    allow_credentials=True,  # 重要！允许携带 Cookie
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化AuthHub客户端
authhub_client = AuthHubClient(
    authhub_url="http://localhost:8000",
    system_id="1",  # 系统ID
    system_token="eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJkYXRhLWNlbnRlciIsInVzZXJfdHlwZSI6InN5c3RlbSIsInN5c3RlbV9uYW1lIjoiXHU2NTcwXHU2MzZlXHU1ZTczXHU1M2YwIiwiZXhwIjoxNzk0ODgzOTc3LCJpYXQiOjE3NjMzNDc5NzcsImp0aSI6InN5c3RlbV9kYXRhLWNlbnRlcl8xNzYzMzE5MTc3In0.rkqllcDUM_wjANolpBRkrpv5XHN7YpWP1MZzEO1D6TY0HF8GMDQwL0eFXABklt3Y5lFMbgmF1iY-s2ov_CHw_ruf_wxVMoBL8gI3YVW65ePpLjqVW8T5_xXwVx0NXkQq-i9-v-cDry2oJ1hwqCQbGCbvLQtIgbrgL1xdayRXsIMaueZxFwcB11vBJe6RJIdqz3Z3f07v7rfBYtCxkumVd5dTLIKzGf349TYj5MASZ-BQQyHYxGJ5-6ugPPVh_MA1pgDqkA9itRINRkSjNr6leUuM_1jz-yjKKY9z6_klAVCBCFALY2subsJ3PqVX3KIYBqhgoyNx7yZX8dj-MFp9vw",
    namespace="data-center",  # 系统代码
    redis_url="redis://localhost:6379/0",
)

# 一行代码完成SSO集成！（自动注册路由和中间件）
setup_sso(
    app,
    client=authhub_client,
    callback_path="/auth/callback",  # SSO回调路径
    login_path="/auth/login",  # 登录路径
    logout_path="/auth/logout",  # 登出路径
    cookie_name="authhub_token",  # Cookie名称
    cookie_secure=False,  # 开发环境设为False，生产环境应为True
    cookie_httponly=True,  # 防止XSS
    cookie_samesite="lax",  # 防止CSRF
    cookie_max_age=3600,  # 1小时
    public_routes=["/health", "/docs", "/openapi.json", "/debug/cookies"],  # 公开路由
    login_required=True,  # 要求登录
    redirect_to_login=True,  # 未登录时重定向到登录页
    after_login_redirect="/dashboard",  # 登录成功后重定向
)


@app.get("/health")
async def health():
    """健康检查(公开路由)"""
    return {"status": "ok"}


@app.get("/debug/cookies")
async def debug_cookies(request: Request):
    """调试：查看所有 Cookie(公开路由)"""
    return {
        "cookies": dict(request.cookies),
        "headers": dict(request.headers),
    }


@app.get("/")
async def root(request: Request):
    """首页 - 会重定向到登录页"""
    # 如果已登录，显示用户信息
    user = getattr(request.state, "user", None)
    if user:
        return {
            "message": "欢迎使用AuthHub SSO",
            "logged_in": True,
            "user": {
                "username": user.get("username"),
                "email": user.get("email"),
                "user_id": user.get("sub"),
                "global_roles": user.get("global_roles", []),
                "system_roles": user.get("system_roles", {}),
            },
        }
    return {"message": "欢迎使用AuthHub SSO", "logged_in": False}


@app.get("/dashboard")
async def dashboard(request: Request):
    """
    仪表板(需要登录)

    用户信息会自动注入到request.state.user
    """
    user = request.state.user
    return {
        "message": "欢迎回来",
        "user": {
            "username": user.get("username"),
            "email": user.get("email"),
            "roles": user.get("global_roles", []),
        },
    }


@app.get("/api/me")
async def get_current_user(request: Request):
    """
    获取当前登录用户信息(前端需要)

    返回完整的用户信息供前端 Dashboard 使用
    中间件会自动验证 Token 并注入 request.state.user
    """
    # 中间件已经验证了 Token，直接使用 request.state.user
    user = request.state.user

    return {
        "sub": user.get("sub"),
        "username": user.get("username"),
        "email": user.get("email"),
        "global_roles": user.get("global_roles", []),
        "system_roles": user.get("system_roles", {}),
    }


@app.get("/api/documents")
async def get_documents(request: Request):
    """获取文档列表(需要登录)"""
    user = request.state.user
    return {
        "user": user.get("username"),
        "documents": [{"id": 1, "title": "文档1"}, {"id": 2, "title": "文档2"}],
    }


@app.post("/api/documents")
async def create_document(request: Request):
    """创建文档(需要登录和权限)"""
    user = request.state.user

    # 检查权限
    if not authhub_client.check_permission(user, "document", "write"):
        return {"error": "权限不足"}, 403

    return {"message": "文档创建成功"}


@app.get("/api/protected")
async def protected_route(request: Request):
    """受保护的路由"""
    user = request.state.user

    # 检查系统角色
    if not authhub_client.has_system_role(user, "admin"):
        return {"error": "需要管理员权限"}, 403

    return {"message": "这是受保护的内容"}


if __name__ == "__main__":
    import uvicorn

    print("=" * 60)
    print("FastAPI SSO 示例应用")
    print("=" * 60)
    print()
    print("访问 http://localhost:8001 开始体验SSO登录")
    print()
    print("⚠️  重要提示:")
    print("  请确保飞书应用配置的回调地址包含:")
    print("  http://localhost:8001/auth/callback")
    print()
    print("SSO路由:")
    print("  - GET  /auth/login    - 触发登录")
    print("  - GET  /auth/callback - SSO回调(自动处理)")
    print("  - POST /auth/logout   - 登出")
    print()
    print("业务路由:")
    print("  - GET  /              - 首页")
    print("  - GET  /dashboard     - 仪表板(需要登录)")
    print("  - GET  /api/documents - 文档列表(需要登录)")
    print("  - POST /api/documents - 创建文档(需要权限)")
    print()
    print("=" * 60)

    # 使用 127.0.0.1 而不是 0.0.0.0，这样 request.base_url 会是 http://127.0.0.1:8001
    uvicorn.run(app, host="127.0.0.1", port=8001)
