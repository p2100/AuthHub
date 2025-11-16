# Vue SSO Example

这是一个使用 AuthHub SDK 的 Vue 3 SSO 示例应用。

## 功能展示

- ✅ 使用 `LoginPage` 组件的登录页面
- ✅ 使用 `SSOCallback` 组件的回调处理
- ✅ 使用 `ProtectedView` 保护的视图
- ✅ 使用 `useSSO` composable 的状态管理
- ✅ 完整的登录/登出流程

## 快速开始

### 1. 安装依赖

```bash
npm install
# or
pnpm install
```

### 2. 配置

修改 `src/config.ts` 中的配置：

```typescript
export const AUTHHUB_URL = 'http://localhost:8000'; // AuthHub服务地址
```

### 3. 启动开发服务器

```bash
npm run dev
```

访问 http://localhost:5174

## 项目结构

```
src/
  ├── App.vue           # 主应用组件
  ├── config.ts         # 配置文件
  ├── main.ts           # 入口文件
  ├── router.ts         # 路由配置
  └── pages/
      ├── Login.vue     # 登录页面
      ├── Callback.vue  # SSO回调页面
      └── Dashboard.vue # 仪表板(受保护)
```

## 使用说明

### 1. 基础登录页面

```vue
<template>
  <LoginPage
    :authhubUrl="AUTHHUB_URL"
    title="我的应用"
    subtitle="使用飞书账号登录"
  />
</template>

<script setup>
import { LoginPage } from '@authhub/sdk/components/vue';
import { AUTHHUB_URL } from './config';
</script>
```

### 2. SSO回调处理

```vue
<template>
  <SSOCallback
    :authhubUrl="AUTHHUB_URL"
    redirectTo="/dashboard"
    @success="handleSuccess"
  />
</template>

<script setup>
import { SSOCallback } from '@authhub/sdk/components/vue';
import { AUTHHUB_URL } from './config';

const handleSuccess = () => {
  console.log('登录成功');
};
</script>
```

### 3. 保护视图

```vue
<template>
  <ProtectedView :authhubUrl="AUTHHUB_URL">
    <div>这是受保护的内容</div>
  </ProtectedView>
</template>

<script setup>
import { ProtectedView } from '@authhub/sdk/components/vue';
import { AUTHHUB_URL } from './config';
</script>
```

### 4. 使用 Composable

```vue
<template>
  <div v-if="!isAuthenticated">
    <button @click="login">登录</button>
  </div>
  <div v-else>
    <p>欢迎, {{ user?.username }}</p>
    <button @click="logout">登出</button>
  </div>
</template>

<script setup>
import { useSSO } from '@authhub/sdk/composables';

const { isAuthenticated, user, login, logout } = useSSO({
  authhubUrl: 'http://localhost:8000',
});
</script>
```

## 许可证

MIT

