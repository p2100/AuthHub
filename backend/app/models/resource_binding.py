"""资源绑定模型"""

from datetime import datetime

from sqlalchemy import JSON, Column, DateTime, ForeignKey, Index, Integer, String
from sqlalchemy.orm import relationship

from app.core.database import Base


class ResourceBinding(Base):
    """用户-资源绑定"""

    __tablename__ = "resource_bindings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        String(100), ForeignKey("users.feishu_user_id", ondelete="CASCADE"), nullable=False, index=True
    )
    namespace = Column(String(50), nullable=False, index=True, comment="命名空间: global, system_a")
    system_id = Column(Integer, ForeignKey("systems.id", ondelete="CASCADE"), nullable=True)
    resource_type = Column(String(50), nullable=False, comment="资源类型: project, team, document")
    resource_id = Column(String(100), nullable=False, comment="资源ID")
    action = Column(String(50), comment="操作: read, write, admin")
    extended_metadata = Column(JSON, comment="扩展字段")
    created_by = Column(String(100), ForeignKey("users.feishu_user_id"), comment="创建人ID")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    expires_at = Column(DateTime, nullable=True, comment="过期时间")

    # 关系
    user = relationship("User", back_populates="resource_bindings", foreign_keys=[user_id])
    system = relationship("System", back_populates="resource_bindings")

    # 索引
    __table_args__ = (
        Index("idx_user_namespace", "user_id", "namespace"),
        Index("idx_resource", "resource_type", "resource_id"),
    )

    def __repr__(self):
        return f"<ResourceBinding user={self.user_id} resource={self.resource_type}:{self.resource_id}>"
