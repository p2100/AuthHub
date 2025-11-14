import { Table, Button, Space } from 'antd'
import { PlusOutlined } from '@ant-design/icons'

const SystemList = () => {
  const columns = [
    {
      title: '系统代码',
      dataIndex: 'code',
      key: 'code',
    },
    {
      title: '系统名称',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: '描述',
      dataIndex: 'description',
      key: 'description',
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
    },
    {
      title: '操作',
      key: 'action',
      render: () => (
        <Space size="middle">
          <a>查看</a>
          <a>编辑</a>
        </Space>
      ),
    },
  ]

  const data: any[] = []

  return (
    <div>
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between' }}>
        <h1>系统管理</h1>
        <Button type="primary" icon={<PlusOutlined />}>
          注册新系统
        </Button>
      </div>
      <Table columns={columns} dataSource={data} />
    </div>
  )
}

export default SystemList

