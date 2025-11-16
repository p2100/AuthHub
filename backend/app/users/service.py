"""用户服务"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Dict, Optional
from datetime import datetime

from app.models.user import User


class UserService:
    """用户服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def sync_user_from_feishu(self, user_info: Dict) -> User:
        """
        从飞书同步用户信息
        
        Args:
            user_info: 飞书用户信息
            
        Returns:
            User对象
        """
        # 优先使用user_id，如果没有则使用open_id
        feishu_user_id = user_info.get("user_id") or user_info.get("open_id")
        
        # 查找现有用户（使用异步查询）
        result = await self.db.execute(
            select(User).filter(User.feishu_user_id == feishu_user_id)
        )
        user = result.scalar_one_or_none()
        
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
        
        await self.db.commit()
        await self.db.refresh(user)
        
        return user
    
    async def update_user_departments(self, user_id: int, dept_ids: list, dept_names: list):
        """
        更新用户部门信息
        
        Args:
            user_id: 用户ID
            dept_ids: 部门ID列表
            dept_names: 部门名称列表
        """
        result = await self.db.execute(select(User).filter(User.id == user_id))
        user = result.scalar_one_or_none()
        if user:
            user.dept_ids = dept_ids
            user.dept_names = dept_names
            await self.db.commit()
    
    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """根据ID获取用户"""
        result = await self.db.execute(select(User).filter(User.id == user_id))
        return result.scalar_one_or_none()
    
    async def get_user_by_feishu_id(self, feishu_user_id: str) -> Optional[User]:
        """根据飞书ID获取用户"""
        result = await self.db.execute(
            select(User).filter(User.feishu_user_id == feishu_user_id)
        )
        return result.scalar_one_or_none()

