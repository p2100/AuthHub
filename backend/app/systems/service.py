"""系统管理服务"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, Dict, List
from datetime import datetime

from app.models.system import System
from app.models.role import Role
from app.models.permission import Permission
from app.models.route_pattern import RoutePattern
from app.core.security import jwt_handler


class SystemService:
    """系统管理服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_system(
        self,
        code: str,
        name: str,
        description: str = "",
        api_endpoint: str = ""
    ) -> System:
        """
        创建系统并生成系统Token
        
        Args:
            code: 系统代码
            name: 系统名称
            description: 系统描述
            api_endpoint: API地址
            
        Returns:
            System对象
        """
        # 生成系统Token(1年有效期)
        system_token = jwt_handler.generate_system_token(
            system_id=code,
            system_name=name,
            expires_days=365
        )
        
        system = System(
            code=code,
            name=name,
            description=description,
            api_endpoint=api_endpoint,
            system_token=system_token,
            status='active'
        )
        
        self.db.add(system)
        await self.db.commit()
        await self.db.refresh(system)
        
        return system
    
    async def get_system_by_code(self, code: str) -> Optional[System]:
        """根据代码获取系统"""
        result = await self.db.execute(select(System).filter(System.code == code))
        return result.scalar_one_or_none()
    
    async def get_system_by_id(self, system_id: int) -> Optional[System]:
        """根据ID获取系统"""
        result = await self.db.execute(select(System).filter(System.id == system_id))
        return result.scalar_one_or_none()
    
    async def list_systems(self) -> List[System]:
        """获取所有系统列表"""
        result = await self.db.execute(select(System).order_by(System.created_at.desc()))
        return list(result.scalars().all())
    
    async def update_system(
        self,
        system_id: int,
        name: Optional[str] = None,
        description: Optional[str] = None,
        api_endpoint: Optional[str] = None
    ) -> Optional[System]:
        """
        更新系统信息
        
        Args:
            system_id: 系统ID
            name: 系统名称
            description: 系统描述
            api_endpoint: API地址
            
        Returns:
            更新后的System对象
        """
        result = await self.db.execute(select(System).filter(System.id == system_id))
        system = result.scalar_one_or_none()
        
        if system:
            if name is not None:
                system.name = name
            if description is not None:
                system.description = description
            if api_endpoint is not None:
                system.api_endpoint = api_endpoint
            
            await self.db.commit()
            await self.db.refresh(system)
        
        return system
    
    async def update_system_status(self, system_id: int, status: str) -> Optional[System]:
        """
        更新系统状态
        
        Args:
            system_id: 系统ID
            status: 状态 (active/inactive)
            
        Returns:
            更新后的System对象
        """
        result = await self.db.execute(select(System).filter(System.id == system_id))
        system = result.scalar_one_or_none()
        
        if system:
            system.status = status
            await self.db.commit()
            await self.db.refresh(system)
        
        return system
    
    async def regenerate_system_token(self, system_id: int) -> Optional[System]:
        """
        重新生成系统Token
        
        Args:
            system_id: 系统ID
            
        Returns:
            更新后的System对象
        """
        result = await self.db.execute(select(System).filter(System.id == system_id))
        system = result.scalar_one_or_none()
        
        if system:
            # 生成新的系统Token
            system_token = jwt_handler.generate_system_token(
                system_id=system.code,
                system_name=system.name,
                expires_days=365
            )
            system.system_token = system_token
            
            await self.db.commit()
            await self.db.refresh(system)
        
        return system
    
    async def get_system_roles(self, system_id: int) -> List[Role]:
        """获取系统的角色列表"""
        result = await self.db.execute(
            select(Role).filter(Role.system_id == system_id).order_by(Role.created_at.desc())
        )
        return list(result.scalars().all())
    
    async def get_system_permissions(self, system_id: int) -> List[Permission]:
        """获取系统的权限列表"""
        result = await self.db.execute(
            select(Permission).filter(Permission.system_id == system_id).order_by(Permission.created_at.desc())
        )
        return list(result.scalars().all())


class ConfigSyncService:
    """配置同步服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_system_config(self, system: System) -> Dict:
        """
        获取系统的完整权限配置
        
        Args:
            system: 系统对象
            
        Returns:
            配置字典
        """
        namespace = system.code
        
        # 查询系统的角色
        roles_result = await self.db.execute(
            select(Role).filter(Role.namespace == namespace)
        )
        roles = list(roles_result.scalars().all())
        
        # 查询系统的权限
        permissions_result = await self.db.execute(
            select(Permission).filter(Permission.namespace == namespace)
        )
        permissions = list(permissions_result.scalars().all())
        
        # 查询系统的路由规则
        route_patterns_result = await self.db.execute(
            select(RoutePattern).filter(RoutePattern.system_id == system.id)
        )
        route_patterns = list(route_patterns_result.scalars().all())
        
        # 构建配置
        config = {
            "version": self._get_config_version(system),
            "updated_at": int(datetime.utcnow().timestamp()),
            "namespace": namespace,
            
            "roles": {
                self._strip_namespace(role.code, namespace): {
                    "id": role.id,
                    "name": role.name,
                    "description": role.description,
                    "permissions": [
                        self._strip_namespace(rp.permission.code, namespace)
                        for rp in role.permissions
                    ]
                }
                for role in roles
            },
            
            "permissions": {
                self._strip_namespace(perm.code, namespace): {
                    "id": perm.id,
                    "name": perm.name,
                    "resource_type": perm.resource_type,
                    "action": perm.action
                }
                for perm in permissions
            },
            
            "route_patterns": [
                {
                    "role": self._strip_namespace(route.role.code, namespace),
                    "pattern": route.pattern,
                    "method": route.method,
                    "priority": route.priority
                }
                for route in route_patterns
            ]
        }
        
        return config
    
    def _strip_namespace(self, code: str, namespace: str) -> str:
        """去除命名空间前缀"""
        prefix = f"{namespace}:"
        if code.startswith(prefix):
            return code[len(prefix):]
        return code
    
    def _get_config_version(self, system: System) -> str:
        """获取配置版本号"""
        return f"v{system.code}_{int(datetime.utcnow().timestamp())}"

