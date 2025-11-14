"""应用配置管理"""
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    """应用配置"""
    
    # 应用配置
    APP_NAME: str = "AuthHub"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # 数据库配置
    DATABASE_URL: str = Field(..., description="PostgreSQL数据库连接URL")
    
    # Redis配置
    REDIS_URL: str = Field(..., description="Redis连接URL")
    
    # JWT配置
    JWT_ALGORITHM: str = "RS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    JWT_PRIVATE_KEY_PATH: str = "./keys/private_key.pem"
    JWT_PUBLIC_KEY_PATH: str = "./keys/public_key.pem"
    
    # 飞书配置
    FEISHU_APP_ID: str = Field(..., description="飞书应用ID")
    FEISHU_APP_SECRET: str = Field(..., description="飞书应用Secret")
    FEISHU_ENCRYPT_KEY: str = ""
    FEISHU_VERIFICATION_TOKEN: str = ""
    
    # CORS配置
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


# 全局配置实例
settings = Settings()

