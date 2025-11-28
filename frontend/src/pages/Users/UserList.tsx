import { useState } from 'react'
import { Table, Tag, Input, Select, Button, Space, Switch, message, Spin } from 'antd'
import { SearchOutlined, UserOutlined } from '@ant-design/icons'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { apiGet, apiPut } from '@/utils/api'
import type { User, UserListResponse } from '@/types/api'
import UserPermissionModal from './components/UserPermissionModal'
import AssignRoleModal from './components/AssignRoleModal'

const { Search } = Input

const UserList = () => {
  const queryClient = useQueryClient()
  const [search, setSearch] = useState('')
  const [status, setStatus] = useState<string | undefined>(undefined)
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(20)
  const [selectedUser, setSelectedUser] = useState<User | null>(null)
  const [permissionModalVisible, setPermissionModalVisible] = useState(false)
  const [assignRoleModalVisible, setAssignRoleModalVisible] = useState(false)

  // 获取用户列表
  const { data, isLoading, error } = useQuery<UserListResponse>({
    queryKey: ['users', page, pageSize, search, status],
    queryFn: () => {
      const params = new URLSearchParams()
      params.append('skip', String((page - 1) * pageSize))
      params.append('limit', String(pageSize))
      if (search) params.append('search', search)
      if (status) params.append('status', status)
      return apiGet<UserListResponse>(`/users?${params.toString()}`)
    },
  })

  // 更新用户状态
  const updateStatusMutation = useMutation({
    mutationFn: ({ userId, status }: { userId: string; status: 'active' | 'inactive' }) =>
      apiPut<User>(`/users/${userId}/status`, { status }),
    onSuccess: () => {
      message.success('用户状态更新成功')
      queryClient.invalidateQueries({ queryKey: ['users'] })
    },
    onError: (error: any) => {
      message.error(`更新失败: ${error.message}`)
    },
  })

  const handleStatusChange = (userId: string, checked: boolean) => {
    updateStatusMutation.mutate({
      userId,
      status: checked ? 'active' : 'inactive',
    })
  }

  const handleViewPermissions = (user: User) => {
    setSelectedUser(user)
    setPermissionModalVisible(true)
  }

  const handleAssignRole = (user: User) => {
    setSelectedUser(user)
    setAssignRoleModalVisible(true)
  }

  const columns = [
    {
      title: '用户名',
      dataIndex: 'username',
      key: 'username',
      render: (text: string) => (
        <Space>
          <UserOutlined />
          <span>{text}</span>
        </Space>
      ),
    },
    {
      title: '邮箱',
      dataIndex: 'email',
      key: 'email',
    },
    {
      title: '手机号',
      dataIndex: 'mobile',
      key: 'mobile',
    },
    {
      title: '部门',
      dataIndex: 'dept_names',
      key: 'dept_names',
      render: (depts: string[]) => (
        <>
          {depts?.map((dept, index) => (
            <Tag key={index}>{dept}</Tag>
          ))}
        </>
      ),
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status: string, record: User) => (
        <Switch
          checked={status === 'active'}
          checkedChildren="启用"
          unCheckedChildren="禁用"
          onChange={(checked) => handleStatusChange(record.feishu_user_id, checked)}
          loading={updateStatusMutation.isPending}
        />
      ),
    },
    {
      title: '最后登录',
      dataIndex: 'last_login',
      key: 'last_login',
      render: (time: string) => (time ? new Date(time).toLocaleString('zh-CN') : '-'),
    },
    {
      title: '操作',
      key: 'action',
      render: (_: any, record: User) => (
        <Space size="middle">
          <Button type="link" onClick={() => handleViewPermissions(record)}>
            查看权限
          </Button>
          <Button type="link" onClick={() => handleAssignRole(record)}>
            分配角色
          </Button>
        </Space>
      ),
    },
  ]

  if (error) {
    return (
      <div>
        <h1>用户管理</h1>
        <div style={{ color: 'red', marginTop: 16 }}>加载失败: {error.message}</div>
      </div>
    )
  }

  return (
    <div>
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h1>用户管理</h1>
      </div>

      <div style={{ marginBottom: 16, display: 'flex', gap: 16 }}>
        <Search
          placeholder="搜索用户名或邮箱"
          allowClear
          enterButton={<SearchOutlined />}
          style={{ width: 300 }}
          onSearch={setSearch}
        />
        <Select
          placeholder="筛选状态"
          allowClear
          style={{ width: 150 }}
          value={status}
          onChange={setStatus}
          options={[
            { value: 'active', label: '启用' },
            { value: 'inactive', label: '禁用' },
          ]}
        />
      </div>

      <Spin spinning={isLoading}>
        <Table
          columns={columns}
          dataSource={data?.items || []}
          rowKey="feishu_user_id"
          pagination={{
            current: page,
            pageSize: pageSize,
            total: data?.total || 0,
            showSizeChanger: true,
            showTotal: (total) => `共 ${total} 条`,
            onChange: (page, pageSize) => {
              setPage(page)
              setPageSize(pageSize)
            },
          }}
        />
      </Spin>

      {/* 查看权限Modal */}
      {selectedUser && (
        <UserPermissionModal
          visible={permissionModalVisible}
          userId={selectedUser.feishu_user_id}
          username={selectedUser.username}
          onClose={() => {
            setPermissionModalVisible(false)
            setSelectedUser(null)
          }}
        />
      )}

      {/* 分配角色Modal */}
      {selectedUser && (
        <AssignRoleModal
          visible={assignRoleModalVisible}
          userId={selectedUser.feishu_user_id}
          username={selectedUser.username}
          onClose={() => {
            setAssignRoleModalVisible(false)
            setSelectedUser(null)
          }}
          onSuccess={() => {
            queryClient.invalidateQueries({ queryKey: ['users'] })
          }}
        />
      )}
    </div>
  )
}

export default UserList
