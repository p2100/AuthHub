"""RBAC相关的Pydantic模式"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class RoleCreate(BaseModel):
    """创建角色"""
    code: str = Field(..., description="角色代码")
    name: str = Field(..., description="角色名称")
    namespace: str = Field(..., description="命名空间")
    system_id: Optional[int] = Field(None, description="系统ID")
    description: str = ""


class RoleResponse(BaseModel):
    """角色响应"""
    id: int
    code: str
    name: str
    namespace: str
    system_id: Optional[int]
    description: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class PermissionCreate(BaseModel):
    """创建权限"""
    code: str
    name: str
    namespace: str
    system_id: Optional[int] = None
    resource_type: str = ""
    action: str = ""
    description: str = ""


class PermissionResponse(BaseModel):
    """权限响应"""
    id: int
    code: str
    name: str
    namespace: str
    resource_type: str
    action: str
    
    class Config:
        from_attributes = True


class RoutePatternCreate(BaseModel):
    """创建路由规则"""
    system_id: int
    role_id: int
    pattern: str = Field(..., description="路由正则表达式")
    method: str = Field("*", description="HTTP方法")
    priority: int = Field(0, description="优先级")
    description: str = ""


class ResourceBindingCreate(BaseModel):
    """创建资源绑定"""
    user_id: int
    namespace: str
    resource_type: str
    resource_ids: List[str]
    system_id: Optional[int] = None
    action: str = ""


class UpdateRolePermissions(BaseModel):
    """更新角色权限"""
    permission_ids: List[int]

