import React from 'react';
import { SSOCallback } from '@authhub/sdk/components';
import { AUTHHUB_URL } from '../config';

function Callback() {
  return (
    <SSOCallback
      authhubUrl={AUTHHUB_URL}
      redirectTo="/dashboard"
      onSuccess={(token) => {
        console.log('Token交换成功:', token);
      }}
      onError={(error) => {
        console.error('登录失败:', error);
      }}
    />
  );
}

export default Callback;

