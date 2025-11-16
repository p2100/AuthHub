import { useEffect } from 'react'
import { Modal, Form, Input, Select, InputNumber, message } from 'antd'
import { useMutation, useQuery } from '@tanstack/react-query'
import { apiPut, apiGet } from '@/utils/api'
import type { RoutePatternCreate, RoutePattern, System, Role } from '@/types/api'

interface EditRouteModalProps {
  visible: boolean
  route: RoutePattern | null
  onClose: () => void
  onSuccess: () => void
}

const EditRouteModal = ({ visible, route, onClose, onSuccess }: EditRouteModalProps) => {
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

  // 更新路由规则
  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: RoutePatternCreate }) => 
      apiPut<RoutePattern>(`/rbac/routes/${id}`, data),
    onSuccess: () => {
      message.success('路由规则更新成功')
      onSuccess()
      onClose()
      form.resetFields()
    },
    onError: (error: any) => {
      message.error(`更新失败: ${error.message}`)
    },
  })

  useEffect(() => {
    if (visible && route) {
      form.setFieldsValue({
        system_id: route.system_id,
        role_id: route.role_id,
        pattern: route.pattern,
        method: route.method,
        priority: route.priority,
        description: route.description,
      })
    } else if (!visible) {
      form.resetFields()
    }
  }, [visible, route, form])

  const handleOk = () => {
    if (!route) return
    
    form.validateFields().then((values) => {
      updateMutation.mutate({ id: route.id, data: values })
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
      title="编辑路由规则"
      open={visible}
      onCancel={onClose}
      onOk={handleOk}
      confirmLoading={updateMutation.isPending}
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
            disabled
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

export default EditRouteModal
