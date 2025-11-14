"""装饰器"""
from functools import wraps
from typing import Optional
from authhub_sdk.exceptions import PermissionDeniedException

# 全局客户端实例(需要在应用初始化时设置)
_client: Optional[object] = None


def init_client(client):
    """初始化全局客户端"""
    global _client
    _client = client


def extract_token_from_request():
    """从请求中提取Token(需要根据框架实现)"""
    # 这里需要根据具体框架实现
    # FastAPI: request.headers.get('Authorization')
    # Flask: flask.request.headers.get('Authorization')
    raise NotImplementedError("请使用框架特定的中间件")


def require_auth(func):
    """
    要求用户登录
    
    Usage:
        @require_auth
        def my_function(user_info):
            pass
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        if _client is None:
            raise RuntimeError("AuthHubClient未初始化,请先调用init_client()")
        
        token = extract_token_from_request()
        if not token:
            raise PermissionDeniedException("缺少认证Token")
        
        # 验证Token
        user_info = _client.verify_token(token)
        
        # 注入user_info
        kwargs['user_info'] = user_info
        return func(*args, **kwargs)
    
    return wrapper


def require_role(role: str):
    """
    要求特定角色
    
    Args:
        role: 角色名称,支持 "editor" 或 "global:admin"
        
    Usage:
        @require_role("editor")
        def my_function(user_info):
            pass
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if _client is None:
                raise RuntimeError("AuthHubClient未初始化")
            
            token = extract_token_from_request()
            if not token:
                raise PermissionDeniedException("缺少认证Token")
            
            user_info = _client.verify_token(token)
            
            # 判断是全局角色还是系统角色
            if ':' in role:
                namespace, role_name = role.split(':', 1)
                if namespace == 'global':
                    has_role = role_name in user_info.get('global_roles', [])
                else:
                    system_roles = user_info.get('system_roles', {})
                    has_role = role_name in system_roles.get(namespace, [])
            else:
                # 默认检查当前系统角色
                has_role = _client.has_system_role(user_info, role)
            
            if not has_role:
                raise PermissionDeniedException(f"需要角色: {role}")
            
            kwargs['user_info'] = user_info
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


def require_permission(resource: str, action: str):
    """
    要求特定权限
    
    Args:
        resource: 资源类型
        action: 操作
        
    Usage:
        @require_permission("document", "write")
        def my_function(user_info):
            pass
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if _client is None:
                raise RuntimeError("AuthHubClient未初始化")
            
            token = extract_token_from_request()
            if not token:
                raise PermissionDeniedException("缺少认证Token")
            
            user_info = _client.verify_token(token)
            
            if not _client.check_permission(user_info, resource, action):
                raise PermissionDeniedException(
                    f"需要权限: {resource}:{action}"
                )
            
            kwargs['user_info'] = user_info
            return func(*args, **kwargs)
        
        return wrapper
    return decorator

