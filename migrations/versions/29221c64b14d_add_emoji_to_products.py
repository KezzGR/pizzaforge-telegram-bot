"""add emoji to products

Revision ID: 29221c64b14d
Revises: 20260819_0001
Create Date: 2026-08-22 01:26:28.291546
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "29221c64b14d"
down_revision: str | None = "20260819_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("products", sa.Column("emoji", sa.String(length=16), nullable=True))

    product_emojis = {
        1: "🍕",
        2: "🍕🌶️",
        3: "🍕🧀",
        4: "🥤",
        5: "🍊🧃",
        6: "💧",
        7: "☕",
        8: "🍟",
        9: "🧀",
        10: "🍗",
        11: "🥗",
        12: "🍰",
        13: "🍫",
        14: "🍦",
        15: "🍮☕",
    }
    products = sa.table(
        "products",
        sa.column("id", sa.Integer()),
        sa.column("emoji", sa.String(length=16)),
    )
    connection = op.get_bind()
    for product_id, emoji in product_emojis.items():
        connection.execute(
            products.update().where(products.c.id == product_id).values(emoji=emoji)
        )

    connection.execute(
        products.update().where(products.c.emoji.is_(None)).values(emoji="🍽️")
    )
    op.alter_column(
        "products",
        "emoji",
        existing_type=sa.String(length=16),
        nullable=False,
    )


def downgrade() -> None:
    op.drop_column("products", "emoji")
