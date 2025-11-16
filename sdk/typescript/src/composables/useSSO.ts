/**
 * Vue SSO Composable
 * 
 * Vue 3 Composition API for SSO
 */

import { ref, computed, onMounted, onUnmounted } from 'vue';
import { SSOClient } from '../sso';
import { TokenManager } from '../tokenManager';
import type { TokenPayload } from '../types';

export interface UseSSOOptions {
  authhubUrl: string;
  redirectUri?: string;
  onLoginSuccess?: (user: TokenPayload) => void;
  onLogout?: () => void;
}

/**
 * Vue SSO Composable
 * 
 * @example
 * ```vue
 * <script setup>
 * import { useSSO } from '@authhub/sdk/composables';
 * 
 * const { isAuthenticated, user, login, logout } = useSSO({
 *   authhubUrl: 'http://localhost:8000'
 * });
 * </script>
 * 
 * <template>
 *   <div v-if="!isAuthenticated">
 *     <button @click="login">登录</button>
 *   </div>
 *   <div v-else>
 *     <p>欢迎, {{ user?.username }}</p>
 *     <button @click="logout">登出</button>
 *   </div>
 * </template>
 * ```
 */
export function useSSO(options: UseSSOOptions) {
  const { authhubUrl, redirectUri, onLoginSuccess, onLogout } = options;

  const ssoClient = new SSOClient(authhubUrl);
  const isAuthenticated = ref(false);
  const user = ref<TokenPayload | null>(null);
  const isLoading = ref(true);

  /**
   * 刷新认证状态
   */
  const refresh = () => {
    const authenticated = ssoClient.isAuthenticated();
    isAuthenticated.value = authenticated;

    if (authenticated) {
      const currentUser = ssoClient.getCurrentUser();
      user.value = currentUser;
    } else {
      user.value = null;
    }
  };

  /**
   * 初始化认证状态
   */
  onMounted(() => {
    isLoading.value = true;
    refresh();
    isLoading.value = false;
  });

  /**
   * 监听storage事件(支持多标签页同步)
   */
  const handleStorageChange = (e: StorageEvent) => {
    if (e.key === 'authhub_token' || e.key === 'authhub_token_payload') {
      refresh();
    }
  };

  onMounted(() => {
    window.addEventListener('storage', handleStorageChange);
  });

  onUnmounted(() => {
    window.removeEventListener('storage', handleStorageChange);
  });

  /**
   * 登录
   */
  const login = async () => {
    try {
      await ssoClient.login(redirectUri);
    } catch (error) {
      console.error('登录失败:', error);
      throw error;
    }
  };

  /**
   * 登出
   */
  const logout = () => {
    ssoClient.logout();
    isAuthenticated.value = false;
    user.value = null;
    onLogout?.();
  };

  return {
    isAuthenticated: computed(() => isAuthenticated.value),
    user: computed(() => user.value),
    isLoading: computed(() => isLoading.value),
    login,
    logout,
    refresh,
  };
}

