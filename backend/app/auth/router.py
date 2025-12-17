"""认证API路由"""

import secrets
from typing import Optional

from fastapi import APIRouter, Body, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.feishu import feishu_client
from app.core.cache import cache
from app.core.config import settings
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.logger import logger
from app.core.security import jwt_handler
from app.schemas.auth import (
    PublicKeyResponse,
    RefreshTokenRequest,
    SSOExchangeTokenRequest,
    SSOLoginUrlRequest,
    SSOLoginUrlResponse,
    TokenResponse,
)
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
        logger.info(f"[登录回调] 步骤4: 收集用户权限 - feishu_user_id: {user.feishu_user_id}")
        permission_collector = PermissionCollector(db)
        user_permissions = await permission_collector.collect(user.feishu_user_id)
        logger.info(
            f"[登录回调] 步骤4完成 - 权限: global_roles={user_permissions.get('global_roles')}, system_roles数量={len(user_permissions.get('system_roles', {}))}"
        )

        # 5. 生成JWT Token
        logger.info("[登录回调] 步骤5: 生成JWT Token")
        token = jwt_handler.create_access_token(
            feishu_user_id=user.feishu_user_id,
            name=user.name,
            username=user.username,
            avatar=user.avatar,
            email=user.email or "",
            global_roles=user_permissions.get("global_roles", []),
            system_roles=user_permissions.get("system_roles", {}),
            global_resources=user_permissions.get("global_resources", {}),
            system_resources=user_permissions.get("system_resources", {}),
            dept_ids=user.dept_ids or [],
            dept_names=user.dept_names or [],
        )
        logger.info(f"[登录回调] 步骤5完成 - token: {token[:50]}***")

        # 6. 生成 Refresh Token
        logger.info("[登录回调] 步骤6: 生成 Refresh Token")
        refresh_token = jwt_handler.create_refresh_token(user.feishu_user_id)
        logger.info(f"[登录回调] 步骤6完成 - refresh_token: {refresh_token[:30]}***")

        logger.info(f"[登录回调] ✅ 登录成功 - 用户: {user.username} (ID: {user.feishu_user_id})")
        return TokenResponse(
            access_token=token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=3600,
            refresh_expires_in=604800,
        )

    except Exception as e:
        logger.error(f"[登录回调] ❌ 登录失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail=f"登录失败: {str(e)}")


@router.post("/logout")
async def logout(
    current_user: dict = Depends(get_current_user),
    refresh_token: Optional[str] = Body(None, embed=True),
):
    """
    登出 - 将Token加入黑名单并撤销 refresh token

    Args:
        current_user: 当前用户信息
        refresh_token: 可选的 refresh token（用于撤销，从请求body中获取）

    Returns:
        成功消息
    """
    # 撤销 access token（加入黑名单）
    jti = current_user.get("jti", "")
    if jti:
        jwt_handler.add_to_blacklist(jti, expire_seconds=3600)
        logger.info(f"[登出] Access token 已加入黑名单 - jti: {jti}")

    # 撤销 refresh token
    if refresh_token:
        jwt_handler.revoke_refresh_token(refresh_token)
        logger.info(f"[登出] Refresh token 已撤销 - token: {refresh_token[:30]}***")

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


@router.post("/refresh", response_model=TokenResponse)
async def refresh_access_token(request: RefreshTokenRequest, db: AsyncSession = Depends(get_db)):
    """
    刷新访问令牌

    使用 refresh token 获取新的 access token 和 refresh token (rotation)

    Args:
        request: 包含 refresh_token
        db: 数据库会话

    Returns:
        新的 access token 和 refresh token
    """
    logger.info(f"[Token刷新] 开始刷新 - refresh_token: {request.refresh_token[:30]}***")

    # 1. 验证 refresh token
    feishu_user_id = jwt_handler.verify_refresh_token(request.refresh_token)
    if not feishu_user_id:
        logger.error("[Token刷新] ❌ Refresh token 无效或已过期")
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    logger.info(f"[Token刷新] Refresh token 验证通过 - feishu_user_id: {feishu_user_id}")

    # 2. 获取用户信息
    from sqlalchemy import select

    from app.models.user import User

    result = await db.execute(select(User).where(User.feishu_user_id == feishu_user_id))
    user = result.scalar_one_or_none()

    if not user:
        logger.error(f"[Token刷新] ❌ 用户不存在 - feishu_user_id: {feishu_user_id}")
        raise HTTPException(status_code=404, detail="User not found")

    logger.info(f"[Token刷新] 用户信息获取成功 - username: {user.username}")

    # 3. 收集权限
    permission_collector = PermissionCollector(db)
    user_permissions = await permission_collector.collect(user.feishu_user_id)
    logger.info(f"[Token刷新] 权限收集完成")

    # 4. 撤销旧的 refresh token (rotation)
    jwt_handler.revoke_refresh_token(request.refresh_token)
    logger.info("[Token刷新] 旧 refresh token 已撤销")

    # 5. 生成新的 tokens
    access_token = jwt_handler.create_access_token(
        feishu_user_id=user.feishu_user_id,
        name=user.name,
        username=user.username,
        avatar=user.avatar,
        email=user.email or "",
        global_roles=user_permissions.get("global_roles", []),
        system_roles=user_permissions.get("system_roles", {}),
        global_resources=user_permissions.get("global_resources", {}),
        system_resources=user_permissions.get("system_resources", {}),
        dept_ids=user.dept_ids or [],
        dept_names=user.dept_names or [],
    )

    new_refresh_token = jwt_handler.create_refresh_token(user.feishu_user_id)

    logger.info(f"[Token刷新] ✅ Token 刷新成功 - 用户: {user.username} (ID: {user.feishu_user_id})")

    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
        expires_in=3600,
        refresh_expires_in=604800,
    )


# ========== SSO 代理端点 ==========


@router.post("/sso/login-url", response_model=SSOLoginUrlResponse)
async def get_sso_login_url(request: SSOLoginUrlRequest):
    """
    获取 SSO 登录 URL（供 SDK 使用）

    为业务系统提供统一的登录入口，无需直接对接飞书

    Args:
        request: 包含 redirect_uri 和可选的 state

    Returns:
        飞书授权 URL 和 state 参数
    """
    # 生成或使用提供的 state（防 CSRF）
    state = request.state or secrets.token_urlsafe(32)

    # 将 state 存储到 Redis（5分钟有效期）
    state_key = f"sso:state:{state}"
    cache.setex(state_key, 300, request.redirect_uri)  # 存储回调地址

    logger.info(
        f"[SSO] 生成登录 URL - state: {state[:10]}***, redirect_uri: {request.redirect_uri}"
    )

    # 构建飞书授权 URL
    login_url = (
        f"https://open.feishu.cn/open-apis/authen/v1/index"
        f"?app_id={settings.FEISHU_APP_ID}"
        f"&redirect_uri={request.redirect_uri}"
        f"&state={state}"
    )

    return SSOLoginUrlResponse(login_url=login_url, state=state)


@router.post("/sso/exchange-token", response_model=TokenResponse)
async def exchange_sso_token(request: SSOExchangeTokenRequest, db: AsyncSession = Depends(get_db)):
    """
    用 OAuth code 交换 JWT Token（供 SDK 使用）

    验证 state，获取用户信息，生成 JWT Token

    Args:
        request: 包含 code 和 state
        db: 数据库会话

    Returns:
        JWT Token
    """
    logger.info(
        f"[SSO] Token 交换请求 - code: {request.code[:10]}***, state: {request.state[:10] if request.state else 'None'}***"
    )

    # 验证 state（如果提供）
    if request.state:
        state_key = f"sso:state:{request.state}"
        stored_redirect = cache.get(state_key)

        if not stored_redirect:
            logger.error(f"[SSO] State 验证失败 - state: {request.state[:10]}***")
            raise HTTPException(status_code=400, detail="无效的 state 参数或已过期")

        # 删除已使用的 state（一次性）
        cache.delete(state_key)
        logger.info(f"[SSO] State 验证通过 - redirect_uri: {stored_redirect}")

    try:
        # 1. 获取用户访问令牌
        logger.info("[SSO] 步骤1: 获取用户访问令牌")
        user_access_token = await feishu_client.get_user_access_token(request.code)

        # 2. 获取用户信息
        logger.info("[SSO] 步骤2: 获取用户信息")
        user_info = await feishu_client.get_user_info(user_access_token)

        # 3. 同步用户到数据库
        logger.info(f"[SSO] 步骤3: 同步用户 - name: {user_info.get('name')}")
        user_service = UserService(db)
        user = await user_service.sync_user_from_feishu(user_info)

        # 4. 收集用户完整权限
        logger.info(f"[SSO] 步骤4: 收集权限 - feishu_user_id: {user.feishu_user_id}")
        permission_collector = PermissionCollector(db)
        user_permissions = await permission_collector.collect(user.feishu_user_id)

        # 5. 生成 JWT Token
        logger.info("[SSO] 步骤5: 生成 JWT Token")
        token = jwt_handler.create_access_token(
            feishu_user_id=user.feishu_user_id,
            name=user.name,
            username=user.username,
            avatar=user.avatar,
            email=user.email or "",
            global_roles=user_permissions.get("global_roles", []),
            system_roles=user_permissions.get("system_roles", {}),
            global_resources=user_permissions.get("global_resources", {}),
            system_resources=user_permissions.get("system_resources", {}),
            dept_ids=user.dept_ids or [],
            dept_names=user.dept_names or [],
        )

        # 6. 生成 Refresh Token
        logger.info("[SSO] 步骤6: 生成 Refresh Token")
        refresh_token = jwt_handler.create_refresh_token(user.feishu_user_id)
        logger.info(f"[SSO] 步骤6完成 - refresh_token: {refresh_token[:30]}***")

        logger.info(f"[SSO] ✅ Token 交换成功 - 用户: {user.username} (ID: {user.feishu_user_id})")
        return TokenResponse(
            access_token=token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=3600,
            refresh_expires_in=604800,
        )

    except Exception as e:
        logger.error(f"[SSO] ❌ Token 交换失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail=f"Token 交换失败: {str(e)}")
