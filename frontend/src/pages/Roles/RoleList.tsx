import { useState } from 'react'
import { Table, Button, Space, Select, Modal, message } from 'antd'
import { PlusOutlined, EditOutlined, DeleteOutlined, SettingOutlined, TeamOutlined } from '@ant-design/icons'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { apiGet, apiDelete } from '@/utils/api'
import type { Role, System } from '@/types/api'
import CreateRoleModal from './components/CreateRoleModal'
import EditRoleModal from './components/EditRoleModal'
import ConfigureRolePermissionsModal from './components/ConfigureRolePermissionsModal'
import RoleUsersDrawer from './components/RoleUsersDrawer'

const RoleList = () => {
  const queryClient = useQueryClient()
  const [createModalVisible, setCreateModalVisible] = useState(false)
  const [editModalVisible, setEditModalVisible] = useState(false)
  const [configPermissionsModalVisible, setConfigPermissionsModalVisible] = useState(false)
  const [usersDrawerVisible, setUsersDrawerVisible] = useState(false)
  const [selectedRole, setSelectedRole] = useState<Role | null>(null)
  const [namespaceFilter, setNamespaceFilter] = useState<string | undefined>(undefined)
  const [systemFilter, setSystemFilter] = useState<number | undefined>(undefined)

  // 获取系统列表用于筛选
  const { data: systems } = useQuery<System[]>({
    queryKey: ['systems'],
    queryFn: () => apiGet<System[]>('/systems'),
  })

  // 获取角色列表
  const { data: roles, isLoading } = useQuery<Role[]>({
    queryKey: ['roles', namespaceFilter, systemFilter],
    queryFn: () => {
      const params = new URLSearchParams()
      if (namespaceFilter) params.append('namespace', namespaceFilter)
      if (systemFilter) params.append('system_id', String(systemFilter))
      return apiGet<Role[]>(`/rbac/roles${params.toString() ? '?' + params.toString() : ''}`)
    },
  })

  // 删除角色
  const deleteMutation = useMutation({
    mutationFn: (roleId: number) => apiDelete(`/rbac/roles/${roleId}`),
    onSuccess: () => {
      message.success('角色删除成功')
      queryClient.invalidateQueries({ queryKey: ['roles'] })
    },
    onError: (error: any) => {
      message.error(`删除失败: ${error.message}`)
    },
  })

  const handleDelete = (role: Role) => {
    Modal.confirm({
      title: '确认删除',
      content: `确定要删除角色 "${role.name}" 吗？删除后，所有分配给用户的此角色也会被移除。`,
      okText: '确认',
      cancelText: '取消',
      okType: 'danger',
      onOk: () => {
        deleteMutation.mutate(role.id)
      },
    })
  }

  const handleEdit = (role: Role) => {
    setSelectedRole(role)
    setEditModalVisible(true)
  }

  const handleConfigPermissions = (role: Role) => {
    setSelectedRole(role)
    setConfigPermissionsModalVisible(true)
  }

  const handleViewUsers = (role: Role) => {
    setSelectedRole(role)
    setUsersDrawerVisible(true)
  }

  const columns = [
    {
      title: '角色代码',
      dataIndex: 'code',
      key: 'code',
    },
    {
      title: '角色名称',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: '命名空间',
      dataIndex: 'namespace',
      key: 'namespace',
    },
    {
      title: '描述',
      dataIndex: 'description',
      key: 'description',
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (time: string) => new Date(time).toLocaleString('zh-CN'),
    },
    {
      title: '操作',
      key: 'action',
      render: (_: any, record: Role) => (
        <Space size="small">
          <Button
            type="link"
            size="small"
            icon={<SettingOutlined />}
            onClick={() => handleConfigPermissions(record)}
          >
            配置权限
          </Button>
          <Button
            type="link"
            size="small"
            icon={<TeamOutlined />}
            onClick={() => handleViewUsers(record)}
          >
            查看用户
          </Button>
          <Button
            type="link"
            size="small"
            icon={<EditOutlined />}
            onClick={() => handleEdit(record)}
          >
            编辑
          </Button>
          <Button
            type="link"
            size="small"
            danger
            icon={<DeleteOutlined />}
            onClick={() => handleDelete(record)}
            loading={deleteMutation.isPending}
          >
            删除
          </Button>
        </Space>
      ),
    },
  ]

  return (
    <div>
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1 style={{ display: 'inline-block', marginRight: 16 }}>角色管理</h1>
          <Select
            placeholder="筛选命名空间"
            allowClear
            style={{ width: 200, marginRight: 8 }}
            value={namespaceFilter}
            onChange={setNamespaceFilter}
            options={[
              { value: 'global', label: '全局角色' },
              ...(systems?.map((s) => ({ value: s.code, label: s.name })) || []),
            ]}
          />
          <Select
            placeholder="筛选系统"
            allowClear
            style={{ width: 200 }}
            value={systemFilter}
            onChange={setSystemFilter}
            options={systems?.map((s) => ({ value: s.id, label: s.name }))}
          />
        </div>
        <Button
          type="primary"
          icon={<PlusOutlined />}
          onClick={() => setCreateModalVisible(true)}
        >
          创建角色
        </Button>
      </div>

      <Table
        columns={columns}
        dataSource={roles || []}
        rowKey="id"
        loading={isLoading}
      />

      {/* 创建角色Modal */}
      <CreateRoleModal
        visible={createModalVisible}
        onClose={() => setCreateModalVisible(false)}
        onSuccess={() => {
          queryClient.invalidateQueries({ queryKey: ['roles'] })
        }}
      />

      {/* 编辑角色Modal */}
      {selectedRole && (
        <EditRoleModal
          visible={editModalVisible}
          role={selectedRole}
          onClose={() => {
            setEditModalVisible(false)
            setSelectedRole(null)
          }}
          onSuccess={() => {
            queryClient.invalidateQueries({ queryKey: ['roles'] })
          }}
        />
      )}

      {/* 配置权限Modal */}
      {selectedRole && (
        <ConfigureRolePermissionsModal
          visible={configPermissionsModalVisible}
          role={selectedRole}
          onClose={() => {
            setConfigPermissionsModalVisible(false)
            setSelectedRole(null)
          }}
          onSuccess={() => {
            queryClient.invalidateQueries({ queryKey: ['roles'] })
          }}
        />
      )}

      {/* 查看用户Drawer */}
      {selectedRole && (
        <RoleUsersDrawer
          visible={usersDrawerVisible}
          role={selectedRole}
          onClose={() => {
            setUsersDrawerVisible(false)
            setSelectedRole(null)
          }}
        />
      )}
    </div>
  )
}

export default RoleList
