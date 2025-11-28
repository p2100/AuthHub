# 用户管理系统 ID 字段切换至飞书用户 ID 修改计划

**文档版本**: 1.0
**创建日期**: 2025-11-28
**修改范围**: 全系统用户管理标识字段切换
**优先级**: 高

---

## 📋 目录

- [1. 项目背景](#1-项目背景)
- [2. 现状分析](#2-现状分析)
  - [2.1 数据库层面](#21-数据库层面)
  - [2.2 后端层面](#22-后端层面)
  - [2.3 前端层面](#23-前端层面)
- [3. 修改目标](#3-修改目标)
- [4. 详细实施计划](#4-详细实施计划)
  - [4.1 第一阶段：数据库迁移](#41-第一阶段数据库迁移)
  - [4.2 第二阶段：后端代码重构](#42-第二阶段后端代码重构)
  - [4.3 第三阶段：前端代码重构](#43-第三阶段前端代码重构)
  - [4.4 第四阶段：测试验证](#44-第四阶段测试验证)
  - [4.5 第五阶段：部署上线](#45-第五阶段部署上线)
- [5. 风险评估与注意事项](#5-风险评估与注意事项)
  - [5.1 兼容性处理](#51-兼容性处理)
  - [5.2 数据一致性](#52-数据一致性)
  - [5.3 性能优化](#53-性能优化)
  - [5.4 回滚方案](#54-回滚方案)
- [6. 涉及文件清单](#6-涉及文件清单)
  - [6.1 后端文件](#61-后端文件)
  - [6.2 前端文件](#62-前端文件)
  - [6.3 数据库表](#63-数据库表)
- [7. 时间估算](#7-时间估算)
- [8. 相关文档](#8-相关文档)

---

## 1. 项目背景

当前系统用户管理体系基于自增整型 `id` 字段作为用户唯一标识，所有业务关联、权限管理、API 调用均依赖此字段。随着系统与飞书生态的深度融合，内部 ID 与飞书用户标识 `feishu_user_id` 之间的映射增加了系统复杂性。

为简化架构、提升系统一致性，决定将用户管理的主标识从 `id` 字段切换至 `feishu_user_id` 字段，实现以下目标：

- **统一标识体系**：直接使用飞书用户 ID，消除内外部标识映射
- **降低维护成本**：简化用户同步、权限管理等核心逻辑
- **提升扩展性**：为未来多租户、多身份源接入奠定基础

---

## 2. 现状分析

### 2.1 数据库层面

| 表名 | 当前字段 | 外键关联 | 影响程度 |
|------|---------|---------|---------|
| `users` | `id` (PK, int) `feishu_user_id` (UK, string) | 主表 | 🔴 高 |
| `user_roles` | `user_id` (FK→users.id, int) `created_by` (int) | 用户角色关联 | 🔴 高 |
| `resource_bindings` | `user_id` (FK→users.id, int) `created_by` (int) | 资源权限绑定 | 🔴 高 |
| `audit_logs` | `operator_id` (FK→users.id, int)<br>`target_id` (int, 多态) | 审计日志 (target_id 需改为 String 以支持 feishu_user_id) | 🔴 高 |

**当前 Schema 特点：**
- `users` 表采用自增整型 `id` 作为主键
- `feishu_user_id` 字段已存在，具有唯一索引，用于存储飞书用户标识
- 多个业务表通过 `user_id` 外键关联到 `users.id`
- JWT Token 的 `sub` 字段存储的是 `user.id`

### 2.2 后端层面

**核心服务层（app/users/service.py）：**
```python
# 当前实现
async def get_user_by_id(self, user_id: int) -> Optional[User]
async def update_user_status(self, user_id: int, status: str) -> Optional[User]
async def update_user_departments(self, user_id: int, dept_ids: list, dept_names: list)
```

**认证系统（app/auth/router.py 和 app/core/security.py）：**
- JWT Token 生成：`sub` 字段使用 `user.id`
- Token 刷新：通过 `user.id` 查询用户信息
- 权限收集：基于 `user.id` 聚合用户角色和资源权限

**RBAC 系统（app/rbac/service.py）：**
- 角色分配：`assign_role_to_user(user_id: int, ...)`
- 资源绑定：所有方法接受 `user_id: int` 参数
- 路由规则：基于用户 ID 的权限判断

**API 路由层：**
```python
# 当前路径参数
@router.get("/users/{user_id}")
@router.put("/users/{user_id}/status")
@router.get("/users/{user_id}/roles")
@router.get("/users/{user_id}/permissions")
```

### 2.3 前端层面

**API 类型定义（src/types/api.ts）：**
```typescript
export interface User {
  id: number              // 当前主标识
  feishu_user_id: string  // 飞书用户ID
  username: string
  email?: string
  // ...
}
```

**组件实现（src/pages/Users/UserList.tsx）：**
- 表格 rowKey 使用 `"id"`
- 操作按钮传递 `userId: number` 参数
- 状态更新 API 调用 `/users/${userId}/status`

**认证上下文（src/contexts/AuthContext.tsx）：**
- JWT Token 解析后 `sub` 字段为字符串（user.id 的字符串形式）
- 当前未直接使用用户 ID 进行业务操作

---

## 3. 修改目标

### 3.1 核心技术目标

1. **数据库层**
   - 将所有 `user_id` 外键字段类型从 `int` 改为 `string`
   - 外键引用从 `users.id` 改为 `users.feishu_user_id`
   - 保持 `users.id` 作为内部标识，但不用于业务关联

2. **认证授权层**
   - JWT Token 的 `sub` 字段改为存储 `feishu_user_id`
   - Token 刷新逻辑基于 `feishu_user_id` 查询用户
   - 权限收集和验证基于 `feishu_user_id`

3. **API 接口层**
   - 所有用户相关 API 从接受 `user_id: int` 改为 `feishu_user_id: string`
   - URL 路径参数更新为 `/users/{feishu_user_id}`
   - 保持 API 版本的向后兼容性（可选）

4. **前端应用层**
   - User 接口的 `id` 字段改为 `feishu_user_id: string`
   - 组件逻辑使用飞书用户 ID 进行操作
   - 表格 rowKey 等标识字段更新

### 3.2 业务价值目标

- ✨ **简化系统集成**：直接使用飞书用户 ID，无需维护映射关系
- 🚀 **提升开发效率**：统一标识体系，减少转换逻辑
- 🔒 **增强数据一致性**：从源头统一用户标识
- 📈 **支持未来扩展**：为多身份源接入奠定基础

---

## 4. 详细实施计划

### 4.1 第一阶段：数据库迁移

#### 4.1.1 创建数据库迁移脚本

**执行命令：**
```bash
cd /Users/leo/code/work/AuthHub/backend
alembic revision -m "migrate_user_id_to_feishu_user_id"
```

**迁移脚本核心内容：**

```python
"""Migrate user_id to feishu_user_id

Revision ID: xxxxxxx
Revises: 836823124d94
Create Date: 2025-11-28

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


def upgrade() -> None:
    # 1. 为 users 表 feishu_user_id 字段创建索引（如不存在）
    op.create_index('ix_users_feishu_user_id', 'users', ['feishu_user_id'], unique=False)

    # 2. 更新 user_roles 表
    # 2.1 添加新字段（feishu_user_id）
    op.add_column('user_roles', sa.Column('user_feishu_user_id', sa.String(100), nullable=True))
    op.add_column('user_roles', sa.Column('creator_feishu_user_id', sa.String(100), nullable=True))

    # 2.2 数据迁移：将 user_id 转换为 feishu_user_id
    op.execute("""
        UPDATE user_roles ur
        SET user_feishu_user_id = (SELECT feishu_user_id FROM users u WHERE u.id = ur.user_id)
        WHERE ur.user_feishu_user_id IS NULL
    """)
    op.execute("""
        UPDATE user_roles ur
        SET creator_feishu_user_id = (SELECT feishu_user_id FROM users u WHERE u.id = ur.created_by)
        WHERE ur.creator_feishu_user_id IS NULL AND ur.created_by IS NOT NULL
    """)

    # 2.3 删除旧外键约束
    op.drop_constraint('user_roles_user_id_fkey', 'user_roles', type_='foreignkey')
    op.drop_constraint('user_roles_created_by_fkey', 'user_roles', type_='foreignkey')

    # 2.4 删除旧字段
    op.drop_column('user_roles', 'user_id')
    op.drop_column('user_roles', 'created_by')

    # 2.5 重命名字段
    op.alter_column('user_roles', 'user_feishu_user_id', new_column_name='user_id')
    op.alter_column('user_roles', 'creator_feishu_user_id', new_column_name='created_by')

    # 2.6 添加新外键约束
    op.create_foreign_key('user_roles_user_id_fkey', 'user_roles', 'users', ['user_id'], ['feishu_user_id'], ondelete='CASCADE')
    op.create_foreign_key('user_roles_created_by_fkey', 'user_roles', 'users', ['created_by'], ['feishu_user_id'])

    # 3. 更新 resource_bindings 表（类似步骤）
    # ...

    # 4. 更新 audit_logs 表
    # 4.1 operator_id 迁移 (逻辑同 user_roles)
    op.add_column('audit_logs', sa.Column('operator_feishu_user_id', sa.String(100), nullable=True))
    op.execute("""
        UPDATE audit_logs al
        SET operator_feishu_user_id = (SELECT feishu_user_id FROM users u WHERE u.id = al.operator_id)
        WHERE al.operator_id IS NOT NULL
    """)
    # ... (删除旧外键，重命名新字段等)

    # 4.2 target_id 类型变更 (关键风险点)
    # target_id 是多态字段，存储 User/Role/Permission 的 ID。
    # 变为 String 以兼容 feishu_user_id。
    op.alter_column('audit_logs', 'target_id',
               existing_type=sa.Integer(),
               type_=sa.String(length=100),
               postgresql_using='target_id::varchar')


def downgrade() -> None:
    # 提供回滚逻辑
    pass
```

#### 4.1.2 数据一致性检查

```sql
-- 验证迁移后数据完整性
SELECT
    ur.id,
    ur.user_id as feishu_user_id,
    u.feishu_user_id as expected_feishu_user_id,
    ur.created_by
FROM user_roles ur
JOIN users u ON ur.user_id = u.feishu_user_id
WHERE ur.user_id IS NOT NULL;

-- 检查是否有孤儿记录
SELECT COUNT(*)
FROM user_roles ur
LEFT JOIN users u ON ur.user_id = u.feishu_user_id
WHERE u.feishu_user_id IS NULL;
```

**预计耗时**: 4-6小时
**执行人员**: 后端开发 + DBA
**验证标准**:
- 迁移后数据完整性 100%
- 所有外键约束正常
- 索引生效

---

### 4.2 第二阶段：后端代码重构

#### 4.2.1 修改核心认证模块

**文件**: `app/core/security.py`

```python
# 修改前
def create_access_token(
    self,
    user_id: int,  # 整型 ID
    feishu_user_id: str,
    # ...
) -> str:
    payload = {
        "sub": str(user_id),  # 转换为字符串
        # ...
    }

# 修改后
def create_access_token(
    self,
    feishu_user_id: str,  # 直接使用飞书用户 ID
    username: str,
    # ... 移除 user_id 参数
) -> str:
    payload = {
        "sub": feishu_user_id,  # 直接使用
        # ...
    }
```

**文件**: `app/core/dependencies.py`

```python
# 修改前：user_id 是整型字符串
payload = jwt.decode(token, public_key, algorithms=[settings.JWT_ALGORITHM])
user_id = int(payload.get("sub"))  # 需要转换

# 修改后：sub 直接是 feishu_user_id
payload = jwt.decode(token, public_key, algorithms=[settings.JWT_ALGORITHM])
feishu_user_id = payload.get("sub")  # 直接使用
```

#### 4.2.2 重构 UserService

**文件**: `app/users/service.py`

```python
# 修改前
class UserService:
    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        result = await self.db.execute(select(User).filter(User.id == user_id))
        return result.scalar_one_or_none()

# 修改后
class UserService:
    async def get_user_by_feishu_id(self, feishu_user_id: str) -> Optional[User]:
        result = await self.db.execute(
            select(User).filter(User.feishu_user_id == feishu_user_id)
        )
        return result.scalar_one_or_none()

    # 保留方法名但更新实现，或重命
    async def get_user_by_id(self, user_id: str) -> Optional[User]:  # 改为 string
        result = await self.db.execute(
            select(User).filter(User.feishu_user_id == user_id)
        )
        return result.scalar_one_or_none()
```

**同步用户方法修改：**
```python
# 修改前
async def sync_user_from_feishu(self, user_info: Dict) -> User:
    feishu_user_id = user_info.get("user_id") or user_info.get("open_id")
    result = await self.db.execute(
        select(User).filter(User.feishu_user_id == feishu_user_id)
    )
    user = result.scalar_one_or_none()
    # ... 创建或更新
    return user  # 返回的 user.id 用于后续操作

# 修改后 - 保持逻辑不变，但后续操作使用 feishu_user_id
```

#### 4.2.3 更新 API 路由

**文件**: `app/users/router.py`

```python
# 修改前
@router.get("/{user_id}", response_model=UserDetailResponse)
async def get_user(
    user_id: int,  # 整型参数
    # ...
):
    user = await user_service.get_user_by_id(user_id)
    # ...

# 修改后
@router.get("/{feishu_user_id}", response_model=UserDetailResponse)
async def get_user(
    feishu_user_id: str,  # 字符串参数
    # ...
):
    user = await user_service.get_user_by_feishu_id(feishu_user_id)
    # ...
```

**批量修改路由：**
- `GET /users/{user_id}` → `GET /users/{feishu_user_id}`
- `PUT /users/{user_id}/status` → `PUT /users/{feishu_user_id}/status`
- `GET /users/{user_id}/roles` → `GET /users/{feishu_user_id}/roles`
- `GET /users/{user_id}/permissions` → `GET /users/{feishu_user_id}/permissions`

#### 4.2.4 重构 RBAC 系统

**文件**: `app/rbac/service.py`

```python
# 修改前
async def assign_role_to_user(self, user_id: int, role_id: int, created_by: Optional[int] = None):
    user_role = UserRole(
        user_id=user_id,  # 整型
        role_id=role_id,
        created_by=created_by
    )
    # ...
    permission_notifier.notify_user_permissions_changed(user_id)

# 补充修改：通知器参数类型
# 文件: app/rbac/notifier.py
# def notify_user_permissions_changed(self, user_id: int) -> void
# 改为:
# def notify_user_permissions_changed(self, user_id: str) -> void

# 修改后
async def assign_role_to_user(self, user_id: str, role_id: int, created_by: Optional[str] = None):
    user_role = UserRole(
        user_id=user_id,  # 字符串类型
        role_id=role_id,
        created_by=created_by
    )
    # ...
    permission_notifier.notify_user_permissions_changed(user_id)
```

#### 4.2.5 更新认证相关代码

**文件**: `app/auth/router.py`

```python
# 飞书登录回调 - Token 生成部分
# 修改前
token = jwt_handler.create_access_token(
    user_id=user.id,  # 整型
    feishu_user_id=user.feishu_user_id,
    # ...
)

# 修改后
token = jwt_handler.create_access_token(
    feishu_user_id=user.feishu_user_id,  # 直接使用
    username=user.username,
    # ... 移除 user_id 参数
)
```

**Token 刷新接口：**
```python
# 修改前 - 从 refresh token 获取 user_id，查询用户信息
user_id = jwt_handler.verify_refresh_token(request.refresh_token)
result = await db.execute(select(User).where(User.id == user_id))

# 修改后 - 需要调整 refresh token 存储方式
# 方案：在 refresh token 中存储 feishu_user_id
# 注意：同时需更新 Redis 存储逻辑 (set/get) 以支持字符串 ID
feishu_user_id = jwt_handler.verify_refresh_token(request.refresh_token)
result = await db.execute(select(User).where(User.feishu_user_id == feishu_user_id))
```

#### 4.2.6 更新 Schemas

**文件**: `app/schemas/user.py`

```python
# 修改前
class UserResponse(BaseModel):
    id: int  # 整型
    feishu_user_id: str
    # ...

# 修改后
class UserResponse(BaseModel):
    feishu_user_id: str  # 作为主标识
    username: str
    # ...
    # 可选：保留 id 字段用于内部调试
    internal_id: Optional[int] = None
```

**预计耗时**: 8-12小时
**执行人员**: 后端开发团队（2人）
**验证标准**:
- 所有 API 测试通过
- Token 生成和验证正常
- RBAC 功能完整

---

### 4.3 第三阶段：前端代码重构

#### 4.3.1 更新 API 类型定义

**文件**: `src/types/api.ts`

```typescript
// 修改前
export interface User {
  id: number              // 主标识
  feishu_user_id: string
  username: string
  // ...
}

// 修改后
export interface User {
  feishu_user_id: string  // 主标识（字符串）
  username: string
  // ...
  // 可选：保留内部 ID 用于特殊场景
  internal_id?: number
}

// 更新相关接口
export interface AssignRoleRequest {
  user_id: string  // 改为 string
  role_id: number
}

export interface ResourceBinding {
  id: number
  user_id: string  // 改为 string
  created_by: string // 改为 string
  // ...
}

export interface UserRole {
  // ...
  created_by?: string // 改为 string
}

export interface ResourceBindingCreate {
  user_id: string // 改为 string
  // ...
}
```

#### 4.3.2 更新组件代码

**文件**: `src/pages/Users/UserList.tsx`

```typescript
// 修改前
columns = [
  {
    title: '操作',
    render: (_: any, record: User) => (
      <Space>
        <Button onClick={() => handleViewPermissions(record.id)}>
          查看权限
        </Button>
        <Button onClick={() => handleAssignRole(record.id)}>
          分配角色
        </Button>
      </Space>
    ),
  },
]

<Table
  rowKey="id"  // 使用 id
  dataSource={data?.items || []}
/>

// 修改后
columns = [
  {
    title: '操作',
    render: (_: any, record: User) => (
      <Space>
        <Button onClick={() => handleViewPermissions(record.feishu_user_id)}>
          查看权限
        </Button>
        <Button onClick={() => handleAssignRole(record.feishu_user_id)}>
          分配角色
        </Button>
      </Space>
    ),
  },
]

<Table
  rowKey="feishu_user_id"  // 使用飞书用户 ID
  dataSource={data?.items || []}
/>
```

**状态更新函数：**
```typescript
// 修改前
const handleStatusChange = (userId: number, checked: boolean) => {
  updateStatusMutation.mutate({
    userId,  // number
    status: checked ? 'active' : 'inactive',
  })
}

// 修改后
const handleStatusChange = (userId: string, checked: boolean) => {
  updateStatusMutation.mutate({
    userId,  // string
    status: checked ? 'active' : 'inactive',
  })
}
```

#### 4.3.3 更新组件 Props 接口

**文件**: `src/pages/Users/components/UserPermissionModal.tsx`

```typescript
// 修改前
interface Props {
  userId: number
  username: string
  visible: boolean
  onClose: () => void
}

// 修改后
interface Props {
  userId: string  // 改为 string
  username: string
  visible: boolean
  onClose: () => void
}
```

#### 4.3.4 更新 API 请求

**文件**: `src/utils/api.ts`

```typescript
// 修改前 - 接口调用
export const updateUserStatus = (userId: number, status: 'active' | 'inactive') => {
  return apiPut<User>(`/users/${userId}/status`, { status })
}

export const getUserPermissions = (userId: number) => {
  return apiGet<UserPermissionDetail>(`/users/${userId}/permissions`)
}

// 修改后
export const updateUserStatus = (userId: string, status: 'active' | 'inactive') => {
  return apiPut<User>(`/users/${userId}/status`, { status })
}

export const getUserPermissions = (userId: string) => {
  return apiGet<UserPermissionDetail>(`/users/${userId}/permissions`)
}
```

**预计耗时**: 6-8小时
**执行人员**: 前端开发团队（1-2人）
**验证标准**:
- 所有页面正常渲染
- 用户操作功能完整
- TypeScript 类型检查通过

---

### 4.4 第四阶段：测试验证

#### 4.4.1 单元测试

**测试文件**: `tests/users/test_service.py`

```python
# 测试用例示例
@pytest.mark.asyncio
async def test_get_user_by_feishu_id(db_session, test_user):
    """测试通过 feishu_user_id 获取用户"""
    service = UserService(db_session)
    user = await service.get_user_by_feishu_id(test_user.feishu_user_id)

    assert user is not None
    assert user.feishu_user_id == test_user.feishu_user_id
    assert user.username == test_user.username

@pytest.mark.asyncio
async def test_update_user_status_by_feishu_id(db_session, test_user):
    """测试通过 feishu_user_id 更新用户状态"""
    service = UserService(db_session)
    updated = await service.update_user_status(
        test_user.feishu_user_id,
        'inactive'
    )

    assert updated is not None
    assert updated.status == 'inactive'
```

#### 4.4.2 集成测试

**测试场景清单：**

| 场景 | 测试点 | 期望结果 |
|------|--------|---------|
| 飞书登录 | 新用户首次登录 | 成功创建用户，Token sub 为 feishu_user_id |
| 飞书登录 | 老用户再次登录 | 更新用户信息，Token 正常生成 |
| Token 刷新 | 使用 refresh token 获取新 token | 新 token 的 sub 为 feishu_user_id |
| 权限查询 | 查询用户角色和权限 | 返回正确的角色和资源信息 |
| 角色分配 | 为用户分配角色 | 数据库记录 user_id 为 feishu_user_id |
| 资源绑定 | 绑定用户到资源 | 数据库记录 user_id 为 feishu_user_id |
| 用户状态 | 启用/禁用用户 | 状态更新成功，查询结果正确 |

**自动化测试脚本：**
```bash
# 运行测试
pytest tests/ -v -k "test_user" --tb=short

# 覆盖率检查
pytest tests/ --cov=app.users --cov-report=html
```

#### 4.4.3 端到端测试

**前端测试场景：**

1. **用户列表页**
   - ✅ 页面正常加载，表格展示用户数据
   - ✅ 搜索功能正常工作
   - ✅ 状态切换按钮正常工作
   - ✅ 查看权限按钮点击后弹出正确数据
   - ✅ 分配角色功能正常

2. **权限管理页**
   - ✅ 角色列表正常展示
   - ✅ 为用户分配角色成功
   - ✅ 移除用户角色成功

3. **资源绑定页**
   - ✅ 资源绑定列表正常展示
   - ✅ 创建新的资源绑定成功
   - ✅ 删除资源绑定成功

**测试工具：**
- Playwright / Cypress 自动化测试
- 人工回归测试清单

**预计耗时**: 8-10小时
**执行人员**: 测试团队 + 开发团队
**验证标准**:
- 单元测试覆盖率 ≥ 80%
- 集成测试全部通过
- 端到端测试核心流程通过

---

### 4.5 第五阶段：部署上线

#### 4.5.1 预发布环境部署

```bash
# 1. 部署后端
kubectl apply -f k8s/staging/backend-deployment.yaml

# 2. 执行数据库迁移
kubectl exec -it backend-pod -- alembic upgrade head

# 3. 部署前端
npm run build:staging
kubectl apply -f k8s/staging/frontend-deployment.yaml

# 4. 验证部署
curl -f https://staging-api.authhub.com/health
curl -f https://staging.authhub.com
```

#### 4.5.2 灰度发布策略

**阶段 1：内部测试（10% 流量）**
- 仅内部员工可访问新版本
- 监控关键指标：错误率、响应时间、用户反馈
- 验证核心功能：登录、权限查询、角色分配

**阶段 2：小范围用户（30% 流量）**
- 选择部分友好用户进行测试
- 收集用户反馈，修复发现的问题
- 监控数据库性能，观察查询效率

**阶段 3：全面发布（100% 流量）**
- 全量发布新版本
- 密切监控系统指标
- 准备回滚方案

#### 4.5.3 监控指标

| 指标 | 正常范围 | 告警阈值 |
|------|---------|---------|
| API 请求错误率 | < 0.1% | > 0.5% |
| 数据库查询平均耗时 | < 100ms | > 200ms |
| 用户登录成功率 | > 99% | < 95% |
| 页面加载时间 | < 2s | > 5s |
| Token 验证失败率 | < 0.01% | > 0.1% |

**预计耗时**: 4-6小时（包含监控时间）
**执行人员**: 运维团队 + 开发团队
**验证标准**:
- 系统稳定运行 2 小时无严重问题
- 核心功能监控指标正常
- 用户反馈良好

---

## 5. 风险评估与注意事项

### 5.1 兼容性处理

**问题描述**：
- 旧版 Token 的 sub 字段存储的是 user.id，新版改为 feishu_user_id
- 已发布的客户端可能仍在使用旧的 API 接口

**解决方案**：

1. **Token 兼容性方案**
   ```python
   async def get_current_user(authorization: str = Header(...)) -> dict:
       token = authorization.replace("Bearer ", "")
       payload = jwt.decode(token, public_key, algorithms=[settings.JWT_ALGORITHM])

       sub = payload.get("sub")

       # 判断 sub 是旧版 user.id 还是新版 feishu_user_id
       if sub.isdigit():
           # 旧版 Token，查询用户
           result = await db.execute(select(User).filter(User.id == int(sub)))
           user = result.scalar_one_or_none()
           if user:
               # 更新 payload 为新版格式
               payload["sub"] = user.feishu_user_id
               return payload
       else:
           # 新版 Token，直接使用
           return payload
   ```

2. **API 版本控制**
   ```python
   # 保留旧版 API 一段时间（可选）
   @router.get("/v1/users/{user_id}", deprecated=True)
   async def get_user_by_old_id(...):
       # 假设 user_id 是旧版 ID，查询 feishu_user_id
       pass

   @router.get("/v2/users/{feishu_user_id}")
   async def get_user(...):
       # 新版实现
       pass
   ```

3. **过渡期策略**
   - 在 Token 中同时包含 user.id 和 feishu_user_id
   - 服务层同时支持两种 ID 查询
   - 给客户端足够的升级时间（建议 2-4 周）

### 5.2 数据一致性

**风险点：**
- 数据库迁移过程中可能出现数据丢失或不一致
- 外键约束更新失败导致关联数据异常

**应对措施：**

1. **迁移前备份**
   ```bash
   # 全量备份
   pg_dump -h localhost -U authhub authhubdb > backup_pre_migration_$(date +%Y%m%d).sql

   # 验证备份
   psql -h localhost -U authhub test_restore < backup_pre_migration_$(date +%Y%m%d).sql
   ```

2. **事务性迁移**
   ```python
   # 使用 Alembic 的事务特性
   def upgrade():
       try:
           # 所有操作在一个事务中
           op.execute("BEGIN")
           # ... 迁移逻辑
           op.execute("COMMIT")
       except Exception as e:
           op.execute("ROLLBACK")
           raise e
   ```

3. **数据验证脚本**
   ```python
   async def verify_migration(db: AsyncSession):
       """验证迁移后数据完整性"""
       # 检查 user_roles 表
       result = await db.execute("""
           SELECT COUNT(*) as mismatch
           FROM user_roles ur
           LEFT JOIN users u ON ur.user_id = u.feishu_user_id
           WHERE u.feishu_user_id IS NULL
       """)
       mismatch = result.scalar()
       if mismatch > 0:
           raise Exception(f"发现 {mismatch} 条无效的用户角色关联")
   ```

### 5.3 性能优化

**潜在性能问题：**
- `feishu_user_id` 为字符串类型，索引效率可能低于整型
- 外键关联查询性能可能下降

**优化策略：**

1. **索引优化**
   ```sql
   -- 确保 feishu_user_id 有索引
   CREATE INDEX idx_users_feishu_user_id ON users(feishu_user_id);

   -- 更新统计信息
   ANALYZE users;
   ANALYZE user_roles;
   ANALYZE resource_bindings;
   ```

2. **查询优化**
   ```python
   # 使用 selectinload 减少 N+1 查询
   from sqlalchemy.orm import selectinload

   result = await db.execute(
       select(User)
       .filter(User.feishu_user_id == feishu_user_id)
       .options(
           selectinload(User.roles),
           selectinload(User.resource_bindings)
       )
   )
   ```

3. **缓存策略**
   ```python
   # Redis 缓存频繁查询的用户信息
   @cached(key="user:{feishu_user_id}", ttl=300)
   async def get_user_by_feishu_id(feishu_user_id: str) -> Optional[User]:
       # 查询逻辑
       pass
   ```

### 5.4 回滚方案

**数据库回滚：**

```python
def downgrade() -> None:
    # 1. 恢复外键约束
    op.drop_constraint('user_roles_user_id_fkey', 'user_roles', type_='foreignkey')
    op.create_foreign_key('user_roles_user_id_fkey', 'user_roles', 'users', ['user_id'], ['id'])

    # 2. 字段类型回滚
    op.alter_column('user_roles', 'user_id', type_=sa.Integer, nullable=False)

    # 3. 数据回滚（如果可能）
    # 注意：需要有备份数据
```

**代码回滚：**

1. **Git 分支策略**
   ```bash
   # 创建发布分支
   git checkout -b release/user-id-migration

   # 打标签
   git tag -a v1.2.0-migration -m "User ID to Feishu User ID Migration"
   ```

2. **快速回滚命令**
   ```bash
   # 回滚数据库
   alembic downgrade 836823124d94

   # 回滚代码
   git checkout main
   git branch -D release/user-id-migration

   # 重新部署
   kubectl rollout undo deployment/backend
   ```

**回滚触发条件：**
- API 错误率 > 1%
- 用户登录失败率 > 5%
- 数据库查询性能下降 > 50%
- 核心业务功能不可用

---

## 6. 涉及文件清单

### 6.1 后端文件

| 文件路径 | 修改内容 | 优先级 |
|---------|---------|--------|
| `app/core/security.py` | JWT Token 生成逻辑，sub 字段改为 feishu_user_id | 🔴 高 |
| `app/core/dependencies.py` | Token 解析逻辑，处理 feishu_user_id | 🔴 高 |
| `app/models/user.py` | 可选：调整索引，保持 id 作为内部标识 | 🟡 中 |
| `app/models/user_role.py` | 外键字段类型从 int 改为 string | 🔴 高 |
| `app/models/resource_binding.py` | 外键字段类型从 int 改为 string | 🔴 高 |
| `app/models/audit_log.py` | operator_id 字段类型从 int 改为 string | 🟡 中 |
| `app/users/service.py` | 所有方法从使用 id 改为 feishu_user_id | 🔴 高 |
| `app/users/router.py` | API 路径参数从 user_id: int 改为 feishu_user_id: string | 🔴 高 |
| `app/users/permission_collector.py` | 权限收集逻辑使用 feishu_user_id | 🔴 高 |
| `app/auth/router.py` | 登录、刷新 token 逻辑使用 feishu_user_id | 🔴 高 |
| `app/auth/feishu.py` | 可选：优化用户同步逻辑 | 🟢 低 |
| `app/rbac/service.py` | 角色分配、权限管理使用 feishu_user_id | 🔴 高 |
| `app/rbac/router.py` | API 接口参数类型修改 | 🔴 高 |
| `app/schemas/user.py` | Response schema 更新 | 🟡 中 |
| `app/schemas/rbac.py` | RBAC 相关 schema 更新 | 🟡 中 |
| `alembic/versions/xxx_migration.py` | 数据库迁移脚本 | 🔴 高 |

### 6.2 前端文件

| 文件路径 | 修改内容 | 优先级 |
|---------|---------|--------|
| `src/types/api.ts` | User 接口 id: number → feishu_user_id: string | 🔴 高 |
| `src/pages/Users/UserList.tsx` | 表格 rowKey、操作按钮传参 | 🔴 高 |
| `src/pages/Users/components/UserPermissionModal.tsx` | Props 接口 userId 类型 | 🔴 高 |
| `src/pages/Users/components/AssignRoleModal.tsx` | Props 接口 userId 类型 | 🔴 高 |
| `src/contexts/AuthContext.tsx` | 可选：用户标识处理 | 🟡 中 |
| `src/utils/api.ts` | API 请求函数参数类型 | 🔴 高 |

### 6.3 数据库表

| 表名 | 修改字段 | 变更类型 | 影响 |
|------|---------|---------|------|
| `users` | `feishu_user_id` | 添加索引（如缺失） | 中 |
| `user_roles` | `user_id`, `created_by` | int → string | 高 |
| `resource_bindings` | `user_id`, `created_by` | int → string | 高 |
| `audit_logs` | `operator_id` | int → string | 中 |

---

## 7. 时间估算

| 阶段 | 任务 | 预计工时 | 执行人员 |
|------|------|---------|---------|
| 1 | 数据库迁移 | 4-6小时 | 后端 + DBA |
| 2 | 后端代码重构 | 8-12小时 | 后端团队（2人） |
| 3 | 前端代码重构 | 6-8小时 | 前端团队（1-2人） |
| 4 | 测试验证 | 8-10小时 | 测试 + 开发 |
| 5 | 部署上线 | 4-6小时 | 运维 + 开发 |
| **总计** | | **30-42小时** | **5-6人天** |

**建议排期：**
- **Week 1**: 数据库迁移 + 后端重构（3天）
- **Week 2**: 前端重构 + 单元测试（2天）
- **Week 3**: 集成测试 + 部署准备（2天）
- **Week 4**: 灰度发布 + 监控 + 优化（3天）

---

## 8. 相关文档

- [飞书 OAuth2.0 集成文档](./authentication/feishu-oauth.md)
- [JWT Token 设计与实现](./authentication/jwt-implementation.md)
- [RBAC 权限系统设计](./rbac/design.md)
- [数据库设计文档](./architecture/database-schema.md)
- [API 接口文档](./api/README.md)

---

## 9. 附录

### 9.1 术语表

| 术语 | 说明 |
|------|------|
| **feishu_user_id** | 飞书用户唯一标识，对应飞书开放平台的 user_id 或 open_id |
| **id** | 系统内部自增整数标识，当前作为主键使用 |
| **JWT** | JSON Web Token，用于用户认证和授权 |
| **RBAC** | 基于角色的访问控制（Role-Based Access Control） |
| **sub** | JWT Token 的标准字段，表示主题（Subject），通常存储用户标识 |

### 9.2 联系方式

- **项目负责人**: [姓名]
- **技术负责人**: [姓名]
- **数据库负责人**: [姓名]
- **测试负责人**: [姓名]

---

**文档变更记录**

| 版本 | 日期 | 修改内容 | 作者 |
|------|------|---------|------|
| 1.0 | 2025-11-28 | 初始版本 | Claude Code |

---

**审批记录**

| 审批人 | 角色 | 审批日期 | 状态 |
|--------|------|---------|------|
| | | | |
| | | | |
| | | | |

---

*本文档由 Claude Code 自动生成，基于对代码库的全面分析*
*最后更新: 2025-11-28*
