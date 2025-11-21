"""FastAPI应用主入口"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.auth.router import router as auth_router
from app.systems.router import router as systems_router
from app.rbac.router import router as rbac_router
from app.users.router import router as users_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    print(f"🚀 {settings.APP_NAME} v{settings.APP_VERSION} 启动中...")
    print(f"📝 Swagger文档: http://{settings.HOST}:{settings.PORT}/docs")
    
    yield
    
    # 关闭时执行
    print(f"👋 {settings.APP_NAME} 关闭中...")


# 创建FastAPI应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="飞书SSO统一权限管理平台",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth_router, prefix="/api/v1")
app.include_router(systems_router, prefix="/api/v1")
app.include_router(rbac_router, prefix="/api/v1")
app.include_router(users_router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "ok"}


# 静态文件配置 (用于生产环境 serving 前端)
import os
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")

if os.path.exists(STATIC_DIR):
    # 挂载静态资源目录 (CSS, JS, Images)
    # Vite 默认构建输出包含 assets 目录
    assets_dir = os.path.join(STATIC_DIR, "assets")
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        """服务前端单页应用 (SPA)"""
        # 尝试直接返回请求的文件 (如 favicon.ico, robots.txt)
        file_path = os.path.join(STATIC_DIR, full_path)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)
        
        # 默认返回 index.html 处理前端路由
        return FileResponse(os.path.join(STATIC_DIR, "index.html"))

else:
    # 开发模式或未构建前端时的默认根路径
    @app.get("/")
    async def root():
        """根路径"""
        return {
            "name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "docs": "/docs",
            "message": "Frontend not found. Running in API-only mode."
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )

