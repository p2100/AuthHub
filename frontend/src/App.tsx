import { Routes, Route, Navigate } from 'react-router-dom'
import MainLayout from './components/Layout/MainLayout'
import ProtectedRoute from './components/ProtectedRoute'
import Login from './pages/Login'
import LoginCallback from './pages/Login/Callback'
import Dashboard from './pages/Dashboard'
import SystemList from './pages/Systems/SystemList'
import UserList from './pages/Users/UserList'
import RoleList from './pages/Roles/RoleList'
import PermissionList from './pages/Permissions/PermissionList'

function App() {
  return (
    <Routes>
      {/* 公开路由 */}
      <Route path="/login" element={<Login />} />
      <Route path="/login/callback" element={<LoginCallback />} />
      
      {/* 受保护的管理后台路由 */}
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <MainLayout />
          </ProtectedRoute>
        }
      >
        <Route index element={<Navigate to="/dashboard" replace />} />
        <Route path="dashboard" element={<Dashboard />} />
        <Route path="systems" element={<SystemList />} />
        <Route path="users" element={<UserList />} />
        <Route path="roles" element={<RoleList />} />
        <Route path="permissions" element={<PermissionList />} />
      </Route>
    </Routes>
  )
}

export default App

