"""FastAPI中间件"""
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from authhub_sdk.exceptions import TokenException


class AuthHubMiddleware(BaseHTTPMiddleware):
    """
    AuthHub FastAPI中间件
    
    自动验证Token和检查路由权限
    """
    
    def __init__(self, app, client, public_routes: list = None):
        """
        Args:
            app: FastAPI应用
            client: AuthHubClient实例
            public_routes: 公开路由列表(不需要认证)
        """
        super().__init__(app)
        self.client = client
        self.public_routes = public_routes or ['/health', '/docs', '/openapi.json', '/redoc']
    
    async def dispatch(self, request: Request, call_next):
        """处理请求"""
        # 跳过公开路由
        if self._is_public_route(request.url.path):
            return await call_next(request)
        
        # 提取Token
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return JSONResponse(
                status_code=401,
                content={"error": "缺少认证Token"}
            )
        
        token = auth_header.replace('Bearer ', '')
        
        try:
            # 验证Token
            user_info = self.client.verify_token(token)
            
            # 检查路由权限
            if not self.client.check_route(
                user_info,
                request.url.path,
                request.method
            ):
                return JSONResponse(
                    status_code=403,
                    content={"error": "权限不足"}
                )
            
            # 注入用户信息到request.state
            request.state.user = user_info
            
        except TokenException as e:
            return JSONResponse(
                status_code=401,
                content={"error": str(e)}
            )
        
        response = await call_next(request)
        return response
    
    def _is_public_route(self, path: str) -> bool:
        """判断是否是公开路由"""
        return path in self.public_routes

