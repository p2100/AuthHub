<template>
  <SSOCallback
    :authhubUrl="AUTHHUB_URL"
    redirectTo="/dashboard"
    :onSuccess="handleSuccess"
    :onError="handleError"
  />
</template>

<script setup lang="ts">
import { SSOCallback } from '@authhub/sdk/components/vue';
import { AUTHHUB_URL } from '../config';

const handleSuccess = (token: string) => {
  console.log('Token交换成功:', token);
};

const handleError = (error: Error) => {
  console.error('登录失败:', error);
};
</script>

