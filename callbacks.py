from aiogram.filters.callback_data import CallbackData


class StartCallback(CallbackData, prefix="start"):
    choice: str


class MenuCallback(CallbackData, prefix="menu"):
    category: str


class InCartCallback(CallbackData, prefix="incart"):
    product_id: int


class CartEventCallback(CallbackData, prefix="event"):
    event: str
    page: int = 0


class CartPageCallback(CallbackData, prefix="cartpage"):
    page: int


class CartEditCallback(CallbackData, prefix="cartedit"):
    product_id: int
    page: int


class CartQuantityCallback(CallbackData, prefix="cartqty"):
    product_id: int
    action: str
    page: int


class OrderCallback(CallbackData, prefix="order"):
    confirm: bool
    page: int = 0


class ReturnCallback(CallbackData, prefix="return"):
    return_to: str
