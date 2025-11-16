import { useEffect, useState } from 'react'
import { Modal, Form, Select, Input, message, Tag } from 'antd'
import { useMutation, useQuery } from '@tanstack/react-query'
import { apiPost, apiGet } from '@/utils/api'
import type { ResourceBindingCreate, User, System } from '@/types/api'

interface CreateResourceBindingModalProps {
  visible: boolean
  onClose: () => void
  onSuccess: () => void
}

const CreateResourceBindingModal = ({ visible, onClose, onSuccess }: CreateResourceBindingModalProps) => {
  const [form] = Form.useForm()
  const [resourceIds, setResourceIds] = useState<string[]>([])
  const [inputValue, setInputValue] = useState('')

  // 获取用户列表
  const { data: usersData } = useQuery<{ total: number; items: User[] }>({
    queryKey: ['users', 'all'],
    queryFn: () => apiGet<{ total: number; items: User[] }>('/users?page=1&page_size=1000'),
    enabled: visible,
  })

  // 获取系统列表
  const { data: systems } = useQuery<System[]>({
    queryKey: ['systems'],
    queryFn: () => apiGet<System[]>('/systems'),
    enabled: visible,
  })

  // 创建资源绑定
  const createMutation = useMutation({
    mutationFn: (data: ResourceBindingCreate) => apiPost('/rbac/resource-bindings', data),
    onSuccess: () => {
      message.success('资源绑定创建成功')
      onSuccess()
      onClose()
      form.resetFields()
      setResourceIds([])
    },
    onError: (error: any) => {
      message.error(`创建失败: ${error.message}`)
    },
  })

  useEffect(() => {
    if (!visible) {
      form.resetFields()
      setResourceIds([])
      setInputValue('')
    }
  }, [visible, form])

  const handleOk = () => {
    if (resourceIds.length === 0) {
      message.error('请至少添加一个资源ID')
      return
    }

    form.validateFields().then((values) => {
      const data: ResourceBindingCreate = {
        ...values,
        resource_ids: resourceIds,
      }
      createMutation.mutate(data)
    })
  }

  const handleNamespaceChange = (namespace: string) => {
    if (namespace === 'global') {
      form.setFieldsValue({ system_id: undefined })
    }
  }

  const handleAddResourceId = () => {
    if (inputValue.trim() && !resourceIds.includes(inputValue.trim())) {
      setResourceIds([...resourceIds, inputValue.trim()])
      setInputValue('')
    }
  }

  const handleRemoveResourceId = (id: string) => {
    setResourceIds(resourceIds.filter(item => item !== id))
  }

  const handleInputKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault()
      handleAddResourceId()
    }
  }

  // 常用资源类型选项
  const resourceTypeOptions = [
    { value: 'project', label: '项目 (project)' },
    { value: 'team', label: '团队 (team)' },
    { value: 'document', label: '文档 (document)' },
    { value: 'company', label: '公司 (company)' },
    { value: 'workspace', label: '工作区 (workspace)' },
    { value: 'folder', label: '文件夹 (folder)' },
    { value: 'dataset', label: '数据集 (dataset)' },
  ]

  // 常用操作选项
  const actionOptions = [
    { value: 'read', label: '读取 (read)' },
    { value: 'write', label: '写入 (write)' },
    { value: 'admin', label: '管理 (admin)' },
    { value: 'delete', label: '删除 (delete)' },
    { value: 'share', label: '共享 (share)' },
    { value: 'member', label: '成员 (member)' },
    { value: 'owner', label: '所有者 (owner)' },
  ]

  return (
    <Modal
      title="创建资源绑定"
      open={visible}
      onCancel={onClose}
      onOk={handleOk}
      confirmLoading={createMutation.isPending}
      width={650}
    >
      <Form form={form} layout="vertical" style={{ marginTop: 16 }}>
        <Form.Item
          name="user_id"
          label="用户"
          rules={[{ required: true, message: '请选择用户' }]}
        >
          <Select
            placeholder="请选择用户"
            showSearch
            filterOption={(input, option) =>
              (option?.label ?? '').toLowerCase().includes(input.toLowerCase())
            }
            options={usersData?.items.map((u) => ({ 
              value: u.id, 
              label: `${u.username} (${u.email || u.feishu_user_id})` 
            }))}
          />
        </Form.Item>

        <Form.Item
          name="namespace"
          label="命名空间"
          rules={[{ required: true, message: '请选择命名空间' }]}
        >
          <Select
            placeholder="请选择命名空间"
            onChange={handleNamespaceChange}
            options={[
              { value: 'global', label: '全局 (global)' },
              ...(systems?.map((s) => ({ value: s.code, label: `${s.name} (${s.code})` })) || []),
            ]}
          />
        </Form.Item>

        <Form.Item
          noStyle
          shouldUpdate={(prevValues, currentValues) => prevValues.namespace !== currentValues.namespace}
        >
          {({ getFieldValue }) => {
            const namespace = getFieldValue('namespace')
            return namespace && namespace !== 'global' ? (
              <Form.Item name="system_id" label="关联系统">
                <Select
                  placeholder="请选择系统（可选）"
                  allowClear
                  options={systems?.map((s) => ({ value: s.id, label: s.name }))}
                />
              </Form.Item>
            ) : null
          }}
        </Form.Item>

        <Form.Item
          name="resource_type"
          label="资源类型"
          rules={[{ required: true, message: '请选择或输入资源类型' }]}
          tooltip="选择常用类型或输入自定义类型"
        >
          <Select
            placeholder="例如: project, team, document"
            showSearch
            mode="tags"
            maxCount={1}
            options={resourceTypeOptions}
          />
        </Form.Item>

        <Form.Item
          label="资源ID列表"
          required
          tooltip="输入资源ID后按回车添加，支持批量添加多个资源"
        >
          <Input
            placeholder="输入资源ID后按回车添加，例如: proj_123"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleInputKeyPress}
            onBlur={handleAddResourceId}
            suffix={
              <span style={{ color: '#999', fontSize: '12px' }}>
                按回车添加
              </span>
            }
          />
          <div style={{ marginTop: 8, minHeight: 32 }}>
            {resourceIds.map((id) => (
              <Tag
                key={id}
                closable
                onClose={() => handleRemoveResourceId(id)}
                style={{ marginBottom: 4 }}
              >
                {id}
              </Tag>
            ))}
            {resourceIds.length > 0 && (
              <span style={{ color: '#999', fontSize: '12px', marginLeft: 8 }}>
                共 {resourceIds.length} 个资源
              </span>
            )}
          </div>
        </Form.Item>

        <Form.Item
          name="action"
          label="操作权限"
          tooltip="指定用户对这些资源的操作权限"
        >
          <Select
            placeholder="例如: read, write, admin"
            showSearch
            mode="tags"
            maxCount={1}
            options={actionOptions}
          />
        </Form.Item>
      </Form>
    </Modal>
  )
}

export default CreateResourceBindingModal

