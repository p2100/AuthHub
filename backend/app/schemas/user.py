"""用户相关的Pydantic模式"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime


class UserResponse(BaseModel):
    """用户响应"""
    id: int
    feishu_user_id: str
    username: str
    email: Optional[str]
    avatar: Optional[str]
    mobile: Optional[str]
    dept_ids: Optional[List] = []
    dept_names: Optional[List] = []
    status: str
    last_login: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    """用户列表响应"""
    total: int = Field(..., description="总数")
    items: List[UserResponse] = Field(..., description="用户列表")


class UserDetailResponse(UserResponse):
    """用户详情响应（包含更多信息）"""
    pass


class UserStatusUpdate(BaseModel):
    """更新用户状态"""
    status: str = Field(..., description="状态: active, inactive")


class UserRoleResponse(BaseModel):
    """用户角色响应"""
    role_id: int
    role_code: str
    role_name: str
    namespace: str
    assigned_at: datetime
    created_by: Optional[int]
    
    class Config:
        from_attributes = True


class UserPermissionDetail(BaseModel):
    """用户权限详情"""
    global_roles: List[str] = Field(default_factory=list, description="全局角色")
    system_roles: Dict[str, List[str]] = Field(default_factory=dict, description="系统角色")
    global_resources: Dict[str, List[str]] = Field(default_factory=dict, description="全局资源")
    system_resources: Dict[str, Dict[str, List[str]]] = Field(default_factory=dict, description="系统资源")
    roles: List[UserRoleResponse] = Field(default_factory=list, description="角色详情列表")

