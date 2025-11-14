# AuthHub 架构设计概述

## 系统架构

AuthHub 是一个基于飞书的企业级SSO单点登录和权限配置中心,采用去中心化权限校验架构。

### 核心特点

1. **统一权限管理**: 所有系统的权限在AuthHub中集中配置
2. **去中心化校验**: 业务系统本地校验权限,零网络开销
3. **多命名空间**: 支持全局权限和系统专属权限
4. **实时同步**: 权限变更通过Redis Pub/Sub实时通知

## 架构图

```
┌─────────────────────────────────────────┐
│        AuthHub (统一权限平台)            │
│                                         │
│  - 飞书OAuth2.0登录                     │
│  - JWT Token颁发(RS256)                │
│  - 权限配置管理(全局+各系统)             │
│  - 配置同步API                          │
│  - 权限变更通知(Redis Pub/Sub)          │
└─────────────────────────────────────────┘
          ↓ JWT Token + 配置同步
    ┌──────────────────┐
    │ 业务系统 A/B/C    │
    │                  │
    │ SDK功能:         │
    │ - Token验证(公钥)│
    │ - 权限校验(本地) │
    │ - 配置缓存       │
    │ - 实时通知订阅   │
    └──────────────────┘
```

## 核心组件

### 1. AuthHub后端服务

**技术栈**: FastAPI + SQLAlchemy + PostgreSQL + Redis

**核心功能**:
- 飞书OAuth2.0集成
- JWT Token管理(RS256签名)
- RBAC权限模型
- 系统注册和管理
- 权限配置同步
- 审计日志

### 2. Python SDK

**核心功能**:
- 本地Token验证(使用公钥)
- 本地权限校验(基于缓存配置)
- 配置自动同步
- 权限变更实时通知
- FastAPI/Flask/Django中间件

### 3. TypeScript SDK

**核心功能**:
- 本地Token验证
- 本地权限校验
- React Hooks (useAuth, usePermission, useRole)
- Express/Koa/Next.js中间件

### 4. React管理后台

**核心功能**:
- 系统管理
- 用户管理(跨系统权限视图)
- 角色和权限配置
- 路由规则配置
- 资源绑定管理
- 审计日志查看

## 权限模型

### 命名空间设计

```
global (全局)
  ├── 角色: admin, employee
  └── 资源: project, team, department

system_a (系统A)
  ├── 角色: editor, reviewer
  ├── 权限: document:read, document:write
  ├── 路由规则: /api/v1/documents/*
  └── 资源: document

system_b (系统B)
  ├── 角色: order_admin, finance_viewer
  ├── 权限: order:read, order:write
  └── 资源: order, invoice
```

### JWT Token结构

```json
{
  "sub": "user_id",
  "user_type": "user",
  "username": "张三",
  "global_roles": ["admin"],
  "system_roles": {
    "system_a": ["editor"],
    "system_b": ["viewer"]
  },
  "global_resources": {
    "project": [123, 456],
    "team": [789]
  },
  "system_resources": {
    "system_a": {
      "document": [100, 101]
    }
  },
  "exp": 1734195600,
  "jti": "uuid"
}
```

## 权限校验流程

### 1. 用户登录

```
1. 用户访问 → 重定向到飞书授权页
2. 飞书回调 → AuthHub换取access_token
3. 获取用户信息 → 创建/更新本地用户
4. 收集用户完整权限(全局+各系统)
5. 生成富JWT Token → 返回给用户
```

### 2. 业务请求

```
1. 用户携带JWT Token请求业务系统
2. SDK验证Token签名(使用公钥)
3. SDK检查黑名单(查询Redis,1-2ms)
4. SDK本地校验权限(纯内存计算)
5. 通过 → 执行业务逻辑
   拒绝 → 返回403
```

### 3. 权限变更

```
1. 管理员修改权限配置
2. AuthHub发布消息到Redis
3. 各业务系统订阅并收到通知
4. 业务系统重新拉取配置
5. 更新本地缓存
```

## 性能优化

### 1. 零网络开销

- Token验证: 本地公钥验证
- 权限校验: 本地配置匹配
- 唯一网络调用: Redis黑名单检查(1-2ms)

### 2. 缓存策略

- 本地内存缓存权限配置
- 定期同步(5分钟)
- 实时通知更新

### 3. 高可用

- AuthHub故障不影响业务
- 业务系统继续使用缓存配置
- Token仍可本地验证

## 安全性

### 1. Token安全

- RS256非对称加密
- 短期有效(1小时)
- 支持撤销(黑名单)

### 2. 权限安全

- 细粒度RBAC
- 路由正则匹配
- 资源级权限控制

### 3. 审计

- 完整的权限变更日志
- 用户操作追踪
- IP和User Agent记录

## 部署架构

```
┌─────────────┐
│   Nginx     │ (反向代理)
└─────────────┘
      ↓
┌─────────────┐    ┌─────────────┐
│  AuthHub    │ →  │ PostgreSQL  │
│  (Backend)  │    │  (用户提供) │
└─────────────┘    └─────────────┘
      ↓
┌─────────────┐
│    Redis    │
│  (用户提供) │
└─────────────┘

┌─────────────┐
│   React     │ (管理后台)
│  (Frontend) │
└─────────────┘
```

## 扩展性

### 1. 水平扩展

- AuthHub无状态,可多实例部署
- Redis作为共享缓存
- PostgreSQL支持主从复制

### 2. 系统接入

- 简单注册获取系统Token
- 集成SDK(几行代码)
- 灵活配置权限

### 3. 权限模型扩展

- 支持自定义资源类型
- 支持自定义权限动作
- 支持复杂的路由规则

