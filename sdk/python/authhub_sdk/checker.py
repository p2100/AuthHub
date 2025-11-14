"""权限检查器"""
import re
from typing import Dict


class PermissionChecker:
    """权限检查器 - 本地校验权限"""
    
    def __init__(self, namespace: str):
        self.namespace = namespace
    
    def check_permission(
        self,
        token_payload: Dict,
        resource: str,
        action: str,
        config: Dict
    ) -> bool:
        """
        检查权限
        
        优先级:
        1. 全局管理员
        2. Token中的system_resources
        3. Token中的system_roles -> 配置中的角色权限
        
        Args:
            token_payload: Token payload
            resource: 资源类型
            action: 操作
            config: 权限配置
            
        Returns:
            是否有权限
        """
        # 1. 全局管理员
        if 'admin' in token_payload.get('global_roles', []):
            return True
        
        # 2. 构建权限代码
        perm_code = f"{resource}:{action}"
        
        # 3. 检查系统角色
        system_roles = token_payload.get('system_roles', {})
        user_roles = system_roles.get(self.namespace, [])
        
        for role_name in user_roles:
            role_config = config.get('roles', {}).get(role_name, {})
            role_permissions = role_config.get('permissions', [])
            
            # 检查精确匹配
            if perm_code in role_permissions:
                return True
            
            # 检查通配符
            if f"{resource}:*" in role_permissions:
                return True
            if "*:*" in role_permissions:
                return True
        
        return False
    
    def check_route(
        self,
        token_payload: Dict,
        path: str,
        method: str,
        config: Dict
    ) -> bool:
        """
        检查路由权限(正则匹配)
        
        Args:
            token_payload: Token payload
            path: 路由路径
            method: HTTP方法
            config: 权限配置
            
        Returns:
            是否有权限
        """
        # 全局管理员
        if 'admin' in token_payload.get('global_roles', []):
            return True
        
        # 获取用户的系统角色
        system_roles = token_payload.get('system_roles', {})
        user_roles = system_roles.get(self.namespace, [])
        
        # 遍历路由规则(按优先级排序)
        route_patterns = config.get('route_patterns', [])
        sorted_patterns = sorted(
            route_patterns,
            key=lambda x: x.get('priority', 0),
            reverse=True
        )
        
        for pattern_rule in sorted_patterns:
            # 检查角色
            if pattern_rule['role'] not in user_roles:
                continue
            
            # 检查方法
            rule_method = pattern_rule.get('method', '*')
            if rule_method != '*' and rule_method != method:
                continue
            
            # 正则匹配路径
            pattern = pattern_rule.get('pattern', '')
            if re.match(pattern, path):
                return True
        
        return False
    
    def check_resource_access(
        self,
        token_payload: Dict,
        resource_type: str,
        resource_id: int
    ) -> bool:
        """
        检查资源访问权限
        
        Args:
            token_payload: Token payload
            resource_type: 资源类型
            resource_id: 资源ID
            
        Returns:
            是否有权限
        """
        # 检查全局资源
        global_resources = token_payload.get('global_resources', {})
        if resource_id in global_resources.get(resource_type, []):
            return True
        
        # 检查系统资源
        system_resources = token_payload.get('system_resources', {})
        namespace_resources = system_resources.get(self.namespace, {})
        if resource_id in namespace_resources.get(resource_type, []):
            return True
        
        return False

