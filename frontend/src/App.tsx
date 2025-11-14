import { Routes, Route, Navigate } from 'react-router-dom'
import MainLayout from './components/Layout/MainLayout'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import SystemList from './pages/Systems/SystemList'
import UserList from './pages/Users/UserList'
import RoleList from './pages/Roles/RoleList'
import PermissionList from './pages/Permissions/PermissionList'

function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/" element={<MainLayout />}>
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

