import { useState, useEffect } from 'react'
import { Modal, Select, Form, message, Spin } from 'antd'
import { useQuery, useMutation } from '@tanstack/react-query'
import { apiGet, apiPost } from '@/utils/api'
import type { Role } from '@/types/api'

interface AssignRoleModalProps {
  visible: boolean
  userId: number
  username: string
  onClose: () => void
  onSuccess: () => void
}

const AssignRoleModal = ({ visible, userId, username, onClose, onSuccess }: AssignRoleModalProps) => {
  const [form] = Form.useForm()
  const [selectedRoleId, setSelectedRoleId] = useState<number | null>(null)

  // 获取所有角色列表
  const { data: roles, isLoading } = useQuery<Role[]>({
    queryKey: ['roles'],
    queryFn: () => apiGet<Role[]>('/rbac/roles'),
    enabled: visible,
  })

  // 分配角色
  const assignMutation = useMutation({
    mutationFn: (roleId: number) => apiPost(`/rbac/users/${userId}/roles/${roleId}`, {}),
    onSuccess: () => {
      message.success('角色分配成功')
      onSuccess()
      onClose()
      form.resetFields()
    },
    onError: (error: any) => {
      message.error(`分配失败: ${error.message}`)
    },
  })

  useEffect(() => {
    if (!visible) {
      form.resetFields()
      setSelectedRoleId(null)
    }
  }, [visible, form])

  const handleOk = () => {
    form.validateFields().then((values) => {
      if (values.roleId) {
        assignMutation.mutate(values.roleId)
      }
    })
  }

  return (
    <Modal
      title={`分配角色 - ${username}`}
      open={visible}
      onCancel={onClose}
      onOk={handleOk}
      confirmLoading={assignMutation.isPending}
    >
      <Spin spinning={isLoading}>
        <Form form={form} layout="vertical">
          <Form.Item
            name="roleId"
            label="选择角色"
            rules={[{ required: true, message: '请选择要分配的角色' }]}
          >
            <Select
              placeholder="请选择角色"
              showSearch
              filterOption={(input, option) =>
                (option?.label ?? '').toLowerCase().includes(input.toLowerCase())
              }
              options={roles?.map((role) => ({
                value: role.id,
                label: `${role.name} (${role.namespace})`,
              }))}
              onChange={(value) => setSelectedRoleId(value)}
            />
          </Form.Item>
        </Form>
      </Spin>
    </Modal>
  )
}

export default AssignRoleModal

