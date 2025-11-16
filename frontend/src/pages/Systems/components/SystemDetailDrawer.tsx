import { useState } from 'react'
import { Drawer, Descriptions, Tag, Button, Space, Modal, Input, message, Tabs, Table } from 'antd'
import { ReloadOutlined, CopyOutlined } from '@ant-design/icons'
import { useQuery, useMutation } from '@tanstack/react-query'
import { apiGet, apiPost } from '@/utils/api'
import type { System, SystemWithToken, Role, Permission } from '@/types/api'

interface SystemDetailDrawerProps {
  visible: boolean
  system: System
  onClose: () => void
  onSuccess: () => void
}

const SystemDetailDrawer = ({ visible, system, onClose, onSuccess }: SystemDetailDrawerProps) => {
  const [activeTab, setActiveTab] = useState('info')

  // 获取系统角色
  const { data: roles } = useQuery<Role[]>({
    queryKey: ['system-roles', system.id],
    queryFn: () => apiGet<Role[]>(`/systems/${system.id}/roles`),
    enabled: visible && activeTab === 'roles',
  })

  // 获取系统权限
  const { data: permissions } = useQuery<Permission[]>({
    queryKey: ['system-permissions', system.id],
    queryFn: () => apiGet<Permission[]>(`/systems/${system.id}/permissions`),
    enabled: visible && activeTab === 'permissions',
  })

  // 重新生成Token
  const regenerateTokenMutation = useMutation({
    mutationFn: () => apiPost<{}, SystemWithToken>(`/systems/${system.id}/token/regenerate`, {}),
    onSuccess: (data) => {
      Modal.success({
        title: '系统Token已重新生成',
        width: 600,
        content: (
          <div>
            <p>请妥善保存新的系统Token：</p>
            <Input.TextArea
              value={data.system_token}
              rows={4}
              readOnly
              style={{ fontFamily: 'monospace', fontSize: 12 }}
            />
          </div>
        ),
      })
      onSuccess()
    },
    onError: (error: any) => {
      message.error(`重新生成失败: ${error.message}`)
    },
  })

  const handleRegenerateToken = () => {
    Modal.confirm({
      title: '确认重新生成Token?',
      content: '重新生成后，旧Token将立即失效。请确保在所有使用该Token的地方更新配置。',
      okText: '确认',
      cancelText: '取消',
      okType: 'danger',
      onOk: () => {
        regenerateTokenMutation.mutate()
      },
    })
  }

  const roleColumns = [
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
  ]

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

  const tabItems = [
    {
      key: 'info',
      label: '基本信息',
      children: (
        <Descriptions bordered column={1}>
          <Descriptions.Item label="系统代码">{system.code}</Descriptions.Item>
          <Descriptions.Item label="系统名称">{system.name}</Descriptions.Item>
          <Descriptions.Item label="系统描述">{system.description || '-'}</Descriptions.Item>
          <Descriptions.Item label="API端点">{system.api_endpoint || '-'}</Descriptions.Item>
          <Descriptions.Item label="状态">
            <Tag color={system.status === 'active' ? 'green' : 'red'}>
              {system.status === 'active' ? '启用' : '禁用'}
            </Tag>
          </Descriptions.Item>
          <Descriptions.Item label="创建时间">
            {new Date(system.created_at).toLocaleString('zh-CN')}
          </Descriptions.Item>
          <Descriptions.Item label="系统Token">
            <Space>
              <span style={{ color: '#999' }}>已加密存储（请重新生成以查看）</span>
              <Button
                type="link"
                size="small"
                icon={<ReloadOutlined />}
                onClick={handleRegenerateToken}
                loading={regenerateTokenMutation.isPending}
              >
                重新生成
              </Button>
            </Space>
          </Descriptions.Item>
        </Descriptions>
      ),
    },
    {
      key: 'roles',
      label: `角色 (${roles?.length || 0})`,
      children: (
        <Table
          columns={roleColumns}
          dataSource={roles || []}
          rowKey="id"
          pagination={false}
        />
      ),
    },
    {
      key: 'permissions',
      label: `权限 (${permissions?.length || 0})`,
      children: (
        <Table
          columns={permissionColumns}
          dataSource={permissions || []}
          rowKey="id"
          pagination={false}
        />
      ),
    },
  ]

  return (
    <Drawer
      title={`系统详情 - ${system.name}`}
      open={visible}
      onClose={onClose}
      width={720}
    >
      <Tabs activeKey={activeTab} onChange={setActiveTab} items={tabItems} />
    </Drawer>
  )
}

export default SystemDetailDrawer

