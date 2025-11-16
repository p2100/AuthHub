"""系统相关的Pydantic模式"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, List
from datetime import datetime


class SystemCreate(BaseModel):
    """创建系统"""
    code: str = Field(..., description="系统代码", min_length=2, max_length=50)
    name: str = Field(..., description="系统名称", min_length=1, max_length=100)
    description: str = ""
    api_endpoint: str = ""


class SystemResponse(BaseModel):
    """系统响应"""
    id: int
    code: str
    name: str
    description: str
    api_endpoint: str
    status: str
    created_at: datetime
    # 注意: system_token只在创建时返回一次
    
    class Config:
        from_attributes = True


class SystemWithToken(SystemResponse):
    """带Token的系统响应(仅创建时)"""
    system_token: str


class SystemConfigResponse(BaseModel):
    """系统配置响应"""
    version: str
    updated_at: int
    namespace: str
    roles: Dict[str, Dict]
    permissions: Dict[str, Dict]
    route_patterns: List[Dict]


class SystemUpdate(BaseModel):
    """更新系统"""
    name: Optional[str] = None
    description: Optional[str] = None
    api_endpoint: Optional[str] = None


class SystemStatusUpdate(BaseModel):
    """更新系统状态"""
    status: str = Field(..., description="状态: active, inactive")

