import { useState } from 'react'
import { Modal, Transfer, message } from 'antd'
import type { TransferProps } from 'antd'
import { useQuery, useMutation } from '@tanstack/react-query'
import { apiGet, apiPut } from '@/utils/api'
import type { Role, Permission } from '@/types/api'

interface ConfigureRolePermissionsModalProps {
  visible: boolean
  role: Role
  onClose: () => void
  onSuccess: () => void
}

const ConfigureRolePermissionsModal = ({ visible, role, onClose, onSuccess }: ConfigureRolePermissionsModalProps) => {
  const [targetKeys, setTargetKeys] = useState<number[]>([])

  // 获取所有权限
  const { data: permissions, isLoading } = useQuery<Permission[]>({
    queryKey: ['permissions'],
    queryFn: () => apiGet<Permission[]>('/rbac/permissions'),
    enabled: visible,
  })

  // 获取角色当前权限 (从role对象中没有权限信息，需要额外获取或从permissions判断)
  // 这里简化处理，实际应该有API返回角色的权限ID列表

  // 更新角色权限
  const updateMutation = useMutation({
    mutationFn: (permission_ids: number[]) =>
      apiPut(`/rbac/roles/${role.id}/permissions`, { permission_ids }),
    onSuccess: () => {
      message.success('权限配置成功')
      onSuccess()
      onClose()
    },
    onError: (error: any) => {
      message.error(`配置失败: ${error.message}`)
    },
  })

  const handleOk = () => {
    updateMutation.mutate(targetKeys)
  }

  const handleChange: TransferProps['onChange'] = (newTargetKeys) => {
    // 将 Key[] 转换为 number[]
    setTargetKeys(newTargetKeys.map(key => Number(key)))
  }

  const dataSource = permissions?.map((perm) => ({
    key: perm.id,
    title: `${perm.name} (${perm.code})`,
    description: perm.resource_type || '',
  })) || []

  return (
    <Modal
      title={`配置权限 - ${role.name}`}
      open={visible}
      onCancel={onClose}
      onOk={handleOk}
      confirmLoading={updateMutation.isPending}
      width={700}
    >
      <Transfer
        dataSource={dataSource}
        titles={['可选权限', '已分配权限']}
        targetKeys={targetKeys}
        onChange={handleChange}
        render={(item) => item.title}
        listStyle={{
          width: 300,
          height: 400,
        }}
        showSearch
        filterOption={(inputValue, item) =>
          item.title!.toLowerCase().includes(inputValue.toLowerCase())
        }
      />
      {isLoading && <div style={{ textAlign: 'center', padding: '20px' }}>加载中...</div>}
    </Modal>
  )
}

export default ConfigureRolePermissionsModal

