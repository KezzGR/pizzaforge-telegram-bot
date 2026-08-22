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

    def test_cart_keyboard_has_quantity_controls_and_safe_clear(self) -> None:
        cart = [
            CartItem(id=2, name="Пепперони", emoji="🌶️", price=550, quantity=2)
        ]

        markup = keyboards.get_cart_inline_keyboard(cart).as_markup()
        buttons = [button for row in markup.inline_keyboard for button in row]

        self.assertEqual(buttons[0].callback_data, "cartitem:2:decrease")
        self.assertEqual(buttons[1].text, "🌶️ 2 шт.")
        self.assertEqual(buttons[2].callback_data, "cartitem:2:increase")
        self.assertIn(
            "event:clear_request", [button.callback_data for button in buttons]
        )

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
