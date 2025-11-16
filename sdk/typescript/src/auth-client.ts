/**
 * 轻量级认证客户端
 * 所有 OAuth 逻辑由后端处理
 */

export interface AuthConfig {
  backendUrl: string; // 业务后端地址
  loginPath?: string;
  logoutPath?: string;
  mePath?: string;
}

export interface User {
  sub: string;
  username: string;
  email?: string;
  global_roles?: string[];
  system_roles?: Record<string, string[]>;
  dept_ids?: number[];
  dept_names?: string[];
}

export class AuthClient {
  private config: Required<AuthConfig>;

  constructor(config: AuthConfig) {
    this.config = {
      backendUrl: config.backendUrl.replace(/\/$/, ''),
      loginPath: config.loginPath || '/auth/login',
      logoutPath: config.logoutPath || '/auth/logout',
      mePath: config.mePath || '/api/me',
    };
  }

  /**
   * 触发登录（跳转到后端登录路由）
   */
  login(returnUrl?: string): void {
    const url = new URL(this.config.loginPath, this.config.backendUrl);
    if (returnUrl) {
      url.searchParams.set('return_url', returnUrl);
    }
    window.location.href = url.toString();
  }

  /**
   * 登出
   */
  async logout(): Promise<void> {
    try {
      await fetch(`${this.config.backendUrl}${this.config.logoutPath}`, {
        method: 'POST',
        credentials: 'include', // 重要：带上 Cookie
      });
    } catch (error) {
      console.error('Logout failed:', error);
    }
  }

  /**
   * 获取当前用户信息
   */
  async getCurrentUser(): Promise<User | null> {
    try {
      const response = await fetch(
        `${this.config.backendUrl}${this.config.mePath}`,
        {
          credentials: 'include', // 重要：带上 Cookie
        }
      );

      if (!response.ok) {
        if (response.status === 401) {
          return null; // 未登录
        }
        throw new Error(`Failed to fetch user: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Get current user failed:', error);
      return null;
    }
  }

  /**
   * 检查是否已登录
   */
  async isAuthenticated(): Promise<boolean> {
    const user = await this.getCurrentUser();
    return user !== null;
  }
}

