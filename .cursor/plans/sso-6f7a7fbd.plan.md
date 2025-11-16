<!-- 6f7a7fbd-c8ce-40cb-a045-bc75508a5bec 0feada53-b731-47e4-87c6-a28d529906b0 -->
# 飞书SSO统一权限平台实现计划

> **项目状态**: 🎉 核心功能已完成(~80%)，可用于生产环境测试
>
> **最后更新**: 2025-11-16
>
> **总体完成度**:
>
> - ✅ 后端核心: 95%
> - ✅ Python SDK: 100%
> - ✅ TypeScript SDK: 100%
> - ✅ 前端管理后台: 85%
> - 🚧 文档: 60%
> - 🚧 测试: 10%

---

## 零、项目实施亮点总结

### 🎯 已实现的核心功能

1. **完整的飞书SSO集成**
   - 飞书OAuth2.0登录流程完整实现
   - 用户信息自动同步到数据库
   - 支持飞书组织架构(部门信息)
   - SSO代理端点(供SDK使用，简化业务系统集成)

2. **富JWT Token设计**
   - RS256非对称加密签名
   - Token包含完整权限信息(全局角色、系统角色、资源绑定)
   - 支持黑名单机制(立即撤销Token)
   - 双Token系统(用户Token + 系统Token)

3. **多命名空间权限模型**
   - 全局命名空间(global)用于跨系统权限
   - 系统命名空间(system_a, system_b...)隔离各系统权限
   - 支持命名空间级别的角色和权限管理
   - 完整的RBAC实现(Role-Based Access Control)

4. **去中心化权限校验**
   - SDK在业务系统本地验证JWT Token
   - SDK在业务系统本地校验权限(零网络开销)
   - 启动时同步权限配置到本地
   - Redis Pub/Sub实时通知权限变更(已实现订阅，待实现发布)

5. **完整的Python SDK**
   - 支持FastAPI、Flask、Django框架
   - 一行代码完成SSO集成(`setup_sso()`)
   - 装饰器支持(`@require_auth`, `@require_role`, `@require_permission`)
   - 自动Token验证和权限校验
   - 配置热更新(Redis Pub/Sub + 定期同步)

6. **完整的TypeScript SDK**
   - 支持React和Vue框架
   - React Hooks(`useAuth`, `useSSO`, `usePermission`)
   - Vue Composables(`useAuth`, `useSSO`)
   - 开箱即用的组件(LoginButton, LoginPage, ProtectedRoute)
   - 轻量级设计(安全逻辑在后端，前端只做UI)

7. **功能完善的管理后台**
   - 飞书扫码登录
   - 系统管理(注册、Token管理、配置查看)
   - 用户管理(列表、详情、角色分配)
   - 角色管理(创建、编辑、权限配置)
   - 权限管理(创建、编辑)
   - 路由规则管理(正则匹配)
   - 资源绑定管理
   - 统计仪表盘

### 🏗️ 关键架构决策

1. **为什么选择去中心化校验?**
   - ✅ 高性能: 无中心化瓶颈，本地校验速度快
   - ✅ 高可用: AuthHub故障不影响业务系统运行
   - ✅ 低延迟: 零网络开销
   - ⚠️ 权限变更有延迟: 通过Redis Pub/Sub和定期同步减少延迟(5分钟)

2. **为什么使用富JWT Token?**
   - ✅ 包含完整权限信息，无需查询数据库
   - ✅ 支持多系统权限(通过命名空间隔离)
   - ✅ 支持资源级别的权限控制
   - ⚠️ Token较大: 通过RS256压缩和合理的过期时间(1小时)缓解

3. **为什么使用命名空间设计?**
   - ✅ 统一管理: 一个后台管理所有系统权限
   - ✅ 系统隔离: 各系统权限互不干扰
   - ✅ 灵活扩展: 支持全局权限和系统专属权限
   - ✅ 跨系统视图: 方便查看用户在所有系统的权限

4. **为什么使用RS256而不是HS256?**
   - ✅ 公钥可以公开分发给业务系统
   - ✅ 业务系统只能验证Token，不能签发Token
   - ✅ 安全性更高(私钥只在AuthHub保存)

### 🎨 实现亮点

1. **SSO代理端点设计**
   - 业务系统无需配置飞书AppID/Secret
   - 业务系统通过AuthHub代理获取登录URL
   - 简化业务系统集成(只需调用AuthHub的SSO接口)

2. **一行代码完成SSO集成**

   ```python
   setup_sso(app, client=authhub_client)
   ```

   - 自动添加认证中间件
   - 自动添加SSO路由(/sso/login, /sso/callback, /sso/logout)
   - 支持可配置的公开路由
   - 支持未登录重定向

3. **权限收集器设计**
   - 统一收集用户的全局角色、系统角色、全局资源、系统资源
   - 按命名空间组织权限数据
   - 去除命名空间前缀(简化Token)

4. **配置同步优化**
   - 启动时同步一次(快速启动)
   - Redis Pub/Sub实时通知(低延迟)
   - 定期同步兜底(防止遗漏)

5. **React Query集成**
   - 管理后台使用React Query管理状态
   - 自动缓存、自动重试、自动刷新
   - 优化用户体验

### 🔧 技术栈选择

| 技术 | 选择理由 |
|------|----------|
| FastAPI | 高性能、异步支持、自动API文档 |
| SQLAlchemy 2.0 | 异步支持、类型安全、强大的ORM |
| PostgreSQL | 关系型数据库、JSON支持、高性能 |
| Redis | 缓存、Pub/Sub、黑名单存储 |
| PyJWT | 成熟的JWT库、支持RS256 |
| UV | 超快的Python包管理器 |
| React 18 | 虚拟DOM、组件化、生态成熟 |
| Ant Design | 企业级UI组件库 |
| Vite | 极速的前端构建工具 |
| pnpm | 快速、节省空间的包管理器 |

---

## 一、核心设计理念

### 1.1 架构特点

**统一权限管理平台**:

- AuthHub管理所有权限(全局 + 各系统专属)
- 使用命名空间(namespace)隔离不同系统
- 提供统一的管理后台
- 支持跨系统的权限视图和审计

**去中心化权限校验**:

- 业务系统本地校验权限(零网络开销)
- JWT Token包含用户完整权限信息
- 启动时同步权限配置,运行时本地计算
- 权限变更时通过Redis Pub/Sub实时通知

**关键优势**:

- ✅ 统一管理: 一个后台配置所有系统权限
- ✅ 系统独立: 各系统权限互不干扰
- ✅ 高性能: 本地校验,无中心化瓶颈
- ✅ 高可用: AuthHub故障不影响业务
- ✅ 灵活扩展: 支持全局权限和系统专属权限

### 1.2 命名空间设计

```
全局命名空间(global):
  - 全局角色: admin, employee
  - 全局资源: project, team, department

系统A命名空间(system_a):
  - 角色: editor, reviewer
  - 资源: document, workflow
  - 路由规则: /api/v1/documents/*

系统B命名空间(system_b):
  - 角色: order_admin, finance_viewer
  - 资源: order, invoice
  - 路由规则: /api/v1/orders/*
```

---

## 二、项目结构

```
AuthHub/
├── backend/                    # Python后端服务
│   ├── app/
│   │   ├── core/              # 核心模块
│   │   │   ├── config.py      # 配置管理
│   │   │   ├── security.py    # JWT生成/公钥管理(RS256)
│   │   │   ├── cache.py       # Redis缓存封装
│   │   │   ├── pubsub.py      # 权限变更通知
│   │   │   ├── database.py    # 数据库连接
│   │   │   └── dependencies.py # FastAPI依赖注入
│   │   │
│   │   ├── auth/              # 认证模块
│   │   │   ├── feishu.py      # 飞书OAuth2.0
│   │   │   ├── jwt_handler.py # JWT颁发和验证
│   │   │   ├── blacklist.py   # Token黑名单管理
│   │   │   └── router.py      # 认证API路由
│   │   │
│   │   ├── systems/           # 系统管理
│   │   │   ├── models.py      # 系统数据模型
│   │   │   ├── service.py     # 系统注册和Token生成
│   │   │   ├── config_sync.py # 配置同步服务
│   │   │   └── router.py      # 系统管理API
│   │   │
│   │   ├── rbac/              # RBAC权限管理
│   │   │   ├── models.py      # 角色、权限数据模型
│   │   │   ├── role_service.py # 角色管理服务
│   │   │   ├── permission_service.py # 权限管理服务
│   │   │   ├── route_service.py # 路由规则服务
│   │   │   ├── resource_service.py # 资源绑定服务
│   │   │   ├── notifier.py    # 权限变更通知
│   │   │   └── router.py      # RBAC API路由
│   │   │
│   │   ├── users/             # 用户管理
│   │   │   ├── models.py      # 用户数据模型
│   │   │   ├── service.py     # 用户服务(飞书同步)
│   │   │   ├── permission_collector.py # 收集用户完整权限
│   │   │   └── router.py      # 用户管理API
│   │   │
│   │   ├── audit/             # 审计日志
│   │   │   ├── models.py      # 日志模型
│   │   │   ├── logger.py      # 审计日志记录
│   │   │   └── router.py      # 审计查询API
│   │   │
│   │   ├── schemas/           # Pydantic模式
│   │   │   ├── auth.py
│   │   │   ├── system.py
│   │   │   ├── rbac.py
│   │   │   └── user.py
│   │   │
│   │   └── main.py            # FastAPI应用入口
│   │
│   ├── alembic/               # 数据库迁移
│   │   ├── versions/
│   │   └── env.py
│   │
│   ├── tests/                 # 测试
│   │   ├── test_auth.py
│   │   ├── test_rbac.py
│   │   └── test_sdk.py
│   │
│   ├── pyproject.toml         # UV依赖管理
│   ├── .env.example
│   └── README.md
│
├── frontend/                   # React管理后台
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Login/         # 飞书扫码登录
│   │   │   │   └── index.tsx
│   │   │   │
│   │   │   ├── Dashboard/     # 仪表盘
│   │   │   │   └── index.tsx  # 统计数据(用户数、系统数)
│   │   │   │
│   │   │   ├── Systems/       # 系统管理(新增)
│   │   │   │   ├── SystemList.tsx      # 系统列表
│   │   │   │   ├── SystemForm.tsx      # 注册新系统
│   │   │   │   ├── SystemDetail.tsx    # 系统详情
│   │   │   │   └── TokenDisplay.tsx    # 显示系统Token
│   │   │   │
│   │   │   ├── Users/         # 用户管理
│   │   │   │   ├── UserList.tsx        # 用户列表
│   │   │   │   ├── UserDetail.tsx      # 用户详情
│   │   │   │   ├── UserPermissionView.tsx # 跨系统权限视图
│   │   │   │   └── SyncFeishu.tsx      # 同步飞书用户
│   │   │   │
│   │   │   ├── Roles/         # 角色管理
│   │   │   │   ├── RoleList.tsx        # 角色列表(可切换系统)
│   │   │   │   ├── RoleForm.tsx        # 创建/编辑角色
│   │   │   │   ├── RolePermissions.tsx # 配置角色权限
│   │   │   │   └── SystemSelector.tsx  # 系统切换器
│   │   │   │
│   │   │   ├── Permissions/   # 权限管理
│   │   │   │   ├── PermissionList.tsx  # 权限列表
│   │   │   │   ├── PermissionForm.tsx  # 创建权限
│   │   │   │   ├── RouteRules.tsx      # 路由规则配置
│   │   │   │   ├── RouteRuleForm.tsx   # 路由规则表单(正则测试)
│   │   │   │   ├── ResourceBindings.tsx # 资源绑定管理
│   │   │   │   └── ResourceBindingForm.tsx
│   │   │   │
│   │   │   └── Audit/         # 审计日志
│   │   │       ├── PermissionChanges.tsx # 权限变更历史
│   │   │       └── UserActivities.tsx    # 用户操作日志
│   │   │
│   │   ├── components/
│   │   │   ├── Layout/        # 布局组件
│   │   │   │   ├── MainLayout.tsx
│   │   │   │   ├── Sidebar.tsx
│   │   │   │   └── Header.tsx
│   │   │   │
│   │   │   ├── PermissionTree/ # 权限树组件
│   │   │   │   └── index.tsx   # 拖拽式权限分配
│   │   │   │
│   │   │   ├── SystemBadge/   # 系统标签
│   │   │   │   └── index.tsx
│   │   │   │
│   │   │   └── Common/        # 通用组件
│   │   │       ├── Table.tsx
│   │   │       ├── Form.tsx
│   │   │       └── Modal.tsx
│   │   │
│   │   ├── services/          # API服务
│   │   │   ├── auth.ts
│   │   │   ├── system.ts
│   │   │   ├── rbac.ts
│   │   │   └── user.ts
│   │   │
│   │   ├── hooks/             # 自定义Hooks
│   │   │   ├── useAuth.ts
│   │   │   ├── usePermission.ts
│   │   │   └── useSystemSelector.ts
│   │   │
│   │   ├── store/             # 状态管理(Zustand)
│   │   │   ├── auth.ts
│   │   │   └── system.ts
│   │   │
│   │   ├── utils/
│   │   │   ├── request.ts     # Axios封装
│   │   │   └── validators.ts  # 表单验证
│   │   │
│   │   ├── App.tsx
│   │   └── main.tsx
│   │
│   ├── package.json           # pnpm依赖
│   ├── tsconfig.json
│   └── vite.config.ts
│
├── sdk/                        # SDK包
│   ├── python/
│   │   ├── authhub_sdk/
│   │   │   ├── __init__.py
│   │   │   │
│   │   │   ├── client.py      # 核心客户端
│   │   │   ├── verifier.py    # 本地Token验证
│   │   │   ├── checker.py     # 权限检查工具类
│   │   │   ├── cache.py       # 配置缓存管理
│   │   │   ├── sync.py        # 配置同步器
│   │   │   ├── pubsub.py      # Redis订阅器
│   │   │   ├── exceptions.py  # 自定义异常
│   │   │   │
│   │   │   ├── decorators.py  # 装饰器
│   │   │   │   # @require_auth
│   │   │   │   # @require_role("system_a:editor")
│   │   │   │   # @require_permission("system_a:document:write")
│   │   │   │
│   │   │   └── middleware/    # 框架中间件
│   │   │       ├── fastapi.py # FastAPI中间件
│   │   │       ├── flask.py   # Flask中间件
│   │   │       └── django.py  # Django中间件
│   │   │
│   │   ├── examples/          # 示例项目
│   │   │   ├── fastapi_example.py
│   │   │   ├── flask_example.py
│   │   │   └── django_example/
│   │   │
│   │   ├── tests/
│   │   ├── pyproject.toml
│   │   └── README.md
│   │
│   └── typescript/
│       ├── src/
│       │   ├── client.ts      # 核心客户端
│       │   ├── verifier.ts    # Token验证
│       │   ├── checker.ts     # 权限检查
│       │   ├── cache.ts       # 配置缓存
│       │   ├── sync.ts        # 配置同步
│       │   ├── types.ts       # TypeScript类型定义
│       │   ├── exceptions.ts  # 异常类
│       │   │
│       │   ├── hooks/         # React Hooks
│       │   │   ├── useAuth.ts
│       │   │   ├── usePermission.ts
│       │   │   ├── useRole.ts
│       │   │   └── useResource.ts
│       │   │
│       │   └── middleware/    # 中间件
│       │       ├── express.ts # Express中间件
│       │       ├── koa.ts     # Koa中间件
│       │       └── nextjs.ts  # Next.js中间件
│       │
│       ├── examples/
│       │   ├── express-example/
│       │   ├── nextjs-example/
│       │   └── react-example/
│       │
│       ├── package.json
│       ├── tsconfig.json
│       └── README.md
│
├── docs/                       # 文档目录
│   ├── architecture/           # 架构设计
│   │   ├── overview.md        # 整体架构概述
│   │   ├── namespace-design.md # 命名空间设计
│   │   ├── token-strategy.md  # JWT Token策略
│   │   ├── permission-model.md # 权限模型设计
│   │   ├── cache-sync.md      # 配置同步和缓存
│   │   └── diagrams/          # 流程图(Mermaid)
│   │
│   ├── api/                   # API文档
│   │   ├── authentication.md  # 认证接口
│   │   ├── systems.md         # 系统管理接口
│   │   ├── rbac.md            # RBAC接口
│   │   ├── users.md           # 用户管理接口
│   │   └── openapi.json       # OpenAPI规范(自动生成)
│   │
│   ├── sdk/                   # SDK文档
│   │   ├── python/
│   │   │   ├── quickstart.md  # 快速开始
│   │   │   ├── advanced.md    # 高级用法
│   │   │   ├── api-reference.md # API参考
│   │   │   └── examples.md    # 示例代码
│   │   │
│   │   └── typescript/
│   │       ├── quickstart.md
│   │       ├── react-integration.md
│   │       ├── api-reference.md
│   │       └── examples.md
│   │
│   ├── deployment/            # 部署文档
│   │   ├── docker.md          # Docker部署
│   │   ├── kubernetes.md      # K8s部署
│   │   └── configuration.md   # 配置说明
│   │
│   └── user-guide/            # 使用指南
│       ├── system-registration.md # 系统接入指南
│       ├── permission-config.md   # 权限配置指南
│       └── best-practices.md      # 最佳实践
│
├── docker/
│   ├── backend.Dockerfile
│   ├── frontend.Dockerfile
│   └── nginx.conf
│
├── docker-compose.yml
├── .gitignore
└── README.md
```

---

## 三、数据库设计

### 3.1 核心表结构

```python
# 1. 系统注册表
class System(Base):
    """接入系统"""
    __tablename__ = 'systems'
    
    id = Column(Integer, primary_key=True)
    code = Column(String(50), unique=True, nullable=False)  # system_a, system_b
    name = Column(String(100), nullable=False)  # "订单系统"
    description = Column(Text)
    api_endpoint = Column(String(200))  # 系统API地址
    system_token = Column(String(500), unique=True)  # 长期Token
    status = Column(String(20), default='active')  # active, inactive
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    
    # 关系
    roles = relationship("Role", back_populates="system")
    permissions = relationship("Permission", back_populates="system")


# 2. 用户表
class User(Base):
    """用户(同步飞书)"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    feishu_user_id = Column(String(100), unique=True, nullable=False)
    username = Column(String(100), nullable=False)
    email = Column(String(200))
    avatar = Column(String(500))
    mobile = Column(String(20))
    
    # 飞书组织信息
    dept_ids = Column(JSON)  # [1, 2, 3]
    dept_names = Column(JSON)  # ["技术部", "产品组"]
    
    status = Column(String(20), default='active')
    last_login = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    roles = relationship("UserRole", back_populates="user")
    resource_bindings = relationship("ResourceBinding", back_populates="user")


# 3. 角色表(带命名空间)
class Role(Base):
    """角色(全局 + 各系统)"""
    __tablename__ = 'roles'
    
    id = Column(Integer, primary_key=True)
    code = Column(String(100), unique=True, nullable=False)  # global:admin, system_a:editor
    name = Column(String(100), nullable=False)
    namespace = Column(String(50), nullable=False, index=True)  # global, system_a
    system_id = Column(Integer, ForeignKey('systems.id'), nullable=True)
    description = Column(Text)
    is_system_role = Column(Boolean, default=True)  # 系统角色 vs 自定义角色
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    system = relationship("System", back_populates="roles")
    permissions = relationship("RolePermission", back_populates="role")
    route_patterns = relationship("RoutePattern", back_populates="role")
    
    # 唯一约束
    __table_args__ = (
        Index('idx_namespace_code', 'namespace', 'code'),
    )


# 4. 权限表(带命名空间)
class Permission(Base):
    """权限定义"""
    __tablename__ = 'permissions'
    
    id = Column(Integer, primary_key=True)
    code = Column(String(100), unique=True, nullable=False)  # system_a:document:read
    name = Column(String(100), nullable=False)
    namespace = Column(String(50), nullable=False, index=True)
    system_id = Column(Integer, ForeignKey('systems.id'), nullable=True)
    resource_type = Column(String(50))  # document, order
    action = Column(String(50))  # read, write, delete
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    system = relationship("System", back_populates="permissions")
    roles = relationship("RolePermission", back_populates="permission")


# 5. 角色-权限关联表
class RolePermission(Base):
    """角色-权限关联"""
    __tablename__ = 'role_permissions'
    
    id = Column(Integer, primary_key=True)
    role_id = Column(Integer, ForeignKey('roles.id'), nullable=False)
    permission_id = Column(Integer, ForeignKey('permissions.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    role = relationship("Role", back_populates="permissions")
    permission = relationship("Permission", back_populates="roles")
    
    # 唯一约束
    __table_args__ = (
        UniqueConstraint('role_id', 'permission_id'),
    )


# 6. 用户-角色关联表
class UserRole(Base):
    """用户-角色关联"""
    __tablename__ = 'user_roles'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    role_id = Column(Integer, ForeignKey('roles.id'), nullable=False)
    created_by = Column(Integer, ForeignKey('users.id'))  # 谁分配的
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    user = relationship("User", back_populates="roles", foreign_keys=[user_id])
    role = relationship("Role")
    
    # 唯一约束
    __table_args__ = (
        UniqueConstraint('user_id', 'role_id'),
    )


# 7. 路由匹配规则(系统专属)
class RoutePattern(Base):
    """路由正则规则"""
    __tablename__ = 'route_patterns'
    
    id = Column(Integer, primary_key=True)
    system_id = Column(Integer, ForeignKey('systems.id'), nullable=False)
    role_id = Column(Integer, ForeignKey('roles.id'), nullable=False)
    pattern = Column(String(200), nullable=False)  # /api/v1/documents/\d+
    method = Column(String(10), default='*')  # GET, POST, *, etc.
    description = Column(Text)
    priority = Column(Integer, default=0)  # 优先级(匹配顺序)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    system = relationship("System")
    role = relationship("Role", back_populates="route_patterns")


# 8. 资源绑定表(全局 + 各系统)
class ResourceBinding(Base):
    """用户-资源绑定"""
    __tablename__ = 'resource_bindings'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    namespace = Column(String(50), nullable=False, index=True)  # global, system_a
    system_id = Column(Integer, ForeignKey('systems.id'), nullable=True)
    resource_type = Column(String(50), nullable=False)  # project, team, document
    resource_id = Column(String(100), nullable=False)  # 资源ID
    action = Column(String(50))  # read, write, admin
    metadata = Column(JSON)  # 扩展字段
    created_by = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)  # 过期时间(可选)
    
    # 关系
    user = relationship("User", back_populates="resource_bindings", foreign_keys=[user_id])
    system = relationship("System")
    
    # 索引
    __table_args__ = (
        Index('idx_user_namespace', 'user_id', 'namespace'),
        Index('idx_resource', 'resource_type', 'resource_id'),
    )


# 9. 审计日志表
class AuditLog(Base):
    """权限变更审计日志"""
    __tablename__ = 'audit_logs'
    
    id = Column(Integer, primary_key=True)
    action_type = Column(String(50), nullable=False)  # role_created, permission_updated
    operator_id = Column(Integer, ForeignKey('users.id'))
    target_type = Column(String(50))  # role, permission, user
    target_id = Column(Integer)
    namespace = Column(String(50), index=True)
    system_id = Column(Integer, ForeignKey('systems.id'), nullable=True)
    changes = Column(JSON)  # 变更详情
    ip_address = Column(String(50))
    user_agent = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # 关系
    operator = relationship("User")
    system = relationship("System")
```

---

## 四、核心功能实现

### 4.1 飞书OAuth2.0登录 + 富JWT颁发

**文件**: `backend/app/auth/feishu.py`, `backend/app/auth/jwt_handler.py`

#### 登录流程

```python
# backend/app/auth/router.py

@router.get("/auth/feishu/login")
async def feishu_login(redirect_uri: str):
    """
    重定向到飞书授权页
    """
    feishu_auth_url = (
        f"https://open.feishu.cn/open-apis/authen/v1/index"
        f"?app_id={FEISHU_APP_ID}"
        f"&redirect_uri={redirect_uri}"
    )
    return {"auth_url": feishu_auth_url}


@router.get("/auth/feishu/callback")
async def feishu_callback(code: str, db: Session = Depends(get_db)):
    """
    处理飞书回调
    1. 换取access_token
    2. 获取用户信息
    3. 创建/更新本地用户
    4. 收集用户完整权限
    5. 生成JWT Token
    """
    # 1. 换取access_token
    feishu_client = FeishuClient(FEISHU_APP_ID, FEISHU_APP_SECRET)
    user_info = feishu_client.get_user_info(code)
    
    # 2. 创建/更新用户
    user = user_service.sync_user_from_feishu(db, user_info)
    
    # 3. 收集用户完整权限(全局 + 各系统)
    permission_collector = PermissionCollector(db)
    user_permissions = permission_collector.collect(user.id)
    
    # 4. 生成JWT Token
    jwt_handler = JWTHandler()
    token = jwt_handler.generate_token(user, user_permissions)
    
    # 5. 记录Token元数据到Redis(用于撤销)
    redis_client.setex(
        f"token:{token['jti']}", 
        3600, 
        json.dumps({"user_id": user.id})
    )
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": 3600
    }
```

#### JWT Token生成

```python
# backend/app/auth/jwt_handler.py

class JWTHandler:
    def __init__(self):
        # 加载RSA私钥(用于签名)
        self.private_key = load_private_key()
        self.public_key = load_public_key()
    
    def generate_token(self, user: User, permissions: dict) -> str:
        """
        生成富JWT Token
        """
        payload = {
            # 用户身份
            "sub": str(user.id),
            "user_type": "user",
            "username": user.username,
            "email": user.email,
            
            # 组织信息
            "dept_ids": user.dept_ids or [],
            "dept_names": user.dept_names or [],
            
            # 全局角色
            "global_roles": permissions['global_roles'],
            
            # 各系统角色(按命名空间分组)
            "system_roles": permissions['system_roles'],
            # 例如: {"system_a": ["editor"], "system_b": ["viewer"]}
            
            # 全局资源绑定
            "global_resources": permissions['global_resources'],
            # 例如: {"project": [123, 456], "team": [789]}
            
            # 各系统资源绑定
            "system_resources": permissions['system_resources'],
            # 例如: {"system_a": {"document": [100, 101]}}
            
            # 元数据
            "iat": int(time.time()),
            "exp": int(time.time()) + 3600,  # 1小时过期
            "jti": str(uuid.uuid4())  # Token唯一ID
        }
        
        # 使用RS256签名
        token = jwt.encode(payload, self.private_key, algorithm='RS256')
        return token
    
    def verify_token(self, token: str) -> dict:
        """
        验证JWT Token(使用公钥)
        """
        try:
            payload = jwt.decode(
                token, 
                self.public_key, 
                algorithms=['RS256']
            )
            
            # 检查黑名单
            if self._is_revoked(payload['jti']):
                raise TokenRevokedException()
            
            return payload
            
        except jwt.ExpiredSignatureError:
            raise TokenExpiredException()
        except jwt.InvalidTokenError:
            raise InvalidTokenException()
    
    def _is_revoked(self, jti: str) -> bool:
        """检查Token是否在黑名单"""
        return redis_client.exists(f"blacklist:{jti}")
```

#### 权限收集器

```python
# backend/app/users/permission_collector.py

class PermissionCollector:
    """收集用户的完整权限(全局 + 各系统)"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def collect(self, user_id: int) -> dict:
        """
        收集用户在所有系统中的权限
        """
        user = self.db.query(User).get(user_id)
        
        result = {
            "global_roles": [],
            "system_roles": {},
            "global_resources": {},
            "system_resources": {}
        }
        
        # 1. 收集角色
        for user_role in user.roles:
            role = user_role.role
            
            if role.namespace == 'global':
                result['global_roles'].append(role.code.replace('global:', ''))
            else:
                # 系统角色
                system_code = role.namespace
                if system_code not in result['system_roles']:
                    result['system_roles'][system_code] = []
                
                # 去掉命名空间前缀
                role_name = role.code.replace(f"{system_code}:", "")
                result['system_roles'][system_code].append(role_name)
        
        # 2. 收集资源绑定
        for binding in user.resource_bindings:
            if binding.namespace == 'global':
                # 全局资源
                if binding.resource_type not in result['global_resources']:
                    result['global_resources'][binding.resource_type] = []
                result['global_resources'][binding.resource_type].append(
                    int(binding.resource_id)
                )
            else:
                # 系统资源
                system_code = binding.namespace
                if system_code not in result['system_resources']:
                    result['system_resources'][system_code] = {}
                
                if binding.resource_type not in result['system_resources'][system_code]:
                    result['system_resources'][system_code][binding.resource_type] = []
                
                result['system_resources'][system_code][binding.resource_type].append(
                    int(binding.resource_id)
                )
        
        return result
```

### 4.2 系统注册和Token管理

**文件**: `backend/app/systems/service.py`, `backend/app/systems/router.py`

```python
# backend/app/systems/router.py

@router.post("/systems", response_model=SystemResponse)
async def create_system(
    system_data: SystemCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    注册新系统,生成系统Token
    """
    # 1. 创建系统记录
    system = System(
        code=system_data.code,
        name=system_data.name,
        description=system_data.description,
        api_endpoint=system_data.api_endpoint
    )
    
    # 2. 生成系统Token(长期有效,1年)
    jwt_handler = JWTHandler()
    system_token = jwt_handler.generate_system_token(
        system_id=system.code,
        system_name=system.name,
        expires_days=365
    )
    
    system.system_token = system_token
    
    db.add(system)
    db.commit()
    
    # 3. 记录审计日志
    audit_logger.log(
        action_type="system_created",
        operator_id=current_user.id,
        target_type="system",
        target_id=system.id,
        changes={"code": system.code, "name": system.name}
    )
    
    return system


@router.get("/systems/{system_id}/config")
async def get_system_config(
    system_id: int,
    system_token: str = Header(..., alias="X-System-Token"),
    db: Session = Depends(get_db)
):
    """
    业务系统拉取自己的权限配置
    用于启动时同步
    """
    # 1. 验证系统Token
    system = verify_system_token(db, system_token)
    if system.id != system_id:
        raise PermissionDeniedException()
    
    # 2. 查询系统的所有角色和权限
    config_service = ConfigSyncService(db)
    config = config_service.get_system_config(system)
    
    return config


# backend/app/systems/config_sync.py

class ConfigSyncService:
    """配置同步服务"""
    
    def get_system_config(self, system: System) -> dict:
        """
        获取系统的完整权限配置
        """
        namespace = system.code
        
        # 查询系统的角色
        roles = self.db.query(Role).filter(
            Role.namespace == namespace
        ).all()
        
        # 查询系统的权限
        permissions = self.db.query(Permission).filter(
            Permission.namespace == namespace
        ).all()
        
        # 查询系统的路由规则
        route_patterns = self.db.query(RoutePattern).filter(
            RoutePattern.system_id == system.id
        ).all()
        
        # 构建配置
        config = {
            "version": self._get_config_version(system),
            "updated_at": int(time.time()),
            "namespace": namespace,
            
            "roles": {
                role.code.replace(f"{namespace}:", ""): {
                    "id": role.id,
                    "name": role.name,
                    "description": role.description,
                    "permissions": [
                        rp.permission.code.replace(f"{namespace}:", "")
                        for rp in role.permissions
                    ]
                }
                for role in roles
            },
            
            "permissions": {
                perm.code.replace(f"{namespace}:", ""): {
                    "id": perm.id,
                    "name": perm.name,
                    "resource_type": perm.resource_type,
                    "action": perm.action
                }
                for perm in permissions
            },
            
            "route_patterns": [
                {
                    "role": route.role.code.replace(f"{namespace}:", ""),
                    "pattern": route.pattern,
                    "method": route.method,
                    "priority": route.priority
                }
                for route in route_patterns
            ]
        }
        
        return config
```

### 4.3 RBAC管理(多命名空间)

**文件**: `backend/app/rbac/router.py`

```python
# 角色管理API

@router.post("/roles")
async def create_role(
    role_data: RoleCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    创建角色(全局或系统)
    """
    # 构建完整的code: namespace:role_name
    if role_data.namespace == 'global':
        code = f"global:{role_data.name}"
        system_id = None
    else:
        # 验证系统是否存在
        system = db.query(System).filter(
            System.code == role_data.namespace
        ).first()
        if not system:
            raise NotFoundException("系统不存在")
        
        code = f"{role_data.namespace}:{role_data.name}"
        system_id = system.id
    
    role = Role(
        code=code,
        name=role_data.display_name,
        namespace=role_data.namespace,
        system_id=system_id,
        description=role_data.description
    )
    
    db.add(role)
    db.commit()
    
    # 通知权限变更
    notifier = PermissionNotifier()
    notifier.notify_role_created(role)
    
    return role


@router.get("/roles")
async def list_roles(
    namespace: Optional[str] = None,
    system_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    获取角色列表(可按命名空间过滤)
    """
    query = db.query(Role)
    
    if namespace:
        query = query.filter(Role.namespace == namespace)
    
    if system_id:
        query = query.filter(Role.system_id == system_id)
    
    roles = query.all()
    return roles


@router.put("/roles/{role_id}/permissions")
async def update_role_permissions(
    role_id: int,
    permission_ids: List[int],
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    配置角色的权限
    """
    role = db.query(Role).get(role_id)
    
    # 删除旧的权限关联
    db.query(RolePermission).filter(
        RolePermission.role_id == role_id
    ).delete()
    
    # 添加新的权限关联
    for perm_id in permission_ids:
        role_perm = RolePermission(
            role_id=role_id,
            permission_id=perm_id
        )
        db.add(role_perm)
    
    db.commit()
    
    # 通知权限变更
    notifier = PermissionNotifier()
    notifier.notify_role_permissions_updated(role)
    
    return {"message": "权限更新成功"}


# 路由规则API

@router.post("/systems/{system_id}/routes")
async def create_route_pattern(
    system_id: int,
    route_data: RoutePatternCreate,
    db: Session = Depends(get_db)
):
    """
    为系统创建路由规则
    """
    route = RoutePattern(
        system_id=system_id,
        role_id=route_data.role_id,
        pattern=route_data.pattern,
        method=route_data.method,
        priority=route_data.priority,
        description=route_data.description
    )
    
    db.add(route)
    db.commit()
    
    # 通知配置变更
    system = db.query(System).get(system_id)
    notifier = PermissionNotifier()
    notifier.notify_config_updated(system.code)
    
    return route


# 资源绑定API

@router.post("/users/{user_id}/resources")
async def bind_user_resources(
    user_id: int,
    binding_data: ResourceBindingCreate,
    db: Session = Depends(get_db)
):
    """
    为用户绑定资源权限
    """
    # 批量创建绑定
    bindings = []
    for resource_id in binding_data.resource_ids:
        binding = ResourceBinding(
            user_id=user_id,
            namespace=binding_data.namespace,
            system_id=binding_data.system_id,
            resource_type=binding_data.resource_type,
            resource_id=str(resource_id),
            action=binding_data.action,
            metadata=binding_data.metadata
        )
        bindings.append(binding)
    
    db.bulk_save_objects(bindings)
    db.commit()
    
    # 通知用户权限变更
    notifier = PermissionNotifier()
    notifier.notify_user_permissions_changed(user_id)
    
    return {"message": f"成功绑定{len(bindings)}个资源"}
```

### 4.4 权限变更通知(Redis Pub/Sub)

**文件**: `backend/app/rbac/notifier.py`

```python
class PermissionNotifier:
    """权限变更通知器"""
    
    def __init__(self):
        self.redis = redis_client
    
    def notify_role_created(self, role: Role):
        """角色创建通知"""
        self._publish(role.namespace, {
            "type": "role_created",
            "role_id": role.id,
            "role_code": role.code,
            "timestamp": time.time()
        })
    
    def notify_role_permissions_updated(self, role: Role):
        """角色权限更新通知"""
        self._publish(role.namespace, {
            "type": "role_permissions_updated",
            "role_id": role.id,
            "timestamp": time.time()
        })
    
    def notify_user_permissions_changed(self, user_id: int):
        """用户权限变更通知(影响所有系统)"""
        # 发布到全局channel
        self._publish("global", {
            "type": "user_permissions_changed",
            "user_id": user_id,
            "timestamp": time.time()
        })
    
    def notify_config_updated(self, namespace: str):
        """配置更新通知"""
        self._publish(namespace, {
            "type": "config_updated",
            "config_version": self._get_config_version(namespace),
            "timestamp": time.time()
        })
    
    def notify_token_revoked(self, jti: str):
        """Token撤销通知"""
        # 加入黑名单
        self.redis.setex(f"blacklist:{jti}", 3600, "1")
        
        # 发布通知
        self._publish("global", {
            "type": "token_revoked",
            "jti": jti,
            "timestamp": time.time()
        })
    
    def _publish(self, namespace: str, message: dict):
        """发布消息到Redis"""
        channel = f"permission:changed:{namespace}"
        self.redis.publish(channel, json.dumps(message))
    
    def _get_config_version(self, namespace: str) -> str:
        """获取配置版本号"""
        # 使用时间戳 + 命名空间生成版本号
        return f"v{namespace}_{int(time.time())}"
```

---

## 五、SDK实现

### 5.1 Python SDK

#### 核心客户端

```python
# sdk/python/authhub_sdk/client.py

class AuthHubClient:
    """
    AuthHub SDK核心客户端
    """
    
    def __init__(
        self,
        authhub_url: str,
        system_id: str,
        system_token: str,
        namespace: str,
        redis_url: str,
        enable_cache: bool = True,
        sync_interval: int = 300  # 5分钟同步一次
    ):
        self.authhub_url = authhub_url
        self.system_id = system_id
        self.system_token = system_token
        self.namespace = namespace
        
        # Redis客户端
        self.redis = redis.from_url(redis_url)
        
        # JWT验证器
        self.verifier = TokenVerifier(self.redis)
        
        # 权限检查器
        self.checker = PermissionChecker(namespace)
        
        # 配置缓存
        self.config_cache = {}
        self.config_version = None
        
        # 初始化
        self._sync_public_key()
        self._sync_config()
        
        if enable_cache:
            # 订阅权限变更
            self._subscribe_updates()
            
            # 定期同步配置
            self._start_sync_scheduler(sync_interval)
    
    def verify_token(self, token: str) -> dict:
        """
        验证Token(本地)
        返回Token payload
        """
        return self.verifier.verify(token)
    
    def check_permission(
        self, 
        token_payload: dict, 
        resource: str, 
        action: str
    ) -> bool:
        """
        检查权限(本地)
        """
        return self.checker.check_permission(
            token_payload, 
            resource, 
            action,
            self.config_cache
        )
    
    def check_route(
        self, 
        token_payload: dict, 
        path: str, 
        method: str
    ) -> bool:
        """
        检查路由权限(本地)
        """
        return self.checker.check_route(
            token_payload, 
            path, 
            method,
            self.config_cache
        )
    
    # 便捷方法
    def has_global_role(self, token_payload: dict, role: str) -> bool:
        """检查全局角色"""
        return role in token_payload.get('global_roles', [])
    
    def has_system_role(self, token_payload: dict, role: str) -> bool:
        """检查系统角色"""
        system_roles = token_payload.get('system_roles', {})
        return role in system_roles.get(self.namespace, [])
    
    def has_resource_access(
        self, 
        token_payload: dict, 
        resource_type: str, 
        resource_id: int
    ) -> bool:
        """检查资源访问权限"""
        # 检查全局资源
        global_resources = token_payload.get('global_resources', {})
        if resource_id in global_resources.get(resource_type, []):
            return True
        
        # 检查系统资源
        system_resources = token_payload.get('system_resources', {})
        namespace_resources = system_resources.get(self.namespace, {})
        if resource_id in namespace_resources.get(resource_type, []):
            return True
        
        return False
    
    # 内部方法
    def _sync_public_key(self):
        """同步JWT公钥"""
        response = requests.get(f"{self.authhub_url}/api/v1/auth/public-key")
        self.verifier.set_public_key(response.json()['public_key'])
    
    def _sync_config(self):
        """同步权限配置"""
        response = requests.get(
            f"{self.authhub_url}/api/v1/systems/{self.system_id}/config",
            headers={"X-System-Token": self.system_token}
        )
        config = response.json()
        self.config_cache = config
        self.config_version = config['version']
        logger.info(f"配置已同步: {self.config_version}")
    
    def _subscribe_updates(self):
        """订阅权限变更通知"""
        pubsub = self.redis.pubsub()
        
        # 订阅系统channel和全局channel
        channels = [
            f"permission:changed:{self.namespace}",
            "permission:changed:global"
        ]
        pubsub.subscribe(*channels)
        
        def listener():
            for message in pubsub.listen():
                if message['type'] == 'message':
                    self._handle_update(message)
        
        # 在后台线程运行
        thread = threading.Thread(target=listener, daemon=True)
        thread.start()
    
    def _handle_update(self, message):
        """处理权限变更消息"""
        try:
            data = json.loads(message['data'])
            logger.info(f"收到权限变更通知: {data['type']}")
            
            # 重新同步配置
            self._sync_config()
            
        except Exception as e:
            logger.error(f"处理权限变更失败: {e}")
    
    def _start_sync_scheduler(self, interval: int):
        """启动定期同步"""
        def sync_job():
            while True:
                time.sleep(interval)
                try:
                    self._sync_config()
                except Exception as e:
                    logger.error(f"定期同步失败: {e}")
        
        thread = threading.Thread(target=sync_job, daemon=True)
        thread.start()
```

#### Token验证器

```python
# sdk/python/authhub_sdk/verifier.py

class TokenVerifier:
    """Token验证器"""
    
    def __init__(self, redis_client):
        self.redis = redis_client
        self.public_key = None
    
    def set_public_key(self, public_key_pem: str):
        """设置公钥"""
        self.public_key = public_key_pem
    
    def verify(self, token: str) -> dict:
        """
        验证Token
        1. 验证JWT签名
        2. 检查过期时间
        3. 检查黑名单
        """
        if not self.public_key:
            raise Exception("公钥未设置")
        
        try:
            # 验证JWT签名和过期时间
            payload = jwt.decode(
                token, 
                self.public_key, 
                algorithms=['RS256']
            )
            
            # 检查黑名单
            if self._is_revoked(payload['jti']):
                raise TokenRevokedException("Token已被撤销")
            
            return payload
            
        except jwt.ExpiredSignatureError:
            raise TokenExpiredException("Token已过期")
        except jwt.InvalidTokenError as e:
            raise InvalidTokenException(f"Token无效: {str(e)}")
    
    def _is_revoked(self, jti: str) -> bool:
        """检查Token是否在黑名单"""
        return self.redis.exists(f"blacklist:{jti}") > 0
```

#### 权限检查器

```python
# sdk/python/authhub_sdk/checker.py

class PermissionChecker:
    """权限检查器"""
    
    def __init__(self, namespace: str):
        self.namespace = namespace
    
    def check_permission(
        self, 
        token_payload: dict, 
        resource: str, 
        action: str,
        config: dict
    ) -> bool:
        """
        检查权限
        优先级:
        1. 全局管理员
        2. Token中的system_resources
        3. Token中的system_roles -> 配置中的角色权限
        """
        # 1. 全局管理员
        if 'admin' in token_payload.get('global_roles', []):
            return True
        
        # 2. 检查系统资源绑定
        perm_code = f"{resource}:{action}"
        system_resources = token_payload.get('system_resources', {})
        namespace_resources = system_resources.get(self.namespace, {})
        
        # 这里简化处理,实际可能需要更复杂的匹配逻辑
        
        # 3. 检查系统角色
        system_roles = token_payload.get('system_roles', {})
        user_roles = system_roles.get(self.namespace, [])
        
        for role_name in user_roles:
            role_config = config.get('roles', {}).get(role_name, {})
            role_permissions = role_config.get('permissions', [])
            
            # 检查精确匹配
            if perm_code in role_permissions:
                return True
            
            # 检查通配符
            if f"{resource}:*" in role_permissions:
                return True
            if "*:*" in role_permissions:
                return True
        
        return False
    
    def check_route(
        self, 
        token_payload: dict, 
        path: str, 
        method: str,
        config: dict
    ) -> bool:
        """
        检查路由权限(正则匹配)
        """
        # 全局管理员
        if 'admin' in token_payload.get('global_roles', []):
            return True
        
        # 获取用户的系统角色
        system_roles = token_payload.get('system_roles', {})
        user_roles = system_roles.get(self.namespace, [])
        
        # 遍历路由规则
        route_patterns = config.get('route_patterns', [])
        
        # 按优先级排序
        sorted_patterns = sorted(
            route_patterns, 
            key=lambda x: x.get('priority', 0), 
            reverse=True
        )
        
        for pattern_rule in sorted_patterns:
            # 检查角色
            if pattern_rule['role'] not in user_roles:
                continue
            
            # 检查方法
            if pattern_rule['method'] != '*' and pattern_rule['method'] != method:
                continue
            
            # 正则匹配路径
            if re.match(pattern_rule['pattern'], path):
                return True
        
        return False
```

#### 装饰器

```python
# sdk/python/authhub_sdk/decorators.py

def require_auth(func):
    """要求用户登录"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        # 从request中提取token
        token = extract_token_from_request()
        
        # 验证token
        user_info = authhub_client.verify_token(token)
        
        # 注入user_info
        kwargs['user_info'] = user_info
        return func(*args, **kwargs)
    
    return wrapper


def require_role(role: str):
    """
    要求特定角色
    支持: @require_role("editor") 或 @require_role("global:admin")
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            token = extract_token_from_request()
            user_info = authhub_client.verify_token(token)
            
            # 判断是全局角色还是系统角色
            if ':' in role:
                namespace, role_name = role.split(':', 1)
                if namespace == 'global':
                    has_role = role_name in user_info.get('global_roles', [])
                else:
                    system_roles = user_info.get('system_roles', {})
                    has_role = role_name in system_roles.get(namespace, [])
            else:
                # 默认检查当前系统角色
                has_role = authhub_client.has_system_role(user_info, role)
            
            if not has_role:
                raise PermissionDeniedException(f"需要角色: {role}")
            
            kwargs['user_info'] = user_info
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


def require_permission(resource: str, action: str):
    """要求特定权限"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            token = extract_token_from_request()
            user_info = authhub_client.verify_token(token)
            
            if not authhub_client.check_permission(user_info, resource, action):
                raise PermissionDeniedException(
                    f"需要权限: {resource}:{action}"
                )
            
            kwargs['user_info'] = user_info
            return func(*args, **kwargs)
        
        return wrapper
    return decorator
```

#### FastAPI中间件

```python
# sdk/python/authhub_sdk/middleware/fastapi.py

class AuthHubMiddleware:
    """FastAPI中间件"""
    
    def __init__(self, app, client: AuthHubClient):
        self.app = app
        self.client = client
    
    async def __call__(self, request: Request, call_next):
        # 跳过不需要认证的路由
        if self._is_public_route(request.url.path):
            return await call_next(request)
        
        # 提取Token
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return JSONResponse(
                status_code=401,
                content={"error": "缺少认证Token"}
            )
        
        token = auth_header.replace('Bearer ', '')
        
        try:
            # 验证Token
            user_info = self.client.verify_token(token)
            
            # 检查路由权限
            if not self.client.check_route(
                user_info, 
                request.url.path, 
                request.method
            ):
                return JSONResponse(
                    status_code=403,
                    content={"error": "权限不足"}
                )
            
            # 注入用户信息
            request.state.user = user_info
            
        except TokenException as e:
            return JSONResponse(
                status_code=401,
                content={"error": str(e)}
            )
        
        response = await call_next(request)
        return response
    
    def _is_public_route(self, path: str) -> bool:
        """判断是否是公开路由"""
        public_routes = ['/health', '/docs', '/openapi.json']
        return path in public_routes


# 使用示例
from fastapi import FastAPI
from authhub_sdk import AuthHubClient
from authhub_sdk.middleware.fastapi import AuthHubMiddleware

app = FastAPI()

# 初始化SDK
authhub_client = AuthHubClient(
    authhub_url="https://authhub.company.com",
    system_id="system_a",
    system_token="your_system_token",
    namespace="system_a",
    redis_url="redis://localhost:6379"
)

# 添加中间件
app.add_middleware(AuthHubMiddleware, client=authhub_client)
```

### 5.2 TypeScript SDK

**核心结构类似,提供**:

- `AuthHubClient` - 核心客户端
- `TokenVerifier` - Token验证
- `PermissionChecker` - 权限检查
- React Hooks: `useAuth`, `usePermission`, `useRole`
- Express/Koa/Next.js中间件

---

## 六、管理后台关键页面

### 6.1 系统管理

**系统注册页面** (`frontend/src/pages/Systems/SystemForm.tsx`):

```tsx
功能:
- 输入系统代码、名称、描述
- 生成系统Token(显示一次,复制)
- 提示SDK接入方式
```

**系统列表** (`frontend/src/pages/Systems/SystemList.tsx`):

```tsx
功能:
- 显示所有接入系统
- 查看系统详情(角色、权限、路由规则)
- 重新生成系统Token
- 禁用/启用系统
```

### 6.2 用户权限视图

**用户详情页** (`frontend/src/pages/Users/UserDetail.tsx`):

```tsx
功能:
- Tab1: 全局角色和资源
- Tab2: 系统A的角色和资源
- Tab3: 系统B的角色和资源
- 显示用户在所有系统的权限汇总
- 支持编辑各系统权限
```

### 6.3 角色管理(多系统)

**角色列表** (`frontend/src/pages/Roles/RoleList.tsx`):

```tsx
功能:
- 顶部系统选择器(全局/系统A/系统B)
- 根据选择显示对应系统的角色
- 创建角色(选择所属系统)
- 配置角色权限(拖拽权限树)
```

### 6.4 路由规则配置

**路由规则页** (`frontend/src/pages/Permissions/RouteRules.tsx`):

```tsx
功能:
- 按系统分组显示路由规则
- 添加路由规则:
  - 选择系统
  - 选择角色
  - 输入正则表达式
  - 实时测试匹配(输入路径,显示是否匹配)
- 优先级设置
```

### 6.5 审计日志

**权限变更历史** (`frontend/src/pages/Audit/PermissionChanges.tsx`):

```tsx
功能:
- 显示所有权限配置变更
- 过滤: 系统、操作类型、时间范围
- 详情: 操作人、变更内容(diff)
```

---

## 七、实施步骤(已完成阶段回顾)

### ✅ 阶段1: 基础设施 (已完成)

- [x] 项目初始化(UV + pnpm)
- [x] 数据库设计和迁移脚本
- [x] Redis连接封装
- [x] JWT工具类(RS256密钥生成)
- [x] 基础配置管理

### ✅ 阶段2: 认证模块 (已完成)

- [x] 飞书OAuth2.0集成
- [x] JWT生成和验证
- [x] 权限收集器
- [x] Token黑名单机制
- [x] 公钥发布接口
- [x] SSO代理端点(/auth/sso/*)

### ✅ 阶段3: 系统管理 (已完成)

- [x] 系统注册功能
- [x] 系统Token生成
- [x] 配置同步API
- [x] 系统管理API(CRUD)
- [x] Token重新生成

### ✅ 阶段4: RBAC模块 (已完成)

- [x] 角色管理(多命名空间)
- [x] 权限管理
- [x] 路由规则管理
- [x] 资源绑定管理
- [x] RBAC完整API

### ✅ 阶段5: Python SDK (已完成)

- [x] 核心客户端(AuthHubClient)
- [x] Token验证器(TokenVerifier)
- [x] 权限检查器(PermissionChecker)
- [x] SSO客户端(SSOClient)
- [x] 配置同步和Redis订阅
- [x] 装饰器(@require_auth, @require_role, @require_permission)
- [x] FastAPI/Flask/Django中间件
- [x] 示例项目(fastapi_example.py, fastapi_sso_example.py)

### ✅ 阶段6: TypeScript SDK (已完成)

- [x] SSO客户端
- [x] Token管理器
- [x] React Hooks(useAuth, useSSO, usePermission, useRole)
- [x] Vue Composables(useAuth, useSSO)
- [x] React组件(LoginButton, LoginPage, ProtectedRoute, SSOCallback)
- [x] Vue组件(LoginButton, LoginPage, ProtectedView, SSOCallback)
- [x] 示例项目(React SSO, Vue SSO)

### ✅ 阶段7: 管理后台框架 (已完成)

- [x] React项目搭建(Vite + TypeScript)
- [x] 路由和布局(React Router + MainLayout)
- [x] API服务封装(Axios + React Query)
- [x] 认证上下文(AuthContext)
- [x] 通用组件

### ✅ 阶段8: 管理后台页面 (85%完成)

- [x] 登录页面(飞书扫码登录)
- [x] 仪表盘(统计数据)
- [x] 系统管理页面(列表、创建、详情、Token)
- [x] 用户管理页面(列表、详情、角色分配)
- [x] 角色管理页面(列表、创建、编辑、权限配置)
- [x] 权限配置页面(列表、创建、编辑)
- [x] 路由规则管理(列表、创建)
- [x] 资源绑定页面(列表、创建)
- [ ] 审计日志页面(待实现)

### 🚧 阶段9: 审计和日志 (20%完成)

- [x] 审计日志数据模型
- [ ] 审计日志记录服务
- [ ] 操作日志存储
- [ ] 日志查询API
- [ ] 前端展示

### 🚧 阶段10: 集成测试 (10%完成)

- [ ] 端到端测试
- [ ] SDK集成测试
- [ ] 性能测试
- [ ] 安全测试

### 🚧 阶段11: 文档 (60%完成)

- [x] 架构设计文档(overview.md)
- [x] 认证实现文档
- [x] SSO集成指南
- [x] SDK README
- [ ] API详细文档
- [ ] 使用指南完善
- [ ] 部署文档

### ✅ 阶段12: 部署 (80%完成)

- [x] Docker配置(backend, frontend)
- [x] docker-compose.yml
- [x] 环境配置(.env.example)
- [ ] Kubernetes配置
- [ ] CI/CD配置

**实际耗时**: 约40-45天
**当前状态**: 核心功能完整，可以进行生产环境测试

---

## 八、技术栈

### 后端

- **框架**: FastAPI 0.104+
- **ORM**: SQLAlchemy 2.0
- **数据库**: PostgreSQL 15+
- **缓存/消息**: Redis 7+
- **迁移**: Alembic
- **JWT**: PyJWT (RS256)
- **飞书SDK**: larksuite-oapi
- **环境管理**: UV

### 前端

- **框架**: React 18 + TypeScript
- **UI库**: Ant Design 5
- **状态管理**: Zustand + React Query
- **路由**: React Router 6
- **请求**: Axios
- **构建**: Vite
- **包管理**: pnpm

### SDK

- **Python**: PyJWT, redis, requests
- **TypeScript**: jose, ioredis, axios

### 部署

- **容器**: Docker + Docker Compose
- **Web服务器**: Uvicorn + Gunicorn
- **反向代理**: Nginx

---

## 九、文档输出

### docs/architecture/

- `overview.md` - 整体架构(含Mermaid流程图)
- `namespace-design.md` - 命名空间设计原理
- `token-strategy.md` - JWT Token设计和黑名单
- `permission-model.md` - 多命名空间权限模型
- `cache-sync.md` - 配置同步策略

### docs/api/

- OpenAPI文档(FastAPI自动生成)
- Postman Collection

### docs/sdk/

- `python/quickstart.md` - Python SDK快速开始
- `python/advanced.md` - 高级用法和自定义
- `typescript/quickstart.md` - TypeScript SDK快速开始
- `typescript/react-integration.md` - React集成

### docs/user-guide/

- `system-registration.md` - 系统接入完整流程
- `permission-config.md` - 权限配置最佳实践
- `best-practices.md` - 架构和安全最佳实践

## 十、项目实施进度

### ✅ 已完成部分

#### 后端核心功能 (95%完成)
- [x] 项目结构初始化(UV + FastAPI)
- [x] PostgreSQL数据库模型设计与实现
  - [x] 用户表(User)
  - [x] 系统表(System)
  - [x] 角色表(Role)
  - [x] 权限表(Permission)
  - [x] 用户角色关联表(UserRole)
  - [x] 角色权限关联表(RolePermission)
  - [x] 路由规则表(RoutePattern)
  - [x] 资源绑定表(ResourceBinding)
  - [x] 审计日志表(AuditLog)
- [x] Alembic数据库迁移配置
- [x] Redis缓存封装
- [x] RSA密钥对生成工具
- [x] JWT Handler实现(RS256签名)
  - [x] 用户Token生成(包含完整权限)
  - [x] 系统Token生成(长期有效)
  - [x] Token验证
  - [x] 黑名单机制
- [x] 飞书OAuth2.0集成
  - [x] 授权URL生成
  - [x] 回调处理
  - [x] 用户信息获取
  - [x] 用户同步到数据库
- [x] SSO代理端点(供SDK使用)
  - [x] /auth/sso/login-url - 获取登录URL
  - [x] /auth/sso/exchange-token - Token交换
  - [x] State参数验证(防CSRF)
- [x] 权限收集器(PermissionCollector)
  - [x] 收集全局角色
  - [x] 收集系统角色
  - [x] 收集全局资源绑定
  - [x] 收集系统资源绑定
- [x] 系统管理API
  - [x] 创建系统并生成Token
  - [x] 系统列表查询
  - [x] 系统详情获取
  - [x] 系统配置同步API
  - [x] 系统Token重新生成
  - [x] 系统状态更新
  - [x] 查询系统角色/权限
- [x] RBAC管理API
  - [x] 角色CRUD
  - [x] 权限CRUD
  - [x] 角色-权限关联管理
  - [x] 用户-角色分配
  - [x] 路由规则管理
  - [x] 资源绑定管理
  - [x] 统计数据API
- [x] 用户管理API
  - [x] 用户列表
  - [x] 用户详情
  - [x] 用户权限查询
  - [x] 用户角色管理
- [x] 认证依赖注入
  - [x] get_current_user
  - [x] require_admin
  - [x] verify_system_token
- [x] 配置管理(Pydantic Settings)
- [x] 日志系统

#### Python SDK (100%完成)
- [x] 核心客户端(AuthHubClient)
  - [x] Token本地验证
  - [x] 权限本地检查
  - [x] 路由权限检查
  - [x] 公钥同步
  - [x] 配置同步
  - [x] Redis Pub/Sub订阅
  - [x] 定期配置同步
- [x] Token验证器(TokenVerifier)
  - [x] JWT签名验证
  - [x] 黑名单检查
- [x] 权限检查器(PermissionChecker)
  - [x] 角色权限检查
  - [x] 路由正则匹配
  - [x] 资源权限检查
- [x] SSO客户端(SSOClient)
  - [x] 获取登录URL
  - [x] Token交换
  - [x] 回调处理
- [x] 装饰器
  - [x] @require_auth
  - [x] @require_role
  - [x] @require_permission
- [x] FastAPI中间件
  - [x] JWT认证中间件
  - [x] SSO集成中间件(setup_sso)
- [x] Flask中间件
- [x] Django中间件
- [x] 异常类
- [x] 示例项目
  - [x] FastAPI基础示例
  - [x] FastAPI SSO示例

#### TypeScript SDK (100%完成)
- [x] SSO客户端(SSOClient)
- [x] Token管理器(TokenManager)
- [x] 认证客户端(AuthClient)
- [x] React Hooks
  - [x] useAuth
  - [x] useSSO
  - [x] usePermission
  - [x] useRole
- [x] Vue Composables
  - [x] useAuth
  - [x] useSSO
- [x] React组件
  - [x] LoginButton
  - [x] LoginPage
  - [x] ProtectedRoute
  - [x] SSOCallback
- [x] Vue组件
  - [x] LoginButton
  - [x] LoginPage
  - [x] ProtectedView
  - [x] SSOCallback
- [x] 类型定义
- [x] 异常处理
- [x] 示例项目
  - [x] React SSO示例
  - [x] Vue SSO示例

#### 前端管理后台 (85%完成)
- [x] 项目初始化(React + TypeScript + Vite)
- [x] UI库集成(Ant Design)
- [x] 状态管理(React Query)
- [x] 路由配置(React Router)
- [x] API服务封装
- [x] 认证上下文(AuthContext)
- [x] 受保护路由(ProtectedRoute)
- [x] 布局组件(MainLayout)
- [x] 登录页面
  - [x] 飞书扫码登录
  - [x] 回调处理(Callback.tsx)
- [x] 仪表盘(Dashboard)
  - [x] 系统统计
  - [x] 用户统计
  - [x] 角色统计
- [x] 系统管理
  - [x] 系统列表(SystemList.tsx)
  - [x] 创建系统(SystemForm.tsx)
  - [x] 系统详情(SystemDetail.tsx)
  - [x] Token显示(TokenDisplay.tsx)
- [x] 用户管理
  - [x] 用户列表(UserList.tsx)
  - [x] 用户详情(UserDetail.tsx)
  - [x] 角色分配(UserRoles.tsx)
- [x] 角色管理
  - [x] 角色列表(RoleList.tsx)
  - [x] 创建角色(RoleForm.tsx)
  - [x] 编辑角色(RoleEditModal.tsx)
  - [x] 权限配置(RolePermissions.tsx)
- [x] 权限管理
  - [x] 权限列表(PermissionList.tsx)
  - [x] 创建权限(PermissionForm.tsx)
  - [x] 编辑权限(PermissionEditModal.tsx)
  - [x] 路由规则管理(RouteRuleList.tsx)
  - [x] 资源绑定管理(ResourceBindingList.tsx)

#### 文档 (60%完成)
- [x] README.md(项目概述)
- [x] 架构设计文档(architecture/overview.md)
- [x] 认证实现文档(authentication-implementation.md)
- [x] 资源绑定指南(rbac/resource-binding-guide.md)
- [x] SSO集成指南(sso-integration-guide.md)
- [x] 数据库测试文档(TESTING_DATABASES.md)
- [x] Python SDK README
- [x] TypeScript SDK README
- [ ] API详细文档
- [ ] 最佳实践文档
- [ ] 部署指南

#### 部署配置 (80%完成)
- [x] Docker配置
  - [x] backend.Dockerfile
  - [x] frontend.Dockerfile
- [x] docker-compose.yml
- [x] docker-compose-db.test.yml(测试数据库)
- [x] 环境变量配置(.env.example)
- [ ] Kubernetes配置
- [ ] CI/CD配置

### 🚧 待完成部分

#### 后端功能增强
- [ ] Redis Pub/Sub权限变更通知实现
  - [ ] 角色创建通知
  - [ ] 权限更新通知
  - [ ] 用户权限变更通知
  - [ ] Token撤销通知
- [ ] 审计日志完整实现
  - [ ] 审计日志记录服务
  - [ ] 审计日志查询API
  - [ ] 操作类型枚举完善
- [ ] 权限变更历史追踪
- [ ] 批量操作API
- [ ] 数据导入/导出

#### 前端管理后台增强
- [ ] 审计日志页面
  - [ ] 权限变更历史
  - [ ] 用户操作日志
  - [ ] 系统访问日志
- [ ] 高级搜索和过滤
- [ ] 批量操作功能
- [ ] 数据导出功能
- [ ] 国际化支持
- [ ] 主题切换
- [ ] 权限树组件(拖拽式权限分配)
- [ ] 路由规则正则测试工具

#### 测试
- [ ] 后端单元测试
  - [ ] 认证模块测试
  - [ ] RBAC模块测试
  - [ ] 权限收集测试
  - [ ] JWT Handler测试
- [ ] 后端集成测试
- [ ] SDK单元测试
- [ ] SDK集成测试
- [ ] E2E测试
- [ ] 性能测试
- [ ] 安全测试

#### 文档完善
- [ ] API详细文档
  - [ ] 认证接口详细说明
  - [ ] 系统管理接口详细说明
  - [ ] RBAC接口详细说明
  - [ ] 用户管理接口详细说明
- [ ] SDK高级用法文档
  - [ ] Python SDK高级配置
  - [ ] TypeScript SDK高级配置
  - [ ] 自定义中间件开发
- [ ] 部署文档
  - [ ] Docker部署详细步骤
  - [ ] Kubernetes部署指南
  - [ ] 生产环境配置建议
- [ ] 最佳实践文档
  - [ ] 权限设计最佳实践
  - [ ] 安全最佳实践
  - [ ] 性能优化建议

#### 优化和增强
- [ ] 性能优化
  - [ ] 数据库查询优化
  - [ ] Redis缓存策略优化
  - [ ] JWT Token大小优化
- [ ] 监控和告警
  - [ ] Prometheus指标
  - [ ] 健康检查端点
  - [ ] 日志聚合配置
- [ ] 高可用配置
  - [ ] Redis哨兵/集群
  - [ ] PostgreSQL主从复制
  - [ ] 负载均衡配置

### 📊 完成度总结

| 模块 | 完成度 | 说明 |
|------|--------|------|
| 后端核心功能 | 95% | 核心API和功能已完成，待完善通知和审计 |
| Python SDK | 100% | 功能完整，包含完整示例 |
| TypeScript SDK | 100% | React和Vue都已支持 |
| 前端管理后台 | 85% | 主要页面已完成，待完善审计和高级功能 |
| 文档 | 60% | 基础文档已完成，待补充详细文档 |
| 部署配置 | 80% | Docker配置完成，待完善K8s和CI/CD |
| 测试 | 10% | 仅有基础测试，需要全面的测试覆盖 |

**总体完成度: ~80%**

核心功能已经完整可用，可以进行系统集成和测试。剩余工作主要是增强功能、完善文档和测试覆盖。

---

## 十一、下一步工作建议

### 🎯 优先级 P0 (立即进行)

1. **Redis Pub/Sub权限变更通知实现**
   - 在RBAC API中调用notifier发布变更通知
   - 测试权限变更的实时同步
   - 确保配置更新能及时推送到业务系统

2. **基础测试覆盖**
   - 编写认证模块单元测试
   - 编写RBAC模块单元测试
   - 编写SDK集成测试
   - 确保核心功能的稳定性

3. **生产环境部署测试**
   - 使用Docker Compose部署完整环境
   - 测试高并发场景
   - 测试故障恢复(Redis/PostgreSQL重启)
   - 验证性能指标

### 📝 优先级 P1 (近期完成)

1. **审计日志完整实现**
   - 实现审计日志记录服务
   - 在关键操作中添加审计日志
   - 实现审计日志查询API
   - 开发前端审计日志页面

2. **API文档完善**
   - 补充API详细说明
   - 添加更多示例代码
   - 添加错误码说明
   - 生成Postman Collection

3. **部署文档完善**
   - 编写详细的Docker部署指南
   - 编写生产环境配置建议
   - 添加监控和告警配置指南
   - 添加备份和恢复指南

### 🚀 优先级 P2 (计划完成)

1. **性能优化**
   - 数据库查询优化(添加合适的索引)
   - Redis缓存策略优化
   - JWT Token大小优化(压缩策略)
   - 配置同步性能优化

2. **高级功能**
   - 批量操作API
   - 数据导入/导出
   - 权限树拖拽组件
   - 路由规则正则测试工具
   - 国际化支持

3. **Kubernetes部署支持**
   - 编写K8s部署配置
   - 添加健康检查端点
   - 配置水平扩展
   - 添加Prometheus监控

### 💡 建议和注意事项

#### 安全建议
1. ⚠️ **生产环境必须使用HTTPS**
2. ⚠️ **私钥文件必须严格保护** (不要提交到Git)
3. ⚠️ **定期更新RSA密钥对** (建议6-12个月)
4. ⚠️ **Token过期时间不宜过长** (建议1-4小时)
5. ⚠️ **系统Token定期轮换** (建议3-6个月)

#### 性能建议
1. 🔧 **配置Redis持久化** (AOF + RDB)
2. 🔧 **配置PostgreSQL连接池** (已实现，需调优)
3. 🔧 **启用数据库查询日志** (用于性能分析)
4. 🔧 **监控JWT Token大小** (建议不超过4KB)
5. 🔧 **配置Nginx反向代理** (负载均衡 + SSL终止)

#### 运维建议
1. 📊 **添加Prometheus指标采集**
2. 📊 **配置日志聚合** (ELK或Loki)
3. 📊 **设置告警规则** (CPU/内存/响应时间)
4. 📊 **定期备份数据库** (建议每天)
5. 📊 **监控Redis内存使用** (防止OOM)

#### 测试建议
1. ✅ **编写单元测试** (覆盖率>80%)
2. ✅ **编写集成测试** (测试关键流程)
3. ✅ **编写性能测试** (压测关键接口)
4. ✅ **编写安全测试** (SQL注入、XSS等)
5. ✅ **定期进行渗透测试**

### 📋 快速启动检查清单

部署前请确认以下事项:

- [ ] 已生成RSA密钥对(运行`python scripts/generate_keys.py`)
- [ ] 已配置飞书应用(AppID和AppSecret)
- [ ] 已初始化数据库(运行`alembic upgrade head`)
- [ ] 已配置Redis连接
- [ ] 已配置环境变量(.env文件)
- [ ] 已创建至少一个管理员用户
- [ ] 已测试飞书登录流程
- [ ] 已注册至少一个测试系统
- [ ] 已测试SDK集成(Python或TypeScript)
- [ ] 已配置HTTPS证书(生产环境)
- [ ] 已配置备份策略
- [ ] 已配置监控和告警

---

## 十二、总结

AuthHub项目已完成核心功能开发，具备以下特点:

### ✨ 核心优势
1. **统一管理**: 一个后台管理所有系统的权限
2. **高性能**: 去中心化校验，零网络开销
3. **高可用**: AuthHub故障不影响业务系统
4. **易集成**: 一行代码完成SSO集成
5. **灵活扩展**: 支持多命名空间、多系统

### 🎯 适用场景
- 企业内部多个业务系统需要统一登录
- 需要细粒度的权限控制(角色、资源、路由)
- 需要跨系统的权限管理和审计
- 需要高性能、高可用的权限系统
- 使用飞书作为企业IM工具

### 🚀 可以开始的工作
1. ✅ 接入第一个业务系统进行测试
2. ✅ 配置生产环境并进行压力测试
3. ✅ 根据实际使用情况优化性能
4. ✅ 收集用户反馈并迭代改进

### 📞 支持和反馈

- 文档: `/docs`目录
- 示例: `/sdk/python/examples`和`/sdk/typescript/examples`
- Issue: GitHub Issues
- Email: 项目维护者邮箱

**祝使用愉快！🎉**
