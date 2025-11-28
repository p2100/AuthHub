"""用户管理API路由"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_admin, require_admin_or_system
from app.schemas.user import (
    UserDetailResponse,
    UserListResponse,
    UserPermissionDetail,
    UserResponse,
    UserRoleResponse,
    UserSimpleListResponse,
    UserSimpleResponse,
    UserStatusUpdate,
)
from app.users.permission_collector import PermissionCollector
from app.users.service import UserService

router = APIRouter(prefix="/users", tags=["用户管理"])


@router.get("/simple", response_model=UserSimpleListResponse)
async def list_users_simple(
    skip: int = Query(0, ge=0, description="跳过数量"),
    limit: int = Query(100, ge=1, le=1000, description="每页数量"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    获取用户简单列表（仅ID和用户名）

    只需要有效的Token（用户或系统Token均可）
    """
    user_service = UserService(db)
    users, total = await user_service.list_users_simple(skip=skip, limit=limit, search=search)

    # 将结果转换为响应格式
    items = [
        UserSimpleResponse(feishu_user_id=user.feishu_user_id, username=user.username)
        for user in users
    ]

    return UserSimpleListResponse(total=total, items=items)


@router.get("", response_model=UserListResponse)
async def list_users(
    skip: int = Query(0, ge=0, description="跳过数量"),
    limit: int = Query(100, ge=1, le=1000, description="每页数量"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    dept_id: Optional[str] = Query(None, description="部门ID筛选"),
    status: Optional[str] = Query(None, description="状态筛选"),
    current_user: dict = Depends(require_admin_or_system),
    db: AsyncSession = Depends(get_db),
):
    """
    获取用户列表

    需要管理员权限或系统Token
    """
    user_service = UserService(db)
    users, total = await user_service.list_users(
        skip=skip, limit=limit, search=search, dept_id=dept_id, status=status
    )

    return UserListResponse(total=total, items=users)


@router.get("/{user_id}", response_model=UserDetailResponse)
async def get_user(
    user_id: str,
    current_user: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    获取用户详情

    需要管理员权限
    """
    user_service = UserService(db)
    user = await user_service.get_user_by_id(user_id)

    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    return user


@router.put("/{user_id}/status", response_model=UserResponse)
async def update_user_status(
    user_id: str,
    status_update: UserStatusUpdate,
    current_user: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    更新用户状态

    需要管理员权限
    """
    # 验证状态值
    if status_update.status not in ["active", "inactive"]:
        raise HTTPException(status_code=400, detail="无效的状态值")

    user_service = UserService(db)
    user = await user_service.update_user_status(user_id, status_update.status)

    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    return user


@router.get("/{user_id}/roles", response_model=list[UserRoleResponse])
async def get_user_roles(
    user_id: str,
    current_user: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    获取用户的角色列表

    需要管理员权限
    """
    user_service = UserService(db)

    # 检查用户是否存在
    user = await user_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 获取用户角色
    user_roles = await user_service.get_user_roles(user_id)

    # 转换为响应格式
    result = []
    for ur in user_roles:
        result.append(
            UserRoleResponse(
                role_id=ur.role_id,
                role_code=ur.role.code,
                role_name=ur.role.name,
                namespace=ur.role.namespace,
                assigned_at=ur.created_at,
                created_by=ur.created_by,
            )
        )

    return result


@router.get("/{user_id}/permissions", response_model=UserPermissionDetail)
async def get_user_permissions(
    user_id: str,
    current_user: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    获取用户的权限详情

    需要管理员权限
    """
    user_service = UserService(db)

    # 检查用户是否存在
    user = await user_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 收集用户权限
    permission_collector = PermissionCollector(db)
    permissions = await permission_collector.collect(user_id)

    # 获取角色详情
    user_roles = await user_service.get_user_roles(user_id)
    roles_detail = []
    for ur in user_roles:
        roles_detail.append(
            UserRoleResponse(
                role_id=ur.role_id,
                role_code=ur.role.code,
                role_name=ur.role.name,
                namespace=ur.role.namespace,
                assigned_at=ur.created_at,
                created_by=ur.created_by,
            )
        )

    return UserPermissionDetail(
        global_roles=permissions.get("global_roles", []),
        system_roles=permissions.get("system_roles", {}),
        global_resources=permissions.get("global_resources", {}),
        system_resources=permissions.get("system_resources", {}),
        roles=roles_detail,
    )
