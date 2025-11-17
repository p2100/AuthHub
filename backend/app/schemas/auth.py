"""认证相关的Pydantic模式"""
from pydantic import BaseModel, Field
from typing import Optional, Dict


class TokenResponse(BaseModel):
    """Token响应"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 3600
    refresh_expires_in: int = 604800  # 7天


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


class SSOLoginUrlRequest(BaseModel):
    """SSO登录URL请求"""
    redirect_uri: str = Field(..., description="回调URI")
    state: Optional[str] = Field(None, description="状态参数(防CSRF)")


class SSOLoginUrlResponse(BaseModel):
    """SSO登录URL响应"""
    login_url: str = Field(..., description="登录URL")
    state: str = Field(..., description="状态参数")


class SSOExchangeTokenRequest(BaseModel):
    """SSO Token交换请求"""
    code: str = Field(..., description="授权码")
    state: Optional[str] = Field(None, description="状态参数")


class RefreshTokenRequest(BaseModel):
    """刷新Token请求"""
    refresh_token: str = Field(..., description="Refresh Token")

