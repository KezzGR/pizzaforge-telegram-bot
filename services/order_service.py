from sqlalchemy.ext.asyncio import AsyncSession

from db.repositories import OrderRepository
from models.cart import CartItem


class OrderService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._orders = OrderRepository(session)

    async def create_demo_order(
        self, telegram_user_id: int, cart: list[CartItem]
    ) -> int:
        if not cart:
            raise ValueError("Нельзя оформить заказ с пустой корзиной")

        try:
            order = await self._orders.create_demo_order(telegram_user_id, cart)
            await self._session.commit()
        except Exception:
            await self._session.rollback()
            raise

        return order.id
