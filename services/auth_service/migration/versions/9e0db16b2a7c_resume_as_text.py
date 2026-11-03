"""Allow resumes longer than 10,000 characters.

Revision ID: 9e0db16b2a7c
Revises: 635a59fcdd98
Create Date: 2026-11-03
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "9e0db16b2a7c"
down_revision: Union[str, Sequence[str], None] = "635a59fcdd98"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "users",
        "resume",
        existing_type=sa.String(length=10000),
        type_=sa.Text(),
        existing_nullable=True,
    )


def downgrade() -> None:
    op.alter_column(
        "users",
        "resume",
        existing_type=sa.Text(),
        type_=sa.String(length=10000),
        existing_nullable=True,
        postgresql_using="LEFT(resume, 10000)",
    )
