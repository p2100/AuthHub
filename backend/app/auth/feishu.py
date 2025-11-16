"""飞书OAuth2.0集成"""

from typing import Dict

import httpx

from app.core.config import settings
from app.core.logger import logger


class FeishuClient:
    """飞书API客户端"""

    def __init__(self):
        self.app_id = settings.FEISHU_APP_ID
        self.app_secret = settings.FEISHU_APP_SECRET
        self.base_url = "https://open.feishu.cn/open-apis"

    async def get_app_access_token(self) -> str:
        """
        获取应用访问令牌

        Returns:
            app_access_token
        """
        url = f"{self.base_url}/auth/v3/app_access_token/internal"
        payload = {"app_id": self.app_id, "app_secret": "***"}  # 日志中隐藏secret

        logger.info(f"[飞书API] 获取app_access_token - URL: {url}")
        logger.debug(f"[飞书API] 请求payload: {payload}")

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                real_payload = {"app_id": self.app_id, "app_secret": self.app_secret}
                response = await client.post(url, json=real_payload)

                logger.info(f"[飞书API] 响应状态码: {response.status_code}")
                logger.debug(f"[飞书API] 响应头: {dict(response.headers)}")

                data = response.json()
                logger.debug(f"[飞书API] 响应数据: {data}")

                if data.get("code") != 0:
                    logger.error(
                        f"[飞书API] 获取app_access_token失败 - code: {data.get('code')}, msg: {data.get('msg')}"
                    )
                    raise Exception(f"获取app_access_token失败: {data.get('msg')}")

                logger.info("[飞书API] 成功获取app_access_token")
                return data.get("app_access_token")
        except httpx.ConnectError as e:
            logger.error(f"[飞书API] 连接失败: {str(e)}")
            raise Exception(f"连接飞书API失败: {str(e)}")
        except httpx.TimeoutException as e:
            logger.error(f"[飞书API] 请求超时: {str(e)}")
            raise Exception(f"飞书API请求超时: {str(e)}")
        except Exception as e:
            logger.error(f"[飞书API] 未知错误: {str(e)}", exc_info=True)
            raise

    async def get_user_access_token(self, code: str) -> str:
        """
        获取用户访问令牌

        Args:
            code: 飞书授权码

        Returns:
            user_access_token
        """
        logger.info(f"[飞书API] 开始获取user_access_token - code: {code[:10]}***")

        app_access_token = await self.get_app_access_token()

        url = f"{self.base_url}/authen/v1/access_token"
        payload = {"grant_type": "authorization_code", "code": code}

        logger.info(f"[飞书API] 获取user_access_token - URL: {url}")
        logger.debug(f"[飞书API] 请求payload: {payload}")

        try:
            real_headers = {
                "Authorization": f"Bearer {app_access_token}",
                "Content-Type": "application/json",
            }
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, headers=real_headers, json=payload)

                logger.info(f"[飞书API] 响应状态码: {response.status_code}")
                data = response.json()
                logger.debug(f"[飞书API] 响应数据: {data}")

                if data.get("code") != 0:
                    logger.error(
                        f"[飞书API] 获取user_access_token失败 - code: {data.get('code')}, msg: {data.get('msg')}"
                    )
                    raise Exception(f"获取user_access_token失败: {data.get('msg')}")

                logger.info("[飞书API] 成功获取user_access_token")
                return data.get("data", {}).get("access_token")
        except httpx.ConnectError as e:
            logger.error(f"[飞书API] 连接失败: {str(e)}")
            raise Exception(f"连接飞书API失败: {str(e)}")
        except httpx.TimeoutException as e:
            logger.error(f"[飞书API] 请求超时: {str(e)}")
            raise Exception(f"飞书API请求超时: {str(e)}")
        except Exception as e:
            logger.error(f"[飞书API] 未知错误: {str(e)}", exc_info=True)
            raise

    async def get_user_info(self, user_access_token: str) -> Dict:
        """
        获取用户信息

        Args:
            user_access_token: 用户访问令牌

        Returns:
            用户信息字典
        """
        url = f"{self.base_url}/authen/v1/user_info"

        logger.info(f"[飞书API] 获取用户信息 - URL: {url}")
        logger.debug(f"[飞书API] user_access_token: {user_access_token[:20]}***")

        headers = {
            "Authorization": f"Bearer {user_access_token}",
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, headers=headers)

                logger.info(f"[飞书API] 响应状态码: {response.status_code}")
                data = response.json()
                logger.debug(f"[飞书API] 响应数据: {data}")

                if data.get("code") != 0:
                    logger.error(
                        f"[飞书API] 获取用户信息失败 - code: {data.get('code')}, msg: {data.get('msg')}"
                    )
                    raise Exception(f"获取用户信息失败: {data.get('msg')}")

                user_info = data.get("data", {})
                logger.info(
                    f"[飞书API] 成功获取用户信息 - name: {user_info.get('name')}, open_id: {user_info.get('open_id')}"
                )
                return user_info
        except httpx.ConnectError as e:
            logger.error(f"[飞书API] 连接失败: {str(e)}")
            raise Exception(f"连接飞书API失败: {str(e)}")
        except httpx.TimeoutException as e:
            logger.error(f"[飞书API] 请求超时: {str(e)}")
            raise Exception(f"飞书API请求超时: {str(e)}")
        except Exception as e:
            logger.error(f"[飞书API] 未知错误: {str(e)}", exc_info=True)
            raise

    async def get_user_detail(self, user_id: str) -> Dict:
        """
        获取用户详细信息(包含部门信息)

        Args:
            user_id: 飞书用户ID

        Returns:
            用户详细信息
        """
        logger.info(f"[飞书API] 获取用户详细信息 - user_id: {user_id}")

        app_access_token = await self.get_app_access_token()

        url = f"{self.base_url}/contact/v3/users/{user_id}"
        headers = {
            "Authorization": f"Bearer {app_access_token}",
        }
        params = {"user_id_type": "open_id"}

        logger.info(f"[飞书API] 获取用户详细信息 - URL: {url}")
        logger.debug(f"[飞书API] 请求参数: {params}")

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, headers=headers, params=params)

                logger.info(f"[飞书API] 响应状态码: {response.status_code}")
                data = response.json()
                logger.debug(f"[飞书API] 响应数据: {data}")

                if data.get("code") != 0:
                    logger.error(
                        f"[飞书API] 获取用户详细信息失败 - code: {data.get('code')}, msg: {data.get('msg')}"
                    )
                    raise Exception(f"获取用户详细信息失败: {data.get('msg')}")

                user_detail = data.get("data", {}).get("user", {})
                logger.info("[飞书API] 成功获取用户详细信息")
                return user_detail
        except httpx.ConnectError as e:
            logger.error(f"[飞书API] 连接失败: {str(e)}")
            raise Exception(f"连接飞书API失败: {str(e)}")
        except httpx.TimeoutException as e:
            logger.error(f"[飞书API] 请求超时: {str(e)}")
            raise Exception(f"飞书API请求超时: {str(e)}")
        except Exception as e:
            logger.error(f"[飞书API] 未知错误: {str(e)}", exc_info=True)
            raise


# 全局飞书客户端实例
feishu_client = FeishuClient()
