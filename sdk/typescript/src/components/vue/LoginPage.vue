<template>
  <div :style="containerStyle">
    <div :style="cardStyle">
      <img v-if="logo" :src="logo" alt="Logo" :style="logoStyle" />
      <h1 :style="titleStyle">{{ title }}</h1>
      <p :style="subtitleStyle">{{ subtitle }}</p>
      <button
        @click="login"
        :disabled="isLoading"
        :style="buttonStyle"
        @mouseenter="handleMouseEnter"
        @mouseleave="handleMouseLeave"
      >
        {{ isLoading ? '加载中...' : '使用飞书登录' }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { useSSO } from '../../composables/useSSO';

interface Props {
  authhubUrl: string;
  redirectUri?: string;
  title?: string;
  subtitle?: string;
  logo?: string;
  backgroundColor?: string;
  onLoginSuccess?: (user: any) => void;
}

const props = withDefaults(defineProps<Props>(), {
  title: 'AuthHub',
  subtitle: '统一认证平台',
  backgroundColor: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
});

const { login: ssoLogin, isLoading } = useSSO({
  authhubUrl: props.authhubUrl,
  redirectUri: props.redirectUri,
  onLoginSuccess: props.onLoginSuccess,
});

const isHovered = ref(false);

const containerStyle = computed(() => ({
  minHeight: '100vh',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  background: props.backgroundColor,
  fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
}));

const cardStyle = {
  backgroundColor: 'white',
  borderRadius: '12px',
  boxShadow: '0 4px 20px rgba(0, 0, 0, 0.1)',
  padding: '48px',
  width: '100%',
  maxWidth: '400px',
  textAlign: 'center' as const,
};

const logoStyle = {
  width: '80px',
  height: '80px',
  marginBottom: '24px',
  borderRadius: '50%',
};

const titleStyle = {
  fontSize: '28px',
  fontWeight: 600,
  marginBottom: '8px',
  color: '#333',
};

const subtitleStyle = {
  fontSize: '14px',
  color: '#666',
  marginBottom: '32px',
};

const buttonStyle = computed(() => ({
  width: '100%',
  padding: '14px',
  fontSize: '16px',
  fontWeight: 500,
  backgroundColor: isHovered.value ? '#40a9ff' : '#1890ff',
  color: 'white',
  border: 'none',
  borderRadius: '6px',
  cursor: 'pointer',
  transition: 'all 0.3s',
  transform: isHovered.value ? 'translateY(-2px)' : 'translateY(0)',
  boxShadow: isHovered.value ? '0 4px 12px rgba(24, 144, 255, 0.3)' : 'none',
}));

const login = () => {
  ssoLogin();
};

const handleMouseEnter = () => {
  isHovered.value = true;
};

const handleMouseLeave = () => {
  isHovered.value = false;
};
</script>

