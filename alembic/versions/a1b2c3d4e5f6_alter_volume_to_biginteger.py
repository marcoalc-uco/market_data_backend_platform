"""Alter volume column to BigInteger in market_prices

Revision ID: a1b2c3d4e5f6
Revises: 28ed6f4d74d0
Create Date: 2026-02-17 18:00:00.000000

Reason: Crypto volumes (e.g. BTC) can exceed INTEGER max (2,147,483,647).
BigInteger supports up to 9,223,372,036,854,775,807.
"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, Sequence[str], None] = "28ed6f4d74d0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Change volume column from INTEGER to BIGINT."""
    op.alter_column(
        "market_prices",
        "volume",
        existing_type=sa.Integer(),
        type_=sa.BigInteger(),
        existing_nullable=False,
    )


def downgrade() -> None:
    """Revert volume column from BIGINT to INTEGER."""
    op.alter_column(
        "market_prices",
        "volume",
        existing_type=sa.BigInteger(),
        type_=sa.Integer(),
        existing_nullable=False,
    )
