import React from 'react';
import { LoginPage } from '@authhub/sdk/components';
import { AUTHHUB_URL } from '../config';

function Login() {
  return (
    <LoginPage
      authhubUrl={AUTHHUB_URL}
      title="React SSO 示例"
      subtitle="使用飞书账号登录"
      onLoginSuccess={(user) => {
        console.log('登录成功:', user);
      }}
    />
  );
}

export default Login;

