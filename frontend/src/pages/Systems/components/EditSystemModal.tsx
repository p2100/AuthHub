import { useEffect } from 'react'
import { Modal, Form, Input, message } from 'antd'
import { useMutation } from '@tanstack/react-query'
import { apiPut } from '@/utils/api'
import type { System, SystemUpdate } from '@/types/api'

interface EditSystemModalProps {
  visible: boolean
  system: System
  onClose: () => void
  onSuccess: () => void
}

const EditSystemModal = ({ visible, system, onClose, onSuccess }: EditSystemModalProps) => {
  const [form] = Form.useForm()

  // 更新系统
  const updateMutation = useMutation({
    mutationFn: (data: SystemUpdate) => apiPut<SystemUpdate, System>(`/systems/${system.id}`, data),
    onSuccess: () => {
      message.success('系统更新成功')
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
        name: system.name,
        description: system.description,
        api_endpoint: system.api_endpoint,
      })
    }
  }, [visible, system, form])

  const handleOk = () => {
    form.validateFields().then((values) => {
      updateMutation.mutate(values)
    })
  }

  return (
    <Modal
      title={`编辑系统 - ${system.code}`}
      open={visible}
      onCancel={onClose}
      onOk={handleOk}
      confirmLoading={updateMutation.isPending}
    >
      <Form form={form} layout="vertical" style={{ marginTop: 16 }}>
        <Form.Item
          name="name"
          label="系统名称"
          rules={[
            { required: true, message: '请输入系统名称' },
            { max: 100, message: '长度不能超过100' },
          ]}
        >
          <Input placeholder="例如: 用户中心" />
        </Form.Item>

        <Form.Item name="description" label="系统描述">
          <Input.TextArea rows={3} placeholder="简要描述系统的功能" />
        </Form.Item>

        <Form.Item name="api_endpoint" label="API端点">
          <Input placeholder="例如: https://api.example.com" />
        </Form.Item>
      </Form>
    </Modal>
  )
}

export default EditSystemModal

