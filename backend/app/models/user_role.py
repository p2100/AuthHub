"""用户-角色关联模型"""
from sqlalchemy import Column, Integer, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base


class UserRole(Base):
    """用户-角色关联"""
    __tablename__ = 'user_roles'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    role_id = Column(Integer, ForeignKey('roles.id', ondelete='CASCADE'), nullable=False, index=True)
    created_by = Column(Integer, ForeignKey('users.id'), comment="分配人ID")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    
    # 关系
    user = relationship("User", back_populates="roles", foreign_keys=[user_id])
    role = relationship("Role", back_populates="user_roles")
    creator = relationship("User", back_populates="created_user_roles", foreign_keys=[created_by])
    
    # 唯一约束
    __table_args__ = (
        UniqueConstraint('user_id', 'role_id', name='uq_user_role'),
    )
    
    def __repr__(self):
        return f"<UserRole user_id={self.user_id} role_id={self.role_id}>"

