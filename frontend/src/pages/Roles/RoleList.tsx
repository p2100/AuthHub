import { Table, Button, Space, Select } from 'antd'
import { PlusOutlined } from '@ant-design/icons'

const RoleList = () => {
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
      title: '操作',
      key: 'action',
      render: () => (
        <Space size="middle">
          <a>配置权限</a>
          <a>编辑</a>
          <a>删除</a>
        </Space>
      ),
    },
  ]

  const data: any[] = []

  return (
    <div>
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1 style={{ display: 'inline-block', marginRight: 16 }}>角色管理</h1>
          <Select
            defaultValue="all"
            style={{ width: 200 }}
            options={[
              { value: 'all', label: '全部系统' },
              { value: 'global', label: '全局角色' },
              { value: 'system_a', label: '系统A' },
            ]}
          />
        </div>
        <Button type="primary" icon={<PlusOutlined />}>
          创建角色
        </Button>
      </div>
      <Table columns={columns} dataSource={data} />
    </div>
  )
}

export default RoleList

