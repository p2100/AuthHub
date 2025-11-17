"""AuthHub SSO客户端"""

from typing import Dict, Optional
from urllib.parse import urlencode

import requests


class SSOClient:
    """
    SSO客户端

    提供完整的SSO登录流程支持
    """

    def __init__(self, authhub_url: str):
        """
        初始化SSO客户端

        Args:
            authhub_url: AuthHub服务地址
        """
        self.authhub_url = authhub_url.rstrip("/")
        self.base_url = f"{self.authhub_url}/api/v1/auth/sso"

    def get_login_url(self, redirect_uri: str, state: Optional[str] = None) -> Dict[str, str]:
        """
        获取SSO登录URL

        Args:
            redirect_uri: 回调URI
            state: 可选的state参数(防CSRF)

        Returns:
            包含login_url和state的字典

        Raises:
            Exception: 请求失败时抛出异常
        """
        try:
            payload = {"redirect_uri": redirect_uri}
            if state:
                payload["state"] = state

            response = requests.post(f"{self.base_url}/login-url", json=payload, timeout=10)
            response.raise_for_status()
            data = response.json()

            return {"login_url": data["login_url"], "state": data["state"]}
        except requests.RequestException as e:
            raise Exception(f"获取登录URL失败: {str(e)}")

    def exchange_token(self, code: str, state: Optional[str] = None) -> Dict[str, str]:
        """
        用授权码交换JWT Token

        Args:
            code: 授权码
            state: 状态参数

        Returns:
            Token信息字典
            {
                "access_token": "xxx",
                "refresh_token": "xxx",
                "token_type": "bearer",
                "expires_in": 3600,
                "refresh_expires_in": 604800
            }

        Raises:
            Exception: 交换失败时抛出异常
        """
        try:
            payload = {"code": code}
            if state:
                payload["state"] = state

            response = requests.post(f"{self.base_url}/exchange-token", json=payload, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise Exception(f"Token交换失败: {str(e)}")

    def handle_callback(self, code: str, state: Optional[str] = None) -> Dict[str, str]:
        """
        处理SSO回调(便捷方法)

        Args:
            code: 授权码
            state: 状态参数

        Returns:
            完整的Token数据（包含access_token和refresh_token）
        """
        token_data = self.exchange_token(code, state)
        return token_data
