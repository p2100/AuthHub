"""FastAPI SSO中间件"""

from typing import Callable, List, Optional

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse, RedirectResponse
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware

from authhub_sdk.client import AuthHubClient
from authhub_sdk.sso import SSOClient


def register_sso_routes(
    app: FastAPI,
    client: AuthHubClient,
    callback_path: str = "/auth/callback",
    login_path: str = "/auth/login",
    logout_path: str = "/auth/logout",
    cookie_name: str = "authhub_token",
    cookie_secure: bool = True,
    cookie_httponly: bool = True,
    cookie_samesite: str = "lax",
    cookie_max_age: int = 3600,
    after_login_redirect: str = "/",
):
    """
    注册SSO相关路由到FastAPI应用

    必须在添加中间件之前调用
    """
    sso_client = SSOClient(client.authhub_url)

    @app.get(login_path)
    async def login(request: Request, redirect: Optional[str] = None):
        """
        触发SSO登录

        Args:
            redirect: 登录成功后的重定向地址
        """
        # 构建回调URI
        callback_uri = str(request.base_url).rstrip("/") + callback_path

        # 保存原始重定向地址到query参数
        if redirect:
            callback_uri += f"?redirect={redirect}"

        # 获取登录URL
        try:
            result = sso_client.get_login_url(callback_uri)
            return RedirectResponse(url=result["login_url"])
        except Exception as e:
            return JSONResponse(status_code=500, content={"error": f"获取登录URL失败: {str(e)}"})

    @app.get(callback_path)
    async def callback(
        request: Request, code: str, state: Optional[str] = None, redirect: Optional[str] = None
    ):
        """
        SSO回调处理

        Args:
            code: 授权码
            state: 状态参数
            redirect: 登录成功后的重定向地址
        """
        try:
            # 交换Token（现在返回包含access_token和refresh_token的字典）
            token_data = sso_client.handle_callback(code, state)
            access_token = token_data["access_token"]
            refresh_token = token_data["refresh_token"]

            # 确定重定向地址
            redirect_url = redirect or after_login_redirect

            # 创建响应并设置Cookie
            response = RedirectResponse(url=redirect_url)

            # 设置 access token cookie（延长到 7 天，确保刷新逻辑能触发）
            # JWT 本身仍然 1 小时过期，Cookie 过期时间只是浏览器存储时间
            response.set_cookie(
                key=cookie_name,
                value=access_token,
                max_age=7 * 24 * 3600,  # 7天（与 refresh_token 相同）
                httponly=cookie_httponly,
                secure=cookie_secure,
                samesite=cookie_samesite,
            )

            # 设置 refresh token cookie（7天过期）
            response.set_cookie(
                key=f"{cookie_name}_refresh",
                value=refresh_token,
                max_age=7 * 24 * 3600,  # 7天
                httponly=True,  # 强制 httponly
                secure=cookie_secure,
                samesite=cookie_samesite,
            )

            return response
        except Exception as e:
            return JSONResponse(status_code=400, content={"error": f"登录失败: {str(e)}"})

    @app.post(logout_path)
    @app.get(logout_path)
    async def logout(request: Request):
        """登出"""
        response = JSONResponse(content={"message": "登出成功"})
        response.delete_cookie(key=cookie_name)
        return response


class AuthHubSSOMiddleware(BaseHTTPMiddleware):
    """
    FastAPI SSO中间件

    处理登录状态检查和Cookie验证

    注意: 必须先调用 register_sso_routes() 注册路由，再添加此中间件
    """

    def __init__(
        self,
        app: FastAPI,
        client: AuthHubClient,
        callback_path: str = "/auth/callback",
        login_path: str = "/auth/login",
        logout_path: str = "/auth/logout",
        cookie_name: str = "authhub_token",
        cookie_secure: bool = True,
        cookie_samesite: str = "lax",
        public_routes: Optional[List[str]] = None,
        login_required: bool = True,
        redirect_to_login: bool = True,
    ):
        """
        初始化SSO中间件

        Args:
            app: FastAPI应用实例
            client: AuthHub客户端
            callback_path: SSO回调路径
            login_path: 登录路径
            logout_path: 登出路径
            cookie_name: Cookie名称
            cookie_secure: Cookie secure标志
            cookie_samesite: Cookie SameSite策略
            public_routes: 公开路由列表(不需要登录)
            login_required: 是否要求登录
            redirect_to_login: 未登录时是否重定向到登录页
        """
        super().__init__(app)
        self.client = client

        # 路径配置
        self.callback_path = callback_path
        self.login_path = login_path
        self.logout_path = logout_path

        # Cookie配置
        self.cookie_name = cookie_name
        self.cookie_secure = cookie_secure
        self.cookie_samesite = cookie_samesite

        # 认证配置
        self.public_routes = public_routes or []
        self.login_required = login_required
        self.redirect_to_login = redirect_to_login

    async def _try_refresh_token(self, request: Request, call_next: Callable) -> Optional[Response]:
        """
        尝试使用 refresh token 刷新 access token

        Args:
            request: FastAPI 请求对象
            call_next: 下一个中间件/路由处理器

        Returns:
            Response: 如果刷新成功，返回带有新 Cookie 的响应
            None: 如果刷新失败或 refresh token 不存在
        """
        refresh_token = request.cookies.get(f"{self.cookie_name}_refresh")
        if not refresh_token:
            logger.debug(f"[Token刷新] refresh_token 不存在 - Path: {request.url.path}")
            return None

        logger.info(
            f"[Token刷新] 开始尝试刷新 - Path: {request.url.path}, refresh_token: {refresh_token[:20]}***"
        )

        try:
            # 尝试刷新token
            new_tokens = self.client.refresh_token(refresh_token)
            new_access_token = new_tokens["access_token"]
            new_refresh_token = new_tokens["refresh_token"]

            logger.info("[Token刷新] ✅ 刷新成功 - 获取到新的 tokens")

            # 验证新token并注入用户信息
            user_info = self.client.verify_token(new_access_token)
            request.state.user = user_info

            logger.info(
                f"[Token刷新] ✅ 用户信息已注入 - username: {user_info.get('username')}, user_id: {user_info.get('sub')}"
            )

            # 继续处理请求
            response = await call_next(request)

            # 在响应中更新cookies（access_token 和 refresh_token 都是 7 天）
            response.set_cookie(
                key=self.cookie_name,
                value=new_access_token,
                max_age=7 * 24 * 3600,  # 7天
                httponly=True,
                secure=self.cookie_secure,
                samesite=self.cookie_samesite,
            )
            response.set_cookie(
                key=f"{self.cookie_name}_refresh",
                value=new_refresh_token,
                max_age=7 * 24 * 3600,  # 7天
                httponly=True,
                secure=self.cookie_secure,
                samesite=self.cookie_samesite,
            )

            logger.info("[Token刷新] ✅ Cookie 已更新并返回响应")
            return response
        except Exception as e:
            # 刷新失败（refresh token 无效或过期）
            logger.error(f"[Token刷新] ❌ 刷新失败 - Error: {str(e)}")
            return None

    async def dispatch(self, request: Request, call_next: Callable):
        """
        中间件处理逻辑

        1. 检查是否为公开路由
        2. 从Cookie获取Token
        3. 如果 access_token 不存在，尝试使用 refresh_token 刷新
        4. 验证Token
        5. 如果 access_token 无效，尝试使用 refresh_token 刷新
        6. 注入用户信息到request.state
        """
        # 检查是否为公开路由或SSO路由
        path = request.url.path
        if (
            path in self.public_routes
            or path == self.callback_path
            or path == self.login_path
            or path == self.logout_path
        ):
            logger.debug(f"[SSO中间件] 公开路由或SSO路由，直接放行 - Path: {path}")
            return await call_next(request)

        # 从Cookie获取Token
        token = request.cookies.get(self.cookie_name)

        logger.debug(f"[SSO中间件] 处理受保护路由 - Path: {path}, access_token存在: {bool(token)}")

        # 情况1: access_token 不存在（Cookie 过期或被删除）
        if not token:
            logger.warning(f"[SSO中间件] access_token 不存在 - Path: {path}")

            # 尝试使用 refresh_token 刷新
            response = await self._try_refresh_token(request, call_next)
            if response:
                logger.info(f"[SSO中间件] ✅ 通过 refresh_token 恢复会话成功 - Path: {path}")
                return response

            # refresh_token 也不存在或无效，重定向到登录
            logger.warning(f"[SSO中间件] refresh_token 也无效，需要重新登录 - Path: {path}")

            if self.login_required:
                if self.redirect_to_login:
                    # 重定向到登录页，并保存原始URL
                    logger.info(f"[SSO中间件] 重定向到登录页 - Path: {path}")
                    return RedirectResponse(url=f"{self.login_path}?redirect={path}")
                else:
                    return JSONResponse(status_code=401, content={"error": "未登录"})
            else:
                # 不要求登录，继续处理请求
                logger.debug(f"[SSO中间件] 不要求登录，继续处理 - Path: {path}")
                return await call_next(request)

        # 情况2: access_token 存在，验证其有效性
        try:
            logger.debug(f"[SSO中间件] 验证 access_token - Path: {path}, token: {token[:20]}***")
            user_info = self.client.verify_token(token)
            request.state.user = user_info
            logger.info(
                f"[SSO中间件] ✅ Token 验证成功 - Path: {path}, username: {user_info.get('username')}"
            )
        except Exception as e:
            # Token无效（JWT 过期、签名错误等），尝试使用 refresh_token 刷新
            logger.warning(f"[SSO中间件] access_token 验证失败 - Path: {path}, Error: {str(e)}")

            response = await self._try_refresh_token(request, call_next)
            if response:
                logger.info(f"[SSO中间件] ✅ Token 刷新成功，会话恢复 - Path: {path}")
                return response

            # refresh_token 也无效，清除 Cookie 并重定向到登录
            logger.error(f"[SSO中间件] ❌ Token 刷新失败，需要重新登录 - Path: {path}")

            if self.login_required:
                response = RedirectResponse(url=f"{self.login_path}?redirect={path}")
                response.delete_cookie(key=self.cookie_name)
                response.delete_cookie(key=f"{self.cookie_name}_refresh")
                logger.info(f"[SSO中间件] 已清除 Cookie 并重定向到登录页 - Path: {path}")
                return response
            else:
                request.state.user = None

        return await call_next(request)


def setup_sso(
    app: FastAPI,
    client: AuthHubClient,
    callback_path: str = "/auth/callback",
    login_path: str = "/auth/login",
    logout_path: str = "/auth/logout",
    cookie_name: str = "authhub_token",
    cookie_secure: bool = True,
    cookie_httponly: bool = True,
    cookie_samesite: str = "lax",
    cookie_max_age: int = 3600,
    public_routes: Optional[List[str]] = None,
    login_required: bool = True,
    redirect_to_login: bool = True,
    after_login_redirect: str = "/",
):
    """
    便捷方法: 一次性设置SSO路由和中间件

    Args:
        app: FastAPI应用
        client: AuthHub客户端
        callback_path: SSO回调路径
        login_path: 登录路径
        logout_path: 登出路径
        cookie_name: Cookie名称
        cookie_secure: 是否只在HTTPS下发送
        cookie_httponly: 是否禁止JS访问
        cookie_samesite: SameSite策略
        cookie_max_age: Cookie过期时间(秒)
        public_routes: 公开路由列表(不需要登录)
        login_required: 是否要求登录
        redirect_to_login: 未登录时是否重定向到登录页
        after_login_redirect: 登录成功后重定向路径
    """
    # 先注册路由
    register_sso_routes(
        app,
        client,
        callback_path=callback_path,
        login_path=login_path,
        logout_path=logout_path,
        cookie_name=cookie_name,
        cookie_secure=cookie_secure,
        cookie_httponly=cookie_httponly,
        cookie_samesite=cookie_samesite,
        cookie_max_age=cookie_max_age,
        after_login_redirect=after_login_redirect,
    )

    # 再添加中间件
    app.add_middleware(
        AuthHubSSOMiddleware,
        client=client,
        callback_path=callback_path,
        login_path=login_path,
        logout_path=logout_path,
        cookie_name=cookie_name,
        cookie_secure=cookie_secure,
        cookie_samesite=cookie_samesite,
        public_routes=public_routes,
        login_required=login_required,
        redirect_to_login=redirect_to_login,
    )
