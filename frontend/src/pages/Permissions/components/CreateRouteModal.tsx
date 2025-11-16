import { useEffect } from 'react'
import { Modal, Form, Input, Select, InputNumber, message } from 'antd'
import { useMutation, useQuery } from '@tanstack/react-query'
import { apiPost, apiGet } from '@/utils/api'
import type { RoutePatternCreate, RoutePattern, System, Role } from '@/types/api'

interface CreateRouteModalProps {
  visible: boolean
  onClose: () => void
  onSuccess: () => void
}

const CreateRouteModal = ({ visible, onClose, onSuccess }: CreateRouteModalProps) => {
  const [form] = Form.useForm()

  // 获取系统列表
  const { data: systems } = useQuery<System[]>({
    queryKey: ['systems'],
    queryFn: () => apiGet<System[]>('/systems'),
    enabled: visible,
  })

  // 获取角色列表
  const { data: roles } = useQuery<Role[]>({
    queryKey: ['roles'],
    queryFn: () => apiGet<Role[]>('/rbac/roles'),
    enabled: visible,
  })

  // 创建路由规则
  const createMutation = useMutation({
    mutationFn: (data: RoutePatternCreate) => apiPost<RoutePattern>('/rbac/routes', data),
    onSuccess: () => {
      message.success('路由规则创建成功')
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

  // HTTP方法选项
  const methodOptions = [
    { value: '*', label: '所有方法 (*)' },
    { value: 'GET', label: 'GET' },
    { value: 'POST', label: 'POST' },
    { value: 'PUT', label: 'PUT' },
    { value: 'DELETE', label: 'DELETE' },
    { value: 'PATCH', label: 'PATCH' },
    { value: 'HEAD', label: 'HEAD' },
    { value: 'OPTIONS', label: 'OPTIONS' },
  ]

  return (
    <Modal
      title="创建路由规则"
      open={visible}
      onCancel={onClose}
      onOk={handleOk}
      confirmLoading={createMutation.isPending}
      width={600}
    >
      <Form form={form} layout="vertical" style={{ marginTop: 16 }}>
        <Form.Item
          name="system_id"
          label="所属系统"
          rules={[{ required: true, message: '请选择系统' }]}
        >
          <Select
            placeholder="请选择系统"
            options={systems?.map((s) => ({ value: s.id, label: s.name }))}
          />
        </Form.Item>

        <Form.Item
          name="role_id"
          label="关联角色"
          rules={[{ required: true, message: '请选择角色' }]}
        >
          <Select
            placeholder="请选择角色"
            showSearch
            filterOption={(input, option) =>
              (option?.label ?? '').toLowerCase().includes(input.toLowerCase())
            }
            options={roles?.map((r) => ({ 
              value: r.id, 
              label: `${r.name} (${r.code})` 
            }))}
          />
        </Form.Item>

        <Form.Item
          name="pattern"
          label="路由正则"
          rules={[{ required: true, message: '请输入路由正则表达式' }]}
          tooltip="支持正则表达式，例如: ^/api/users/.*"
        >
          <Input placeholder="例如: ^/api/users/.*" />
        </Form.Item>

        <Form.Item
          name="method"
          label="HTTP方法"
          initialValue="*"
          rules={[{ required: true, message: '请选择HTTP方法' }]}
        >
          <Select
            placeholder="请选择HTTP方法"
            options={methodOptions}
          />
        </Form.Item>

        <Form.Item
          name="priority"
          label="优先级"
          initialValue={0}
          tooltip="数值越大优先级越高，默认为0"
        >
          <InputNumber 
            style={{ width: '100%' }} 
            min={0} 
            max={1000}
            placeholder="0"
          />
        </Form.Item>

        <Form.Item name="description" label="描述">
          <Input.TextArea rows={3} placeholder="简要描述该路由规则的作用" />
        </Form.Item>
      </Form>
    </Modal>
  )
}

export default CreateRouteModal

