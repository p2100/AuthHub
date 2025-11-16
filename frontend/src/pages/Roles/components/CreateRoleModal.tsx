import { useEffect } from 'react'
import { Modal, Form, Input, Select, message } from 'antd'
import { useMutation, useQuery } from '@tanstack/react-query'
import { apiPost, apiGet } from '@/utils/api'
import type { RoleCreate, Role, System } from '@/types/api'

interface CreateRoleModalProps {
  visible: boolean
  onClose: () => void
  onSuccess: () => void
}

const CreateRoleModal = ({ visible, onClose, onSuccess }: CreateRoleModalProps) => {
  const [form] = Form.useForm()

  // 获取系统列表
  const { data: systems } = useQuery<System[]>({
    queryKey: ['systems'],
    queryFn: () => apiGet<System[]>('/systems'),
    enabled: visible,
  })

  // 创建角色
  const createMutation = useMutation({
    mutationFn: (data: RoleCreate) => apiPost<RoleCreate, Role>('/rbac/roles', data),
    onSuccess: () => {
      message.success('角色创建成功')
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
      title="创建角色"
      open={visible}
      onCancel={onClose}
      onOk={handleOk}
      confirmLoading={createMutation.isPending}
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
          label="角色代码"
          rules={[
            { required: true, message: '请输入角色代码' },
            { pattern: /^[a-z0-9_-]+$/, message: '只能包含小写字母、数字、下划线和连字符' },
          ]}
        >
          <Input placeholder="例如: admin" />
        </Form.Item>

        <Form.Item
          name="name"
          label="角色名称"
          rules={[{ required: true, message: '请输入角色名称' }]}
        >
          <Input placeholder="例如: 管理员" />
        </Form.Item>

        <Form.Item name="description" label="角色描述">
          <Input.TextArea rows={3} placeholder="简要描述角色的职能" />
        </Form.Item>
      </Form>
    </Modal>
  )
}

export default CreateRoleModal

