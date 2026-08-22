from aiogram.filters.callback_data import CallbackData


class StartCallback(CallbackData, prefix="start"):
    choice: str


class MenuCallback(CallbackData, prefix="menu"):
    category: str


class InCartCallback(CallbackData, prefix="incart"):
    product_id: int


class CartEventCallback(CallbackData, prefix="event"):
    event: str


class CartItemCallback(CallbackData, prefix="cartitem"):
    product_id: int
    action: str


class OrderCallback(CallbackData, prefix="order"):
    confirm: bool


class ReturnCallback(CallbackData, prefix="return"):
    return_to: str
