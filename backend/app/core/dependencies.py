"""依赖注入"""

from functools import wraps
from typing import AsyncGenerator

import jwt
from fastapi import Depends, Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.cache import redis_client
from app.core.config import settings
from app.core.database import get_db
from app.core.pubsub import pubsub_manager
from app.models.system import System


def get_redis_client():
    """获取Redis客户端"""
    return redis_client


def get_pubsub_client():
    """获取Pub/Sub客户端"""
    return pubsub_manager


async def get_current_user(authorization: str = Header(..., description="Bearer token")) -> dict:
    """
    获取当前用户信息

    从JWT Token中提取用户信息
    """
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="无效的认证头")

    token = authorization.replace("Bearer ", "")

    try:
        # 读取公钥
        with open(settings.JWT_PUBLIC_KEY_PATH, "r") as f:
            public_key = f.read()

        # 验证Token
        payload = jwt.decode(token, public_key, algorithms=[settings.JWT_ALGORITHM])

        # 检查黑名单
        jti = payload.get("jti", "")
        if redis_client.exists(f"blacklist:{jti}"):
            raise HTTPException(status_code=401, detail="Token已被撤销")

        return payload

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token已过期")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token无效")


async def require_admin(current_user: dict = Depends(get_current_user)) -> dict:
    """要求管理员权限"""
    global_roles = current_user.get("global_roles", [])

    if "admin" not in global_roles:
        raise HTTPException(status_code=403, detail="需要管理员权限")

    return current_user


def verify_system_token(token: str, db: AsyncSession) -> dict:
    """
    验证系统Token

    用于系统间API调用的认证
    """
    print(f"🔍 [系统Token验证] 开始验证")
    print(f"🔍 [系统Token验证] Token前30字符: {token[:30]}...")

    try:
        # 读取公钥
        with open(settings.JWT_PUBLIC_KEY_PATH, "r") as f:
            public_key = f.read()
        print(f"✅ [系统Token验证] 公钥读取成功")

        # 验证Token
        payload = jwt.decode(token, public_key, algorithms=[settings.JWT_ALGORITHM])
        print(f"✅ [系统Token验证] Token解码成功")
        print(f"🔍 [系统Token验证] Payload: {payload}")

        # 验证Token类型是否为系统Token
        # 注意: 使用 user_type 字段而不是 type 字段
        token_type = payload.get("user_type")
        print(f"🔍 [系统Token验证] Token类型(user_type): {token_type}")

        if token_type != "system":
            print(f"❌ [系统Token验证] Token类型不是system，而是: {token_type}")
            raise HTTPException(status_code=401, detail="无效的Token类型")

        # 检查系统是否存在
        system_code = payload.get("sub")
        print(f"🔍 [系统Token验证] 系统代码: {system_code}")

        if not system_code:
            print(f"❌ [系统Token验证] Token中缺少系统标识")
            raise HTTPException(status_code=401, detail="Token中缺少系统标识")

        print(f"✅ [系统Token验证] 验证通过")
        return payload

    except jwt.ExpiredSignatureError as e:
        print(f"❌ [系统Token验证] Token已过期: {e}")
        raise HTTPException(status_code=401, detail="Token已过期")
    except jwt.InvalidTokenError as e:
        print(f"❌ [系统Token验证] Token无效: {e}")
        raise HTTPException(status_code=401, detail="Token无效")
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ [系统Token验证] 未知错误: {type(e).__name__}: {e}")
        raise HTTPException(status_code=401, detail=f"Token验证失败: {str(e)}")
