from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from db.models import Order, OrderItem
from db.models import Product as ProductModel
from models.cart import CartItem
from models.product import Product


class ProductRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_active_by_id(self, product_id: int) -> Product | None:
        statement = select(ProductModel).where(
            ProductModel.id == product_id,
            ProductModel.is_active.is_(True),
        )
        model = await self._session.scalar(statement)
        return self._to_domain(model) if model else None

    async def list_active_by_category(self, category: str) -> list[Product]:
        statement = (
            select(ProductModel)
            .where(
                ProductModel.category == category,
                ProductModel.is_active.is_(True),
            )
            .order_by(ProductModel.id)
        )
        models: Sequence[ProductModel] = (await self._session.scalars(statement)).all()
        return [self._to_domain(model) for model in models]

    @staticmethod
    def _to_domain(model: ProductModel) -> Product:
        return Product(
            id=model.id,
            name=model.name,
            category=model.category,
            price=model.price,
        )


class OrderRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create_demo_order(
        self, telegram_user_id: int, cart: list[CartItem]
    ) -> Order:
        order = Order(
            telegram_user_id=telegram_user_id,
            status="demo",
            total_price=sum(item.total_price for item in cart),
            items=[
                OrderItem(
                    product_id=item.id,
                    product_name=item.name,
                    unit_price=item.price,
                    quantity=item.quantity,
                )
                for item in cart
            ],
        )
        self._session.add(order)
        await self._session.flush()
        return order

    async def get_by_id(self, order_id: int) -> Order | None:
        statement = (
            select(Order)
            .options(selectinload(Order.items))
            .where(Order.id == order_id)
        )
        return await self._session.scalar(statement)
