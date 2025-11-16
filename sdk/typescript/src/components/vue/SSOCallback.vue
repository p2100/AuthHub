<template>
  <div v-if="error" :style="containerStyle">
    <div :style="cardStyle">
      <div :style="errorIconStyle">✕</div>
      <h2 :style="errorTitleStyle">登录失败</h2>
      <p :style="errorMessageStyle">{{ error.message }}</p>
      <button @click="goBack" :style="backButtonStyle">返回</button>
    </div>
  </div>
  <div v-else-if="isProcessing" :style="containerStyle">
    <div :style="loadingContainerStyle">
      <div :style="spinnerStyle"></div>
      <p :style="loadingTextStyle">正在登录...</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { SSOClient } from '../../sso';

interface Props {
  authhubUrl: string;
  redirectTo?: string;
  onSuccess?: (token: string) => void;
  onError?: (error: Error) => void;
}

const props = withDefaults(defineProps<Props>(), {
  redirectTo: '/',
});

const error = ref<Error | null>(null);
const isProcessing = ref(true);

onMounted(async () => {
  try {
    // 从URL获取code和state
    const urlParams = new URLSearchParams(window.location.search);
    const code = urlParams.get('code');
    const state = urlParams.get('state');

    if (!code) {
      throw new Error('缺少授权码');
    }

    // 创建SSO客户端
    const ssoClient = new SSOClient(props.authhubUrl);

    // 交换Token
    const token = await ssoClient.handleCallback(code, state || undefined);

    // 回调成功处理
    props.onSuccess?.(token);

    // 获取返回URL
    const returnUrl = sessionStorage.getItem('authhub_return_url') || props.redirectTo;
    sessionStorage.removeItem('authhub_return_url');

    // 延迟跳转
    setTimeout(() => {
      window.location.href = returnUrl;
    }, 500);
  } catch (err) {
    const errorObj = err instanceof Error ? err : new Error('登录失败');
    error.value = errorObj;
    isProcessing.value = false;
    props.onError?.(errorObj);
  }
});

const goBack = () => {
  window.history.back();
};

// Styles
const containerStyle = {
  minHeight: '100vh',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
};

const cardStyle = {
  textAlign: 'center' as const,
  padding: '48px',
  backgroundColor: '#fff',
  borderRadius: '12px',
  boxShadow: '0 4px 20px rgba(0, 0, 0, 0.1)',
  maxWidth: '400px',
};

const errorIconStyle = {
  width: '64px',
  height: '64px',
  margin: '0 auto 24px',
  backgroundColor: '#ff4d4f',
  borderRadius: '50%',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  fontSize: '32px',
  color: 'white',
};

const errorTitleStyle = {
  fontSize: '24px',
  marginBottom: '12px',
  color: '#333',
};

const errorMessageStyle = {
  fontSize: '14px',
  color: '#666',
  marginBottom: '24px',
};

const backButtonStyle = {
  padding: '10px 24px',
  fontSize: '14px',
  backgroundColor: '#1890ff',
  color: 'white',
  border: 'none',
  borderRadius: '4px',
  cursor: 'pointer',
};

const loadingContainerStyle = {
  textAlign: 'center' as const,
};

const spinnerStyle = {
  width: '48px',
  height: '48px',
  margin: '0 auto 24px',
  border: '4px solid #f0f0f0',
  borderTop: '4px solid #1890ff',
  borderRadius: '50%',
  animation: 'spin 1s linear infinite',
};

const loadingTextStyle = {
  fontSize: '16px',
  color: '#666',
};
</script>

<style scoped>
@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}
</style>

