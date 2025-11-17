"""Token验证器"""

from typing import Dict

import jwt

from authhub_sdk.exceptions import (
    InvalidTokenException,
    TokenExpiredException,
    TokenRevokedException,
)


class TokenVerifier:
    """Token验证器 - 本地验证JWT"""

    def __init__(self, redis_client):
        self.redis = redis_client
        self.public_key: str = ""

    def set_public_key(self, public_key_pem: str):
        """设置公钥"""
        self.public_key = public_key_pem

    def verify(self, token: str) -> Dict:
        """
        验证Token

        1. 验证JWT签名(使用公钥)
        2. 检查过期时间
        3. 检查黑名单

        Args:
            token: JWT Token

        Returns:
            Token payload

        Raises:
            TokenExpiredException: Token过期
            TokenRevokedException: Token已撤销
            InvalidTokenException: Token无效
        """
        if not self.public_key:
            raise InvalidTokenException("公钥未设置")

        try:
            # 验证JWT签名和过期时间
            payload = jwt.decode(token, self.public_key, algorithms=["RS256"])

            # 检查黑名单
            jti = payload.get("jti", "")
            if self._is_revoked(jti):
                raise TokenRevokedException("Token已被撤销")

            return payload

        except jwt.ExpiredSignatureError:
            raise TokenExpiredException("Token已过期")
        except jwt.InvalidTokenError as e:
            raise InvalidTokenException(f"Token无效: {str(e)}")

    def _is_revoked(self, jti: str) -> bool:
        """检查Token是否在黑名单"""
        if not jti:
            return False
        return self.redis.exists(f"blacklist:{jti}") > 0
