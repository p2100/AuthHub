import { Drawer, Table, Tag } from 'antd'
import { useQuery } from '@tanstack/react-query'
import { apiGet } from '@/utils/api'
import type { Role, User } from '@/types/api'

interface RoleUsersDrawerProps {
  visible: boolean
  role: Role
  onClose: () => void
}

const RoleUsersDrawer = ({ visible, role, onClose }: RoleUsersDrawerProps) => {
  // 获取拥有该角色的用户列表
  const { data: users, isLoading } = useQuery<User[]>({
    queryKey: ['role-users', role.id],
    queryFn: () => apiGet<User[]>(`/rbac/roles/${role.id}/users`),
    enabled: visible,
  })

  const columns = [
    {
      title: '用户名',
      dataIndex: 'username',
      key: 'username',
    },
    {
      title: '邮箱',
      dataIndex: 'email',
      key: 'email',
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
      render: (status: string) => (
        <Tag color={status === 'active' ? 'green' : 'red'}>
          {status === 'active' ? '启用' : '禁用'}
        </Tag>
      ),
    },
  ]

  return (
    <Drawer
      title={`角色用户 - ${role.name}`}
      open={visible}
      onClose={onClose}
      width={720}
    >
      <Table
        columns={columns}
        dataSource={users || []}
        rowKey="id"
        loading={isLoading}
        pagination={false}
      />
    </Drawer>
  )
}

export default RoleUsersDrawer

