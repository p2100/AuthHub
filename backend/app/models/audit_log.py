"""审计日志模型"""

from datetime import datetime

from sqlalchemy import JSON, Column, DateTime, ForeignKey, Index, Integer, String
from sqlalchemy.orm import relationship

from app.core.database import Base


class AuditLog(Base):
    """权限变更审计日志"""

    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    action_type = Column(
        String(50), nullable=False, index=True, comment="操作类型: role_created, permission_updated"
    )
    operator_id = Column(String(100), ForeignKey("users.feishu_user_id"), comment="操作人ID")
    target_type = Column(String(50), comment="目标类型: role, permission, user")
    target_id = Column(String(100), comment="目标ID")
    namespace = Column(String(50), index=True, comment="命名空间")
    system_id = Column(Integer, ForeignKey("systems.id"), nullable=True)
    changes = Column(JSON, comment="变更详情")
    ip_address = Column(String(50), comment="IP地址")
    user_agent = Column(String(500), comment="User Agent")
    created_at = Column(DateTime, default=datetime.utcnow, index=True, comment="创建时间")

    # 关系
    operator = relationship("User", back_populates="audit_logs")
    system = relationship("System", back_populates="audit_logs")

    def __repr__(self):
        return f"<AuditLog {self.action_type}>"
