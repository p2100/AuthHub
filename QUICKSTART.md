# AuthHub 快速启动指南

## 前置要求

- Python 3.11+
- Node.js 18+
- PostgreSQL 15+ (需自行准备)
- Redis 7+ (需自行准备)

## 快速开始

### 1. 后端启动

```bash
cd backend

# 安装UV (Python包管理器)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 安装依赖
uv pip install -e .

# 配置环境变量
cp .env.example .env
# 编辑.env文件,填写数据库和Redis连接信息

# 生成RSA密钥对
python scripts/generate_keys.py

# 初始化数据库
alembic upgrade head

# 启动服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

访问 API文档: http://localhost:8000/docs

### 2. 前端启动

```bash
cd frontend

# 安装pnpm
npm install -g pnpm

# 安装依赖
pnpm install

# 启动开发服务器
pnpm dev
```

访问管理后台: http://localhost:3000

### 3. Docker部署

```bash
# 确保已配置.env文件中的数据库和Redis连接信息
docker-compose up -d
```

## 系统接入

### 1. 注册系统

访问管理后台 → 系统管理 → 注册新系统

获取系统Token(只显示一次,请妥善保管)

### 2. 集成Python SDK

```bash
pip install -e sdk/python
```

```python
from authhub_sdk import AuthHubClient
from authhub_sdk.middleware.fastapi import AuthHubMiddleware

# 初始化客户端
client = AuthHubClient(
    authhub_url="http://localhost:8000",
    system_id="1",
    system_token="your_system_token",
    namespace="system_a",
    redis_url="redis://localhost:6379/0"
)

# 添加到FastAPI应用
app.add_middleware(AuthHubMiddleware, client=client)
```

### 3. 集成TypeScript SDK

```bash
pnpm add @authhub/sdk
```

```typescript
import { AuthHubClient } from '@authhub/sdk';

const client = new AuthHubClient({
  authhubUrl: 'http://localhost:8000',
  systemId: '1',
  systemToken: 'your_system_token',
  namespace: 'system_a'
});
```

## 权限配置

### 1. 创建角色

访问管理后台 → 角色管理 → 创建角色

选择所属系统(全局或特定系统)

### 2. 配置权限

- 基础权限: 创建权限定义
- 路由规则: 配置正则表达式匹配路由
- 资源绑定: 绑定用户到特定资源(项目/团队等)

### 3. 分配角色

访问管理后台 → 用户管理 → 查看用户 → 分配角色

## 常见问题

### Q: 如何查看用户的完整权限?

A: 访问管理后台 → 用户管理 → 用户详情,可以看到该用户在所有系统中的权限。

### Q: 权限变更后多久生效?

A: 权限变更后会立即通过Redis Pub/Sub通知所有业务系统,系统收到通知后会重新拉取配置,通常在1-2秒内生效。

### Q: Token被撤销后如何处理?

A: Token撤销后会被加入黑名单,所有业务系统在验证Token时都会检查黑名单,被撤销的Token将无法通过验证。

### Q: 如何自定义权限校验逻辑?

A: SDK只提供基础的Token验证和便捷方法,业务系统可以基于Token中的信息自行实现权限校验逻辑。

## 更多文档

- [架构设计](./docs/architecture/overview.md)
- [API文档](http://localhost:8000/docs)
- [Python SDK文档](./sdk/python/README.md)
- [TypeScript SDK文档](./sdk/typescript/README.md)

