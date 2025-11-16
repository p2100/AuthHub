"""系统管理API路由"""
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import require_admin, verify_system_token
from app.schemas.system import (
    SystemCreate,
    SystemResponse,
    SystemWithToken,
    SystemConfigResponse,
    SystemUpdate,
    SystemStatusUpdate,
)
from app.schemas.rbac import RoleResponse, PermissionResponse
from app.systems.service import SystemService, ConfigSyncService

router = APIRouter(prefix="/systems", tags=["系统管理"])


@router.post("", response_model=SystemWithToken)
async def create_system(
    system_data: SystemCreate,
    current_user: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    创建系统并生成系统Token
    
    需要管理员权限
    """
    system_service = SystemService(db)
    
    # 检查系统代码是否已存在
    existing = await system_service.get_system_by_code(system_data.code)
    if existing:
        raise HTTPException(status_code=400, detail="系统代码已存在")
    
    # 创建系统
    system = await system_service.create_system(
        code=system_data.code,
        name=system_data.name,
        description=system_data.description,
        api_endpoint=system_data.api_endpoint
    )
    
    return system


@router.get("", response_model=list[SystemResponse])
async def list_systems(
    current_user: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """获取系统列表"""
    system_service = SystemService(db)
    systems = await system_service.list_systems()
    return systems


@router.get("/{system_id}", response_model=SystemResponse)
async def get_system(
    system_id: int,
    current_user: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """获取系统详情"""
    system_service = SystemService(db)
    system = await system_service.get_system_by_id(system_id)
    
    if not system:
        raise HTTPException(status_code=404, detail="系统不存在")
    
    return system


@router.get("/{system_id}/config", response_model=SystemConfigResponse)
async def get_system_config(
    system_id: int,
    x_system_token: str = Header(..., alias="X-System-Token"),
    db: AsyncSession = Depends(get_db)
):
    """
    获取系统的权限配置
    
    供业务系统拉取配置使用
    需要提供系统Token
    """
    # 验证系统Token
    system_info = verify_system_token(x_system_token, db)
    
    # 获取系统
    system_service = SystemService(db)
    system = await system_service.get_system_by_id(system_id)
    
    if not system:
        raise HTTPException(status_code=404, detail="系统不存在")
    
    # 验证Token是否属于该系统
    if system_info.get('sub') != system.code:
        raise HTTPException(status_code=403, detail="无权访问该系统配置")
    
    # 获取配置
    config_service = ConfigSyncService(db)
    config = await config_service.get_system_config(system)
    
    return config


@router.put("/{system_id}", response_model=SystemResponse)
async def update_system(
    system_id: int,
    system_data: SystemUpdate,
    current_user: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    更新系统信息
    
    需要管理员权限
    """
    system_service = SystemService(db)
    system = await system_service.update_system(
        system_id=system_id,
        name=system_data.name,
        description=system_data.description,
        api_endpoint=system_data.api_endpoint,
    )
    
    if not system:
        raise HTTPException(status_code=404, detail="系统不存在")
    
    return system


@router.put("/{system_id}/status", response_model=SystemResponse)
async def update_system_status(
    system_id: int,
    status_update: SystemStatusUpdate,
    current_user: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    更新系统状态
    
    需要管理员权限
    """
    # 验证状态值
    if status_update.status not in ["active", "inactive"]:
        raise HTTPException(status_code=400, detail="无效的状态值")
    
    system_service = SystemService(db)
    system = await system_service.update_system_status(system_id, status_update.status)
    
    if not system:
        raise HTTPException(status_code=404, detail="系统不存在")
    
    return system


@router.post("/{system_id}/token/regenerate", response_model=SystemWithToken)
async def regenerate_system_token(
    system_id: int,
    current_user: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    重新生成系统Token
    
    需要管理员权限
    """
    system_service = SystemService(db)
    system = await system_service.regenerate_system_token(system_id)
    
    if not system:
        raise HTTPException(status_code=404, detail="系统不存在")
    
    return system


@router.get("/{system_id}/roles", response_model=list[RoleResponse])
async def get_system_roles(
    system_id: int,
    current_user: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    获取系统的角色列表
    
    需要管理员权限
    """
    system_service = SystemService(db)
    
    # 检查系统是否存在
    system = await system_service.get_system_by_id(system_id)
    if not system:
        raise HTTPException(status_code=404, detail="系统不存在")
    
    roles = await system_service.get_system_roles(system_id)
    return roles


@router.get("/{system_id}/permissions", response_model=list[PermissionResponse])
async def get_system_permissions(
    system_id: int,
    current_user: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    获取系统的权限列表
    
    需要管理员权限
    """
    system_service = SystemService(db)
    
    # 检查系统是否存在
    system = await system_service.get_system_by_id(system_id)
    if not system:
        raise HTTPException(status_code=404, detail="系统不存在")
    
    permissions = await system_service.get_system_permissions(system_id)
    return permissions

