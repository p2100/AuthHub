<template>
  <div v-if="isLoading" :style="loadingContainerStyle">
    <div :style="spinnerStyle"></div>
  </div>
  <div v-else-if="!isAuthenticated" :style="unauthorizedContainerStyle">
    <div :style="unauthorizedContentStyle">
      <p :style="unauthorizedTextStyle">需要登录才能访问</p>
      <p :style="unauthorizedSubtextStyle">正在跳转到登录页...</p>
    </div>
  </div>
  <slot v-else></slot>
</template>

<script setup lang="ts">
import { watch, onMounted } from 'vue';
import { useSSO } from '../../composables/useSSO';

interface Props {
  authhubUrl: string;
  redirectUri?: string;
}

const props = defineProps<Props>();

const { isAuthenticated, isLoading, login } = useSSO({
  authhubUrl: props.authhubUrl,
  redirectUri: props.redirectUri,
});

// 未登录时自动触发登录
watch(
  () => [isLoading.value, isAuthenticated.value],
  ([loading, authenticated]) => {
    if (!loading && !authenticated) {
      login();
    }
  }
);

// Styles
const loadingContainerStyle = {
  minHeight: '100vh',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
};

const spinnerStyle = {
  width: '48px',
  height: '48px',
  border: '4px solid #f0f0f0',
  borderTop: '4px solid #1890ff',
  borderRadius: '50%',
  animation: 'spin 1s linear infinite',
};

const unauthorizedContainerStyle = {
  minHeight: '100vh',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
};

const unauthorizedContentStyle = {
  textAlign: 'center' as const,
};

const unauthorizedTextStyle = {
  fontSize: '16px',
  color: '#666',
  marginBottom: '16px',
};

const unauthorizedSubtextStyle = {
  fontSize: '14px',
  color: '#999',
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

