"""自定义异常"""


class TokenException(Exception):
    """Token异常基类"""
    pass


class TokenExpiredException(TokenException):
    """Token过期异常"""
    pass


class TokenRevokedException(TokenException):
    """Token已撤销异常"""
    pass


class InvalidTokenException(TokenException):
    """Token无效异常"""
    pass


class PermissionDeniedException(Exception):
    """权限不足异常"""
    pass

