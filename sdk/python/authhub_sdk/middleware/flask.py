"""Flask中间件"""
from functools import wraps
from flask import request, g, jsonify
from authhub_sdk.exceptions import TokenException


def init_authhub_middleware(app, client, public_routes: list = None):
    """
    初始化AuthHub Flask中间件
    
    Args:
        app: Flask应用
        client: AuthHubClient实例
        public_routes: 公开路由列表
    """
    public_routes = public_routes or ['/health']
    
    @app.before_request
    def verify_auth():
        """请求前验证"""
        # 跳过公开路由
        if request.path in public_routes:
            return None
        
        # 提取Token
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return jsonify({"error": "缺少认证Token"}), 401
        
        token = auth_header.replace('Bearer ', '')
        
        try:
            # 验证Token
            user_info = client.verify_token(token)
            
            # 检查路由权限
            if not client.check_route(
                user_info,
                request.path,
                request.method
            ):
                return jsonify({"error": "权限不足"}), 403
            
            # 注入用户信息到g
            g.user = user_info
            
        except TokenException as e:
            return jsonify({"error": str(e)}), 401
        
        return None


def auth_required(func):
    """装饰器: 要求认证"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not hasattr(g, 'user'):
            return jsonify({"error": "未认证"}), 401
        return func(*args, **kwargs)
    return wrapper

