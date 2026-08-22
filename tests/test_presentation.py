import unittest

import cached_keyboards as keyboards
import cached_messages as messages
from models.cart import CartItem
from models.product import Product


class PresentationTests(unittest.TestCase):
    def test_product_keyboard_is_built_from_catalog(self) -> None:
        products = [
            Product(
                id=1,
                name="Маргарита",
                emoji="🍕",
                category="pizza",
                price=450,
            )
        ]

        markup = keyboards.get_products_inline_keyboard(products).as_markup()
        buttons = [button for row in markup.inline_keyboard for button in row]

        self.assertEqual(len(buttons), 3)
        self.assertIn("Маргарита", buttons[0].text)
        self.assertEqual(buttons[0].callback_data, "incart:1")

    def test_confirmation_contains_database_order_id(self) -> None:
        text = messages.get_order_confirm_message(42).as_kwargs()["text"]

        self.assertIn("№42", text)
        self.assertIn("PostgreSQL", text)

    def test_cart_message_contains_total(self) -> None:
        cart = [CartItem(id=1, name="Маргарита", emoji="🍕", price=450, quantity=2)]

        text = messages.get_cart_message_text(cart).as_kwargs()["text"]

        self.assertIn("900 ₽", text)


if __name__ == "__main__":
    unittest.main()
