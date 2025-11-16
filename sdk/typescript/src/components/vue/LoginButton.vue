<template>
  <button
    @click="login"
    :disabled="isLoading"
    :class="className"
    :style="buttonStyle"
    @mouseenter="handleMouseEnter"
    @mouseleave="handleMouseLeave"
  >
    {{ isLoading ? '加载中...' : buttonText }}
  </button>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { useSSO } from '../../composables/useSSO';

interface Props {
  authhubUrl: string;
  redirectUri?: string;
  className?: string;
  style?: Record<string, string>;
  buttonText?: string;
  onLoginSuccess?: (user: any) => void;
}

const props = withDefaults(defineProps<Props>(), {
  buttonText: '登录',
});

const { login: ssoLogin, isLoading } = useSSO({
  authhubUrl: props.authhubUrl,
  redirectUri: props.redirectUri,
  onLoginSuccess: props.onLoginSuccess,
});

const isHovered = ref(false);

const buttonStyle = computed(() => ({
  padding: '10px 20px',
  fontSize: '16px',
  backgroundColor: isHovered.value ? '#40a9ff' : '#1890ff',
  color: 'white',
  border: 'none',
  borderRadius: '4px',
  cursor: 'pointer',
  transition: 'background-color 0.3s',
  ...props.style,
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

