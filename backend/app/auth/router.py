"""认证API路由"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.feishu import feishu_client
from app.core.config import settings
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.logger import logger
from app.core.security import jwt_handler
from app.schemas.auth import PublicKeyResponse, TokenResponse
from app.users.permission_collector import PermissionCollector
from app.users.service import UserService

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
    code: str = Query(..., description="飞书授权码"), db: AsyncSession = Depends(get_db)
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
    logger.info(f"[登录回调] 开始处理飞书登录回调 - code: {code[:10]}***")

    try:
        # 1. 获取用户访问令牌
        logger.info("[登录回调] 步骤1: 获取用户访问令牌")
        user_access_token = await feishu_client.get_user_access_token(code)
        logger.info(
            f"[登录回调] 步骤1完成 - token: {user_access_token[:20] if user_access_token else 'None'}***"
        )

        # 2. 获取用户信息
        logger.info("[登录回调] 步骤2: 获取用户信息")
        user_info = await feishu_client.get_user_info(user_access_token)
        logger.info("[登录回调] 步骤2完成 - 飞书返回的完整用户信息:")
        logger.info(f"  - name: {user_info.get('name')}")
        logger.info(f"  - open_id: {user_info.get('open_id')}")
        logger.info(f"  - user_id: {user_info.get('user_id')}")
        logger.info(f"  - union_id: {user_info.get('union_id')}")
        logger.info(f"  - email: {user_info.get('email')}")
        logger.info(f"  - mobile: {user_info.get('mobile')}")
        logger.info(f"  - 完整数据: {user_info}")

        # 3. 同步用户到数据库
        feishu_id_type = "user_id" if user_info.get("user_id") else "open_id"
        feishu_id_value = user_info.get("user_id") or user_info.get("open_id")
        logger.info(
            f"[登录回调] 步骤3: 同步用户到数据库 - 使用飞书{feishu_id_type}: {feishu_id_value}"
        )
        user_service = UserService(db)
        user = await user_service.sync_user_from_feishu(user_info)
        logger.info(
            f"[登录回调] 步骤3完成 - 数据库用户ID: {user.id}, 用户名: {user.username}, feishu_user_id: {user.feishu_user_id}"
        )

        # 4. 收集用户完整权限
        logger.info(f"[登录回调] 步骤4: 收集用户权限 - user_id: {user.id}")
        permission_collector = PermissionCollector(db)
        user_permissions = await permission_collector.collect(user.id)
        logger.info(
            f"[登录回调] 步骤4完成 - 权限: global_roles={user_permissions.get('global_roles')}, system_roles数量={len(user_permissions.get('system_roles', {}))}"
        )

        # 5. 生成JWT Token
        logger.info("[登录回调] 步骤5: 生成JWT Token")
        token = jwt_handler.create_access_token(
            user_id=user.id,
            username=user.username,
            email=user.email or "",
            global_roles=user_permissions.get("global_roles", []),
            system_roles=user_permissions.get("system_roles", {}),
            global_resources=user_permissions.get("global_resources", {}),
            system_resources=user_permissions.get("system_resources", {}),
            dept_ids=user.dept_ids or [],
            dept_names=user.dept_names or [],
        )
        logger.info(f"[登录回调] 步骤5完成 - token: {token[:50]}***")

        logger.info(f"[登录回调] ✅ 登录成功 - 用户: {user.username} (ID: {user.id})")
        return TokenResponse(access_token=token, token_type="bearer", expires_in=3600)

    except Exception as e:
        logger.error(f"[登录回调] ❌ 登录失败: {str(e)}", exc_info=True)
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
    jti = current_user.get("jti", "")
    if jti:
        # 将Token加入黑名单
        jwt_handler.add_to_blacklist(jti, expire_seconds=3600)

    return {"message": "登出成功"}


@router.get("/public-key", response_model=PublicKeyResponse)
async def get_public_key():
    """
    获取JWT验证公钥

    供业务系统使用,用于本地验证JWT Token

    Returns:
        公钥(PEM格式)
    """
    # 读取公钥
    with open(settings.JWT_PUBLIC_KEY_PATH, "r") as f:
        public_key = f.read()

    return PublicKeyResponse(public_key=public_key, algorithm="RS256")


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
