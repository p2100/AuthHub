"""依赖注入"""
from functools import wraps
from typing import AsyncGenerator
from fastapi import Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
import jwt

from app.core.database import get_db
from app.core.cache import redis_client
from app.core.pubsub import redis_pubsub
from app.core.config import settings


def get_redis_client():
    """获取Redis客户端"""
    return redis_client


def get_pubsub_client():
    """获取Pub/Sub客户端"""
    return redis_pubsub


async def get_current_user(
    authorization: str = Header(..., description="Bearer token")
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


async def require_admin(
    current_user: dict = Depends(get_current_user)
) -> dict:
    """要求管理员权限"""
    global_roles = current_user.get('global_roles', [])

    if 'admin' not in global_roles:
        raise HTTPException(status_code=403, detail="需要管理员权限")

    return current_user
