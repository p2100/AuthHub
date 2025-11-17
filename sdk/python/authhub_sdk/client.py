"""AuthHub SDK核心客户端"""

import json
import threading
import time
from typing import Dict, Optional

import redis
import requests
from uvicorn.main import logger

from authhub_sdk.checker import PermissionChecker
from authhub_sdk.verifier import TokenVerifier


class AuthHubClient:
    """
    AuthHub SDK核心客户端

    提供本地Token验证和权限校验功能
    """

    def __init__(
        self,
        authhub_url: str,
        system_id: str,
        system_token: str,
        namespace: str,
        redis_url: str,
        enable_cache: bool = True,
        sync_interval: int = 300,  # 5分钟同步一次
    ):
        """
        初始化客户端

        Args:
            authhub_url: AuthHub服务地址
            system_id: 系统ID
            system_token: 系统Token
            namespace: 命名空间(系统代码)
            redis_url: Redis连接URL
            enable_cache: 是否启用缓存
            sync_interval: 配置同步间隔(秒)
        """
        self.authhub_url = authhub_url.rstrip("/")
        self.system_id = system_id
        self.system_token = system_token
        self.namespace = namespace
        self.enable_cache = enable_cache
        self.sync_interval = sync_interval

        # Redis客户端
        self.redis = redis.from_url(redis_url, decode_responses=True)

        # Token验证器
        self.verifier = TokenVerifier(self.redis)

        # 权限检查器
        self.checker = PermissionChecker(namespace)

        # 配置缓存
        self.config_cache: Dict = {}
        self.config_version: Optional[str] = None

        # 初始化
        self._sync_public_key()
        self._sync_config()

        if enable_cache:
            # 订阅权限变更
            self._subscribe_updates()

            # 定期同步配置
            self._start_sync_scheduler()

    def verify_token(self, token: str) -> Dict:
        """
        验证Token(本地)

        Args:
            token: JWT Token

        Returns:
            Token payload
        """
        return self.verifier.verify(token)

    def check_permission(self, token_payload: Dict, resource: str, action: str) -> bool:
        """
        检查权限(本地)

        Args:
            token_payload: Token payload
            resource: 资源类型
            action: 操作

        Returns:
            是否有权限
        """
        return self.checker.check_permission(token_payload, resource, action, self.config_cache)

    def check_route(self, token_payload: Dict, path: str, method: str) -> bool:
        """
        检查路由权限(本地)

        Args:
            token_payload: Token payload
            path: 路由路径
            method: HTTP方法

        Returns:
            是否有权限
        """
        return self.checker.check_route(token_payload, path, method, self.config_cache)

    # ========== 便捷方法 ==========

    def has_global_role(self, token_payload: Dict, role: str) -> bool:
        """检查全局角色"""
        return role in token_payload.get("global_roles", [])

    def has_system_role(self, token_payload: Dict, role: str) -> bool:
        """检查系统角色"""
        system_roles = token_payload.get("system_roles", {})
        return role in system_roles.get(self.namespace, [])

    def has_resource_access(
        self, token_payload: Dict, resource_type: str, resource_id: int
    ) -> bool:
        """检查资源访问权限"""
        return self.checker.check_resource_access(token_payload, resource_type, resource_id)

    def refresh_token(self, refresh_token: str) -> Dict[str, str]:
        """
        刷新访问令牌
        
        Args:
            refresh_token: Refresh Token
            
        Returns:
            新的token数据（包含access_token和refresh_token）
            
        Raises:
            Exception: 刷新失败时抛出异常
        """
        try:
            response = requests.post(
                f"{self.authhub_url}/api/v1/auth/refresh",
                json={"refresh_token": refresh_token},
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise Exception(f"Token刷新失败: {str(e)}")

    # ========== 内部方法 ==========

    def _sync_public_key(self):
        """同步JWT公钥"""
        try:
            response = requests.get(f"{self.authhub_url}/api/v1/auth/public-key", timeout=10)
            response.raise_for_status()
            data = response.json()
            self.verifier.set_public_key(data["public_key"])
            print(f"✅ 公钥同步成功")
        except Exception as e:
            print(f"❌ 公钥同步失败: {e}")

    def _sync_config(self):
        """同步权限配置"""
        try:
            logger.info(f"{self.system_id} - {self.system_token}")
            response = requests.get(
                f"{self.authhub_url}/api/v1/systems/{self.system_id}/config",
                headers={"X-System-Token": self.system_token},
                timeout=10,
            )
            response.raise_for_status()
            config = response.json()
            self.config_cache = config
            self.config_version = config.get("version")
            print(f"✅ 配置同步成功: {self.config_version}")
        except Exception as e:
            print(f"❌ 配置同步失败: {e}")

    def _subscribe_updates(self):
        """订阅权限变更通知"""

        def listener():
            pubsub = self.redis.pubsub()

            # 订阅系统channel和全局channel
            channels = [f"permission:changed:{self.namespace}", "permission:changed:global"]
            pubsub.subscribe(*channels)

            print(f"📡 已订阅权限变更通知: {channels}")

            for message in pubsub.listen():
                if message["type"] == "message":
                    try:
                        data = json.loads(message["data"])
                        print(f"📨 收到权限变更通知: {data.get('type')}")

                        # 重新同步配置
                        self._sync_config()
                    except Exception as e:
                        print(f"❌ 处理权限变更失败: {e}")

        # 在后台线程运行
        thread = threading.Thread(target=listener, daemon=True)
        thread.start()

    def _start_sync_scheduler(self):
        """启动定期同步"""

        def sync_job():
            while True:
                time.sleep(self.sync_interval)
                try:
                    print(f"🔄 定期同步配置...")
                    self._sync_config()
                except Exception as e:
                    print(f"❌ 定期同步失败: {e}")

        thread = threading.Thread(target=sync_job, daemon=True)
        thread.start()
