import unittest

import cached_keyboards as keyboards
import cached_messages as messages
from models.cart import CartItem
from models.product import Product
from services.cart_service import CartService


class PresentationTests(unittest.TestCase):
    def test_product_keyboard_is_built_from_catalog(self) -> None:
        products = [
            Product(
                id=1,
                name="Маргарита",
                emoji="🍅",
                category="pizza",
                price=450,
            )
        ]

        markup = keyboards.get_products_inline_keyboard(
            products, CartService([])
        ).as_markup()
        buttons = [button for row in markup.inline_keyboard for button in row]

        self.assertEqual(len(buttons), 3)
        self.assertIn("Маргарита", buttons[0].text)
        self.assertEqual(buttons[0].callback_data, "incart:1")
        self.assertEqual(buttons[1].text, "🛒 Корзина · 0")

    def test_cart_keyboard_opens_item_editor_and_has_safe_clear(self) -> None:
        cart = [
            CartItem(id=2, name="Пепперони", emoji="🌶️", price=550, quantity=2)
        ]

        markup = keyboards.get_cart_inline_keyboard(cart).as_markup()
        buttons = [button for row in markup.inline_keyboard for button in row]

        self.assertEqual(buttons[0].callback_data, "cartedit:2:0")
        self.assertIn("Пепперони", buttons[0].text)
        self.assertIn(
            "event:clear_request:0", [button.callback_data for button in buttons]
        )

    def test_cart_page_is_preserved_in_clear_and_checkout_actions(self) -> None:
        cart = [
            CartItem(
                id=index,
                name=f"Позиция {index}",
                emoji="🍽️",
                price=100,
                quantity=1,
            )
            for index in range(1, 5)
        ]

        cart_markup = keyboards.get_cart_inline_keyboard(cart, page=1).as_markup()
        cart_callbacks = [
            button.callback_data
            for row in cart_markup.inline_keyboard
            for button in row
        ]
        clear_markup = keyboards.get_clear_cart_inline_keyboard(page=1).as_markup()
        clear_callbacks = [
            button.callback_data
            for row in clear_markup.inline_keyboard
            for button in row
        ]
        order_markup = keyboards.get_order_inline_keyboard(page=1).as_markup()
        order_callbacks = [
            button.callback_data
            for row in order_markup.inline_keyboard
            for button in row
        ]

        self.assertIn("event:order:1", cart_callbacks)
        self.assertIn("event:clear_request:1", cart_callbacks)
        self.assertIn("event:clear_cancel:1", clear_callbacks)
        self.assertIn("order:0:1", order_callbacks)

    def test_cart_item_keyboard_has_quantity_controls(self) -> None:
        item = CartItem(
            id=2, name="Пепперони", emoji="🌶️", price=550, quantity=2
        )

        markup = keyboards.get_cart_item_inline_keyboard(item, page=0).as_markup()
        buttons = [button for row in markup.inline_keyboard for button in row]

        self.assertEqual(buttons[0].callback_data, "cartqty:2:decrease:0")
        self.assertEqual(buttons[1].text, "2 шт.")
        self.assertEqual(buttons[2].callback_data, "cartqty:2:increase:0")
        self.assertIn("cartqty:2:remove:0", [button.callback_data for button in buttons])

    def test_cart_is_paginated_by_three_positions(self) -> None:
        cart = [
            CartItem(
                id=index,
                name=f"Позиция {index}",
                emoji="🍽️",
                price=100,
                quantity=1,
            )
            for index in range(1, 5)
        ]

        first_page = messages.get_cart_message_text(cart, page=0).as_kwargs()["text"]
        second_page = messages.get_cart_message_text(cart, page=1).as_kwargs()["text"]
        markup = keyboards.get_cart_inline_keyboard(cart, page=0).as_markup()
        buttons = [button for row in markup.inline_keyboard for button in row]

        self.assertIn("Позиция 3", first_page)
        self.assertNotIn("Позиция 4", first_page)
        self.assertIn("Позиция 4", second_page)
        self.assertIn("Показаны позиции 1–3 из 4", first_page)
        self.assertIn("cartpage:1", [button.callback_data for button in buttons])

    def test_order_preview_is_limited_to_five_positions(self) -> None:
        cart = [
            CartItem(
                id=index,
                name=f"Позиция {index}",
                emoji="🍽️",
                price=100,
                quantity=1,
            )
            for index in range(1, 7)
        ]

        text = messages.get_order_message_text(cart).as_kwargs()["text"]

        self.assertIn("Позиция 5", text)
        self.assertNotIn("Позиция 6", text)
        self.assertIn("Ещё позиций: 1", text)

    def test_clear_confirmation_contains_quantity_and_total(self) -> None:
        cart = [
            CartItem(id=2, name="Пепперони", emoji="🌶️", price=550, quantity=2)
        ]

        text = messages.get_clear_cart_message(cart).as_kwargs()["text"]

        self.assertIn("2 шт.", text)
        self.assertIn("1 100 ₽", text)

    def test_confirmation_contains_database_order_id(self) -> None:
        text = messages.get_order_confirm_message(42).as_kwargs()["text"]

        self.assertIn("№42", text)
        self.assertIn("PostgreSQL", text)

    def test_cart_message_contains_total(self) -> None:
        cart = [CartItem(id=1, name="Маргарита", emoji="🍅", price=450, quantity=2)]

        text = messages.get_cart_message_text(cart).as_kwargs()["text"]

        self.assertIn("900 ₽", text)

    def test_cart_message_formats_thousands_with_spaces(self) -> None:
        cart = [
            CartItem(id=2, name="Пепперони", emoji="🌶️", price=550, quantity=2)
        ]

        text = messages.get_cart_message_text(cart).as_kwargs()["text"]

        self.assertIn("1 100 ₽", text)
        self.assertNotIn("1,100 ₽", text)


if __name__ == "__main__":
    unittest.main()
