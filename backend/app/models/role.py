"""角色模型"""

from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import relationship

from app.core.database import Base


class Role(Base):
    """角色(全局 + 各系统)"""

    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
        comment="角色代码: global:admin, system_a:editor",
    )
    name = Column(String(100), nullable=False, comment="角色名称")
    namespace = Column(String(50), nullable=False, index=True, comment="命名空间: global, system_a")
    system_id = Column(Integer, ForeignKey("systems.id"), nullable=True, comment="所属系统ID")
    description = Column(Text, comment="角色描述")
    is_system_role = Column(Boolean, default=True, comment="是否系统角色")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间"
    )

    # 关系
    system = relationship("System", back_populates="roles")
    permissions = relationship(
        "RolePermission", back_populates="role", cascade="all, delete-orphan"
    )
    route_patterns = relationship(
        "RoutePattern", back_populates="role", cascade="all, delete-orphan"
    )
    user_roles = relationship("UserRole", back_populates="role")

    # 索引
    __table_args__ = (Index("idx_namespace_code", "namespace", "code"),)

    def __repr__(self):
        return f"<Role {self.code}>"
