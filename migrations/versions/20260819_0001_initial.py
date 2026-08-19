"""Создаёт каталог и таблицы демо-заказов.

Revision ID: 20260819_0001
Revises:
Create Date: 2026-08-19
"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "20260819_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


PRODUCTS = [
    {"id": 1, "name": "Маргарита", "category": "pizza", "price": 450},
    {"id": 2, "name": "Пепперони", "category": "pizza", "price": 550},
    {"id": 3, "name": "Четыре сыра", "category": "pizza", "price": 600},
    {"id": 4, "name": "Кола", "category": "drinks", "price": 100},
    {"id": 5, "name": "Апельсиновый сок", "category": "drinks", "price": 120},
    {"id": 6, "name": "Вода", "category": "drinks", "price": 80},
    {"id": 7, "name": "Кофе", "category": "drinks", "price": 150},
    {"id": 8, "name": "Картофель фри", "category": "snacks", "price": 150},
    {"id": 9, "name": "Сырные палочки", "category": "snacks", "price": 200},
    {"id": 10, "name": "Наггетсы", "category": "snacks", "price": 180},
    {"id": 11, "name": "Овощной салат", "category": "snacks", "price": 170},
    {"id": 12, "name": "Чизкейк", "category": "desserts", "price": 250},
    {"id": 13, "name": "Брауни", "category": "desserts", "price": 200},
    {"id": 14, "name": "Мороженое", "category": "desserts", "price": 150},
    {"id": 15, "name": "Тирамису", "category": "desserts", "price": 300},
]


def upgrade() -> None:
    products = op.create_table(
        "products",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("category", sa.String(length=50), nullable=False),
        sa.Column("price", sa.Integer(), nullable=False),
        sa.Column(
            "is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.CheckConstraint("price >= 0", name="ck_products_price_non_negative"),
    )
    op.create_index(
        "ix_products_category_active",
        "products",
        ["category", "is_active"],
    )

    op.create_table(
        "orders",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("telegram_user_id", sa.BigInteger(), nullable=False),
        sa.Column(
            "status",
            sa.String(length=20),
            server_default=sa.text("'demo'"),
            nullable=False,
        ),
        sa.Column("total_price", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.CheckConstraint(
            "total_price >= 0", name="ck_orders_total_price_non_negative"
        ),
    )
    op.create_index("ix_orders_telegram_user_id", "orders", ["telegram_user_id"])
    op.create_index("ix_orders_created_at", "orders", ["created_at"])

    op.create_table(
        "order_items",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "order_id",
            sa.Integer(),
            sa.ForeignKey("orders.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "product_id",
            sa.Integer(),
            sa.ForeignKey("products.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("product_name", sa.String(length=100), nullable=False),
        sa.Column("unit_price", sa.Integer(), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.CheckConstraint(
            "unit_price >= 0", name="ck_order_items_unit_price_non_negative"
        ),
        sa.CheckConstraint(
            "quantity > 0", name="ck_order_items_quantity_positive"
        ),
        sa.UniqueConstraint(
            "order_id", "product_id", name="uq_order_items_order_product"
        ),
    )
    op.create_index("ix_order_items_order_id", "order_items", ["order_id"])
    op.create_index("ix_order_items_product_id", "order_items", ["product_id"])

    op.bulk_insert(products, PRODUCTS)
    op.execute(
        "SELECT setval(pg_get_serial_sequence('products', 'id'), "
        "(SELECT MAX(id) FROM products))"
    )


def downgrade() -> None:
    op.drop_index("ix_order_items_product_id", table_name="order_items")
    op.drop_index("ix_order_items_order_id", table_name="order_items")
    op.drop_table("order_items")
    op.drop_index("ix_orders_created_at", table_name="orders")
    op.drop_index("ix_orders_telegram_user_id", table_name="orders")
    op.drop_table("orders")
    op.drop_index("ix_products_category_active", table_name="products")
    op.drop_table("products")
