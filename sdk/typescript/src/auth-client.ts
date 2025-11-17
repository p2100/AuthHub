/**
 * AuthHub 认证客户端
 * 
 * 提供token刷新、用户信息获取等前端认证功能
 */

import axios from 'axios';
import type { SSOTokenResponse } from './sso';
import type { User, AuthConfig } from './types';

export class AuthClient {
  private backendUrl: string;
  private loginPath: string;
  private logoutPath: string;
  private mePath: string;

  constructor(config: string | AuthConfig) {
    // 兼容旧版 API (只传 URL 字符串)
    if (typeof config === 'string') {
      this.backendUrl = config.replace(/\/$/, '');
      this.loginPath = '/api/v1/auth/login';
      this.logoutPath = '/api/v1/auth/logout';
      this.mePath = '/api/v1/auth/me';
    } else {
      this.backendUrl = config.backendUrl.replace(/\/$/, '');
      this.loginPath = config.loginPath || '/api/v1/auth/login';
      this.logoutPath = config.logoutPath || '/api/v1/auth/logout';
      this.mePath = config.mePath || '/api/v1/auth/me';
    }
  }

  /**
   * 获取当前用户信息
   */
  async getCurrentUser(): Promise<User> {
    const response = await axios.get<User>(`${this.backendUrl}${this.mePath}`, {
      withCredentials: true,
    });
    return response.data;
  }

  /**
   * 跳转到登录页面
   */
  login(returnUrl?: string): void {
    const url = new URL(`${this.backendUrl}${this.loginPath}`);
    if (returnUrl) {
      // 将相对路径转换为完整的前端 URL
      const fullReturnUrl = returnUrl.startsWith('http')
        ? returnUrl
        : (typeof window !== 'undefined' ? window.location.origin + returnUrl : returnUrl);
      // 注意：后端 FastAPI SSO 中间件使用的参数名是 'redirect'
      url.searchParams.set('redirect', fullReturnUrl);
    }
    // 仅在浏览器环境下执行
    if (typeof window !== 'undefined') {
      window.location.href = url.toString();
    }
  }

  /**
   * 登出
   */
  async logout(): Promise<void> {
    await axios.post(
      `${this.backendUrl}${this.logoutPath}`,
      {},
      {
        withCredentials: true,
      }
    );
  }

  /**
   * 刷新访问令牌
   * 
   * @param refreshToken Refresh Token
   * @returns 新的token数据（包含access_token和refresh_token）
   */
  async refreshToken(refreshToken: string): Promise<SSOTokenResponse> {
    try {
      const response = await axios.post<SSOTokenResponse>(
        `${this.backendUrl}/api/v1/auth/refresh`,
        { refresh_token: refreshToken }
      );
      return response.data;
    } catch (error) {
      throw new Error(`Token刷新失败: ${error}`);
    }
  }
}
