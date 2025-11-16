"""RBAC API路由"""

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import require_admin
from app.rbac.service import (
    PermissionService,
    ResourceBindingService,
    RoleService,
    RoutePatternService,
)
from app.schemas.rbac import (
    PermissionCreate,
    PermissionResponse,
    ResourceBindingCreate,
    RoleCreate,
    RoleResponse,
    RoutePatternCreate,
    StatsResponse,
    UpdateRolePermissions,
)

router = APIRouter(prefix="/rbac", tags=["RBAC权限管理"])


# ========== 统计数据 ==========


@router.get("/stats", response_model=StatsResponse)
async def get_stats(
    current_user: dict = Depends(require_admin), db: AsyncSession = Depends(get_db)
):
    """
    获取系统统计数据

    需要管理员权限
    """
    from sqlalchemy import func

    from app.models.role import Role
    from app.models.system import System
    from app.models.user import User

    # 统计系统数量
    system_count_result = await db.execute(select(func.count(System.id)))
    system_count = system_count_result.scalar() or 0

    # 统计用户数量
    user_count_result = await db.execute(select(func.count(User.id)))
    user_count = user_count_result.scalar() or 0

    # 统计角色数量
    role_count_result = await db.execute(select(func.count(Role.id)))
    role_count = role_count_result.scalar() or 0

    return StatsResponse(system_count=system_count, user_count=user_count, role_count=role_count)


# ========== 角色管理 ==========


@router.post("/roles", response_model=RoleResponse)
async def create_role(
    role_data: RoleCreate,
    current_user: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """创建角色"""
    role_service = RoleService(db)

    # 构建完整的code
    if role_data.namespace == "global":
        code = f"global:{role_data.code}"
    else:
        code = f"{role_data.namespace}:{role_data.code}"

    role = role_service.create_role(
        code=code,
        name=role_data.name,
        namespace=role_data.namespace,
        system_id=role_data.system_id,
        description=role_data.description,
    )

    return role


@router.get("/roles", response_model=list[RoleResponse])
async def list_roles(
    namespace: Optional[str] = Query(None, description="命名空间过滤"),
    system_id: Optional[int] = Query(None, description="系统ID过滤"),
    db: AsyncSession = Depends(get_db),
):
    """获取角色列表"""
    from app.models.role import Role

    stmt = select(Role)

    if namespace:
        stmt = stmt.where(Role.namespace == namespace)

    if system_id:
        stmt = stmt.where(Role.system_id == system_id)

    result = await db.execute(stmt)
    roles = result.scalars().all()
    return roles


@router.put("/roles/{role_id}/permissions")
async def update_role_permissions(
    role_id: int,
    data: UpdateRolePermissions,
    current_user: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """更新角色的权限"""
    role_service = RoleService(db)
    role_service.update_role_permissions(role_id, data.permission_ids)

    return {"message": "权限更新成功"}


@router.post("/users/{user_id}/roles/{role_id}")
async def assign_role_to_user(
    user_id: int,
    role_id: int,
    current_user: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """为用户分配角色"""
    role_service = RoleService(db)
    creator_id = int(current_user.get("sub", 0))

    role_service.assign_role_to_user(user_id, role_id, creator_id)

    return {"message": "角色分配成功"}


# ========== 权限管理 ==========


@router.post("/permissions", response_model=PermissionResponse)
async def create_permission(
    perm_data: PermissionCreate,
    current_user: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """创建权限"""
    perm_service = PermissionService(db)

    permission = perm_service.create_permission(
        code=perm_data.code,
        name=perm_data.name,
        namespace=perm_data.namespace,
        system_id=perm_data.system_id,
        resource_type=perm_data.resource_type,
        action=perm_data.action,
        description=perm_data.description,
    )

    return permission


@router.get("/permissions", response_model=list[PermissionResponse])
async def list_permissions(
    namespace: Optional[str] = Query(None, description="命名空间过滤"),
    db: AsyncSession = Depends(get_db),
):
    """获取权限列表"""
    from app.models.permission import Permission

    stmt = select(Permission)

    if namespace:
        stmt = stmt.where(Permission.namespace == namespace)

    result = await db.execute(stmt)
    permissions = result.scalars().all()
    return permissions


# ========== 路由规则 ==========


@router.post("/routes")
async def create_route_pattern(
    route_data: RoutePatternCreate,
    current_user: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """创建路由规则"""
    route_service = RoutePatternService(db)

    route = route_service.create_route_pattern(
        system_id=route_data.system_id,
        role_id=route_data.role_id,
        pattern=route_data.pattern,
        method=route_data.method,
        priority=route_data.priority,
        description=route_data.description,
    )

    return route


@router.get("/routes")
async def list_route_patterns(
    system_id: Optional[int] = Query(None, description="系统ID过滤"),
    db: AsyncSession = Depends(get_db),
):
    """获取路由规则列表"""
    from app.models.route_pattern import RoutePattern

    stmt = select(RoutePattern)

    if system_id:
        stmt = stmt.where(RoutePattern.system_id == system_id)

    result = await db.execute(stmt)
    routes = result.scalars().all()
    return routes


# ========== 资源绑定 ==========


@router.post("/resource-bindings")
async def create_resource_bindings(
    binding_data: ResourceBindingCreate,
    current_user: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """批量创建资源绑定"""
    binding_service = ResourceBindingService(db)
    creator_id = int(current_user.get("sub", 0))

    binding_service.batch_create_bindings(
        user_id=binding_data.user_id,
        namespace=binding_data.namespace,
        resource_type=binding_data.resource_type,
        resource_ids=binding_data.resource_ids,
        system_id=binding_data.system_id,
        action=binding_data.action,
        created_by=creator_id,
    )

    return {"message": f"成功绑定{len(binding_data.resource_ids)}个资源"}
