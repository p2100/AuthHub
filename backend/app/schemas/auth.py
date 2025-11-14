"""认证相关的Pydantic模式"""
from pydantic import BaseModel, Field
from typing import Optional, Dict


class TokenResponse(BaseModel):
    """Token响应"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 3600


class UserInfo(BaseModel):
    """用户信息"""
    user_id: str
    username: str
    email: Optional[str] = None
    avatar: Optional[str] = None
    dept_ids: list = []
    dept_names: list = []
    
    class Config:
        from_attributes = True


class LoginCallbackRequest(BaseModel):
    """登录回调请求"""
    code: str = Field(..., description="飞书授权码")


class PublicKeyResponse(BaseModel):
    """公钥响应"""
    public_key: str
    algorithm: str = "RS256"

