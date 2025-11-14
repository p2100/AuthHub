/**
 * AuthHub核心客户端
 */

import axios from 'axios';
import { TokenVerifier } from './verifier';
import { PermissionChecker } from './checker';
import type { AuthHubOptions, TokenPayload, PermissionConfig } from './types';

export class AuthHubClient {
  private authhubUrl: string;
  private systemId: string;
  private systemToken: string;
  private namespace: string;
  private enableCache: boolean;
  private syncInterval: number;

  private verifier: TokenVerifier;
  private checker: PermissionChecker;
  private configCache: PermissionConfig | null = null;

  constructor(options: AuthHubOptions) {
    this.authhubUrl = options.authhubUrl.replace(/\/$/, '');
    this.systemId = options.systemId;
    this.systemToken = options.systemToken;
    this.namespace = options.namespace;
    this.enableCache = options.enableCache ?? true;
    this.syncInterval = options.syncInterval ?? 300000; // 5分钟

    // 初始化验证器和检查器
    this.verifier = new TokenVerifier();
    this.checker = new PermissionChecker(this.namespace);

    // 初始化
    this.init();
  }

  private async init() {
    await this.syncPublicKey();
    await this.syncConfig();

    if (this.enableCache) {
      // 定期同步配置
      setInterval(() => {
        this.syncConfig();
      }, this.syncInterval);
    }
  }

  /**
   * 验证Token
   */
  async verifyToken(token: string): Promise<TokenPayload> {
    return this.verifier.verify(token);
  }

  /**
   * 检查权限
   */
  checkPermission(
    tokenPayload: TokenPayload,
    resource: string,
    action: string
  ): boolean {
    if (!this.configCache) {
      console.warn('配置未加载');
      return false;
    }
    return this.checker.checkPermission(tokenPayload, resource, action, this.configCache);
  }

  /**
   * 检查路由权限
   */
  checkRoute(tokenPayload: TokenPayload, path: string, method: string): boolean {
    if (!this.configCache) {
      console.warn('配置未加载');
      return false;
    }
    return this.checker.checkRoute(tokenPayload, path, method, this.configCache);
  }

  /**
   * 便捷方法: 检查全局角色
   */
  hasGlobalRole(tokenPayload: TokenPayload, role: string): boolean {
    return tokenPayload.global_roles.includes(role);
  }

  /**
   * 便捷方法: 检查系统角色
   */
  hasSystemRole(tokenPayload: TokenPayload, role: string): boolean {
    const systemRoles = tokenPayload.system_roles[this.namespace] || [];
    return systemRoles.includes(role);
  }

  /**
   * 便捷方法: 检查资源访问权限
   */
  hasResourceAccess(
    tokenPayload: TokenPayload,
    resourceType: string,
    resourceId: number
  ): boolean {
    return this.checker.checkResourceAccess(tokenPayload, resourceType, resourceId);
  }

  /**
   * 同步公钥
   */
  private async syncPublicKey() {
    try {
      const response = await axios.get(`${this.authhubUrl}/api/v1/auth/public-key`);
      this.verifier.setPublicKey(response.data.public_key);
      console.log('✅ 公钥同步成功');
    } catch (error) {
      console.error('❌ 公钥同步失败:', error);
    }
  }

  /**
   * 同步配置
   */
  private async syncConfig() {
    try {
      const response = await axios.get(
        `${this.authhubUrl}/api/v1/systems/${this.systemId}/config`,
        {
          headers: {
            'X-System-Token': this.systemToken,
          },
        }
      );
      this.configCache = response.data;
      console.log('✅ 配置同步成功:', this.configCache.version);
    } catch (error) {
      console.error('❌ 配置同步失败:', error);
    }
  }
}

