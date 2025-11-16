<template>
  <ProtectedView :authhubUrl="AUTHHUB_URL">
    <div :style="containerStyle">
      <div :style="headerStyle">
        <h1 :style="titleStyle">Vue SSO 示例</h1>
        <div :style="userInfoStyle">
          <span :style="usernameStyle">欢迎, {{ user?.username }}</span>
          <button @click="handleLogout" :style="buttonStyle">登出</button>
        </div>
      </div>
      <div :style="contentStyle">
        <div :style="cardStyle">
          <h2 :style="cardTitleStyle">用户信息</h2>
          <div :style="userDetailsStyle">
            <p><strong>用户名:</strong> {{ user?.username }}</p>
            <p><strong>邮箱:</strong> {{ user?.email || '未设置' }}</p>
            <p><strong>用户ID:</strong> {{ user?.sub }}</p>
            <p><strong>全局角色:</strong> {{ user?.global_roles?.join(', ') || '无' }}</p>
          </div>
        </div>
        <div :style="cardStyle">
          <h2 :style="cardTitleStyle">SSO 集成说明</h2>
          <p :style="descriptionStyle">
            这是一个使用 AuthHub SDK 的 Vue 3 SSO 示例应用。
            通过简单的组件和 Composable，即可实现完整的 SSO 登录流程。
          </p>
          <ul :style="listStyle">
            <li>使用 <code>LoginPage</code> 组件实现登录页面</li>
            <li>使用 <code>SSOCallback</code> 组件处理回调</li>
            <li>使用 <code>ProtectedView</code> 保护视图</li>
            <li>使用 <code>useSSO</code> Composable 管理登录状态</li>
          </ul>
        </div>
      </div>
    </div>
  </ProtectedView>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router';
import { ProtectedView } from '@authhub/sdk/components/vue';
import { useSSO } from '@authhub/sdk/composables';
import { AUTHHUB_URL } from '../config';

const router = useRouter();
const { user, logout } = useSSO({ authhubUrl: AUTHHUB_URL });

const handleLogout = () => {
  logout();
  router.push('/login');
};

// Styles
const containerStyle = {
  minHeight: '100vh',
  backgroundColor: '#f5f5f5',
};

const headerStyle = {
  backgroundColor: 'white',
  boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)',
  padding: '16px 24px',
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center',
};

const titleStyle = {
  fontSize: '20px',
  fontWeight: '600',
};

const userInfoStyle = {
  display: 'flex',
  alignItems: 'center',
  gap: '16px',
};

const usernameStyle = {
  color: '#666',
};

const buttonStyle = {
  padding: '8px 16px',
  backgroundColor: '#ff4d4f',
  color: 'white',
  border: 'none',
  borderRadius: '4px',
  cursor: 'pointer',
  fontSize: '14px',
};

const contentStyle = {
  padding: '24px',
  maxWidth: '1200px',
  margin: '0 auto',
};

const cardStyle = {
  backgroundColor: 'white',
  borderRadius: '8px',
  padding: '24px',
  boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)',
  marginBottom: '16px',
};

const cardTitleStyle = {
  fontSize: '18px',
  marginBottom: '16px',
};

const userDetailsStyle = {
  lineHeight: '2',
};

const descriptionStyle = {
  lineHeight: '1.6',
  color: '#666',
};

const listStyle = {
  marginTop: '16px',
  paddingLeft: '24px',
  lineHeight: '2',
  color: '#666',
};
</script>

