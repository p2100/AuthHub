"""认证API路由"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import jwt_handler
from app.core.dependencies import get_current_user
from app.schemas.auth import TokenResponse, PublicKeyResponse
from app.auth.feishu import feishu_client
from app.users.service import UserService
from app.users.permission_collector import PermissionCollector

router = APIRouter(prefix="/auth", tags=["认证"])


@router.get("/feishu/login")
async def feishu_login(redirect_uri: str = Query(..., description="回调URI")):
    """
    飞书登录 - 生成授权URL
    
    Args:
        redirect_uri: 授权后的回调地址
        
    Returns:
        授权URL
    """
    from app.core.config import settings
    
    auth_url = (
        f"https://open.feishu.cn/open-apis/authen/v1/index"
        f"?app_id={settings.FEISHU_APP_ID}"
        f"&redirect_uri={redirect_uri}"
    )
    
    return {"auth_url": auth_url}


@router.get("/feishu/callback", response_model=TokenResponse)
async def feishu_callback(
    code: str = Query(..., description="飞书授权码"),
    db: Session = Depends(get_db)
):
    """
    飞书登录回调
    
    1. 换取access_token
    2. 获取用户信息
    3. 创建/更新本地用户
    4. 收集用户完整权限
    5. 生成JWT Token
    
    Args:
        code: 飞书授权码
        db: 数据库会话
        
    Returns:
        JWT Token
    """
    try:
        # 1. 获取用户访问令牌
        user_access_token = await feishu_client.get_user_access_token(code)
        
        # 2. 获取用户信息
        user_info = await feishu_client.get_user_info(user_access_token)
        
        # 3. 同步用户到数据库
        user_service = UserService(db)
        user = user_service.sync_user_from_feishu(user_info)
        
        # 4. 收集用户完整权限
        permission_collector = PermissionCollector(db)
        user_permissions = permission_collector.collect(user.id)
        
        # 5. 生成JWT Token
        token = jwt_handler.generate_token(
            user_id=str(user.id),
            permissions=user_permissions,
            user_type="user",
            username=user.username,
            email=user.email or "",
            dept_ids=user.dept_ids or [],
            dept_names=user.dept_names or []
        )
        
        return TokenResponse(
            access_token=token,
            token_type="bearer",
            expires_in=3600
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"登录失败: {str(e)}")


@router.post("/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    """
    登出 - 将Token加入黑名单
    
    Args:
        current_user: 当前用户信息
        
    Returns:
        成功消息
    """
    jti = current_user.get('jti', '')
    if jti:
        # 将Token加入黑名单
        jwt_handler.revoke_token(jti, ttl=3600)
    
    return {"message": "登出成功"}


@router.get("/public-key", response_model=PublicKeyResponse)
async def get_public_key():
    """
    获取JWT验证公钥
    
    供业务系统使用,用于本地验证JWT Token
    
    Returns:
        公钥(PEM格式)
    """
    public_key = jwt_handler.get_public_key()
    
    return PublicKeyResponse(
        public_key=public_key,
        algorithm="RS256"
    )


@router.get("/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """
    获取当前用户信息
    
    Args:
        current_user: 当前用户信息
        
    Returns:
        用户信息
    """
    return current_user

