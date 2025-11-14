"""Redis缓存封装"""
import json
import redis
from typing import Any, Optional
from app.core.config import settings


class RedisCache:
    """Redis缓存客户端"""
    
    def __init__(self):
        self.client = redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True
        )
    
    def get(self, key: str) -> Optional[str]:
        """获取缓存"""
        return self.client.get(key)
    
    def set(self, key: str, value: str, ex: Optional[int] = None) -> bool:
        """设置缓存"""
        return self.client.set(key, value, ex=ex)
    
    def setex(self, key: str, seconds: int, value: str) -> bool:
        """设置带过期时间的缓存"""
        return self.client.setex(key, seconds, value)
    
    def delete(self, *keys: str) -> int:
        """删除缓存"""
        return self.client.delete(*keys)
    
    def exists(self, key: str) -> int:
        """检查key是否存在"""
        return self.client.exists(key)
    
    def expire(self, key: str, seconds: int) -> bool:
        """设置过期时间"""
        return self.client.expire(key, seconds)
    
    def ttl(self, key: str) -> int:
        """获取剩余过期时间"""
        return self.client.ttl(key)
    
    def get_json(self, key: str) -> Optional[Any]:
        """获取JSON缓存"""
        value = self.get(key)
        if value:
            return json.loads(value)
        return None
    
    def set_json(self, key: str, value: Any, ex: Optional[int] = None) -> bool:
        """设置JSON缓存"""
        return self.set(key, json.dumps(value, ensure_ascii=False), ex=ex)
    
    def publish(self, channel: str, message: str) -> int:
        """发布消息"""
        return self.client.publish(channel, message)
    
    def pubsub(self):
        """获取PubSub对象"""
        return self.client.pubsub()


# 全局Redis客户端实例
redis_client = RedisCache()

