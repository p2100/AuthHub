/**
 * Token管理器
 * 
 * 负责Token的存储、读取和过期检查
 */

import type { TokenPayload } from './types';

const TOKEN_KEY = 'authhub_token';
const TOKEN_PAYLOAD_KEY = 'authhub_token_payload';

export class TokenManager {
  /**
   * 保存Token
   */
  static setToken(token: string): void {
    if (typeof window === 'undefined') return;
    localStorage.setItem(TOKEN_KEY, token);
  }

  /**
   * 获取Token
   */
  static getToken(): string | null {
    if (typeof window === 'undefined') return null;
    return localStorage.getItem(TOKEN_KEY);
  }

  /**
   * 删除Token
   */
  static removeToken(): void {
    if (typeof window === 'undefined') return;
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(TOKEN_PAYLOAD_KEY);
  }

  /**
   * 保存Token Payload
   */
  static setTokenPayload(payload: TokenPayload): void {
    if (typeof window === 'undefined') return;
    localStorage.setItem(TOKEN_PAYLOAD_KEY, JSON.stringify(payload));
  }

  /**
   * 获取Token Payload
   */
  static getTokenPayload(): TokenPayload | null {
    if (typeof window === 'undefined') return null;
    const payload = localStorage.getItem(TOKEN_PAYLOAD_KEY);
    if (!payload) return null;
    try {
      return JSON.parse(payload);
    } catch {
      return null;
    }
  }

  /**
   * 检查Token是否过期
   */
  static isTokenExpired(): boolean {
    const payload = this.getTokenPayload();
    if (!payload) return true;
    
    const now = Math.floor(Date.now() / 1000);
    return payload.exp < now;
  }

  /**
   * 检查Token是否存在且有效
   */
  static hasValidToken(): boolean {
    const token = this.getToken();
    if (!token) return false;
    return !this.isTokenExpired();
  }

  /**
   * 清除所有认证数据
   */
  static clear(): void {
    this.removeToken();
  }
}

