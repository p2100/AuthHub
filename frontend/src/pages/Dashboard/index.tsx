import { Card, Col, Row, Statistic, Spin, Alert } from 'antd'
import { UserOutlined, CloudServerOutlined, SafetyOutlined } from '@ant-design/icons'
import { useQuery } from '@tanstack/react-query'
import { apiGet } from '@/utils/api'
import type { StatsResponse } from '@/types/api'

const Dashboard = () => {
  // 使用react-query获取统计数据
  const { data: stats, isLoading, error } = useQuery<StatsResponse>({
    queryKey: ['stats'],
    queryFn: () => apiGet<StatsResponse>('/rbac/stats'),
  })

  // 加载中状态
  if (isLoading) {
    return (
      <div>
        <h1>仪表盘</h1>
        <div style={{ textAlign: 'center', marginTop: 100 }}>
          <Spin size="large" tip="加载统计数据中..." />
        </div>
      </div>
    )
  }

  // 错误状态
  if (error) {
    return (
      <div>
        <h1>仪表盘</h1>
        <Alert
          message="加载失败"
          description={error instanceof Error ? error.message : '获取统计数据失败'}
          type="error"
          showIcon
          style={{ marginTop: 24 }}
        />
      </div>
    )
  }

  return (
    <div>
      <h1>仪表盘</h1>
      <Row gutter={16} style={{ marginTop: 24 }}>
        <Col span={8}>
          <Card>
            <Statistic
              title="接入系统"
              value={stats?.system_count ?? 0}
              prefix={<CloudServerOutlined />}
              valueStyle={{ color: '#3f8600' }}
            />
          </Card>
        </Col>
        <Col span={8}>
          <Card>
            <Statistic
              title="用户总数"
              value={stats?.user_count ?? 0}
              prefix={<UserOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col span={8}>
          <Card>
            <Statistic
              title="角色数量"
              value={stats?.role_count ?? 0}
              prefix={<SafetyOutlined />}
              valueStyle={{ color: '#cf1322' }}
            />
          </Card>
        </Col>
      </Row>
    </div>
  )
}

export default Dashboard

