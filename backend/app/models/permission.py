"""权限模型"""

from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import relationship

from app.core.database import Base


class Permission(Base):
    """权限定义"""

    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
        comment="权限代码: system_a:document:read",
    )
    name = Column(String(100), nullable=False, comment="权限名称")
    namespace = Column(String(50), nullable=False, index=True, comment="命名空间")
    system_id = Column(Integer, ForeignKey("systems.id"), nullable=True, comment="所属系统ID")
    resource_type = Column(String(50), comment="资源类型: document, order")
    action = Column(String(50), comment="操作: read, write, delete")
    description = Column(Text, comment="权限描述")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")

    # 关系
    system = relationship("System", back_populates="permissions")
    roles = relationship(
        "RolePermission", back_populates="permission", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Permission {self.code}>"


class RolePermission(Base):
    """角色-权限关联表"""

    __tablename__ = "role_permissions"

    id = Column(Integer, primary_key=True, index=True)
    role_id = Column(Integer, ForeignKey("roles.id", ondelete="CASCADE"), nullable=False)
    permission_id = Column(
        Integer, ForeignKey("permissions.id", ondelete="CASCADE"), nullable=False
    )
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")

    # 关系
    role = relationship("Role", back_populates="permissions")
    permission = relationship("Permission", back_populates="roles")

    # 唯一约束
    __table_args__ = (UniqueConstraint("role_id", "permission_id", name="uq_role_permission"),)

    def __repr__(self):
        return f"<RolePermission role_id={self.role_id} permission_id={self.permission_id}>"
