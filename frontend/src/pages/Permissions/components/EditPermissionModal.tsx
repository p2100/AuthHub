import { useEffect } from 'react'
import { Modal, Form, Input, Select, message } from 'antd'
import { useMutation, useQuery } from '@tanstack/react-query'
import { apiPut, apiGet } from '@/utils/api'
import type { PermissionCreate, Permission, System } from '@/types/api'

interface EditPermissionModalProps {
  visible: boolean
  permission: Permission | null
  onClose: () => void
  onSuccess: () => void
}

const EditPermissionModal = ({ visible, permission, onClose, onSuccess }: EditPermissionModalProps) => {
  const [form] = Form.useForm()

  // 获取系统列表
  const { data: systems } = useQuery<System[]>({
    queryKey: ['systems'],
    queryFn: () => apiGet<System[]>('/systems'),
    enabled: visible,
  })

  // 更新权限
  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: PermissionCreate }) => 
      apiPut<Permission>(`/rbac/permissions/${id}`, data),
    onSuccess: () => {
      message.success('权限更新成功')
      onSuccess()
      onClose()
      form.resetFields()
    },
    onError: (error: any) => {
      message.error(`更新失败: ${error.message}`)
    },
  })

  useEffect(() => {
    if (visible && permission) {
      form.setFieldsValue({
        code: permission.code,
        name: permission.name,
        namespace: permission.namespace,
        resource_type: permission.resource_type,
        action: permission.action,
      })
    } else if (!visible) {
      form.resetFields()
    }
  }, [visible, permission, form])

  const handleOk = () => {
    if (!permission) return
    
    form.validateFields().then((values) => {
      updateMutation.mutate({ id: permission.id, data: values })
    })
  }

  return (
    <Modal
      title="编辑权限"
      open={visible}
      onCancel={onClose}
      onOk={handleOk}
      confirmLoading={updateMutation.isPending}
      width={600}
    >
      <Form form={form} layout="vertical" style={{ marginTop: 16 }}>
        <Form.Item
          name="code"
          label="权限代码"
          rules={[
            { required: true, message: '请输入权限代码' },
            { pattern: /^[a-z0-9_:-]+$/, message: '只能包含小写字母、数字、下划线、冒号和连字符' },
          ]}
        >
          <Input placeholder="例如: user:read" disabled />
        </Form.Item>

        <Form.Item
          name="name"
          label="权限名称"
          rules={[{ required: true, message: '请输入权限名称' }]}
        >
          <Input placeholder="例如: 用户读取" />
        </Form.Item>

        <Form.Item
          name="namespace"
          label="命名空间"
          rules={[{ required: true, message: '请选择命名空间' }]}
        >
          <Select
            placeholder="请选择命名空间"
            disabled
            options={[
              { value: 'global', label: '全局' },
              ...(systems?.map((s) => ({ value: s.code, label: s.name })) || []),
            ]}
          />
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
      </Form>
    </Modal>
  )
}

export default EditPermissionModal
