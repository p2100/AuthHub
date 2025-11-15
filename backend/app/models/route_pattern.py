"""路由匹配规则模型"""

from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.core.database import Base


class RoutePattern(Base):
    """路由正则规则"""

    __tablename__ = "route_patterns"

    id = Column(Integer, primary_key=True, index=True)
    system_id = Column(
        Integer, ForeignKey("systems.id", ondelete="CASCADE"), nullable=False, index=True
    )
    role_id = Column(
        Integer, ForeignKey("roles.id", ondelete="CASCADE"), nullable=False, index=True
    )
    pattern = Column(String(200), nullable=False, comment="路由正则: /api/v1/documents/\\d+")
    method = Column(String(10), default="*", comment="HTTP方法: GET, POST, *")
    description = Column(Text, comment="规则描述")
    priority = Column(Integer, default=0, comment="优先级(数字越大优先级越高)")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")

    # 关系
    system = relationship("System", back_populates="route_patterns")
    role = relationship("Role", back_populates="route_patterns")

    def __repr__(self):
        return f"<RoutePattern {self.pattern}>"
