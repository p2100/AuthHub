"""Redis Pub/Sub封装"""
import json
import threading
from typing import Callable, Dict
from app.core.cache import redis_client
import logging

logger = logging.getLogger(__name__)


class PubSubManager:
    """Pub/Sub管理器"""
    
    def __init__(self):
        self.pubsub = redis_client.pubsub()
        self.handlers: Dict[str, Callable] = {}
        self.listener_thread: Optional[threading.Thread] = None
    
    def subscribe(self, channel: str, handler: Callable[[dict], None]):
        """
        订阅频道
        
        Args:
            channel: 频道名称
            handler: 消息处理函数
        """
        self.handlers[channel] = handler
        self.pubsub.subscribe(channel)
        logger.info(f"已订阅频道: {channel}")
    
    def unsubscribe(self, channel: str):
        """取消订阅"""
        if channel in self.handlers:
            del self.handlers[channel]
            self.pubsub.unsubscribe(channel)
            logger.info(f"已取消订阅频道: {channel}")
    
    def start_listening(self):
        """启动监听(在后台线程)"""
        if self.listener_thread and self.listener_thread.is_alive():
            logger.warning("监听线程已在运行")
            return
        
        def listener():
            logger.info("Pub/Sub监听线程已启动")
            for message in self.pubsub.listen():
                if message['type'] == 'message':
                    channel = message['channel']
                    data = message['data']
                    
                    if channel in self.handlers:
                        try:
                            # 解析JSON消息
                            msg_data = json.loads(data)
                            self.handlers[channel](msg_data)
                        except Exception as e:
                            logger.error(f"处理消息失败: {e}", exc_info=True)
        
        self.listener_thread = threading.Thread(target=listener, daemon=True)
        self.listener_thread.start()
    
    def stop_listening(self):
        """停止监听"""
        if self.pubsub:
            self.pubsub.close()
        logger.info("Pub/Sub监听已停止")
    
    def publish(self, channel: str, message: dict):
        """
        发布消息
        
        Args:
            channel: 频道名称
            message: 消息内容(dict)
        """
        redis_client.publish(channel, json.dumps(message, ensure_ascii=False))


# 全局Pub/Sub管理器
pubsub_manager = PubSubManager()

