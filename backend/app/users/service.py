"""用户服务"""
from sqlalchemy.orm import Session
from typing import Dict, Optional
from datetime import datetime

from app.models.user import User


class UserService:
    """用户服务"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def sync_user_from_feishu(self, user_info: Dict) -> User:
        """
        从飞书同步用户信息
        
        Args:
            user_info: 飞书用户信息
            
        Returns:
            User对象
        """
        feishu_user_id = user_info.get("open_id")
        
        # 查找现有用户
        user = self.db.query(User).filter(
            User.feishu_user_id == feishu_user_id
        ).first()
        
        # 用户信息
        username = user_info.get("name", "")
        email = user_info.get("email", "")
        avatar = user_info.get("avatar_url", "")
        mobile = user_info.get("mobile", "")
        
        if user:
            # 更新现有用户
            user.username = username
            user.email = email
            user.avatar = avatar
            user.mobile = mobile
            user.last_login = datetime.utcnow()
            user.status = 'active'
        else:
            # 创建新用户
            user = User(
                feishu_user_id=feishu_user_id,
                username=username,
                email=email,
                avatar=avatar,
                mobile=mobile,
                dept_ids=[],
                dept_names=[],
                status='active',
                last_login=datetime.utcnow()
            )
            self.db.add(user)
        
        self.db.commit()
        self.db.refresh(user)
        
        return user
    
    def update_user_departments(self, user_id: int, dept_ids: list, dept_names: list):
        """
        更新用户部门信息
        
        Args:
            user_id: 用户ID
            dept_ids: 部门ID列表
            dept_names: 部门名称列表
        """
        user = self.db.query(User).get(user_id)
        if user:
            user.dept_ids = dept_ids
            user.dept_names = dept_names
            self.db.commit()
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """根据ID获取用户"""
        return self.db.query(User).get(user_id)
    
    def get_user_by_feishu_id(self, feishu_user_id: str) -> Optional[User]:
        """根据飞书ID获取用户"""
        return self.db.query(User).filter(
            User.feishu_user_id == feishu_user_id
        ).first()

