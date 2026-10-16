"""add roles

Revision ID: c4e8a1b2f3d6
Revises: a19bd9e57a32
Create Date: 2026-10-16 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'c4e8a1b2f3d6'
down_revision: Union[str, None] = 'a19bd9e57a32'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

role_enum = sa.Enum('user', 'admin', name='role_enum')


def upgrade() -> None:
    op.create_table(
        'roles',
        sa.Column('name', role_enum, nullable=False),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('id')
    )
    op.create_index(op.f('ix_roles_name'), 'roles', ['name'], unique=True)

    op.add_column('users', sa.Column('role_id', sa.UUID(), nullable=True))
    op.create_foreign_key(
        'fk_users_role_id_roles', 'users', 'roles', ['role_id'], ['id']
    )


def downgrade() -> None:
    op.drop_constraint('fk_users_role_id_roles', 'users', type_='foreignkey')
    op.drop_column('users', 'role_id')

    op.drop_index(op.f('ix_roles_name'), table_name='roles')
    op.drop_table('roles')
    role_enum.drop(op.get_bind(), checkfirst=True)
