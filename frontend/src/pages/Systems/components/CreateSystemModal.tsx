import { useEffect } from 'react'
import { Modal, Form, Input, message } from 'antd'
import { useMutation } from '@tanstack/react-query'
import { apiPost } from '@/utils/api'
import type { SystemCreate, SystemWithToken } from '@/types/api'

interface CreateSystemModalProps {
  visible: boolean
  onClose: () => void
  onSuccess: () => void
}

const CreateSystemModal = ({ visible, onClose, onSuccess }: CreateSystemModalProps) => {
  const [form] = Form.useForm()

  // 创建系统
  const createMutation = useMutation({
    mutationFn: (data: SystemCreate) => apiPost<SystemWithToken>('/systems', data),
    onSuccess: (data) => {
      // 显示系统Token
      Modal.success({
        title: '系统创建成功',
        width: 600,
        content: (
          <div>
            <p>请妥善保存系统Token，它只会显示一次：</p>
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

  return (
    <Modal
      title="注册新系统"
      open={visible}
      onCancel={onClose}
      onOk={handleOk}
      confirmLoading={createMutation.isPending}
    >
      <Form form={form} layout="vertical" style={{ marginTop: 16 }}>
        <Form.Item
          name="code"
          label="系统代码"
          rules={[
            { required: true, message: '请输入系统代码' },
            { min: 2, max: 50, message: '长度必须在2-50之间' },
            { pattern: /^[a-z0-9_-]+$/, message: '只能包含小写字母、数字、下划线和连字符' },
          ]}
        >
          <Input placeholder="例如: user-center" />
        </Form.Item>

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

export default CreateSystemModal

