"""Заменяет составные эмодзи продуктов на одиночные.

Revision ID: 20260822_0002
Revises: 29221c64b14d
Create Date: 2026-08-22
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260822_0002"
down_revision: str | None = "29221c64b14d"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


NEW_EMOJIS: dict[int, str] = {
    1: "🍅",  # Маргарита
    2: "🌶️",  # Пепперони
    3: "🧀",  # Четыре сыра
    5: "🍊",  # Апельсиновый сок
    15: "🍮",  # Тирамису
}

PREVIOUS_EMOJIS: dict[int, str] = {
    1: "🍕",
    2: "🍕🌶️",
    3: "🍕🧀",
    5: "🍊🧃",
    15: "🍮☕",
}


def _update_product_emojis(product_emojis: dict[int, str]) -> None:
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


def upgrade() -> None:
    _update_product_emojis(NEW_EMOJIS)


def downgrade() -> None:
    _update_product_emojis(PREVIOUS_EMOJIS)
