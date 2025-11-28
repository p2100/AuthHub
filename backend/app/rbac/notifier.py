"""权限变更通知器"""
import json
import time
from typing import Dict
from app.core.cache import redis_client
from app.models.role import Role


class PermissionNotifier:
    """权限变更通知器 - 通过Redis Pub/Sub通知各系统"""
    
    def __init__(self):
        self.redis = redis_client
    
    def notify_role_created(self, role: Role):
        """角色创建通知"""
        self._publish(role.namespace, {
            "type": "role_created",
            "role_id": role.id,
            "role_code": role.code,
            "timestamp": time.time()
        })
    
    def notify_role_updated(self, role: Role):
        """角色更新通知"""
        self._publish(role.namespace, {
            "type": "role_updated",
            "role_id": role.id,
            "timestamp": time.time()
        })
    
    def notify_role_permissions_updated(self, role: Role):
        """角色权限更新通知"""
        self._publish(role.namespace, {
            "type": "role_permissions_updated",
            "role_id": role.id,
            "timestamp": time.time()
        })
    
    def notify_user_permissions_changed(self, user_id: str):
        """用户权限变更通知(影响所有系统)"""
        # 发布到全局channel
        self._publish("global", {
            "type": "user_permissions_changed",
            "user_id": user_id,
            "timestamp": time.time()
        })
    
    def notify_config_updated(self, namespace: str):
        """配置更新通知"""
        self._publish(namespace, {
            "type": "config_updated",
            "config_version": self._get_config_version(namespace),
            "timestamp": time.time()
        })
    
    def notify_token_revoked(self, jti: str):
        """Token撤销通知"""
        # 加入黑名单
        self.redis.setex(f"blacklist:{jti}", 3600, "1")
        
        # 发布通知
        self._publish("global", {
            "type": "token_revoked",
            "jti": jti,
            "timestamp": time.time()
        })
    
    def _publish(self, namespace: str, message: Dict):
        """发布消息到Redis"""
        channel = f"permission:changed:{namespace}"
        self.redis.publish(channel, json.dumps(message, ensure_ascii=False))
    
    def _get_config_version(self, namespace: str) -> str:
        """获取配置版本号"""
        return f"v{namespace}_{int(time.time())}"


# 全局通知器实例
permission_notifier = PermissionNotifier()

