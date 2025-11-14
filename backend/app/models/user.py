"""用户模型"""
from sqlalchemy import Column, Integer, String, DateTime, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base


class User(Base):
    """用户(同步飞书)"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, index=True)
    feishu_user_id = Column(String(100), unique=True, nullable=False, index=True, comment="飞书用户ID")
    username = Column(String(100), nullable=False, comment="用户名")
    email = Column(String(200), index=True, comment="邮箱")
    avatar = Column(String(500), comment="头像URL")
    mobile = Column(String(20), comment="手机号")
    
    # 飞书组织信息
    dept_ids = Column(JSON, comment="部门ID列表")
    dept_names = Column(JSON, comment="部门名称列表")
    
    status = Column(String(20), default='active', comment="状态: active, inactive")
    last_login = Column(DateTime, comment="最后登录时间")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")
    
    # 关系
    roles = relationship("UserRole", back_populates="user", foreign_keys="[UserRole.user_id]")
    resource_bindings = relationship("ResourceBinding", back_populates="user", foreign_keys="[ResourceBinding.user_id]")
    created_user_roles = relationship("UserRole", back_populates="creator", foreign_keys="[UserRole.created_by]")
    audit_logs = relationship("AuditLog", back_populates="operator")
    
    def __repr__(self):
        return f"<User {self.username}>"

