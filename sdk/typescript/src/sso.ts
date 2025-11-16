/**
 * AuthHub SSO客户端
 */

import axios from 'axios';
import { TokenManager } from './tokenManager';
import { TokenVerifier } from './verifier';

export interface SSOLoginUrlResponse {
  login_url: string;
  state: string;
}

export interface SSOTokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
}

export class SSOClient {
  private authhubUrl: string;
  private baseUrl: string;
  private verifier: TokenVerifier;

  constructor(authhubUrl: string) {
    this.authhubUrl = authhubUrl.replace(/\/$/, '');
    this.baseUrl = `${this.authhubUrl}/api/v1/auth/sso`;
    this.verifier = new TokenVerifier();
  }

  /**
   * 获取SSO登录URL
   */
  async getLoginUrl(redirectUri: string, state?: string): Promise<SSOLoginUrlResponse> {
    try {
      const response = await axios.post<SSOLoginUrlResponse>(`${this.baseUrl}/login-url`, {
        redirect_uri: redirectUri,
        state,
      });
      return response.data;
    } catch (error) {
      throw new Error(`获取登录URL失败: ${error}`);
    }
  }

  /**
   * 用授权码交换JWT Token
   */
  async exchangeToken(code: string, state?: string): Promise<SSOTokenResponse> {
    try {
      const response = await axios.post<SSOTokenResponse>(`${this.baseUrl}/exchange-token`, {
        code,
        state,
      });
      return response.data;
    } catch (error) {
      throw new Error(`Token交换失败: ${error}`);
    }
  }

  /**
   * 处理SSO回调(便捷方法)
   * 
   * 自动交换Token并存储到localStorage
   */
  async handleCallback(code: string, state?: string): Promise<string> {
    const tokenData = await this.exchangeToken(code, state);
    const token = tokenData.access_token;

    // 存储Token
    TokenManager.setToken(token);

    // 解析并存储Token Payload
    try {
      const payload = await this.verifier.verify(token);
      TokenManager.setTokenPayload(payload);
    } catch (error) {
      console.warn('Token验证失败，但仍然存储:', error);
    }

    return token;
  }

  /**
   * 触发登录
   * 
   * 跳转到SSO登录页面
   */
  async login(redirectUri?: string): Promise<void> {
    // 默认使用当前页面URL作为回调地址
    const callbackUri = redirectUri || `${window.location.origin}/auth/callback`;
    
    // 保存当前页面URL，用于登录后返回
    if (typeof window !== 'undefined') {
      sessionStorage.setItem('authhub_return_url', window.location.href);
    }

    // 获取登录URL
    const result = await this.getLoginUrl(callbackUri);

    // 跳转到登录页面
    window.location.href = result.login_url;
  }

  /**
   * 登出
   * 
   * 清除本地Token
   */
  logout(): void {
    TokenManager.clear();
  }

  /**
   * 检查是否已登录
   */
  isAuthenticated(): boolean {
    return TokenManager.hasValidToken();
  }

  /**
   * 获取当前用户信息
   */
  getCurrentUser() {
    return TokenManager.getTokenPayload();
  }
}

