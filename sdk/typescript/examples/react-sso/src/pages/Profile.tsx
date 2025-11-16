import React from 'react';
import { ProtectedRoute } from '@authhub/sdk/components';
import { useSSO } from '@authhub/sdk/hooks';
import { AUTHHUB_URL } from '../config';

function ProfileContent() {
  const { user } = useSSO({ authhubUrl: AUTHHUB_URL });

  return (
    <div style={{ padding: '24px' }}>
      <h1>用户资料</h1>
      <div style={{ marginTop: '24px' }}>
        <p>用户名: {user?.username}</p>
        <p>邮箱: {user?.email}</p>
      </div>
    </div>
  );
}

function Profile() {
  return (
    <ProtectedRoute authhubUrl={AUTHHUB_URL}>
      <ProfileContent />
    </ProtectedRoute>
  );
}

export default Profile;

