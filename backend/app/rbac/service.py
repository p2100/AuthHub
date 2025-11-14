"""RBAC服务"""
from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.role import Role
from app.models.permission import Permission, RolePermission
from app.models.user_role import UserRole
from app.models.route_pattern import RoutePattern
from app.models.resource_binding import ResourceBinding
from app.rbac.notifier import permission_notifier


class RoleService:
    """角色服务"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_role(
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
        self.db.commit()
        self.db.refresh(role)
        
        # 通知权限变更
        permission_notifier.notify_role_created(role)
        
        return role
    
    def update_role_permissions(self, role_id: int, permission_ids: List[int]):
        """更新角色权限"""
        role = self.db.query(Role).get(role_id)
        if not role:
            return
        
        # 删除旧的权限关联
        self.db.query(RolePermission).filter(
            RolePermission.role_id == role_id
        ).delete()
        
        # 添加新的权限关联
        for perm_id in permission_ids:
            role_perm = RolePermission(
                role_id=role_id,
                permission_id=perm_id
            )
            self.db.add(role_perm)
        
        self.db.commit()
        
        # 通知权限变更
        permission_notifier.notify_role_permissions_updated(role)
    
    def assign_role_to_user(self, user_id: int, role_id: int, created_by: Optional[int] = None):
        """为用户分配角色"""
        user_role = UserRole(
            user_id=user_id,
            role_id=role_id,
            created_by=created_by
        )
        self.db.add(user_role)
        self.db.commit()
        
        # 通知用户权限变更
        permission_notifier.notify_user_permissions_changed(user_id)


class PermissionService:
    """权限服务"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_permission(
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
        self.db.commit()
        self.db.refresh(permission)
        
        return permission


class RoutePatternService:
    """路由规则服务"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_route_pattern(
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
        self.db.commit()
        self.db.refresh(route)
        
        return route


class ResourceBindingService:
    """资源绑定服务"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_binding(
        self,
        user_id: int,
        namespace: str,
        resource_type: str,
        resource_id: str,
        system_id: Optional[int] = None,
        action: str = "",
        created_by: Optional[int] = None
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
        self.db.commit()
        self.db.refresh(binding)
        
        # 通知用户权限变更
        permission_notifier.notify_user_permissions_changed(user_id)
        
        return binding
    
    def batch_create_bindings(
        self,
        user_id: int,
        namespace: str,
        resource_type: str,
        resource_ids: List[str],
        system_id: Optional[int] = None,
        action: str = "",
        created_by: Optional[int] = None
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
        
        self.db.bulk_save_objects(bindings)
        self.db.commit()
        
        # 通知用户权限变更
        permission_notifier.notify_user_permissions_changed(user_id)

