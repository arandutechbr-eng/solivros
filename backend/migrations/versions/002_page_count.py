"""add page_count to books

Revision ID: 002_page_count
Revises: 001_initial
Create Date: 2026-08-17
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "002_page_count"
down_revision: Union[str, None] = "001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("books", sa.Column("page_count", sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column("books", "page_count")
