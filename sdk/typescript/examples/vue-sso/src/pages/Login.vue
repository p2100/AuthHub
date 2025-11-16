<template>
  <LoginPage
    :authhubUrl="AUTHHUB_URL"
    title="Vue SSO 示例"
    subtitle="使用飞书账号登录"
    :onLoginSuccess="handleLoginSuccess"
  />
</template>

<script setup lang="ts">
import { LoginPage } from '@authhub/sdk/components/vue';
import { AUTHHUB_URL } from '../config';

const handleLoginSuccess = (user: any) => {
  console.log('登录成功:', user);
};
</script>

