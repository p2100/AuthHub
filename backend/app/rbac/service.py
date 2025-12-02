"""RBAC服务"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload
from typing import List, Optional
from app.models.role import Role
from app.models.permission import Permission, RolePermission
from app.models.user_role import UserRole
from app.models.user import User
from app.models.route_pattern import RoutePattern
from app.models.resource_binding import ResourceBinding
from app.rbac.notifier import permission_notifier


class RoleService:
    """角色服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_role(
        self,
        code: str,
        name: str,
        namespace: str,
        system_id: Optional[int] = None,
        description: str = ""
    ) -> Role:
        """创建角色"""
        role = Role(
            code=code,
            name=name,
            namespace=namespace,
            system_id=system_id,
            description=description
        )
        self.db.add(role)
        await self.db.commit()
        await self.db.refresh(role)
        
        # 通知权限变更
        permission_notifier.notify_role_created(role)
        
        return role
    
    async def get_role_by_id(self, role_id: int) -> Optional[Role]:
        """根据ID获取角色"""
        result = await self.db.execute(select(Role).filter(Role.id == role_id))
        return result.scalar_one_or_none()
    
    async def update_role(
        self,
        role_id: int,
        name: Optional[str] = None,
        description: Optional[str] = None
    ) -> Optional[Role]:
        """更新角色信息"""
        result = await self.db.execute(select(Role).filter(Role.id == role_id))
        role = result.scalar_one_or_none()
        
        if role:
            if name is not None:
                role.name = name
            if description is not None:
                role.description = description
            
            await self.db.commit()
            await self.db.refresh(role)
        
        return role
    
    async def delete_role(self, role_id: int) -> bool:
        """删除角色"""
        result = await self.db.execute(select(Role).filter(Role.id == role_id))
        role = result.scalar_one_or_none()
        
        if not role:
            return False
        
        # 删除角色权限关联
        await self.db.execute(
            delete(RolePermission).where(RolePermission.role_id == role_id)
        )
        
        # 删除用户角色关联
        await self.db.execute(
            delete(UserRole).where(UserRole.role_id == role_id)
        )
        
        # 删除角色
        await self.db.delete(role)
        await self.db.commit()
        
        return True
    
    async def get_role_users(self, role_id: int) -> List[User]:
        """获取拥有该角色的用户列表"""
        result = await self.db.execute(
            select(User)
            .join(UserRole, UserRole.user_id == User.feishu_user_id)
            .filter(UserRole.role_id == role_id)
            .order_by(UserRole.created_at.desc())
        )
        return list(result.scalars().all())
    
    async def update_role_permissions(self, role_id: int, permission_ids: List[int]):
        """更新角色权限"""
        result = await self.db.execute(select(Role).filter(Role.id == role_id))
        role = result.scalar_one_or_none()
        if not role:
            return
        
        # 删除旧的权限关联
        await self.db.execute(
            delete(RolePermission).where(RolePermission.role_id == role_id)
        )
        
        # 添加新的权限关联
        for perm_id in permission_ids:
            role_perm = RolePermission(
                role_id=role_id,
                permission_id=perm_id
            )
            self.db.add(role_perm)
        
        await self.db.commit()
        await self.db.refresh(role)
        
        # 通知权限变更
        permission_notifier.notify_role_permissions_updated(role)
    
    async def assign_role_to_user(self, user_id: str, role_id: int, created_by: Optional[str] = None):
        """为用户分配角色"""
        user_role = UserRole(
            user_id=user_id,
            role_id=role_id,
            created_by=created_by
        )
        self.db.add(user_role)
        await self.db.commit()
        
        # 通知用户权限变更
        permission_notifier.notify_user_permissions_changed(user_id)
    
    async def remove_role_from_user(self, user_id: str, role_id: int) -> bool:
        """移除用户角色"""
        result = await self.db.execute(
            delete(UserRole).where(
                UserRole.user_id == user_id,
                UserRole.role_id == role_id
            )
        )
        await self.db.commit()
        
        # 通知用户权限变更
        if result.rowcount > 0:
            permission_notifier.notify_user_permissions_changed(user_id)
            return True
        return False


class PermissionService:
    """权限服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_permission(
        self,
        code: str,
        name: str,
        namespace: str,
        system_id: Optional[int] = None,
        resource_type: str = "",
        action: str = "",
        description: str = ""
    ) -> Permission:
        """创建权限"""
        permission = Permission(
            code=code,
            name=name,
            namespace=namespace,
            system_id=system_id,
            resource_type=resource_type,
            action=action,
            description=description
        )
        self.db.add(permission)
        await self.db.commit()
        await self.db.refresh(permission)
        
        return permission
    
    async def get_permission_by_id(self, permission_id: int) -> Optional[Permission]:
        """根据ID获取权限"""
        result = await self.db.execute(select(Permission).filter(Permission.id == permission_id))
        return result.scalar_one_or_none()
    
    async def update_permission(
        self,
        permission_id: int,
        name: Optional[str] = None,
        description: Optional[str] = None,
        resource_type: Optional[str] = None,
        action: Optional[str] = None
    ) -> Optional[Permission]:
        """更新权限"""
        result = await self.db.execute(select(Permission).filter(Permission.id == permission_id))
        permission = result.scalar_one_or_none()
        
        if permission:
            if name is not None:
                permission.name = name
            if description is not None:
                permission.description = description
            if resource_type is not None:
                permission.resource_type = resource_type
            if action is not None:
                permission.action = action
            
            await self.db.commit()
            await self.db.refresh(permission)
        
        return permission
    
    async def delete_permission(self, permission_id: int) -> bool:
        """删除权限"""
        result = await self.db.execute(select(Permission).filter(Permission.id == permission_id))
        permission = result.scalar_one_or_none()
        
        if not permission:
            return False
        
        # 删除权限与角色的关联
        await self.db.execute(
            delete(RolePermission).where(RolePermission.permission_id == permission_id)
        )
        
        # 删除权限
        await self.db.delete(permission)
        await self.db.commit()
        
        return True


class RoutePatternService:
    """路由规则服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_route_pattern(
        self,
        system_id: int,
        role_id: int,
        pattern: str,
        method: str = "*",
        priority: int = 0,
        description: str = ""
    ) -> RoutePattern:
        """创建路由规则"""
        route = RoutePattern(
            system_id=system_id,
            role_id=role_id,
            pattern=pattern,
            method=method,
            priority=priority,
            description=description
        )
        self.db.add(route)
        await self.db.commit()
        await self.db.refresh(route)
        
        return route
    
    async def get_route_pattern_by_id(self, route_id: int) -> Optional[RoutePattern]:
        """根据ID获取路由规则"""
        result = await self.db.execute(select(RoutePattern).filter(RoutePattern.id == route_id))
        return result.scalar_one_or_none()
    
    async def update_route_pattern(
        self,
        route_id: int,
        pattern: Optional[str] = None,
        method: Optional[str] = None,
        priority: Optional[int] = None,
        description: Optional[str] = None
    ) -> Optional[RoutePattern]:
        """更新路由规则"""
        result = await self.db.execute(select(RoutePattern).filter(RoutePattern.id == route_id))
        route = result.scalar_one_or_none()
        
        if route:
            if pattern is not None:
                route.pattern = pattern
            if method is not None:
                route.method = method
            if priority is not None:
                route.priority = priority
            if description is not None:
                route.description = description
            
            await self.db.commit()
            await self.db.refresh(route)
        
        return route
    
    async def delete_route_pattern(self, route_id: int) -> bool:
        """删除路由规则"""
        result = await self.db.execute(select(RoutePattern).filter(RoutePattern.id == route_id))
        route = result.scalar_one_or_none()
        
        if not route:
            return False
        
        await self.db.delete(route)
        await self.db.commit()
        
        return True


class ResourceBindingService:
    """资源绑定服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_binding(
        self,
        user_id: str,
        namespace: str,
        resource_type: str,
        resource_id: str,
        system_id: Optional[int] = None,
        action: str = "",
        created_by: Optional[str] = None
    ) -> ResourceBinding:
        """创建资源绑定"""
        binding = ResourceBinding(
            user_id=user_id,
            namespace=namespace,
            system_id=system_id,
            resource_type=resource_type,
            resource_id=resource_id,
            action=action,
            created_by=created_by
        )
        self.db.add(binding)
        await self.db.commit()
        await self.db.refresh(binding)
        
        # 通知用户权限变更
        permission_notifier.notify_user_permissions_changed(user_id)
        
        return binding
    
    async def batch_create_bindings(
        self,
        user_id: str,
        namespace: str,
        resource_type: str,
        resource_ids: List[str],
        system_id: Optional[int] = None,
        action: str = "",
        created_by: Optional[str] = None
    ):
        """批量创建资源绑定"""
        bindings = []
        for resource_id in resource_ids:
            binding = ResourceBinding(
                user_id=user_id,
                namespace=namespace,
                system_id=system_id,
                resource_type=resource_type,
                resource_id=resource_id,
                action=action,
                created_by=created_by
            )
            bindings.append(binding)
            self.db.add(binding)
        
        await self.db.commit()
        
        # 通知用户权限变更
        permission_notifier.notify_user_permissions_changed(user_id)
    
    async def list_bindings(
        self,
        user_id: Optional[str] = None,
        system_id: Optional[int] = None,
        namespace: Optional[str] = None
    ) -> List[ResourceBinding]:
        """获取资源绑定列表"""
        stmt = select(ResourceBinding)
        
        if user_id is not None:
            stmt = stmt.filter(ResourceBinding.user_id == user_id)
        if system_id is not None:
            stmt = stmt.filter(ResourceBinding.system_id == system_id)
        if namespace is not None:
            stmt = stmt.filter(ResourceBinding.namespace == namespace)
        
        stmt = stmt.order_by(ResourceBinding.created_at.desc())
        
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
    
    async def delete_binding(self, binding_id: int) -> bool:
        """删除资源绑定"""
        result = await self.db.execute(
            select(ResourceBinding).filter(ResourceBinding.id == binding_id)
        )
        binding = result.scalar_one_or_none()
        
        if not binding:
            return False
        
        user_id = binding.user_id
        await self.db.delete(binding)
        await self.db.commit()
        
        # 通知用户权限变更
        permission_notifier.notify_user_permissions_changed(user_id)
        
        return True


