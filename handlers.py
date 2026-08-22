from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, FSInputFile, Message
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

import cached_keyboards as keyboards
import cached_messages as messages
import callbacks
from catalog import CATEGORY_INFO
from db.repositories import ProductRepository
from logger import logger
from services.cart_service import CartService
from services.order_service import OrderService

router = Router(name=__name__)


async def _show_cart(
    query: CallbackQuery, state: FSMContext, page: int = 0
) -> None:
    cart = CartService.from_state(await state.get_data())
    items = cart.get_items()
    normalized_page = messages.normalize_cart_page(items, page)
    await query.message.edit_text(
        **messages.get_cart_message_text(items, normalized_page).as_kwargs(),
        reply_markup=keyboards.get_cart_inline_keyboard(
            items, normalized_page
        ).as_markup(),
    )


@router.message(CommandStart())
async def start(message: Message, state: FSMContext) -> None:
    cart_service = CartService.from_state(await state.get_data())

    await message.answer_photo(
        FSInputFile("images/banner.png"),
        disable_notification=True,
    )
    await message.answer(
        **messages.start_message.as_kwargs(),
        reply_markup=keyboards.get_start_inline_keyboard(cart_service).as_markup(),
    )


@router.callback_query(callbacks.ReturnCallback.filter(F.return_to == "start"))
async def return_to_start(query: CallbackQuery, state: FSMContext) -> None:
    cart_service = CartService.from_state(await state.get_data())

    await query.answer()
    await query.message.edit_text(
        **messages.start_message.as_kwargs(),
        reply_markup=keyboards.get_start_inline_keyboard(cart_service).as_markup(),
    )


@router.callback_query(callbacks.StartCallback.filter(F.choice == "menu"))
@router.callback_query(callbacks.ReturnCallback.filter(F.return_to == "menu"))
async def menu(query: CallbackQuery, state: FSMContext) -> None:
    cart_service = CartService.from_state(await state.get_data())

    await query.answer()
    await query.message.edit_text(
        **messages.menu_message.as_kwargs(),
        reply_markup=keyboards.get_menu_inline_keyboard(cart_service).as_markup(),
    )


@router.callback_query(callbacks.StartCallback.filter(F.choice == "cart"))
@router.callback_query(callbacks.ReturnCallback.filter(F.return_to == "cart"))
async def cart(query: CallbackQuery, state: FSMContext) -> None:
    await query.answer()
    await _show_cart(query, state)


@router.callback_query(callbacks.CartPageCallback.filter())
async def show_cart_page(
    query: CallbackQuery,
    callback_data: callbacks.CartPageCallback,
    state: FSMContext,
) -> None:
    if callback_data.page < 0:
        await query.answer("Листайте корзину стрелками")
        return

    await query.answer()
    await _show_cart(query, state, callback_data.page)


@router.callback_query(callbacks.StartCallback.filter(F.choice == "owner"))
async def owner(query: CallbackQuery) -> None:
    await query.answer()
    await query.message.edit_text(
        **messages.owner_message.as_kwargs(),
        reply_markup=keyboards.get_owner_inline_keyboard().as_markup(),
    )


@router.callback_query(callbacks.StartCallback.filter(F.choice == "contact"))
async def contact(query: CallbackQuery) -> None:
    await query.answer()
    await query.message.edit_text(
        **messages.contact_message.as_kwargs(),
        reply_markup=keyboards.get_contact_inline_keyboard().as_markup(),
    )


@router.callback_query(callbacks.MenuCallback.filter())
async def category(
    query: CallbackQuery,
    callback_data: callbacks.MenuCallback,
    state: FSMContext,
    session: AsyncSession,
) -> None:
    if callback_data.category not in CATEGORY_INFO:
        await query.answer("Неизвестная категория", show_alert=True)
        return

    products = await ProductRepository(session).list_active_by_category(
        callback_data.category
    )
    cart_service = CartService.from_state(await state.get_data())
    await query.answer()
    await query.message.edit_text(
        **messages.get_category_message(callback_data.category).as_kwargs(),
        reply_markup=keyboards.get_products_inline_keyboard(
            products, cart_service
        ).as_markup(),
    )


@router.callback_query(callbacks.InCartCallback.filter())
async def add_to_cart(
    query: CallbackQuery,
    callback_data: callbacks.InCartCallback,
    state: FSMContext,
    session: AsyncSession,
) -> None:
    repository = ProductRepository(session)
    product = await repository.get_active_by_id(callback_data.product_id)
    cart_service = CartService.from_state(await state.get_data())

    if product is None:
        await query.answer(
            "Товар не найден или больше недоступен", show_alert=True
        )
        return

    item = cart_service.add_product(product)
    await state.update_data(cart=cart_service.get_cart_data())
    products = await repository.list_active_by_category(product.category)
    await query.answer(f"✅ {item.name} · {item.quantity} шт. в корзине")
    await query.message.edit_reply_markup(
        reply_markup=keyboards.get_products_inline_keyboard(
            products, cart_service
        ).as_markup()
    )


@router.callback_query(callbacks.CartEditCallback.filter())
async def edit_cart_item(
    query: CallbackQuery,
    callback_data: callbacks.CartEditCallback,
    state: FSMContext,
) -> None:
    cart_service = CartService.from_state(await state.get_data())
    try:
        item = cart_service.get_item(callback_data.product_id)
    except ValueError as error:
        await query.answer(str(error), show_alert=True)
        await _show_cart(query, state, callback_data.page)
        return

    await query.answer()
    await query.message.edit_text(
        **messages.get_cart_item_message(item).as_kwargs(),
        reply_markup=keyboards.get_cart_item_inline_keyboard(
            item, callback_data.page
        ).as_markup(),
    )


@router.callback_query(callbacks.CartQuantityCallback.filter())
async def change_cart_item_quantity(
    query: CallbackQuery,
    callback_data: callbacks.CartQuantityCallback,
    state: FSMContext,
) -> None:
    cart_service = CartService.from_state(await state.get_data())

    if callback_data.action == "details":
        try:
            item = cart_service.get_item(callback_data.product_id)
        except ValueError as error:
            await query.answer(str(error), show_alert=True)
            return
        await query.answer(
            f"{item.name} · {item.quantity} шт. · "
            f"{messages.format_money(item.total_price)} ₽"
        )
        return

    removed = False
    try:
        if callback_data.action == "increase":
            item = cart_service.increase_quantity(callback_data.product_id)
            notification = f"{item.name}: {item.quantity} шт."
        elif callback_data.action == "decrease":
            item, removed = cart_service.decrease_quantity(callback_data.product_id)
            notification = (
                f"Удалено из корзины: {item.name}"
                if removed
                else f"{item.name}: {item.quantity} шт."
            )
        elif callback_data.action == "remove":
            item = cart_service.remove_item(callback_data.product_id)
            removed = True
            notification = f"Удалено из корзины: {item.name}"
        else:
            await query.answer("Неизвестное действие", show_alert=True)
            return
    except ValueError as error:
        await query.answer(str(error), show_alert=True)
        return

    await state.update_data(cart=cart_service.get_cart_data())
    await query.answer(notification)
    if removed:
        await _show_cart(query, state, callback_data.page)
        return

    await query.message.edit_text(
        **messages.get_cart_item_message(item).as_kwargs(),
        reply_markup=keyboards.get_cart_item_inline_keyboard(
            item, callback_data.page
        ).as_markup(),
    )


@router.callback_query(callbacks.CartEventCallback.filter(F.event == "order"))
async def order(
    query: CallbackQuery,
    callback_data: callbacks.CartEventCallback,
    state: FSMContext,
) -> None:
    cart_service = CartService.from_state(await state.get_data())
    if cart_service.is_empty():
        await query.answer("Корзина пуста", show_alert=True)
        return

    await query.answer()
    await query.message.edit_text(
        **messages.get_order_message_text(cart_service.get_items()).as_kwargs(),
        reply_markup=keyboards.get_order_inline_keyboard(
            callback_data.page
        ).as_markup(),
    )


@router.callback_query(callbacks.CartEventCallback.filter(F.event == "clear_request"))
async def request_clear_cart(
    query: CallbackQuery,
    callback_data: callbacks.CartEventCallback,
    state: FSMContext,
) -> None:
    cart_service = CartService.from_state(await state.get_data())
    if cart_service.is_empty():
        await query.answer("Корзина уже пуста", show_alert=True)
        return

    await query.answer()
    await query.message.edit_text(
        **messages.get_clear_cart_message(cart_service.get_items()).as_kwargs(),
        reply_markup=keyboards.get_clear_cart_inline_keyboard(
            callback_data.page
        ).as_markup(),
    )


@router.callback_query(callbacks.CartEventCallback.filter(F.event == "clear_confirm"))
async def confirm_clear_cart(query: CallbackQuery, state: FSMContext) -> None:
    cart_service = CartService.from_state(await state.get_data())
    cart_service.clear()
    await state.update_data(cart=cart_service.get_cart_data())
    await query.answer("Корзина очищена")
    await _show_cart(query, state)


@router.callback_query(callbacks.CartEventCallback.filter(F.event == "clear_cancel"))
async def cancel_clear_cart(
    query: CallbackQuery,
    callback_data: callbacks.CartEventCallback,
    state: FSMContext,
) -> None:
    await query.answer()
    await _show_cart(query, state, callback_data.page)


@router.callback_query(callbacks.OrderCallback.filter(F.confirm == True))
async def confirm_order(
    query: CallbackQuery, state: FSMContext, session: AsyncSession
) -> None:
    cart_service = CartService.from_state(await state.get_data())
    if cart_service.is_empty():
        await query.answer("Корзина уже пуста", show_alert=True)
        return

    try:
        order_id = await OrderService(session).create_demo_order(
            telegram_user_id=query.from_user.id,
            cart=cart_service.get_items(),
        )
    except SQLAlchemyError:
        logger.exception("Не удалось сохранить демо-заказ")
        await query.answer(
            "База данных временно недоступна. Попробуйте ещё раз.", show_alert=True
        )
        return

    cart_service.clear()
    await state.update_data(cart=cart_service.get_cart_data())
    await query.answer("Демо-заказ сохранён")
    await query.message.edit_text(
        **messages.get_order_confirm_message(order_id).as_kwargs(),
        reply_markup=keyboards.get_order_confirm_inline_keyboard().as_markup(),
    )


@router.callback_query(callbacks.OrderCallback.filter(F.confirm == False))
async def cancel_order(
    query: CallbackQuery,
    callback_data: callbacks.OrderCallback,
    state: FSMContext,
) -> None:
    await query.answer()
    await _show_cart(query, state, callback_data.page)
