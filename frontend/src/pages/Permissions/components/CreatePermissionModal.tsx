import { useEffect } from 'react'
import { Modal, Form, Input, Select, message } from 'antd'
import { useMutation, useQuery } from '@tanstack/react-query'
import { apiPost, apiGet } from '@/utils/api'
import type { PermissionCreate, Permission, System } from '@/types/api'

interface CreatePermissionModalProps {
  visible: boolean
  onClose: () => void
  onSuccess: () => void
}

const CreatePermissionModal = ({ visible, onClose, onSuccess }: CreatePermissionModalProps) => {
  const [form] = Form.useForm()

  // 获取系统列表
  const { data: systems } = useQuery<System[]>({
    queryKey: ['systems'],
    queryFn: () => apiGet<System[]>('/systems'),
    enabled: visible,
  })

  // 创建权限
  const createMutation = useMutation({
    mutationFn: (data: PermissionCreate) => apiPost<Permission>('/rbac/permissions', data),
    onSuccess: () => {
      message.success('权限创建成功')
      onSuccess()
      onClose()
      form.resetFields()
    },
    onError: (error: any) => {
      message.error(`创建失败: ${error.message}`)
    },
  })

  useEffect(() => {
    if (!visible) {
      form.resetFields()
    }
  }, [visible, form])

  const handleOk = () => {
    form.validateFields().then((values) => {
      createMutation.mutate(values)
    })
  }

  const handleNamespaceChange = (namespace: string) => {
    if (namespace === 'global') {
      form.setFieldsValue({ system_id: undefined })
    }
  }

  return (
    <Modal
      title="创建权限"
      open={visible}
      onCancel={onClose}
      onOk={handleOk}
      confirmLoading={createMutation.isPending}
      width={600}
    >
      <Form form={form} layout="vertical" style={{ marginTop: 16 }}>
        <Form.Item
          name="namespace"
          label="命名空间"
          rules={[{ required: true, message: '请选择命名空间' }]}
        >
          <Select
            placeholder="请选择命名空间"
            onChange={handleNamespaceChange}
            options={[
              { value: 'global', label: '全局' },
              ...(systems?.map((s) => ({ value: s.code, label: s.name })) || []),
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
                  placeholder="请选择系统"
                  options={systems?.map((s) => ({ value: s.id, label: s.name }))}
                />
              </Form.Item>
            ) : null
          }}
        </Form.Item>

        <Form.Item
          name="code"
          label="权限代码"
          rules={[
            { required: true, message: '请输入权限代码' },
            { pattern: /^[a-z0-9_:-]+$/, message: '只能包含小写字母、数字、下划线、冒号和连字符' },
          ]}
        >
          <Input placeholder="例如: user:read" />
        </Form.Item>

        <Form.Item
          name="name"
          label="权限名称"
          rules={[{ required: true, message: '请输入权限名称' }]}
        >
          <Input placeholder="例如: 用户读取" />
        </Form.Item>

        <Form.Item
          name="resource_type"
          label="资源类型"
        >
          <Input placeholder="例如: user, order, product" />
        </Form.Item>

        <Form.Item
          name="action"
          label="操作"
        >
          <Input placeholder="例如: read, write, delete" />
        </Form.Item>

        <Form.Item name="description" label="描述">
          <Input.TextArea rows={3} placeholder="简要描述该权限的作用" />
        </Form.Item>
      </Form>
    </Modal>
  )
}

export default CreatePermissionModal

