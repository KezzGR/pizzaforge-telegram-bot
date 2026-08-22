from models.cart import CartItem
from models.product import Product


class CartService:
    """
    Сервис для работы с корзиной пользователя.
    Пока работает с данными из FSM (список CartItem).
    В будущем легко переключим на работу с БД.
    """

    def __init__(self, cart_data: list[CartItem]):
        """
        Принимает текущую корзину (список CartItem).
        Важно: мы не храним состояние внутри сервиса,
        а работаем с переданным списком. Это позволяет
        использовать сервис с разными источниками данных.
        """
        self._cart: list[CartItem] = cart_data

    @classmethod
    def from_state(cls, data: dict):
        """
        Фабричный метод для создания сервиса из данных FSM.
        """
        cart: list[CartItem] = data.get("cart", [])

        if cart and isinstance(cart[0], dict):
            cart = [CartItem(**item) for item in cart]

        return cls(cart)

    def get_items(self) -> list[CartItem]:
        """Возвращает копию списка товаров в корзине."""
        return self._cart.copy()

    def get_item(self, product_id: int) -> CartItem:
        """Возвращает позицию корзины по идентификатору товара."""
        return self._find_item(product_id)

    def get_total_quantity(self) -> int:
        """Возвращает общее количество товаров в корзине."""
        return sum(item.quantity for item in self._cart)

    def add_product(self, product: Product | None) -> CartItem:
        """
        Добавляет товар в корзину. Если товар уже есть, увеличивает количество.
        Возвращает добавленный/обновленный элемент.
        """
        if not product:
            raise ValueError("Товар не найден или больше недоступен")

        for item in self._cart:
            if item.id == product.id:
                item.quantity += 1
                return item

        item = CartItem(
            id=product.id,
            name=product.name,
            emoji=product.emoji,
            price=product.price,
            quantity=1,
        )

        self._cart.append(item)
        return item

    def increase_quantity(self, product_id: int) -> CartItem:
        """Увеличивает количество позиции в корзине на единицу."""
        item = self._find_item(product_id)
        item.quantity += 1
        return item

    def decrease_quantity(self, product_id: int) -> tuple[CartItem, bool]:
        """Уменьшает количество или удаляет последнюю единицу позиции."""
        item = self._find_item(product_id)
        if item.quantity == 1:
            self._cart.remove(item)
            return item, True

        item.quantity -= 1
        return item, False

    def get_total_price(self) -> int:
        """Общая стоимость всех товаров в корзине."""
        return sum(item.total_price for item in self._cart)

    def clear(self) -> None:
        """Очищает корзину."""
        self._cart.clear()

    def is_empty(self) -> bool:
        """Проверяет, пуста ли корзина."""
        return len(self._cart) == 0

    def _find_item(self, product_id: int) -> CartItem:
        for item in self._cart:
            if item.id == product_id:
                return item
        raise ValueError("Позиция больше не находится в корзине")

    def get_cart_data(self) -> list[dict]:
        """Возвращает сериализуемые данные для FSM-хранилища."""
        return [item.model_dump() for item in self._cart]
