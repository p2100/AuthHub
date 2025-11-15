# Alembic 数据库迁移使用指南

本项目使用 Alembic 进行数据库迁移管理。

## 环境要求

- PostgreSQL 数据库（本地或 Docker）
- 已安装 asyncpg: `uv add asyncpg`
- 已安装 greenlet: `uv add greenlet`

## 配置说明

本项目使用异步 SQLAlchemy，但 Alembic 本身需要同步连接。系统会自动处理 URL 转换：

- 应用使用: `postgresql+asyncpg://...` （异步）
- Alembic 使用: `postgresql://...` （同步）

该转换在 `alembic/env.py` 中自动完成，无需手动配置。

## 常用命令

### 1. 生成迁移文件

当模型发生变更后，使用以下命令生成迁移文件：

```bash
uv run alembic revision --autogenerate -m "描述变更内容"
```

例如：
```bash
uv run alembic revision --autogenerate -m "Add user email column"
```

**最佳实践：**
- 使用英文描述，简洁明了
- 描述具体的变更内容（如：add/remove/change）
- 每个 migration 只做一件事，便于回滚

### 2. 执行迁移

将数据库升级到最新版本：

```bash
uv run alembic upgrade head
```

**输出示例：**
```
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade  -> xxxxxxx, Initial migration
```

### 3. 查看当前版本

查看数据库当前 migration 版本：

```bash
uv run alembic current
```

**输出示例：**
```
836823124d94 (head)
```

### 4. 查看版本历史

查看所有 migration 历史：

```bash
uv run alembic history
```

**输出示例：**
```
836823124d94 -> 621f9cbc96e7 (head), Add user email column
<base> -> 836823124d94, Initial migration
```

### 5. 回滚迁移

#### 回滚到上一个版本
```bash
uv run alembic downgrade -1
```

#### 回滚到指定版本
```bash
uv run alembic downgrade 836823124d94
```

#### 回滚所有迁移
```bash
uv run alembic downgrade base
```

**注意：** 回滚会丢失数据，请谨慎操作！

## 工作流程

### 1. 开发新功能时的流程

```bash
# 1. 修改模型文件（app/models/*.py）
# 2. 生成 migration
uv run alembic revision --autogenerate -m "Add new feature"

# 3. 检查生成的 migration 文件（可选但推荐）
# 查看 alembic/versions/xxxx_*.py

# 4. 执行迁移
uv run alembic upgrade head

# 5. 验证数据库变更
uv run alembic current
```

### 2. 首次初始化数据库

```bash
# 1. 确保所有模型都已定义
# 2. 生成初始 migration
uv run alembic revision --autogenerate -m "Initial migration"

# 3. 执行迁移
uv run alembic upgrade head

# 4. 验证
uv run alembic current
# 输出: xxxxxxx (head)
```

### 3. 团队协作时的流程

```bash
# 1. 拉取最新代码
git pull origin main

# 2. 执行迁移（应用团队中其他人创建的 migration）
uv run alembic upgrade head

# 3. 如果遇到冲突，手动解决后生成新的 migration
uv run alembic revision --autogenerate -m "Resolve conflict"
uv run alembic upgrade head
```

## 常见问题

### 1. "No changes detected" 但模型已修改

可能原因：
- 模型文件没有被正确导入在 `alembic/env.py` 中
- 模型继承的 Base 不正确
- 数据库已经是最新状态

解决方案：
```python
# 确保 alembic/env.py 中有：
from app import models  # 导入所有模型
from app.core.database import Base

target_metadata = Base.metadata
```

### 2. Migration 执行失败

常见原因：
- 数据库连接失败（检查 DATABASE_URL）
- 手动修改了数据库结构
- Migration 脚本有语法错误

解决方案：
```bash
# 1. 检查数据库连接
# 2. 手动修复数据库状态
# 3. 标记为已执行（不推荐，仅用于恢复）
uv run alembic stamp head
```

### 3. Alembic 无法连接到数据库

检查：
- 数据库服务是否运行
- DATABASE_URL 是否正确
- 用户名密码是否正确
- 端口是否开放

```bash
# 测试 PostgreSQL 连接（需要安装 psql）
psql postgresql://testuser:testpass123@localhost:5432/testdb
```

### 4. 异步和同步驱动的区别

本项目配置自动处理 URL 转换：

```python
# alembic/env.py
sync_database_url = settings.DATABASE_URL.replace('postgresql+asyncpg://', 'postgresql://')
config.set_main_option('sqlalchemy.url', sync_database_url)
```

**注意：** 如果修改了数据库驱动，需要同步更新此配置。

## Migration 文件结构

```python
# alembic/versions/xxxx_migration_name.py

"""Migration description

Revision ID: xxxxxxx
Revises: yyyyyyy (前一个版本，或 None 如果是第一个)
Create Date: 2025-01-15 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'xxxxxxx'
down_revision = 'yyyyyyy'  # 前一个版本，None 表示是第一个
depends_on = None


def upgrade() -> None:
    # 升级操作
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        ...
    )
    op.create_index(...)


def downgrade() -> None:
    # 回滚操作（与 upgrade 相反）
    op.drop_index(...)
    op.drop_table('users')
```

## 重要提示

1. **不要在 migration 中编辑已有的 `down_revision`**
   - Alembic 用它来构建 migration 依赖树
   - 手动修改会导致依赖关系混乱

2. **不要删除旧的 migration 文件**
   - 即使它们已经被应用
   - 保留历史记录，便于回滚和审计

3. **在执行 migration 前备份数据**（生产环境）
   ```bash
   pg_dump postgresql://testuser:testpass123@localhost:5432/testdb > backup.sql
   ```

4. **在开发环境测试 migration**
   - 先执行 `alembic downgrade base`
   - 再执行 `alembic upgrade head`
   - 确保双向都能正常工作

5. **将 migration 文件提交到 Git**
   ```bash
   git add alembic/versions/
   git commit -m "Add database migration for user email"
   ```

## 进阶用法

### 生成空 migration（手动编写 SQL）

```bash
uv run alembic revision -m "Manual migration"
```

然后手动编辑生成的文件，使用原始 SQL：

```python
def upgrade() -> None:
    op.execute("""
        CREATE INDEX CONCURRENTLY idx_user_email
        ON users (email)
        WHERE email IS NOT NULL;
    """)
```

### 标记数据库为已更新（不使用 migration）

```bash
uv run alembic stamp head
```

**警告：** 这会跳过 migration 执行，仅更新版本号。仅在 recovery 时使用。

### 在 migration 中导入模型

```python
from alembic import op
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker

# 导入模型
from app.models.user import User
from app.core.database import Base


def upgrade() -> None:
    # 创建表
    op.create_table(...)

    # 使用 ORM 操作数据
    bind = op.get_bind()
    Session = sessionmaker(bind=bind)
    session = Session()

    # 添加初始数据
    session.add(User(name="Admin", email="admin@example.com"))
    session.commit()
```

## 参考资料

- [Alembic 官方文档](https://alembic.sqlalchemy.org/)
- [SQLAlchemy 2.0 异步支持](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [Alembic Cookbook](https://alembic.sqlalchemy.org/en/latest/cookbook.html)

## 寻求帮助

如果遇到问题：

1. 查看 Alembic 官方文档
2. 检查 migration 文件语法
3. 查看数据库连接配置
4. 在团队中寻求帮助
