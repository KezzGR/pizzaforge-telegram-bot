from aiogram.utils.keyboard import InlineKeyboardBuilder

import callbacks
from catalog import CATEGORY_INFO
from config import settings
from models.cart import CartItem
from models.product import Product


def get_start_inline_keyboard() -> InlineKeyboardBuilder:
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text="🍕 Открыть меню", callback_data=callbacks.StartCallback(choice="menu")
    )
    keyboard.button(
        text="🛒 Моя корзина", callback_data=callbacks.StartCallback(choice="cart")
    )
    keyboard.button(
        text="👨‍💻 О проекте", callback_data=callbacks.StartCallback(choice="owner")
    )
    keyboard.button(
        text="📩 Связаться", callback_data=callbacks.StartCallback(choice="contact")
    )
    keyboard.adjust(1, 1, 2)
    return keyboard


def get_menu_inline_keyboard() -> InlineKeyboardBuilder:
    keyboard = InlineKeyboardBuilder()
    for category, (emoji, label) in CATEGORY_INFO.items():
        keyboard.button(
            text=f"{emoji} {label}",
            callback_data=callbacks.MenuCallback(category=category),
        )
    keyboard.button(
        text="🛒 Корзина", callback_data=callbacks.ReturnCallback(return_to="cart")
    )
    keyboard.button(
        text="⬅️ На главную", callback_data=callbacks.ReturnCallback(return_to="start")
    )
    keyboard.adjust(2, 2, 2)
    return keyboard


def get_products_inline_keyboard(products: list[Product]) -> InlineKeyboardBuilder:
    keyboard = InlineKeyboardBuilder()
    for product in products:
        emoji = CATEGORY_INFO[product.category][0]
        keyboard.button(
            text=f"{emoji} {product.name} — {product.price} ₽",
            callback_data=callbacks.InCartCallback(product_id=product.id),
        )
    keyboard.button(
        text="🛒 Корзина", callback_data=callbacks.ReturnCallback(return_to="cart")
    )
    keyboard.button(
        text="⬅️ К категориям",
        callback_data=callbacks.ReturnCallback(return_to="menu"),
    )
    keyboard.adjust(*([1] * len(products)), 2)
    return keyboard


def get_cart_inline_keyboard(cart: list[CartItem]) -> InlineKeyboardBuilder:
    keyboard = InlineKeyboardBuilder()
    if cart:
        keyboard.button(
            text="📦 Оформить демо-заказ",
            callback_data=callbacks.CartEventCallback(event="order"),
        )
        keyboard.button(
            text="🗑 Очистить корзину",
            callback_data=callbacks.CartEventCallback(event="clear"),
        )
    keyboard.button(
        text="🍕 Перейти в меню",
        callback_data=callbacks.ReturnCallback(return_to="menu"),
    )
    keyboard.button(
        text="⬅️ На главную", callback_data=callbacks.ReturnCallback(return_to="start")
    )
    keyboard.adjust(1)
    return keyboard


def get_order_inline_keyboard() -> InlineKeyboardBuilder:
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text="✅ Сохранить демо-заказ",
        callback_data=callbacks.OrderCallback(confirm=True),
    )
    keyboard.button(
        text="❌ Вернуться в корзину",
        callback_data=callbacks.OrderCallback(confirm=False),
    )
    keyboard.adjust(1, 1)
    return keyboard


def get_order_confirm_inline_keyboard() -> InlineKeyboardBuilder:
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text="🍕 Сделать ещё заказ",
        callback_data=callbacks.ReturnCallback(return_to="menu"),
    )
    keyboard.button(
        text="⬅️ На главную", callback_data=callbacks.ReturnCallback(return_to="start")
    )
    keyboard.adjust(1, 1)
    return keyboard


def get_owner_inline_keyboard() -> InlineKeyboardBuilder:
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="📩 Написать разработчику", url=settings.tg_url)
    keyboard.button(
        text="⬅️ Назад", callback_data=callbacks.ReturnCallback(return_to="start")
    )
    keyboard.adjust(1, 1)
    return keyboard


def get_contact_inline_keyboard() -> InlineKeyboardBuilder:
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="📩 Открыть Telegram", url=settings.tg_url)
    keyboard.button(
        text="⬅️ Назад", callback_data=callbacks.ReturnCallback(return_to="start")
    )
    keyboard.adjust(1, 1)
    return keyboard
