import { useState } from 'react'
import { Tabs, Table, Button, Space, Modal, message } from 'antd'
import { PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { apiGet, apiDelete } from '@/utils/api'
import type { Permission, RoutePattern, ResourceBinding } from '@/types/api'
import CreatePermissionModal from './components/CreatePermissionModal'
import CreateRouteModal from './components/CreateRouteModal'
import EditPermissionModal from './components/EditPermissionModal'
import EditRouteModal from './components/EditRouteModal'
import CreateResourceBindingModal from './components/CreateResourceBindingModal'

const PermissionList = () => {
  const queryClient = useQueryClient()
  const [activeTab, setActiveTab] = useState('permissions')
  const [createPermissionModalVisible, setCreatePermissionModalVisible] = useState(false)
  const [createRouteModalVisible, setCreateRouteModalVisible] = useState(false)
  const [editPermissionModalVisible, setEditPermissionModalVisible] = useState(false)
  const [editRouteModalVisible, setEditRouteModalVisible] = useState(false)
  const [createResourceBindingModalVisible, setCreateResourceBindingModalVisible] = useState(false)
  const [selectedPermission, setSelectedPermission] = useState<Permission | null>(null)
  const [selectedRoute, setSelectedRoute] = useState<RoutePattern | null>(null)

  // 获取权限列表
  const { data: permissions, isLoading: permissionsLoading } = useQuery<Permission[]>({
    queryKey: ['permissions'],
    queryFn: () => apiGet<Permission[]>('/rbac/permissions'),
    enabled: activeTab === 'permissions',
  })

  // 获取路由规则列表
  const { data: routes, isLoading: routesLoading } = useQuery<RoutePattern[]>({
    queryKey: ['routes'],
    queryFn: () => apiGet<RoutePattern[]>('/rbac/routes'),
    enabled: activeTab === 'routes',
  })

  // 获取资源绑定列表
  const { data: bindings, isLoading: bindingsLoading } = useQuery<ResourceBinding[]>({
    queryKey: ['resource-bindings'],
    queryFn: () => apiGet<ResourceBinding[]>('/rbac/resource-bindings'),
    enabled: activeTab === 'bindings',
  })

  // 删除权限
  const deletePermissionMutation = useMutation({
    mutationFn: (permissionId: number) => apiDelete(`/rbac/permissions/${permissionId}`),
    onSuccess: () => {
      message.success('权限删除成功')
      queryClient.invalidateQueries({ queryKey: ['permissions'] })
    },
    onError: (error: any) => {
      message.error(`删除失败: ${error.message}`)
    },
  })

  // 删除路由规则
  const deleteRouteMutation = useMutation({
    mutationFn: (routeId: number) => apiDelete(`/rbac/routes/${routeId}`),
    onSuccess: () => {
      message.success('路由规则删除成功')
      queryClient.invalidateQueries({ queryKey: ['routes'] })
    },
    onError: (error: any) => {
      message.error(`删除失败: ${error.message}`)
    },
  })

  // 删除资源绑定
  const deleteBindingMutation = useMutation({
    mutationFn: (bindingId: number) => apiDelete(`/rbac/resource-bindings/${bindingId}`),
    onSuccess: () => {
      message.success('资源绑定删除成功')
      queryClient.invalidateQueries({ queryKey: ['resource-bindings'] })
    },
    onError: (error: any) => {
      message.error(`删除失败: ${error.message}`)
    },
  })

  const handleEditPermission = (permission: Permission) => {
    setSelectedPermission(permission)
    setEditPermissionModalVisible(true)
  }

  const handleEditRoute = (route: RoutePattern) => {
    setSelectedRoute(route)
    setEditRouteModalVisible(true)
  }

  const handleDeletePermission = (permission: Permission) => {
    Modal.confirm({
      title: '确认删除',
      content: `确定要删除权限 "${permission.name}" 吗？`,
      okText: '确认',
      cancelText: '取消',
      okType: 'danger',
      onOk: () => {
        deletePermissionMutation.mutate(permission.id)
      },
    })
  }

  const handleDeleteRoute = (route: RoutePattern) => {
    Modal.confirm({
      title: '确认删除',
      content: `确定要删除该路由规则吗？`,
      okText: '确认',
      cancelText: '取消',
      okType: 'danger',
      onOk: () => {
        deleteRouteMutation.mutate(route.id)
      },
    })
  }

  const handleDeleteBinding = (binding: ResourceBinding) => {
    Modal.confirm({
      title: '确认删除',
      content: `确定要删除该资源绑定吗？`,
      okText: '确认',
      cancelText: '取消',
      okType: 'danger',
      onOk: () => {
        deleteBindingMutation.mutate(binding.id)
      },
    })
  }

  const permissionColumns = [
    {
      title: '权限代码',
      dataIndex: 'code',
      key: 'code',
    },
    {
      title: '权限名称',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: '命名空间',
      dataIndex: 'namespace',
      key: 'namespace',
    },
    {
      title: '资源类型',
      dataIndex: 'resource_type',
      key: 'resource_type',
    },
    {
      title: '操作',
      dataIndex: 'action',
      key: 'action',
    },
    {
      title: '操作',
      key: 'action_buttons',
      render: (_: any, record: Permission) => (
        <Space size="small">
          <Button 
            type="link" 
            size="small" 
            icon={<EditOutlined />}
            onClick={() => handleEditPermission(record)}
          >
            编辑
          </Button>
          <Button
            type="link"
            size="small"
            danger
            icon={<DeleteOutlined />}
            onClick={() => handleDeletePermission(record)}
            loading={deletePermissionMutation.isPending}
          >
            删除
          </Button>
        </Space>
      ),
    },
  ]

  const routeColumns = [
    {
      title: '系统ID',
      dataIndex: 'system_id',
      key: 'system_id',
    },
    {
      title: '角色ID',
      dataIndex: 'role_id',
      key: 'role_id',
    },
    {
      title: '路由正则',
      dataIndex: 'pattern',
      key: 'pattern',
    },
    {
      title: 'HTTP方法',
      dataIndex: 'method',
      key: 'method',
    },
    {
      title: '优先级',
      dataIndex: 'priority',
      key: 'priority',
    },
    {
      title: '操作',
      key: 'action',
      render: (_: any, record: RoutePattern) => (
        <Space size="small">
          <Button 
            type="link" 
            size="small" 
            icon={<EditOutlined />}
            onClick={() => handleEditRoute(record)}
          >
            编辑
          </Button>
          <Button
            type="link"
            size="small"
            danger
            icon={<DeleteOutlined />}
            onClick={() => handleDeleteRoute(record)}
            loading={deleteRouteMutation.isPending}
          >
            删除
          </Button>
        </Space>
      ),
    },
  ]

  const bindingColumns = [
    {
      title: '用户ID',
      dataIndex: 'user_id',
      key: 'user_id',
    },
    {
      title: '命名空间',
      dataIndex: 'namespace',
      key: 'namespace',
    },
    {
      title: '资源类型',
      dataIndex: 'resource_type',
      key: 'resource_type',
    },
    {
      title: '资源ID',
      dataIndex: 'resource_id',
      key: 'resource_id',
    },
    {
      title: '操作',
      dataIndex: 'action',
      key: 'action',
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (time: string) => new Date(time).toLocaleString('zh-CN'),
    },
    {
      title: '操作',
      key: 'action_buttons',
      render: (_: any, record: ResourceBinding) => (
        <Button
          type="link"
          size="small"
          danger
          icon={<DeleteOutlined />}
          onClick={() => handleDeleteBinding(record)}
          loading={deleteBindingMutation.isPending}
        >
          删除
        </Button>
      ),
    },
  ]

  const tabItems = [
    {
      key: 'permissions',
      label: '权限列表',
      children: (
        <div>
          <div style={{ marginBottom: 16 }}>
            <Button 
              type="primary" 
              icon={<PlusOutlined />}
              onClick={() => setCreatePermissionModalVisible(true)}
            >
              创建权限
            </Button>
          </div>
          <Table
            columns={permissionColumns}
            dataSource={permissions || []}
            rowKey="id"
            loading={permissionsLoading}
          />
        </div>
      ),
    },
    {
      key: 'routes',
      label: '路由规则',
      children: (
        <div>
          <div style={{ marginBottom: 16 }}>
            <Button 
              type="primary" 
              icon={<PlusOutlined />}
              onClick={() => setCreateRouteModalVisible(true)}
            >
              创建路由规则
            </Button>
          </div>
          <Table
            columns={routeColumns}
            dataSource={routes || []}
            rowKey="id"
            loading={routesLoading}
          />
        </div>
      ),
    },
    {
      key: 'bindings',
      label: '资源绑定',
      children: (
        <div>
          <div style={{ marginBottom: 16 }}>
            <Button 
              type="primary" 
              icon={<PlusOutlined />}
              onClick={() => setCreateResourceBindingModalVisible(true)}
            >
              创建资源绑定
            </Button>
          </div>
          <Table
            columns={bindingColumns}
            dataSource={bindings || []}
            rowKey="id"
            loading={bindingsLoading}
          />
        </div>
      ),
    },
  ]

  return (
    <div>
      <h1>权限管理</h1>
      <Tabs activeKey={activeTab} onChange={setActiveTab} items={tabItems} style={{ marginTop: 16 }} />

      {/* 创建权限Modal */}
      <CreatePermissionModal
        visible={createPermissionModalVisible}
        onClose={() => setCreatePermissionModalVisible(false)}
        onSuccess={() => {
          queryClient.invalidateQueries({ queryKey: ['permissions'] })
        }}
      />

      {/* 创建路由规则Modal */}
      <CreateRouteModal
        visible={createRouteModalVisible}
        onClose={() => setCreateRouteModalVisible(false)}
        onSuccess={() => {
          queryClient.invalidateQueries({ queryKey: ['routes'] })
        }}
      />

      {/* 编辑权限Modal */}
      <EditPermissionModal
        visible={editPermissionModalVisible}
        permission={selectedPermission}
        onClose={() => {
          setEditPermissionModalVisible(false)
          setSelectedPermission(null)
        }}
        onSuccess={() => {
          queryClient.invalidateQueries({ queryKey: ['permissions'] })
        }}
      />

      {/* 编辑路由规则Modal */}
      <EditRouteModal
        visible={editRouteModalVisible}
        route={selectedRoute}
        onClose={() => {
          setEditRouteModalVisible(false)
          setSelectedRoute(null)
        }}
        onSuccess={() => {
          queryClient.invalidateQueries({ queryKey: ['routes'] })
        }}
      />

      {/* 创建资源绑定Modal */}
      <CreateResourceBindingModal
        visible={createResourceBindingModalVisible}
        onClose={() => setCreateResourceBindingModalVisible(false)}
        onSuccess={() => {
          queryClient.invalidateQueries({ queryKey: ['resource-bindings'] })
        }}
      />
    </div>
  )
}

export default PermissionList
