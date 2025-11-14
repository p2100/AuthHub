import { Card, Button } from 'antd'
import { WechatOutlined } from '@ant-design/icons'

const Login = () => {
  const handleFeishuLogin = () => {
    // 调用后端API获取飞书授权URL
    const redirectUri = encodeURIComponent(window.location.origin + '/login/callback')
    fetch(`/api/v1/auth/feishu/login?redirect_uri=${redirectUri}`)
      .then(res => res.json())
      .then(data => {
        // 跳转到飞书授权页
        window.location.href = data.auth_url
      })
  }

  return (
    <div style={{ 
      height: '100vh', 
      display: 'flex', 
      alignItems: 'center', 
      justifyContent: 'center',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
    }}>
      <Card title="AuthHub 登录" style={{ width: 400, textAlign: 'center' }}>
        <Button
          type="primary"
          size="large"
          icon={<WechatOutlined />}
          onClick={handleFeishuLogin}
          style={{ width: '100%' }}
        >
          飞书登录
        </Button>
      </Card>
    </div>
  )
}

export default Login

