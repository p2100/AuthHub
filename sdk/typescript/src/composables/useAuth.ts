/**
 * Vue 认证 Composable (轻量版)
 */

import { ref, computed, onMounted } from 'vue';
import { AuthClient } from '../auth-client';
import type { User } from '../types';

export interface UseAuthOptions {
  backendUrl: string;
  loginPath?: string;
  logoutPath?: string;
  mePath?: string;
  onLogout?: () => void;
}

/**
 * 认证 Composable
 * 
 * @example
 * ```vue
 * <script setup>
 * import { useAuth } from '@authhub/sdk/composables';
 * 
 * const { user, loading, isAuthenticated, login, logout } = useAuth({
 *   backendUrl: 'http://localhost:8001'
 * });
 * </script>
 * 
 * <template>
 *   <div v-if="loading">Loading...</div>
 *   <button v-else-if="!isAuthenticated" @click="login">登录</button>
 *   <div v-else>
 *     <p>欢迎, {{ user?.username }}</p>
 *     <button @click="logout">登出</button>
 *   </div>
 * </template>
 * ```
 */
export function useAuth(options: UseAuthOptions) {
  const client = new AuthClient(options);
  const user = ref<User | null>(null);
  const loading = ref(true);

  const refresh = async () => {
    try {
      const currentUser = await client.getCurrentUser();
      user.value = currentUser;
    } catch (error) {
      console.error('Failed to refresh user:', error);
      user.value = null;
    }
  };

  onMounted(async () => {
    loading.value = true;
    await refresh();
    loading.value = false;
  });

  const login = (returnUrl?: string) => {
    client.login(returnUrl || window.location.pathname);
  };

  const logout = async () => {
    await client.logout();
    user.value = null;
    options.onLogout?.();
  };

  return {
    user: computed(() => user.value),
    loading: computed(() => loading.value),
    isAuthenticated: computed(() => user.value !== null),
    login,
    logout,
    refresh,
  };
}

