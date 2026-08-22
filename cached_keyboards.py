from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

import callbacks
import cached_messages as messages
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
        text="← К категориям",
        callback_data=callbacks.ReturnCallback(return_to="menu"),
    )
    keyboard.adjust(*([1] * len(products)), 1, 1)
    return keyboard


def get_cart_inline_keyboard(
    cart: list[CartItem], page: int = 0
) -> InlineKeyboardBuilder:
    keyboard = InlineKeyboardBuilder()
    if not cart:
        keyboard.button(
            text="🍕 Выбрать блюда",
            callback_data=callbacks.ReturnCallback(return_to="menu"),
        )
        keyboard.button(
            text="🏠 На главную",
            callback_data=callbacks.ReturnCallback(return_to="start"),
        )
        keyboard.adjust(1, 1)
        return keyboard

    normalized_page = messages.normalize_cart_page(cart, page)
    page_items = messages.get_cart_page_items(cart, normalized_page)
    page_count = messages.get_cart_page_count(cart)

    for item in page_items:
        keyboard.row(
            InlineKeyboardButton(
                text=f"{item.emoji} {item.name} · {item.quantity} шт.",
                callback_data=callbacks.CartEditCallback(
                    product_id=item.id, page=normalized_page
                ).pack(),
            )
        )

    if page_count > 1:
        navigation: list[InlineKeyboardButton] = []
        if normalized_page > 0:
            navigation.append(
                InlineKeyboardButton(
                    text="←",
                    callback_data=callbacks.CartPageCallback(
                        page=normalized_page - 1
                    ).pack(),
                )
            )
        navigation.append(
            InlineKeyboardButton(
                text=f"{normalized_page + 1} / {page_count}",
                callback_data=callbacks.CartPageCallback(page=-1).pack(),
            )
        )
        if normalized_page < page_count - 1:
            navigation.append(
                InlineKeyboardButton(
                    text="→",
                    callback_data=callbacks.CartPageCallback(
                        page=normalized_page + 1
                    ).pack(),
                )
            )
        keyboard.row(*navigation)

    keyboard.row(
        InlineKeyboardButton(
            text="📦 К оформлению",
            callback_data=callbacks.CartEventCallback(
                event="order", page=normalized_page
            ).pack(),
        )
    )
    keyboard.row(
        InlineKeyboardButton(
            text="🍕 Добавить",
            callback_data=callbacks.ReturnCallback(return_to="menu").pack(),
        ),
        InlineKeyboardButton(
            text="🗑 Очистить",
            callback_data=callbacks.CartEventCallback(
                event="clear_request", page=normalized_page
            ).pack(),
        ),
    )
    keyboard.row(
        InlineKeyboardButton(
            text="🏠 На главную",
            callback_data=callbacks.ReturnCallback(return_to="start").pack(),
        )
    )
    return keyboard


def get_cart_item_inline_keyboard(
    item: CartItem, page: int
) -> InlineKeyboardBuilder:
    keyboard = InlineKeyboardBuilder()
    keyboard.row(
        InlineKeyboardButton(
            text="−",
            callback_data=callbacks.CartQuantityCallback(
                product_id=item.id, action="decrease", page=page
            ).pack(),
        ),
        InlineKeyboardButton(
            text=f"{item.quantity} шт.",
            callback_data=callbacks.CartQuantityCallback(
                product_id=item.id, action="details", page=page
            ).pack(),
        ),
        InlineKeyboardButton(
            text="+",
            callback_data=callbacks.CartQuantityCallback(
                product_id=item.id, action="increase", page=page
            ).pack(),
        ),
    )
    keyboard.row(
        InlineKeyboardButton(
            text="🗑 Удалить позицию",
            callback_data=callbacks.CartQuantityCallback(
                product_id=item.id, action="remove", page=page
            ).pack(),
        )
    )
    keyboard.row(
        InlineKeyboardButton(
            text="← Вернуться в корзину",
            callback_data=callbacks.CartPageCallback(page=page).pack(),
        )
    )
    return keyboard


def get_clear_cart_inline_keyboard(page: int) -> InlineKeyboardBuilder:
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text="🗑 Да, очистить",
        callback_data=callbacks.CartEventCallback(event="clear_confirm", page=page),
    )
    keyboard.button(
        text="← Оставить товары",
        callback_data=callbacks.CartEventCallback(event="clear_cancel", page=page),
    )
    keyboard.adjust(1, 1)
    return keyboard


def get_order_inline_keyboard(page: int) -> InlineKeyboardBuilder:
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text="✅ Подтвердить заказ",
        callback_data=callbacks.OrderCallback(confirm=True, page=page),
    )
    keyboard.button(
        text="← Изменить корзину",
        callback_data=callbacks.OrderCallback(confirm=False, page=page),
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
    keyboard.button(text="💬 Обсудить свой проект", url=settings.tg_url)
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
