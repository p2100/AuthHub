/**
 * AuthHub 认证客户端
 * 
 * 提供token刷新等认证相关功能
 */

import axios from 'axios';
import type { SSOTokenResponse } from './sso';

export class AuthClient {
  private authhubUrl: string;

  constructor(authhubUrl: string) {
    this.authhubUrl = authhubUrl.replace(/\/$/, '');
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
        `${this.authhubUrl}/api/v1/auth/refresh`,
        { refresh_token: refreshToken }
      );
      return response.data;
    } catch (error) {
      throw new Error(`Token刷新失败: ${error}`);
    }
  }
}
