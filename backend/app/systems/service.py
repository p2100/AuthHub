"""系统管理服务"""
from sqlalchemy.orm import Session
from typing import Optional, Dict
from datetime import datetime

from app.models.system import System
from app.models.role import Role
from app.models.permission import Permission
from app.models.route_pattern import RoutePattern
from app.core.security import jwt_handler


class SystemService:
    """系统管理服务"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_system(
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
        self.db.commit()
        self.db.refresh(system)
        
        return system
    
    def get_system_by_code(self, code: str) -> Optional[System]:
        """根据代码获取系统"""
        return self.db.query(System).filter(System.code == code).first()
    
    def get_system_by_id(self, system_id: int) -> Optional[System]:
        """根据ID获取系统"""
        return self.db.query(System).get(system_id)
    
    def list_systems(self) -> list:
        """获取所有系统列表"""
        return self.db.query(System).all()


class ConfigSyncService:
    """配置同步服务"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_system_config(self, system: System) -> Dict:
        """
        获取系统的完整权限配置
        
        Args:
            system: 系统对象
            
        Returns:
            配置字典
        """
        namespace = system.code
        
        # 查询系统的角色
        roles = self.db.query(Role).filter(
            Role.namespace == namespace
        ).all()
        
        # 查询系统的权限
        permissions = self.db.query(Permission).filter(
            Permission.namespace == namespace
        ).all()
        
        # 查询系统的路由规则
        route_patterns = self.db.query(RoutePattern).filter(
            RoutePattern.system_id == system.id
        ).all()
        
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

