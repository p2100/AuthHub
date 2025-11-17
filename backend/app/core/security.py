"""安全相关工具"""

import secrets
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple

import jwt
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from app.core.cache import redis_client
from app.core.config import settings


class JWTHandler:
    """JWT处理器"""

    def __init__(self):
        self.algorithm = settings.JWT_ALGORITHM
        self.expire_minutes = settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES

    def create_access_token(
        self,
        user_id: int,
        username: str,
        email: str,
        global_roles: list,
        system_roles: dict,
        global_resources: dict,
        system_resources: dict,
        dept_ids: list = None,
        dept_names: list = None,
        expires_delta: Optional[timedelta] = None,
    ) -> str:
        """
        创建用户Token

        Args:
            user_id: 用户ID
            username: 用户名
            email: 邮箱
            global_roles: 全局角色列表
            system_roles: 系统角色字典 {system: [roles]}
            global_resources: 全局资源 {resource_type: [ids]}
            system_resources: 系统资源 {system: {resource_type: [ids]}}
            dept_ids: 部门ID列表
            dept_names: 部门名称列表
            expires_delta: 过期时间

        Returns:
            JWT Token
        """
        if expires_delta is None:
            expires_delta = timedelta(minutes=self.expire_minutes)

        expire = datetime.utcnow() + expires_delta

        payload = {
            "sub": str(user_id),
            "user_type": "user",
            "username": username,
            "email": email,
            "dept_ids": dept_ids or [],
            "dept_names": dept_names or [],
            "global_roles": global_roles,
            "system_roles": system_roles,
            "global_resources": global_resources,
            "system_resources": system_resources,
            "exp": expire,
            "iat": datetime.utcnow(),
            "jti": f"user_{user_id}_{int(datetime.utcnow().timestamp())}",
        }

        # 读取私钥
        with open(settings.JWT_PRIVATE_KEY_PATH, "r") as f:
            private_key = f.read()

        token = jwt.encode(payload, private_key, algorithm=self.algorithm)
        return token

    def generate_system_token(
        self, system_id: str, system_name: str, expires_days: int = 365
    ) -> str:
        """
        生成系统Token

        Args:
            system_id: 系统代码
            system_name: 系统名称
            expires_days: 过期天数

        Returns:
            JWT Token
        """
        expire = datetime.utcnow() + timedelta(days=expires_days)

        payload = {
            "sub": system_id,
            "user_type": "system",
            "system_name": system_name,
            "exp": expire,
            "iat": datetime.utcnow(),
            "jti": f"system_{system_id}_{int(datetime.utcnow().timestamp())}",
        }

        # 读取私钥
        with open(settings.JWT_PRIVATE_KEY_PATH, "r") as f:
            private_key = f.read()

        token = jwt.encode(payload, private_key, algorithm=self.algorithm)
        return token

    def verify_token(self, token: str) -> Dict:
        """
        验证Token

        Args:
            token: JWT Token

        Returns:
            Token payload
        """
        # 读取公钥
        with open(settings.JWT_PUBLIC_KEY_PATH, "r") as f:
            public_key = f.read()

        payload = jwt.decode(token, public_key, algorithms=[self.algorithm])
        return payload

    def add_to_blacklist(self, jti: str, expire_seconds: int = 3600):
        """
        将Token加入黑名单

        Args:
            jti: JWT ID
            expire_seconds: 过期时间(秒)
        """
        redis_client.setex(f"blacklist:{jti}", expire_seconds, "1")

    def is_blacklisted(self, jti: str) -> bool:
        """
        检查Token是否在黑名单

        Args:
            jti: JWT ID

        Returns:
            是否在黑名单
        """
        return redis_client.exists(f"blacklist:{jti}") > 0

    def create_refresh_token(self, user_id: int) -> str:
        """
        生成 refresh token 并存储到 Redis

        Args:
            user_id: 用户ID

        Returns:
            Refresh Token (随机字符串)
        """
        token = secrets.token_urlsafe(64)
        # 存储到 Redis，7天过期
        redis_client.setex(
            f"refresh_token:{token}",
            7 * 24 * 3600,  # 7天
            str(user_id)
        )
        return token

    def verify_refresh_token(self, token: str) -> Optional[int]:
        """
        验证 refresh token

        Args:
            token: Refresh Token

        Returns:
            用户ID，如果无效则返回 None
        """
        user_id = redis_client.get(f"refresh_token:{token}")
        return int(user_id) if user_id else None

    def revoke_refresh_token(self, token: str):
        """
        撤销 refresh token

        Args:
            token: Refresh Token
        """
        redis_client.delete(f"refresh_token:{token}")


def generate_rsa_keys(key_size: int = 2048) -> Tuple[str, str]:
    """
    生成RSA密钥对

    Args:
        key_size: 密钥长度，默认2048位

    Returns:
        (private_key_pem, public_key_pem): 私钥和公钥的PEM格式字符串
    """
    # 生成RSA私钥
    private_key = rsa.generate_private_key(
        public_exponent=65537, key_size=key_size, backend=default_backend()
    )

    # 获取私钥PEM格式
    private_key_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode("utf-8")

    # 获取公钥
    public_key = private_key.public_key()

    # 获取公钥PEM格式
    public_key_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM, format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode("utf-8")

    return private_key_pem, public_key_pem


# 全局实例
jwt_handler = JWTHandler()


# 便捷函数
def create_access_token(*args, **kwargs):
    """创建用户Token"""
    return jwt_handler.create_access_token(*args, **kwargs)


def verify_token(token: str):
    """验证Token"""
    return jwt_handler.verify_token(token)


def add_to_blacklist(jti: str, expire_seconds: int = 3600):
    """加入黑名单"""
    jwt_handler.add_to_blacklist(jti, expire_seconds)


def is_blacklisted(jti: str):
    """检查黑名单"""
    return jwt_handler.is_blacklisted(jti)
