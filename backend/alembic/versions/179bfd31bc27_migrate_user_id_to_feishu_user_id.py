"""migrate_user_id_to_feishu_user_id

Revision ID: 179bfd31bc27
Revises: 836823124d94
Create Date: 2025-11-28 12:12:21.434103

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '179bfd31bc27'
down_revision: Union[str, None] = '836823124d94'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. 为 users 表 feishu_user_id 字段创建索引（如不存在）
    # 注意：根据 autogenerate 结果，users 表可能已经有索引了，这里先检查一下，或者直接跳过如果已存在
    # 既然 autogenerate 没生成 create_index，说明可能已有。但为了保险起见，我们可以不做这一步，
    # 或者如果这是第一次引入该字段的唯一性（之前是 nullable? 不，之前也是 unique=True），
    # 让我们假设 users 表结构本身不需要变更，只是被引用的方式变了。

    # ==================== User Roles Table ====================
    # 1. Add new columns
    op.add_column('user_roles', sa.Column('user_feishu_user_id', sa.String(100), nullable=True))
    op.add_column('user_roles', sa.Column('creator_feishu_user_id', sa.String(100), nullable=True))
    
    # 2. Migrate data
    op.execute("""
        UPDATE user_roles ur
        SET user_feishu_user_id = (SELECT feishu_user_id FROM users u WHERE u.id = ur.user_id)
        WHERE ur.user_feishu_user_id IS NULL AND ur.user_id IS NOT NULL
    """)
    op.execute("""
        UPDATE user_roles ur
        SET creator_feishu_user_id = (SELECT feishu_user_id FROM users u WHERE u.id = ur.created_by)
        WHERE ur.creator_feishu_user_id IS NULL AND ur.created_by IS NOT NULL
    """)

    # 3. Drop old constraints
    op.drop_constraint('user_roles_user_id_fkey', 'user_roles', type_='foreignkey')
    op.drop_constraint('user_roles_created_by_fkey', 'user_roles', type_='foreignkey')
    
    # 4. Drop old columns
    op.drop_column('user_roles', 'user_id')
    op.drop_column('user_roles', 'created_by')

    # 5. Rename new columns
    op.alter_column('user_roles', 'user_feishu_user_id', new_column_name='user_id', nullable=False)
    op.alter_column('user_roles', 'creator_feishu_user_id', new_column_name='created_by')

    # 6. Create new constraints
    op.create_foreign_key(None, 'user_roles', 'users', ['user_id'], ['feishu_user_id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'user_roles', 'users', ['created_by'], ['feishu_user_id'])


    # ==================== Resource Bindings Table ====================
    # 1. Add new columns
    op.add_column('resource_bindings', sa.Column('user_feishu_user_id', sa.String(100), nullable=True))
    op.add_column('resource_bindings', sa.Column('creator_feishu_user_id', sa.String(100), nullable=True))

    # 2. Migrate data
    op.execute("""
        UPDATE resource_bindings rb
        SET user_feishu_user_id = (SELECT feishu_user_id FROM users u WHERE u.id = rb.user_id)
        WHERE rb.user_feishu_user_id IS NULL AND rb.user_id IS NOT NULL
    """)
    op.execute("""
        UPDATE resource_bindings rb
        SET creator_feishu_user_id = (SELECT feishu_user_id FROM users u WHERE u.id = rb.created_by)
        WHERE rb.creator_feishu_user_id IS NULL AND rb.created_by IS NOT NULL
    """)

    # 3. Drop old constraints
    op.drop_constraint('resource_bindings_user_id_fkey', 'resource_bindings', type_='foreignkey')
    op.drop_constraint('resource_bindings_created_by_fkey', 'resource_bindings', type_='foreignkey')

    # 4. Drop old columns
    op.drop_column('resource_bindings', 'user_id')
    op.drop_column('resource_bindings', 'created_by')

    # 5. Rename new columns
    op.alter_column('resource_bindings', 'user_feishu_user_id', new_column_name='user_id', nullable=False)
    op.alter_column('resource_bindings', 'creator_feishu_user_id', new_column_name='created_by')

    # 6. Create new constraints
    op.create_foreign_key(None, 'resource_bindings', 'users', ['user_id'], ['feishu_user_id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'resource_bindings', 'users', ['created_by'], ['feishu_user_id'])


    # ==================== Audit Logs Table ====================
    # 1. Add new columns
    op.add_column('audit_logs', sa.Column('operator_feishu_user_id', sa.String(100), nullable=True))
    # Target ID is polymorphic, so we need a new string column for it too
    op.add_column('audit_logs', sa.Column('target_id_str', sa.String(100), nullable=True))

    # 2. Migrate data
    # 2.1 Migrate operator_id (User ID -> Feishu User ID)
    op.execute("""
        UPDATE audit_logs al
        SET operator_feishu_user_id = (SELECT feishu_user_id FROM users u WHERE u.id = al.operator_id)
        WHERE al.operator_feishu_user_id IS NULL AND al.operator_id IS NOT NULL
    """)

    # 2.2 Migrate target_id
    # Case A: target_type = 'user' -> lookup feishu_user_id
    op.execute("""
        UPDATE audit_logs al
        SET target_id_str = (SELECT feishu_user_id FROM users u WHERE u.id = al.target_id)
        WHERE al.target_type = 'user' AND al.target_id IS NOT NULL
    """)
    # Case B: target_type != 'user' -> cast int to string
    op.execute("""
        UPDATE audit_logs al
        SET target_id_str = CAST(target_id AS VARCHAR)
        WHERE al.target_type != 'user' AND al.target_id IS NOT NULL
    """)

    # 3. Drop old constraints
    op.drop_constraint('audit_logs_operator_id_fkey', 'audit_logs', type_='foreignkey')

    # 4. Drop old columns
    op.drop_column('audit_logs', 'operator_id')
    op.drop_column('audit_logs', 'target_id')

    # 5. Rename new columns
    op.alter_column('audit_logs', 'operator_feishu_user_id', new_column_name='operator_id')
    op.alter_column('audit_logs', 'target_id_str', new_column_name='target_id')

    # 6. Create new constraints
    op.create_foreign_key(None, 'audit_logs', 'users', ['operator_id'], ['feishu_user_id'])


def downgrade() -> None:
    # This is a complex destructive migration. Downgrade is best effort but might lose data if feishu_user_id -> id mapping is lost or not reversible easily without a lookup.
    # For now, we will try to reverse the schema changes, but data restoration would require a backup or complex logic.
    
    # 简化的回滚逻辑：重建旧字段，尝试转回 Integer
    
    # ==================== Audit Logs ====================
    op.drop_constraint(None, 'audit_logs', type_='foreignkey')
    op.alter_column('audit_logs', 'operator_id', new_column_name='operator_feishu_user_id')
    op.add_column('audit_logs', sa.Column('operator_id', sa.Integer(), nullable=True))
    op.create_foreign_key('audit_logs_operator_id_fkey', 'audit_logs', 'users', ['operator_id'], ['id'])
    
    # Reverting target_id
    op.alter_column('audit_logs', 'target_id', new_column_name='target_id_str')
    op.add_column('audit_logs', sa.Column('target_id', sa.Integer(), nullable=True))
    
    op.drop_column('audit_logs', 'operator_feishu_user_id')
    op.drop_column('audit_logs', 'target_id_str')


    # ==================== Resource Bindings ====================
    op.drop_constraint(None, 'resource_bindings', type_='foreignkey')
    op.drop_constraint(None, 'resource_bindings', type_='foreignkey')
    
    op.alter_column('resource_bindings', 'user_id', new_column_name='user_feishu_user_id')
    op.alter_column('resource_bindings', 'created_by', new_column_name='creator_feishu_user_id')
    
    op.add_column('resource_bindings', sa.Column('user_id', sa.Integer(), nullable=True)) # Nullable first
    op.add_column('resource_bindings', sa.Column('created_by', sa.Integer(), nullable=True))
    
    op.create_foreign_key('resource_bindings_user_id_fkey', 'resource_bindings', 'users', ['user_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('resource_bindings_created_by_fkey', 'resource_bindings', 'users', ['created_by'], ['id'])
    
    op.drop_column('resource_bindings', 'user_feishu_user_id')
    op.drop_column('resource_bindings', 'creator_feishu_user_id')


    # ==================== User Roles ====================
    op.drop_constraint(None, 'user_roles', type_='foreignkey')
    op.drop_constraint(None, 'user_roles', type_='foreignkey')

    op.alter_column('user_roles', 'user_id', new_column_name='user_feishu_user_id')
    op.alter_column('user_roles', 'created_by', new_column_name='creator_feishu_user_id')
    
    op.add_column('user_roles', sa.Column('user_id', sa.Integer(), nullable=True))
    op.add_column('user_roles', sa.Column('created_by', sa.Integer(), nullable=True))

    op.create_foreign_key('user_roles_user_id_fkey', 'user_roles', 'users', ['user_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('user_roles_created_by_fkey', 'user_roles', 'users', ['created_by'], ['id'])

    op.drop_column('user_roles', 'user_feishu_user_id')
    op.drop_column('user_roles', 'creator_feishu_user_id')