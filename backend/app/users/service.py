"""用户服务"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from sqlalchemy.orm import selectinload
from typing import Dict, Optional, Tuple, List
from datetime import datetime

from app.models.user import User
from app.models.user_role import UserRole


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
    
    async def update_user_departments(self, user_id: str, dept_ids: list, dept_names: list):
        """
        更新用户部门信息
        
        Args:
            user_id: 用户ID (Feishu User ID)
            dept_ids: 部门ID列表
            dept_names: 部门名称列表
        """
        result = await self.db.execute(select(User).filter(User.feishu_user_id == user_id))
        user = result.scalar_one_or_none()
        if user:
            user.dept_ids = dept_ids
            user.dept_names = dept_names
            await self.db.commit()
    
    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """根据ID获取用户"""
        result = await self.db.execute(select(User).filter(User.feishu_user_id == user_id))
        return result.scalar_one_or_none()
    
    async def get_user_by_feishu_id(self, feishu_user_id: str) -> Optional[User]:
        """根据飞书ID获取用户"""
        return await self.get_user_by_id(feishu_user_id)
    
    async def list_users(
        self,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        dept_id: Optional[str] = None,
        status: Optional[str] = None
    ) -> Tuple[List[User], int]:
        """
        获取用户列表
        
        Args:
            skip: 跳过数量
            limit: 限制数量
            search: 搜索关键词（用户名或邮箱）
            dept_id: 部门ID筛选
            status: 状态筛选
            
        Returns:
            (用户列表, 总数)
        """
        # 构建查询
        stmt = select(User)
        count_stmt = select(func.count(User.id))
        
        # 搜索条件
        if search:
            search_filter = or_(
                User.username.ilike(f"%{search}%"),
                User.email.ilike(f"%{search}%"),
                User.feishu_user_id.ilike(f"%{search}%")
            )
            stmt = stmt.where(search_filter)
            count_stmt = count_stmt.where(search_filter)
        
        # 部门筛选
        if dept_id:
            # dept_ids 是 JSON 数组，需要检查是否包含该ID
            stmt = stmt.where(User.dept_ids.contains([dept_id]))
            count_stmt = count_stmt.where(User.dept_ids.contains([dept_id]))
        
        # 状态筛选
        if status:
            stmt = stmt.where(User.status == status)
            count_stmt = count_stmt.where(User.status == status)
        
        # 获取总数
        total_result = await self.db.execute(count_stmt)
        total = total_result.scalar() or 0
        
        # 分页
        stmt = stmt.offset(skip).limit(limit).order_by(User.created_at.desc())
        
        # 执行查询
        result = await self.db.execute(stmt)
        users = result.scalars().all()
        
        return list(users), total
    
    async def update_user_status(self, user_id: str, status: str) -> Optional[User]:
        """
        更新用户状态
        
        Args:
            user_id: 用户ID (Feishu User ID)
            status: 状态 (active/inactive)
            
        Returns:
            更新后的用户对象
        """
        result = await self.db.execute(select(User).filter(User.feishu_user_id == user_id))
        user = result.scalar_one_or_none()
        
        if user:
            user.status = status
            await self.db.commit()
            await self.db.refresh(user)
        
        return user
    
    async def get_user_roles(self, user_id: str) -> List[UserRole]:
        """
        获取用户的角色列表
        
        Args:
            user_id: 用户ID (Feishu User ID)
            
        Returns:
            用户角色列表
        """
        result = await self.db.execute(
            select(UserRole)
            .options(selectinload(UserRole.role))
            .filter(UserRole.user_id == user_id)
            .order_by(UserRole.created_at.desc())
        )
        return list(result.scalars().all())

