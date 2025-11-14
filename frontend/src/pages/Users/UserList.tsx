import { Table, Tag } from 'antd'

const UserList = () => {
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
      dataIndex: 'depts',
      key: 'depts',
      render: (depts: string[]) => (
        <>
          {depts?.map(dept => (
            <Tag key={dept}>{dept}</Tag>
          ))}
        </>
      ),
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
    },
    {
      title: '操作',
      key: 'action',
      render: () => <a>查看权限</a>,
    },
  ]

  const data: any[] = []

  return (
    <div>
      <h1>用户管理</h1>
      <Table columns={columns} dataSource={data} style={{ marginTop: 16 }} />
    </div>
  )
}

export default UserList

