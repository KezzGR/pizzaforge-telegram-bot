from aiogram.utils.keyboard import InlineKeyboardBuilder

import callbacks
from catalog import CATEGORY_INFO
from config import settings
from models.cart import CartItem
from models.product import Product
from services.cart_service import CartService


def _format_money(value: int) -> str:
    return f"{value:,}".replace(",", " ")


def get_start_inline_keyboard(cart_service: CartService) -> InlineKeyboardBuilder:
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text="🍕 Открыть меню", callback_data=callbacks.StartCallback(choice="menu")
    )
    keyboard.button(
        text=f"🛒 Корзина · {cart_service.get_total_quantity()}",
        callback_data=callbacks.StartCallback(choice="cart"),
    )
    keyboard.button(
        text="ℹ️ О проекте", callback_data=callbacks.StartCallback(choice="owner")
    )
    keyboard.button(
        text="💬 Связаться", callback_data=callbacks.StartCallback(choice="contact")
    )
    keyboard.adjust(1, 1, 2)
    return keyboard


def get_menu_inline_keyboard(cart_service: CartService) -> InlineKeyboardBuilder:
    keyboard = InlineKeyboardBuilder()
    for category, (emoji, label) in CATEGORY_INFO.items():
        keyboard.button(
            text=f"{emoji} {label}",
            callback_data=callbacks.MenuCallback(category=category),
        )
    keyboard.button(
        text=f"🛒 Корзина · {cart_service.get_total_quantity()}",
        callback_data=callbacks.ReturnCallback(return_to="cart"),
    )
    keyboard.button(
        text="🏠 На главную", callback_data=callbacks.ReturnCallback(return_to="start")
    )
    keyboard.adjust(2, 2, 1, 1)
    return keyboard


def get_products_inline_keyboard(
    products: list[Product], cart_service: CartService
) -> InlineKeyboardBuilder:
    keyboard = InlineKeyboardBuilder()
    for product in products:
        keyboard.button(
            text=f"{product.emoji} {product.name} · {_format_money(product.price)} ₽",
            callback_data=callbacks.InCartCallback(product_id=product.id),
        )
    keyboard.button(
        text=f"🛒 Корзина · {cart_service.get_total_quantity()}",
        callback_data=callbacks.ReturnCallback(return_to="cart"),
    )
    keyboard.button(
        text="⬅️ К категориям",
        callback_data=callbacks.ReturnCallback(return_to="menu"),
    )
    keyboard.adjust(*([1] * len(products)), 1, 1)
    return keyboard


def get_cart_inline_keyboard(cart: list[CartItem]) -> InlineKeyboardBuilder:
    keyboard = InlineKeyboardBuilder()
    if cart:
        for item in cart:
            keyboard.button(
                text="➖",
                callback_data=callbacks.CartItemCallback(
                    product_id=item.id, action="decrease"
                ),
            )
            keyboard.button(
                text=f"{item.emoji} {item.quantity} шт.",
                callback_data=callbacks.CartItemCallback(
                    product_id=item.id, action="details"
                ),
            )
            keyboard.button(
                text="➕",
                callback_data=callbacks.CartItemCallback(
                    product_id=item.id, action="increase"
                ),
            )
        keyboard.button(
            text="📦 К оформлению",
            callback_data=callbacks.CartEventCallback(event="order"),
        )
        keyboard.button(
            text="🗑 Очистить корзину",
            callback_data=callbacks.CartEventCallback(event="clear_request"),
        )
        keyboard.button(
            text="🍕 Добавить блюда",
            callback_data=callbacks.ReturnCallback(return_to="menu"),
        )
    else:
        keyboard.button(
            text="🍕 Выбрать блюда",
            callback_data=callbacks.ReturnCallback(return_to="menu"),
        )
    keyboard.button(
        text="🏠 На главную", callback_data=callbacks.ReturnCallback(return_to="start")
    )
    if cart:
        keyboard.adjust(*([3] * len(cart)), 1, 1, 1, 1)
    else:
        keyboard.adjust(1, 1)
    return keyboard


def get_clear_cart_inline_keyboard() -> InlineKeyboardBuilder:
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text="🗑 Да, очистить",
        callback_data=callbacks.CartEventCallback(event="clear_confirm"),
    )
    keyboard.button(
        text="↩️ Оставить товары",
        callback_data=callbacks.CartEventCallback(event="clear_cancel"),
    )
    keyboard.adjust(1, 1)
    return keyboard


def get_order_inline_keyboard() -> InlineKeyboardBuilder:
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text="✅ Подтвердить заказ",
        callback_data=callbacks.OrderCallback(confirm=True),
    )
    keyboard.button(
        text="⬅️ Изменить корзину",
        callback_data=callbacks.OrderCallback(confirm=False),
    )
    keyboard.adjust(1, 1)
    return keyboard


def get_order_confirm_inline_keyboard() -> InlineKeyboardBuilder:
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="💬 Хочу похожего бота", url=settings.tg_url)
    keyboard.button(
        text="🍕 Повторить сценарий",
        callback_data=callbacks.ReturnCallback(return_to="menu"),
    )
    keyboard.button(
        text="🏠 На главную", callback_data=callbacks.ReturnCallback(return_to="start")
    )
    keyboard.adjust(1, 1, 1)
    return keyboard


def get_owner_inline_keyboard() -> InlineKeyboardBuilder:
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="💬 Обсудить похожего бота", url=settings.tg_url)
    keyboard.button(text="💻 Исходный код на GitHub", url=settings.github_url)
    keyboard.button(
        text="🏠 На главную", callback_data=callbacks.ReturnCallback(return_to="start")
    )
    keyboard.adjust(1, 1, 1)
    return keyboard


def get_contact_inline_keyboard() -> InlineKeyboardBuilder:
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="💬 Открыть чат с Никитой", url=settings.tg_url)
    keyboard.button(
        text="🏠 На главную", callback_data=callbacks.ReturnCallback(return_to="start")
    )
    keyboard.adjust(1, 1)
    return keyboard
