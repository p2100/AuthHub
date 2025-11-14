"""FastAPI集成示例"""
from fastapi import FastAPI, Request
from authhub_sdk import AuthHubClient
from authhub_sdk.middleware.fastapi import AuthHubMiddleware

# 创建FastAPI应用
app = FastAPI()

# 初始化AuthHub客户端
authhub_client = AuthHubClient(
    authhub_url="http://localhost:8000",
    system_id="1",  # 系统ID
    system_token="your_system_token",
    namespace="system_a",  # 系统代码
    redis_url="redis://localhost:6379/0"
)

# 添加中间件
app.add_middleware(
    AuthHubMiddleware,
    client=authhub_client,
    public_routes=['/health', '/docs', '/openapi.json']
)


@app.get("/health")
async def health():
    """健康检查(公开路由)"""
    return {"status": "ok"}


@app.get("/api/documents")
async def get_documents(request: Request):
    """获取文档列表(需要认证)"""
    # 用户信息已自动注入到request.state.user
    user = request.state.user
    return {
        "user": user.get('username'),
        "documents": []
    }


@app.post("/api/documents")
async def create_document(request: Request):
    """创建文档(需要认证和权限)"""
    user = request.state.user
    
    # 手动检查权限
    if not authhub_client.check_permission(user, "document", "write"):
        return {"error": "权限不足"}, 403
    
    return {"message": "文档创建成功"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)

