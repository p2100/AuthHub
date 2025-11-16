"""Loguru日志配置"""

import sys
from loguru import logger

from app.core.config import settings

# 移除默认的handler
logger.remove()

# 添加自定义的handler - 控制台输出
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level=settings.LOG_LEVEL,
    colorize=True,
)

# 可选：添加文件日志
# logger.add(
#     "logs/app_{time:YYYY-MM-DD}.log",
#     rotation="00:00",  # 每天午夜轮转
#     retention="30 days",  # 保留30天
#     level=settings.LOG_LEVEL,
#     format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}",
# )

__all__ = ["logger"]

