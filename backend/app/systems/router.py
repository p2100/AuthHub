"""系统管理API路由"""

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import require_admin, verify_system_token
from app.schemas.rbac import PermissionResponse, RoleResponse
from app.schemas.system import (
    SystemConfigResponse,
    SystemCreate,
    SystemResponse,
    SystemStatusUpdate,
    SystemUpdate,
    SystemWithToken,
)
from app.systems.service import ConfigSyncService, SystemService

router = APIRouter(prefix="/systems", tags=["系统管理"])


@router.post("", response_model=SystemWithToken)
async def create_system(
    system_data: SystemCreate,
    current_user: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
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
        api_endpoint=system_data.api_endpoint,
    )

    return system


@router.get("", response_model=list[SystemResponse])
async def list_systems(
    current_user: dict = Depends(require_admin), db: AsyncSession = Depends(get_db)
):
    """获取系统列表"""
    system_service = SystemService(db)
    systems = await system_service.list_systems()
    return systems


@router.get("/{system_id}", response_model=SystemResponse)
async def get_system(
    system_id: int, current_user: dict = Depends(require_admin), db: AsyncSession = Depends(get_db)
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
    db: AsyncSession = Depends(get_db),
):
    """
    获取系统的权限配置

    供业务系统拉取配置使用
    需要提供系统Token
    """
    print(f"\n{'=' * 60}")
    print(f"📥 [获取系统配置] system_id={system_id}")
    print(f"📥 [获取系统配置] X-System-Token前30字符: {x_system_token[:30]}...")

    # 验证系统Token
    print(f"🔐 [获取系统配置] 开始验证系统Token...")
    system_info = verify_system_token(x_system_token, db)
    print(f"✅ [获取系统配置] Token验证通过, 系统代码: {system_info.get('sub')}")

    # 获取系统
    print(f"🔍 [获取系统配置] 查询系统信息...")
    system_service = SystemService(db)
    system = await system_service.get_system_by_id(system_id)

    if not system:
        print(f"❌ [获取系统配置] 系统不存在: system_id={system_id}")
        raise HTTPException(status_code=404, detail="系统不存在")

    print(f"✅ [获取系统配置] 系统信息: code={system.code}, name={system.name}")

    # 验证Token是否属于该系统
    token_system_code = system_info.get("sub")
    print(f"🔍 [获取系统配置] Token系统代码: {token_system_code}")
    print(f"🔍 [获取系统配置] 目标系统代码: {system.code}")

    if token_system_code != system.code:
        print(f"❌ [获取系统配置] 系统代码不匹配! Token={token_system_code}, System={system.code}")
        raise HTTPException(status_code=403, detail="无权访问该系统配置")

    print(f"✅ [获取系统配置] 系统代码匹配")

    # 获取配置
    print(f"🔍 [获取系统配置] 开始获取配置...")
    config_service = ConfigSyncService(db)
    config = await config_service.get_system_config(system)

    print(f"✅ [获取系统配置] 配置获取成功")
    print(f"{'=' * 60}\n")

    return config


@router.put("/{system_id}", response_model=SystemResponse)
async def update_system(
    system_id: int,
    system_data: SystemUpdate,
    current_user: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
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
    db: AsyncSession = Depends(get_db),
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
    system_id: int, current_user: dict = Depends(require_admin), db: AsyncSession = Depends(get_db)
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
    system_id: int, current_user: dict = Depends(require_admin), db: AsyncSession = Depends(get_db)
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
    system_id: int, current_user: dict = Depends(require_admin), db: AsyncSession = Depends(get_db)
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
