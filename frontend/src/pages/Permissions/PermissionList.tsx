import { Table, Tabs } from 'antd'

const PermissionList = () => {
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
      title: '资源类型',
      dataIndex: 'resource_type',
      key: 'resource_type',
    },
    {
      title: '操作',
      dataIndex: 'action',
      key: 'action',
    },
  ]

  const routeColumns = [
    {
      title: '角色',
      dataIndex: 'role',
      key: 'role',
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
  ]

  const data: any[] = []

  const items = [
    {
      key: '1',
      label: '权限列表',
      children: <Table columns={permissionColumns} dataSource={data} />,
    },
    {
      key: '2',
      label: '路由规则',
      children: <Table columns={routeColumns} dataSource={data} />,
    },
    {
      key: '3',
      label: '资源绑定',
      children: <div>资源绑定管理</div>,
    },
  ]

  return (
    <div>
      <h1>权限管理</h1>
      <Tabs items={items} style={{ marginTop: 16 }} />
    </div>
  )
}

export default PermissionList

