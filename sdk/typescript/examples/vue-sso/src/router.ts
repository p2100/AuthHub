import { createRouter, createWebHistory } from 'vue-router';
import Login from './pages/Login.vue';
import Callback from './pages/Callback.vue';
import Dashboard from './pages/Dashboard.vue';

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      redirect: '/dashboard',
    },
    {
      path: '/login',
      component: Login,
    },
    {
      path: '/auth/callback',
      component: Callback,
    },
    {
      path: '/dashboard',
      component: Dashboard,
    },
  ],
});

export default router;

