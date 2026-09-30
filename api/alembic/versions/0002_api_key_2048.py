"""api_key 1024->2048（REQ-012 Fernet 密文包住 1024 明文上限）

Revision ID: 0002
Revises: 0001
Create Date: 2026-09-29
"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = '0002'
down_revision: str | Sequence[str] | None = '0001'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 只改列类型不动数据（存量明文靠双读兜底，下次写回收敛为密文）。
    op.alter_column('model_providers', 'api_key',
               existing_type=sa.String(length=1024),
               type_=sa.String(length=2048),
               existing_nullable=False)


def downgrade() -> None:
    # 逆向缩列：密文可能截断，仅 dev 可用，生产禁用（见 docs/release.md）。
    op.alter_column('model_providers', 'api_key',
               existing_type=sa.String(length=2048),
               type_=sa.String(length=1024),
               existing_nullable=False)
