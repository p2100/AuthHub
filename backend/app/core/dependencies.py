"""依赖注入"""
from functools import wraps
from typing import Generator
from fastapi import Depends, HTTPException, Header
from sqlalchemy.orm import Session
import jwt

from app.core.database import SessionLocal
from app.core.cache import redis_client
from app.core.pubsub import redis_pubsub
from app.core.config import settings


def get_db() -> Generator[Session, None, None]:
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_redis_client():
    """获取Redis客户端"""
    return redis_client


def get_pubsub_client():
    """获取Pub/Sub客户端"""
    return redis_pubsub


def get_current_user(
    authorization: str = Header(..., description="Bearer token"),
    db: Session = Depends(get_db)
) -> dict:
    """
    获取当前用户信息
    
    从JWT Token中提取用户信息
    """
    if not authorization.startswith('Bearer '):
        raise HTTPException(status_code=401, detail="无效的认证头")
    
    token = authorization.replace('Bearer ', '')
    
    try:
        # 读取公钥
        with open(settings.JWT_PUBLIC_KEY_PATH, 'r') as f:
            public_key = f.read()
        
        # 验证Token
        payload = jwt.decode(
            token,
            public_key,
            algorithms=[settings.JWT_ALGORITHM]
        )
        
        # 检查黑名单
        jti = payload.get('jti', '')
        if redis_client.exists(f"blacklist:{jti}"):
            raise HTTPException(status_code=401, detail="Token已被撤销")
        
        return payload
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token已过期")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token无效")


def require_admin(
    current_user: dict = Depends(get_current_user)
) -> dict:
    """要求管理员权限"""
    global_roles = current_user.get('global_roles', [])
    
    if 'admin' not in global_roles:
        raise HTTPException(status_code=403, detail="需要管理员权限")
    
    return current_user


def verify_system_token(
    x_system_token: str,
    db: Session
) -> dict:
    """
    验证系统Token
    
    Args:
        x_system_token: 系统Token
        db: 数据库会话
        
    Returns:
        Token payload
    """
    try:
        # 读取公钥
        with open(settings.JWT_PUBLIC_KEY_PATH, 'r') as f:
            public_key = f.read()
        
        # 验证Token
        payload = jwt.decode(
            x_system_token,
            public_key,
            algorithms=[settings.JWT_ALGORITHM]
        )
        
        # 检查用户类型
        if payload.get('user_type') != 'system':
            raise HTTPException(status_code=403, detail="无效的系统Token")
        
        return payload
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="系统Token已过期")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="系统Token无效")
