"""权限收集器 - 收集用户的完整权限"""

from typing import Dict

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.user import User
from app.models.user_role import UserRole


class PermissionCollector:
    """权限收集器"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def collect(self, user_id: int) -> Dict:
        """
        收集用户在所有系统中的权限

        Args:
            user_id: 用户ID

        Returns:
            权限字典:
            {
                "global_roles": ["admin"],
                "system_roles": {"system_a": ["editor"], "system_b": ["viewer"]},
                "global_resources": {"project": [123, 456], "team": [789]},
                "system_resources": {"system_a": {"document": [100, 101]}}
            }
        """
        # 使用selectinload预加载关联数据
        result = await self.db.execute(
            select(User)
            .filter(User.id == user_id)
            .options(
                selectinload(User.roles).selectinload(UserRole.role),
                selectinload(User.resource_bindings),
            )
        )
        user = result.scalar_one_or_none()
        if not user:
            return self._empty_permissions()

        result = {
            "global_roles": [],
            "system_roles": {},
            "global_resources": {},
            "system_resources": {},
        }

        # 1. 收集角色
        for user_role in user.roles:
            role = user_role.role

            if role.namespace == "global":
                # 全局角色(去掉命名空间前缀)
                role_name = role.code.replace("global:", "")
                result["global_roles"].append(role_name)
            else:
                # 系统角色
                system_code = role.namespace
                if system_code not in result["system_roles"]:
                    result["system_roles"][system_code] = []

                # 去掉命名空间前缀
                role_name = role.code.replace(f"{system_code}:", "")
                result["system_roles"][system_code].append(role_name)

        # 2. 收集资源绑定
        for binding in user.resource_bindings:
            if binding.namespace == "global":
                # 全局资源
                if binding.resource_type not in result["global_resources"]:
                    result["global_resources"][binding.resource_type] = []

                try:
                    resource_id = int(binding.resource_id)
                except ValueError:
                    resource_id = binding.resource_id

                result["global_resources"][binding.resource_type].append(resource_id)
            else:
                # 系统资源
                system_code = binding.namespace
                if system_code not in result["system_resources"]:
                    result["system_resources"][system_code] = {}

                if binding.resource_type not in result["system_resources"][system_code]:
                    result["system_resources"][system_code][binding.resource_type] = []

                try:
                    resource_id = int(binding.resource_id)
                except ValueError:
                    resource_id = binding.resource_id

                result["system_resources"][system_code][binding.resource_type].append(resource_id)

        return result

    def _empty_permissions(self) -> Dict:
        """返回空权限结构"""
        return {
            "global_roles": [],
            "system_roles": {},
            "global_resources": {},
            "system_resources": {},
        }
