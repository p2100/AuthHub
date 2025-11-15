"""系统注册表模型"""

from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.orm import relationship

from app.core.database import Base


class System(Base):
    """接入系统"""

    __tablename__ = "systems"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True, comment="系统代码")
    name = Column(String(100), nullable=False, comment="系统名称")
    description = Column(Text, comment="系统描述")
    api_endpoint = Column(String(200), comment="系统API地址")
    system_token = Column(String(1000), unique=True, comment="系统Token")
    status = Column(String(20), default="active", comment="状态: active, inactive")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间"
    )

    # 关系
    roles = relationship("Role", back_populates="system")
    permissions = relationship("Permission", back_populates="system")
    route_patterns = relationship("RoutePattern", back_populates="system")
    resource_bindings = relationship("ResourceBinding", back_populates="system")
    audit_logs = relationship("AuditLog", back_populates="system")

    def __repr__(self):
        return f"<System {self.code}>"
