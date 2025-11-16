import { Modal, Spin, Descriptions, Tag, Collapse, Typography } from 'antd'
import { useQuery } from '@tanstack/react-query'
import { apiGet } from '@/utils/api'
import type { UserPermissionDetail } from '@/types/api'

const { Panel } = Collapse
const { Text } = Typography

interface UserPermissionModalProps {
  visible: boolean
  userId: number
  username: string
  onClose: () => void
}

const UserPermissionModal = ({ visible, userId, username, onClose }: UserPermissionModalProps) => {
  const { data, isLoading } = useQuery<UserPermissionDetail>({
    queryKey: ['user-permissions', userId],
    queryFn: () => apiGet<UserPermissionDetail>(`/users/${userId}/permissions`),
    enabled: visible,
  })

  return (
    <Modal
      title={`用户权限详情 - ${username}`}
      open={visible}
      onCancel={onClose}
      footer={null}
      width={800}
    >
      <Spin spinning={isLoading}>
        {data && (
          <div>
            {/* 角色列表 */}
            <Descriptions title="分配的角色" bordered column={1} style={{ marginBottom: 24 }}>
              <Descriptions.Item label="角色">
                {data.roles.length > 0 ? (
                  <div>
                    {data.roles.map((role) => (
                      <Tag key={role.role_id} color="blue" style={{ marginBottom: 8 }}>
                        {role.role_name} ({role.namespace})
                      </Tag>
                    ))}
                  </div>
                ) : (
                  <Text type="secondary">暂无角色</Text>
                )}
              </Descriptions.Item>
            </Descriptions>

            {/* 全局角色 */}
            {data.global_roles.length > 0 && (
              <Descriptions title="全局角色" bordered column={1} style={{ marginBottom: 24 }}>
                <Descriptions.Item label="角色代码">
                  {data.global_roles.map((role, index) => (
                    <Tag key={index} color="green">
                      {role}
                    </Tag>
                  ))}
                </Descriptions.Item>
              </Descriptions>
            )}

            {/* 系统角色 */}
            {Object.keys(data.system_roles).length > 0 && (
              <Collapse style={{ marginBottom: 24 }}>
                <Panel header="系统角色" key="system-roles">
                  {Object.entries(data.system_roles).map(([system, roles]) => (
                    <div key={system} style={{ marginBottom: 8 }}>
                      <Text strong>{system}:</Text>{' '}
                      {roles.map((role, index) => (
                        <Tag key={index} color="blue">
                          {role}
                        </Tag>
                      ))}
                    </div>
                  ))}
                </Panel>
              </Collapse>
            )}

            {/* 全局资源 */}
            {Object.keys(data.global_resources).length > 0 && (
              <Collapse style={{ marginBottom: 24 }}>
                <Panel header="全局资源绑定" key="global-resources">
                  {Object.entries(data.global_resources).map(([resourceType, ids]) => (
                    <div key={resourceType} style={{ marginBottom: 8 }}>
                      <Text strong>{resourceType}:</Text>{' '}
                      {ids.map((id, index) => (
                        <Tag key={index}>{id}</Tag>
                      ))}
                    </div>
                  ))}
                </Panel>
              </Collapse>
            )}

            {/* 系统资源 */}
            {Object.keys(data.system_resources).length > 0 && (
              <Collapse>
                <Panel header="系统资源绑定" key="system-resources">
                  {Object.entries(data.system_resources).map(([system, resources]) => (
                    <div key={system} style={{ marginBottom: 16 }}>
                      <Text strong style={{ fontSize: 16 }}>
                        {system}
                      </Text>
                      {Object.entries(resources).map(([resourceType, ids]) => (
                        <div key={resourceType} style={{ marginLeft: 16, marginTop: 8 }}>
                          <Text strong>{resourceType}:</Text>{' '}
                          {ids.map((id, index) => (
                            <Tag key={index}>{id}</Tag>
                          ))}
                        </div>
                      ))}
                    </div>
                  ))}
                </Panel>
              </Collapse>
            )}

            {/* 无权限提示 */}
            {data.roles.length === 0 &&
              data.global_roles.length === 0 &&
              Object.keys(data.system_roles).length === 0 &&
              Object.keys(data.global_resources).length === 0 &&
              Object.keys(data.system_resources).length === 0 && (
                <Text type="secondary">该用户暂无任何权限</Text>
              )}
          </div>
        )}
      </Spin>
    </Modal>
  )
}

export default UserPermissionModal

