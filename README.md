# AuthHub - 飞书SSO统一权限平台

基于飞书的企业级SSO单点登录和权限配置中心,采用去中心化权限校验架构,支持多系统权限统一管理。

## ✨ 核心特性

### 统一权限管理
- 🔐 飞书OAuth2.0单点登录
- 👥 用户和组织架构同步
- 🎯 多命名空间权限隔离
- 🌐 跨系统权限统一配置

### 去中心化校验
- ⚡️ 本地权限校验(零网络开销)
- 🎫 富JWT Token(包含完整权限)
- 🚀 高性能(无中心化瓶颈)
- 💪 高可用(AuthHub故障不影响业务)

### 灵活的权限模型
- 🔑 RBAC角色权限管理
- 📝 路由正则匹配规则
- 🔗 灵活的资源绑定
- 🌍 全局权限 + 系统专属权限

### 全面的SDK支持
- 🐍 Python SDK (FastAPI/Flask/Django)
- 📘 TypeScript SDK (React/Express/Next.js)
- 🎨 React Hooks
- ⚙️ 开箱即用的中间件

## 🏗️ 架构设计

```
┌─────────────────────────────────────┐
│     AuthHub 统一权限平台             │
│  - 飞书登录                          │
│  - 权限配置管理(全局+各系统)         │
│  - JWT Token颁发                    │
│  - 配置同步API                      │
└─────────────────────────────────────┘
          ↓ JWT Token + 配置同步
    ┌──────────────────┐
    │ 业务系统 A/B/C    │
    │ - SDK本地验证Token│
    │ - SDK本地校验权限 │
    │ - 零网络开销      │
    └──────────────────┘
```

## 📦 项目结构

```
AuthHub/
├── backend/       # Python后端服务
├── frontend/      # React管理后台
├── sdk/           # SDK包
│   ├── python/    # Python SDK
│   └── typescript/ # TypeScript SDK
├── docs/          # 文档
└── docker/        # Docker配置
```

## 🚀 快速开始

### 前置要求

- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Redis 7+
- UV (Python包管理器)
- pnpm (Node.js包管理器)

### 1. 克隆项目

```bash
git clone https://github.com/your-org/AuthHub.git
cd AuthHub
```

### 2. 后端启动

```bash
cd backend

# 安装UV
curl -LsSf https://astral.sh/uv/install.sh | sh

# 安装依赖
uv sync

# 配置环境变量
cp .env.example .env
# 编辑.env,填写配置

# 生成RSA密钥对
python scripts/generate_keys.py

# 初始化数据库
uv run alembic upgrade head

# 启动服务
uvicorn app.main:app --reload
```

访问 http://localhost:8000/docs 查看API文档

### 3. 前端启动

```bash
cd frontend

# 安装pnpm
npm install -g pnpm

# 安装依赖
pnpm install

# 启动开发服务器
pnpm dev
```

访问 http://localhost:3000

### 4. Docker部署

```bash
docker-compose up -d
```

## 🚀 SDK 快速开始

### Python SDK

#### 安装

```bash
# 基础安装
pip install authhub-sdk

# 包含FastAPI支持
pip install authhub-sdk[fastapi]

# 包含Flask支持
pip install authhub-sdk[flask]
```

#### FastAPI 集成(SSO登录)

```python
from fastapi import FastAPI, Request
from authhub_sdk import AuthHubClient
from authhub_sdk.middleware.fastapi_sso import setup_sso

app = FastAPI()

# 初始化客户端
client = AuthHubClient(
    authhub_url="http://localhost:8000",
    system_id="your_system_id",
    system_token="your_system_token",
    namespace="system_a",
    redis_url="redis://localhost:6379"
)

# 一行代码集成SSO登录！
setup_sso(
    app,
    client=client,
    login_required=True,
    public_routes=['/health', '/docs']
)

@app.get("/dashboard")
async def dashboard(request: Request):
    user = request.state.user  # 自动注入用户信息
    return {"user": user.get("username")}
```

**自动提供的路由:**
- `GET /auth/login` - 触发SSO登录
- `GET /auth/callback` - SSO回调处理
- `GET/POST /auth/logout` - 登出

更多示例: [sdk/python/examples](./sdk/python/examples)

### TypeScript SDK

#### 安装

```bash
npm install @authhub/sdk
# 或
yarn add @authhub/sdk
```

#### React 集成

```typescript
import { AuthHubProvider, useAuthHub } from '@authhub/sdk/react';

function App() {
  return (
    <AuthHubProvider
      config={{
        authhubUrl: 'http://localhost:8000',
        systemId: 'your_system_id',
        systemToken: 'your_system_token',
        namespace: 'system_a'
      }}
    >
      <Dashboard />
    </AuthHubProvider>
  );
}

function Dashboard() {
  const { user, login, logout, checkPermission } = useAuthHub();

  if (!user) {
    return <button onClick={login}>登录</button>;
  }

  return (
    <div>
      <h1>欢迎, {user.username}</h1>
      <button onClick={logout}>登出</button>
      {checkPermission('document', 'write') && (
        <button>创建文档</button>
      )}
    </div>
  );
}
```

更多示例: [sdk/typescript/examples](./sdk/typescript/examples)

## 📖 文档

- [架构设计](./docs/architecture/overview.md)
- [API文档](./backend/app)
- [Python SDK示例](./sdk/python/examples)
- [TypeScript SDK示例](./sdk/typescript/examples)
- [系统接入指南](./docs/user-guide/system-registration.md)

## 🔧 技术栈

### 后端
- FastAPI
- SQLAlchemy 2.0
- PostgreSQL
- Redis
- PyJWT (RS256)
- Alembic

### 前端
- React 18 + TypeScript
- Ant Design 5
- Zustand + React Query
- Vite

### SDK
- Python: PyJWT, redis, requests
- TypeScript: jose, ioredis, axios

## 📝 许可证

MIT License

## 🤝 贡献

欢迎贡献代码!请查看 [CONTRIBUTING.md](./CONTRIBUTING.md)

## 📮 联系方式

- Issue: https://github.com/your-org/AuthHub/issues
- Email: support@yourcompany.com

