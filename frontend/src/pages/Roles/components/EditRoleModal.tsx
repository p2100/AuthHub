import { useEffect } from 'react'
import { Modal, Form, Input, message } from 'antd'
import { useMutation } from '@tanstack/react-query'
import { apiPut } from '@/utils/api'
import type { Role, RoleUpdate } from '@/types/api'

interface EditRoleModalProps {
  visible: boolean
  role: Role
  onClose: () => void
  onSuccess: () => void
}

const EditRoleModal = ({ visible, role, onClose, onSuccess }: EditRoleModalProps) => {
  const [form] = Form.useForm()

  // 更新角色
  const updateMutation = useMutation({
    mutationFn: (data: RoleUpdate) => apiPut<Role>(`/rbac/roles/${role.id}`, data),
    onSuccess: () => {
      message.success('角色更新成功')
      onSuccess()
      onClose()
    },
    onError: (error: any) => {
      message.error(`更新失败: ${error.message}`)
    },
  })

  useEffect(() => {
    if (visible) {
      form.setFieldsValue({
        name: role.name,
        description: role.description,
      })
    }
  }, [visible, role, form])

  const handleOk = () => {
    form.validateFields().then((values) => {
      updateMutation.mutate(values)
    })
  }

  return (
    <Modal
      title={`编辑角色 - ${role.code}`}
      open={visible}
      onCancel={onClose}
      onOk={handleOk}
      confirmLoading={updateMutation.isPending}
    >
      <Form form={form} layout="vertical" style={{ marginTop: 16 }}>
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

export default EditRoleModal

