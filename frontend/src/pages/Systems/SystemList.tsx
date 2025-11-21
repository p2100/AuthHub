import { useState } from 'react'
import { Table, Button, Space, Tag } from 'antd'
import { PlusOutlined, EyeOutlined, EditOutlined } from '@ant-design/icons'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { apiGet } from '@/utils/api'
import type { System } from '@/types/api'
import CreateSystemModal from './components/CreateSystemModal'
import EditSystemModal from './components/EditSystemModal'
import SystemDetailDrawer from './components/SystemDetailDrawer'

const SystemList = () => {
  const queryClient = useQueryClient()
  const [createModalVisible, setCreateModalVisible] = useState(false)
  const [editModalVisible, setEditModalVisible] = useState(false)
  const [detailDrawerVisible, setDetailDrawerVisible] = useState(false)
  const [selectedSystem, setSelectedSystem] = useState<System | null>(null)

  // 获取系统列表
  const { data: systems, isLoading } = useQuery<System[]>({
    queryKey: ['systems'],
    queryFn: () => apiGet<System[]>('/systems'),
  })

  const handleEdit = (system: System) => {
    setSelectedSystem(system)
    setEditModalVisible(true)
  }

  const handleViewDetail = (system: System) => {
    setSelectedSystem(system)
    setDetailDrawerVisible(true)
  }

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
      title: 'API端点',
      dataIndex: 'api_endpoint',
      key: 'api_endpoint',
      ellipsis: true,
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
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (time: string) => new Date(time).toLocaleString('zh-CN'),
    },
    {
      title: '操作',
      key: 'action',
      render: (_: any, record: System) => (
        <Space size="small">
          <Button
            type="link"
            size="small"
            icon={<EyeOutlined />}
            onClick={() => handleViewDetail(record)}
          >
            查看
          </Button>
          <Button
            type="link"
            size="small"
            icon={<EditOutlined />}
            onClick={() => handleEdit(record)}
          >
            编辑
          </Button>
        </Space>
      ),
    },
  ]

  return (
    <div>
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between' }}>
        <h1>系统管理</h1>
        <Button
          type="primary"
          icon={<PlusOutlined />}
          onClick={() => setCreateModalVisible(true)}
        >
          注册新系统
        </Button>
      </div>

      <Table
        columns={columns}
        dataSource={systems || []}
        rowKey="id"
        loading={isLoading}
      />

      {/* 创建系统Modal */}
      <CreateSystemModal
        visible={createModalVisible}
        onClose={() => setCreateModalVisible(false)}
        onSuccess={() => {
          queryClient.invalidateQueries({ queryKey: ['systems'] })
        }}
      />

      {/* 编辑系统Modal */}
      {selectedSystem && (
        <EditSystemModal
          visible={editModalVisible}
          system={selectedSystem}
          onClose={() => {
            setEditModalVisible(false)
            setSelectedSystem(null)
          }}
          onSuccess={() => {
            queryClient.invalidateQueries({ queryKey: ['systems'] })
          }}
        />
      )}

      {/* 系统详情Drawer */}
      {selectedSystem && (
        <SystemDetailDrawer
          visible={detailDrawerVisible}
          system={selectedSystem}
          onClose={() => {
            setDetailDrawerVisible(false)
            setSelectedSystem(null)
          }}
          onSuccess={() => {
            queryClient.invalidateQueries({ queryKey: ['systems'] })
          }}
        />
      )}
    </div>
  )
}

export default SystemList
